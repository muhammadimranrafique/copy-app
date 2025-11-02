// API client that can fall back to mock data. Set VITE_USE_MOCK=true to use the built-in mocks.
import { mockOrders, mockLeaders, mockProducts, mockPayments, mockExpenses } from './mock-data';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJSON(path: string, opts: RequestInit = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { 'Content-Type': 'application/json', ...getAuthHeaders(), ...(opts.headers || {}) } as Record<string,string>;

  // Debug logging: Log the request
  const isDebug = import.meta.env.VITE_DEBUG === 'true';
  if (isDebug) {
    // eslint-disable-next-line no-console
    console.debug('[API Request]', opts.method || 'GET', url, opts.body ? JSON.parse(opts.body as string) : '');
  }

  const res = await fetch(url, { ...opts, headers });

  // Debug logging: Log the response status
  if (isDebug) {
    // eslint-disable-next-line no-console
    console.debug('[API Response]', res.status, res.statusText, url);
  }

  // Special handling of auth errors to trigger logout
  if (res.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    if (isDebug) {
      // eslint-disable-next-line no-console
      console.debug('[API Error Body]', url, body);
    }
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }

  // Handle 204 No Content
  if (res.status === 204) {
    if (isDebug) {
      // eslint-disable-next-line no-console
      console.debug('[API Response Body]', url, '=> (204 No Content)');
    }
    return null;
  }

  // Read response text once and parse it
  try {
    const text = await res.text();

    if (isDebug) {
      // eslint-disable-next-line no-console
      console.debug('[API Response Text]', url, '=>', text.substring(0, 500) + (text.length > 500 ? '...' : ''));
    }

    // Try to parse as JSON
    const isJson = text && (text.trim().startsWith('{') || text.trim().startsWith('['));
    if (isJson) {
      try {
        const parsed = JSON.parse(text);
        if (isDebug) {
          // eslint-disable-next-line no-console
          console.debug('[API Response JSON]', url, '=>', parsed);
        }
        return parsed;
      } catch (parseError) {
        if (isDebug) {
          // eslint-disable-next-line no-console
          console.error('[API JSON Parse Error]', url, parseError, 'Raw text:', text);
        }
        throw new Error(`Failed to parse JSON response: ${parseError}`);
      }
    } else {
      // Not JSON, return as text
      if (isDebug) {
        // eslint-disable-next-line no-console
        console.debug('[API Response (non-JSON)]', url, '=>', text);
      }
      return text;
    }
  } catch (e) {
    if (isDebug) {
      // eslint-disable-next-line no-console
      console.error('[API Fetch Error]', url, e);
    }
    throw e;
  }
}

export async function getOrders(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { orders: mockOrders };
  }
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const res = await fetchJSON(`/orders/${qs}`);
  // backend returns an array of orders; normalize to { orders }
  return { orders: Array.isArray(res) ? res : (res?.orders ?? []) };
}

export async function createOrder(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, order: { id: Date.now().toString(), ...data } };
  }
  const res = await fetchJSON('/orders/', { method: 'POST', body: JSON.stringify(data) });
  return { success: true, order: res };
}

export async function getLeaders(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { leaders: mockLeaders };
  }
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const res = await fetchJSON(`/leaders/${qs}`);
  return { leaders: Array.isArray(res) ? res : (res?.leaders ?? []) };
}

export async function createLeader(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, leader: { id: Date.now().toString(), ...data } };
  }
  const res = await fetchJSON('/leaders/', { method: 'POST', body: JSON.stringify(data) });
  return { success: true, leader: res };
}

export async function getProducts(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { products: mockProducts };
  }
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const res = await fetchJSON(`/products/${qs}`);
  return { products: Array.isArray(res) ? res : (res?.products ?? []) };
}

export async function createProduct(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, product: { id: Date.now().toString(), ...data } };
  }
  const res = await fetchJSON('/products/', { method: 'POST', body: JSON.stringify(data) });
  return { success: true, product: res };
}

export async function getPayments(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { payments: mockPayments };
  }
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const res = await fetchJSON(`/payments/${qs}`);
  return { payments: Array.isArray(res) ? res : (res?.payments ?? []) };
}

export async function createPayment(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, payment: { id: Date.now().toString(), ...data } };
  }
  const res = await fetchJSON('/payments/', { method: 'POST', body: JSON.stringify(data) });
  return { success: true, payment: res };
}

export async function getDashboardData(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    // Calculate totals
    const totalOrders = mockOrders.length;
    const totalRevenue = mockOrders.reduce((sum, order) => sum + (order.totalAmount || 0), 0);
    const totalPayments = mockPayments.reduce((sum, payment) => sum + (payment.amount || 0), 0);
    const netProfit = totalRevenue - totalPayments;
    return {
      totalOrders,
      totalRevenue,
      totalPayments,
      netProfit,
      recentOrders: mockOrders.slice(0, 5),
      recentPayments: mockPayments.slice(0, 5)
    };
  }
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const res = await fetchJSON(`/dashboard/${qs}`);
  return res;
}

export async function getExpenses(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { expenses: mockExpenses };
  }
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const res = await fetchJSON(`/expenses/${qs}`);
  return { expenses: Array.isArray(res) ? res : (res?.expenses ?? []) };
}

export async function createExpense(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, expense: { id: Date.now().toString(), ...data } };
  }
  const res = await fetchJSON('/expenses/', { method: 'POST', body: JSON.stringify(data) });
  return { success: true, expense: res };
}

export async function updateExpense(id: string, data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, expense: { id, ...data } };
  }
  const res = await fetchJSON(`/expenses/${id}/`, { method: 'PUT', body: JSON.stringify(data) });
  return { success: true, expense: res };
}

export async function deleteExpense(id: string) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true };
  }
  await fetchJSON(`/expenses/${id}`, { method: 'DELETE' });
  return { success: true };
}

// Type exports kept for compatibility
export type Order = { id: string; orderNumber?: string; leaderId?: string; orderDate?: string; totalAmount?: number; status?: string };
export type Leader = { id: string; name: string; type: string; contact: string; address: string; openingBalance: number };
export type Product = { id: string; productName?: string; category?: string; costPrice?: number; salePrice?: number; stockQuantity?: number; unit?: string };
export type Payment = { id: string; amount?: number; method?: string; paymentDate?: string; leaderId?: string; referenceNumber?: string };
export type Expense = { id: string; category: string; amount: number; description: string; expenseDate: string; paymentMethod?: string; referenceNumber?: string };
