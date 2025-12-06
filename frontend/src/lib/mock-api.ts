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
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...getAuthHeaders(),
    ...(opts.headers || {})
  } as Record<string, string>;

  // Add CORS mode and credentials
  opts.mode = 'cors';
  opts.credentials = 'include';

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
  try {
    const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
    const res = await fetchJSON(`/orders/${qs}`);

    // Debug logging for response
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Orders Response]', res);
    }

    // Normalize response to always return { orders: [] }
    const orders = Array.isArray(res) ? res : (res?.orders ?? []);

    // Define order type for proper typing
    type OrderResponse = {
      id: string;
      orderNumber: string;
      leaderId: string;
      leaderName?: string;
      totalAmount: number;
      paidAmount: number;
      balance: number;
      status: string;
      orderDate: string;
      createdAt: string;
    };

    // Debug logging
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Raw Orders Data]', orders);
    }

    // Ensure all required fields are present and properly formatted
    // CRITICAL: Include paidAmount and balance for payment tracking display
    const normalizedOrders = orders.map((order: any) => {
      const totalAmount = Number(order.totalAmount || order.total_amount || 0);
      const paidAmount = Number(order.paidAmount || order.paid_amount || 0);
      const balance = Number(order.balance ?? (totalAmount - paidAmount));

      return {
        id: order.id || '',
        orderNumber: order.orderNumber || order.order_number || 'N/A',
        leaderId: order.leaderId || order.client_id || '',
        leaderName: order.leaderName || 'N/A',
        totalAmount,
        paidAmount,
        balance,
        status: order.status || 'Pending',
        orderDate: order.orderDate || order.order_date || new Date().toISOString(),
        createdAt: order.createdAt || order.created_at || new Date().toISOString()
      };
    });

    return { orders: normalizedOrders };
  } catch (error) {
    console.error('[Orders API Error]', error);
    throw error;
  }
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

export async function getPayments(params: any = {}) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { payments: mockPayments };
  }
  try {
    const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
    const res = await fetchJSON(`/payments/${qs}`);

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Payments Response]', res);
    }

    // Normalize response to always return { payments: [] }
    const payments = Array.isArray(res) ? res : (res?.payments ?? []);

    // Ensure all required fields are present and properly formatted
    const normalizedPayments = payments.map((payment: any) => ({
      id: payment.id || '',
      amount: Number(payment.amount || 0),
      method: payment.method || 'Cash',
      status: payment.status || 'Completed',
      paymentDate: payment.paymentDate || new Date().toISOString(),
      createdAt: payment.createdAt || new Date().toISOString(),
      leaderId: payment.leaderId || '',
      orderId: payment.orderId || undefined,
      referenceNumber: payment.referenceNumber || undefined,
      client: payment.client ? {
        id: payment.client.id,
        name: payment.client.name,
        type: payment.client.type,
        contact: payment.client.contact,
        address: payment.client.address
      } : null
    }));

    return { payments: normalizedPayments };
  } catch (error) {
    console.error('[Payments API Error]', error);
    throw error;
  }
}

export async function createPayment(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, payment: { id: Date.now().toString(), ...data } };
  }

  try {
    // Validate required fields
    if (!data.amount || !data.method || !data.leaderId) {
      throw new Error('Missing required fields: amount, method, and leaderId are required');
    }

    // Format the payment data for the API
    const paymentData = {
      amount: Number(data.amount),
      method: data.method,  // Send as-is, backend will handle conversion
      leaderId: data.leaderId,
      paymentDate: data.paymentDate ? new Date(data.paymentDate).toISOString().split('T')[0] : undefined,
      referenceNumber: data.referenceNumber || undefined,
      orderId: data.orderId || undefined
    };

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Payment Request]', paymentData);
    }

    const res = await fetchJSON('/payments/', {
      method: 'POST',
      body: JSON.stringify(paymentData)
    });

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Payment Response]', res);
    }

    return { success: true, payment: res };
  } catch (error) {
    console.error('[Create Payment Error]', error);
    throw error;
  }
}

export async function downloadPaymentReceipt(paymentId: string): Promise<void> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 500));
    console.log('Mock: Would download receipt for payment', paymentId);
    return;
  }

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication required. Please log in again.');
    }

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Download Receipt Request]', { paymentId, hasToken: !!token });
    }

    // Make request to generate and download PDF
    const response = await fetch(`${API_BASE}/payments/${paymentId}/receipt`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Download Receipt Response]', { status: response.status, statusText: response.statusText });
    }

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      const errorText = await response.text();
      throw new Error(`Failed to download receipt: ${errorText}`);
    }

    // Get the filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `payment_receipt_${paymentId}.pdf`;

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Convert response to blob and trigger download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Download Receipt Success]', { filename });
    }
  } catch (error) {
    console.error('[Download Receipt Error]', error);
    throw error;
  }
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
  try {
    const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
    const res = await fetchJSON(`/dashboard/stats${qs}`);

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Dashboard Response]', res);
    }

    return res;
  } catch (error) {
    console.error('[Dashboard API Error]', error);
    throw error;
  }
}

export async function getExpenses(params: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { expenses: mockExpenses };
  }
  try {
    const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
    const res = await fetchJSON(`/expenses/${qs}`);

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Expenses Response]', res);
    }

    // Normalize response to always return { expenses: [] }
    const expenses = Array.isArray(res) ? res : (res?.expenses ?? []);

    // Ensure all required fields are present and properly formatted
    const normalizedExpenses = expenses.map((expense: any) => ({
      id: expense.id || '',
      category: expense.category || 'MISC',
      amount: Number(expense.amount || 0),
      description: expense.description || '',
      expenseDate: expense.expenseDate || expense.expense_date || new Date().toISOString(),
      paymentMethod: expense.paymentMethod || expense.payment_method || 'Cash',
      referenceNumber: expense.referenceNumber || expense.reference_number || undefined
    }));

    return { expenses: normalizedExpenses };
  } catch (error) {
    console.error('[Expenses API Error]', error);
    throw error;
  }
}

export async function createExpense(data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, expense: { id: Date.now().toString(), ...data } };
  }

  try {
    // Validate required fields
    if (!data.category || !data.amount || !data.description) {
      throw new Error('Missing required fields: category, amount, and description are required');
    }

    // Format the expense data for the API
    const expenseData = {
      category: data.category,
      amount: Number(data.amount),
      description: data.description,
      expenseDate: data.expenseDate || new Date().toISOString().split('T')[0],
      paymentMethod: data.paymentMethod || 'Cash',
      referenceNumber: data.referenceNumber || undefined
    };

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Expense Request]', expenseData);
    }

    const res = await fetchJSON('/expenses/', {
      method: 'POST',
      body: JSON.stringify(expenseData)
    });

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Expense Response]', res);
    }

    return { success: true, expense: res };
  } catch (error) {
    console.error('[Create Expense Error]', error);
    throw error;
  }
}

export async function updateExpense(id: string, data: any) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true, expense: { id, ...data } };
  }

  try {
    // Validate required fields
    if (!data.category || !data.amount || !data.description) {
      throw new Error('Missing required fields: category, amount, and description are required');
    }

    // Format the expense data for the API
    const expenseData = {
      category: data.category,
      amount: Number(data.amount),
      description: data.description,
      expenseDate: data.expenseDate || new Date().toISOString().split('T')[0],
      paymentMethod: data.paymentMethod || 'Cash',
      referenceNumber: data.referenceNumber || undefined
    };

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Update Expense Request]', expenseData);
    }

    const res = await fetchJSON(`/expenses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(expenseData)
    });

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Update Expense Response]', res);
    }

    return { success: true, expense: res };
  } catch (error) {
    console.error('[Update Expense Error]', error);
    throw error;
  }
}

export async function deleteExpense(id: string) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return { success: true };
  }
  await fetchJSON(`/expenses/${id}`, { method: 'DELETE' });
  return { success: true };
}

export async function getExpense(id: string) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    const expense = mockExpenses.find(e => e.id === id);
    if (!expense) throw new Error('Expense not found');
    return expense;
  }

  try {
    const res = await fetchJSON(`/expenses/${id}`);

    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Get Expense Response]', res);
    }

    // Normalize the response
    return {
      id: res.id || '',
      category: res.category || 'MISC',
      amount: Number(res.amount || 0),
      description: res.description || '',
      expenseDate: res.expenseDate || res.expense_date || new Date().toISOString(),
      paymentMethod: res.paymentMethod || res.payment_method || 'Cash',
      referenceNumber: res.referenceNumber || res.reference_number || undefined
    };
  } catch (error) {
    console.error('[Get Expense Error]', error);
    throw error;
  }
}

// Import and re-export types from api-types.ts for consistency
export type { Order, Leader, Product, Payment, PaymentCreate, Expense, DashboardData } from './api-types';
