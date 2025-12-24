import { QueryClient } from '@tanstack/react-query';
import type {
  Leader,
  Order,
  Product,
  Payment,
  DashboardData,
  Settings,
  SettingsUpdate,
  QueryParams,
  ApiResponse,
  ListResponse
} from './api-types';

// Create a client with proper caching and retry logic
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
      gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 404s or auth errors
        if (error.status === 404 || error.status === 401 || error.status === 403) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 2, // Retry failed mutations twice
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080/api/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const isDebug = import.meta.env.VITE_DEBUG === 'true';

    // Debug logging
    if (isDebug) {
      console.debug('[API Response]', {
        status: response.status,
        statusText: response.statusText,
        url: response.url,
      });
    }

    // Handle auth errors
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('current_user');
      window.location.href = '/login';
      throw new ApiError(401, 'Session expired. Please log in again.');
    }

    // For 204 No Content
    if (response.status === 204) {
      return null as T;
    }

    // Try to parse response
    let data: any;
    const text = await response.text();

    try {
      data = text ? JSON.parse(text) : null;
      if (isDebug) {
        console.debug('[API Response Data]', data);
      }
    } catch (error) {
      console.error('[API Parse Error]', error);
      throw new ApiError(
        response.status,
        'Invalid JSON response from server'
      );
    }

    // Handle error responses
    if (!response.ok) {
      throw new ApiError(
        response.status,
        data?.message || response.statusText,
        data
      );
    }

    return data;
  }

  private async fetchJson<T>(
    endpoint: string,
    init: RequestInit = {}
  ): Promise<T> {
    const isDebug = import.meta.env.VITE_DEBUG === 'true';
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...(init.headers || {}),
    };

    const url = `${API_BASE}${endpoint}`;

    if (isDebug) {
      console.debug('[API Request]', {
        method: init.method || 'GET',
        url,
        body: init.body ? JSON.parse(init.body as string) : undefined,
      });
    }

    try {
      const response = await fetch(url, { ...init, headers });
      return await this.handleResponse<T>(response);
    } catch (error: any) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(0, `Network error: ${error.message}`);
    }
  }

  // Endpoint implementations with proper types
  async getLeaders(params?: QueryParams): Promise<ListResponse<Leader>> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Leader[]>(`/leaders/${qs}`);
    return {
      items: response,
      total: response.length,
    };
  }

  async createLeader(data: Partial<Leader>): Promise<ApiResponse<Leader>> {
    const response = await this.fetchJson<Leader>('/leaders/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, data: response };
  }

  async getOrders(params?: QueryParams): Promise<ListResponse<Order>> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Order[]>(`/orders/${qs}`);
    return {
      items: response,
      total: response.length,
    };
  }

  async createOrder(data: Partial<Order>): Promise<ApiResponse<Order>> {
    const response = await this.fetchJson<Order>('/orders/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, data: response };
  }

  async getProducts(params?: QueryParams): Promise<ListResponse<Product>> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Product[]>(`/products/${qs}`);
    return {
      items: response,
      total: response.length,
    };
  }

  async createProduct(data: Partial<Product>): Promise<ApiResponse<Product>> {
    const response = await this.fetchJson<Product>('/products/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, data: response };
  }

  async getPayments(params?: QueryParams): Promise<ListResponse<Payment>> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Payment[]>(`/payments/${qs}`);
    return {
      items: response,
      total: response.length,
    };
  }

  async createPayment(data: Partial<Payment>): Promise<ApiResponse<Payment>> {
    const response = await this.fetchJson<Payment>('/payments/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, data: response };
  }

  async getLeaderLedger(leaderId: string): Promise<any> {
    return await this.fetchJson<any>(`/leaders/${leaderId}/ledger`);
  }

  async getOrdersByLeader(leaderId: string): Promise<any[]> {
    return await this.fetchJson<any[]>(`/orders/school/${leaderId}`);
  }

  async getDashboardData(params?: QueryParams): Promise<DashboardData> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    return await this.fetchJson<DashboardData>(`/dashboard/stats${qs}`);
  }

  // Settings endpoints
  async getSettings(): Promise<Settings> {
    return await this.fetchJson<Settings>('/settings/');
  }

  async updateSettings(data: SettingsUpdate): Promise<Settings> {
    return await this.fetchJson<Settings>('/settings/', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
  async downloadPaymentReceipt(paymentId: string): Promise<void> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/payments/${paymentId}/receipt`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) throw new Error('Failed to download receipt');
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `receipt-${paymentId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  async updatePayment(paymentId: string, data: any): Promise<any> {
    return this.fetchJson<any>(`/payments/${paymentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePayment(paymentId: string): Promise<void> {
    await this.fetchJson<void>(`/payments/${paymentId}`, {
      method: 'DELETE',
    });
  }
}

// Export a singleton instance
export const api = new ApiClient();