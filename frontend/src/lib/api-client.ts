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
  ApiResponse
} from './api-types';

// Create a client with proper caching and retry logic
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 30 * 60 * 1000,
      retry: (failureCount, error: any) => {
        if (error.status === 404 || error.status === 401 || error.status === 403) {
          return false;
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080/api/v1';

if (import.meta.env.PROD) {
  console.log('[API] Using base URL:', API_BASE);
}

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

    if (isDebug) {
      console.debug('[API Response]', {
        status: response.status,
        statusText: response.statusText,
        url: response.url,
        headers: {
          'content-type': response.headers.get('content-type'),
          'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
        }
      });
    }

    // Handle 401 Unauthorized
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('current_user');
      window.location.href = '/login';
      throw new ApiError(401, 'Session expired. Please log in again.');
    }

    // Handle 204 No Content (successful DELETE operations)
    if (response.status === 204) {
      console.log('[API Success] 204 No Content - Operation completed successfully', {
        url: response.url,
        method: 'DELETE'
      });
      return null as T;
    }

    // Handle responses with body
    let data: any;
    const text = await response.text();

    try {
      data = text ? JSON.parse(text) : null;
      if (isDebug) {
        console.debug('[API Response Data]', data);
      }
    } catch (error) {
      console.error('[API Parse Error]', {
        error,
        responseText: text,
        status: response.status,
        url: response.url
      });

      // If response is not OK and we can't parse it, throw error
      if (!response.ok) {
        throw new ApiError(
          response.status,
          `Server error: ${response.statusText}`,
          { responseText: text }
        );
      }

      throw new ApiError(
        response.status,
        'Invalid JSON response from server'
      );
    }

    if (!response.ok) {
      const errorMessage = data?.detail || data?.message || response.statusText;
      console.error('[API Error]', {
        status: response.status,
        message: errorMessage,
        url: response.url,
        data
      });

      throw new ApiError(
        response.status,
        errorMessage,
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

  // Leaders
  async getLeaders(params?: QueryParams): Promise<any> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Leader[]>(`/leaders/${qs}`);
    // Normalization to match legacy expectations
    const leaders = Array.isArray(response) ? response : [];
    return {
      leaders,
      items: leaders,
      total: leaders.length,
    };
  }

  async createLeader(data: Partial<Leader>): Promise<ApiResponse<Leader>> {
    const response = await this.fetchJson<Leader>('/leaders/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, leader: response, data: response };
  }

  async getOrdersByLeader(leaderId: string): Promise<Order[]> {
    const response = await this.fetchJson<Order[]>(`/leaders/${leaderId}/orders`);
    const orders = Array.isArray(response) ? response : [];

    // Normalize orders to match frontend expectations
    return orders.map((order: any) => {
      const totalAmount = Number(order.totalAmount || order.total_amount || 0);
      const paidAmount = Number(order.paidAmount || order.paid_amount || 0);
      const balance = Number(order.balance ?? (totalAmount - paidAmount));

      return {
        ...order,
        orderNumber: order.orderNumber || order.order_number || 'N/A',
        totalAmount,
        paidAmount,
        balance,
        orderDate: order.orderDate || order.order_date || new Date().toISOString()
      };
    });
  }

  // Orders
  async getOrders(params?: QueryParams): Promise<any> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Order[]>(`/orders/${qs}`);

    const orders = Array.isArray(response) ? response : [];
    const normalizedOrders = orders.map((order: any) => {
      const totalAmount = Number(order.totalAmount || order.total_amount || 0);
      const paidAmount = Number(order.paidAmount || order.paid_amount || 0);
      const balance = Number(order.balance ?? (totalAmount - paidAmount));

      return {
        ...order,
        orderNumber: order.orderNumber || order.order_number || 'N/A',
        totalAmount,
        paidAmount,
        balance,
        orderDate: order.orderDate || order.order_date || new Date().toISOString()
      };
    });

    return {
      orders: normalizedOrders,
      items: normalizedOrders,
      total: normalizedOrders.length,
    };
  }

  async createOrder(data: any): Promise<ApiResponse<Order>> {
    const response = await this.fetchJson<Order>('/orders/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, order: response, data: response };
  }

  async updateOrder(orderId: string, data: any): Promise<ApiResponse<Order>> {
    const response = await this.fetchJson<Order>(`/orders/${orderId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return { success: true, order: response, data: response };
  }

  async deleteOrder(orderId: string): Promise<void> {
    await this.fetchJson<void>(`/orders/${orderId}`, {
      method: 'DELETE',
    });
  }

  async getOrderPaymentSummary(orderId: string): Promise<any> {
    return await this.fetchJson<any>(`/orders/${orderId}/payment-summary`);
  }

  // Products
  async getProducts(params?: QueryParams): Promise<any> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Product[]>(`/products/${qs}`);
    const products = Array.isArray(response) ? response : [];
    return {
      products,
      items: products,
      total: products.length,
    };
  }

  async createProduct(data: Partial<Product>): Promise<ApiResponse<Product>> {
    const response = await this.fetchJson<Product>('/products/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, product: response, data: response };
  }

  // Payments
  async getPayments(params?: QueryParams): Promise<any> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<Payment[]>(`/payments/${qs}`);
    const payments = Array.isArray(response) ? response : [];

    const normalizedPayments = payments.map((payment: any) => ({
      ...payment,
      amount: Number(payment.amount || 0),
      paymentDate: payment.paymentDate || payment.payment_date || new Date().toISOString()
    }));

    return {
      payments: normalizedPayments,
      items: normalizedPayments,
      total: normalizedPayments.length,
    };
  }

  async createPayment(data: any): Promise<ApiResponse<Payment>> {
    const response = await this.fetchJson<Payment>('/payments/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, payment: response, data: response };
  }

  async updatePayment(paymentId: string, data: any): Promise<any> {
    return this.fetchJson<any>(`/payments/${paymentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePayment(paymentId: string): Promise<void> {
    console.log('[API] Deleting payment:', paymentId);

    try {
      await this.fetchJson<void>(`/payments/${paymentId}`, {
        method: 'DELETE',
      });

      console.log('[API] Payment deleted successfully:', paymentId);
    } catch (error: any) {
      console.error('[API] Failed to delete payment:', {
        paymentId,
        error: error.message,
        status: error.status,
        data: error.data
      });

      // Re-throw with enhanced error message
      if (error instanceof ApiError) {
        throw new ApiError(
          error.status,
          `Failed to delete payment: ${error.message}`,
          error.data
        );
      }
      throw error;
    }
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
    const filename = `receipt-${paymentId}.pdf`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // Expenses
  async getExpenses(params?: QueryParams): Promise<any> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await this.fetchJson<any[]>(`/expenses/${qs}`);
    const expenses = Array.isArray(response) ? response : [];
    return {
      expenses,
      items: expenses,
      total: expenses.length
    };
  }

  async createExpense(data: any): Promise<any> {
    return this.fetchJson<any>('/expenses/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateExpense(id: string, data: any): Promise<any> {
    return this.fetchJson<any>(`/expenses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteExpense(id: string): Promise<void> {
    await this.fetchJson<void>(`/expenses/${id}`, {
      method: 'DELETE',
    });
  }

  // Business logic
  async getLeaderLedger(leaderId: string): Promise<any> {
    return await this.fetchJson<any>(`/leaders/${leaderId}/ledger`);
  }

  async getDashboardData(params?: QueryParams): Promise<DashboardData> {
    const qs = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    return await this.fetchJson<DashboardData>(`/dashboard/stats${qs}`);
  }

  // Settings
  async getSettings(): Promise<Settings> {
    return await this.fetchJson<Settings>('/settings/');
  }

  async updateSettings(data: SettingsUpdate): Promise<Settings> {
    return await this.fetchJson<Settings>('/settings/', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiClient();