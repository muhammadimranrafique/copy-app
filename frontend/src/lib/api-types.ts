// API Response Types
export interface Leader {
  id: string;
  name: string;
  type: string;
  contact: string;
  address: string;
  openingBalance: number;
}

export interface Order {
  id: string;
  orderNumber?: string;
  leaderId?: string;
  orderDate?: string;
  totalAmount?: number;
  status?: string;
}

export interface Product {
  id: string;
  productName?: string;
  category?: string;
  costPrice?: number;
  salePrice?: number;
  stockQuantity?: number;
  unit?: string;
}

export interface ClientInfo {
  id: string;
  name: string;
  type: string;
  contact: string;
  address: string;
}

export interface Payment {
  id: string;
  amount: number;
  method: string;
  status: string;
  paymentDate: string;
  createdAt: string;
  leaderId: string;
  orderId?: string;
  referenceNumber?: string;
  client?: ClientInfo | null;
}

export interface PaymentCreate {
  amount: number;
  method: string;
  leaderId: string;
  paymentDate?: string;
  referenceNumber?: string;
  orderId?: string;
}

export type ExpenseCategory = 'MATERIAL' | 'STAFF' | 'UTILITIES' | 'PRINTING' | 'DELIVERY' | 'MISC';

export interface Expense {
  id: string;
  category: ExpenseCategory;
  amount: number;
  description: string;
  expenseDate: string;
  paymentMethod?: string;
  referenceNumber?: string;
  createdAt?: string;
}

export interface ExpenseCreate {
  category: ExpenseCategory;
  amount: number;
  description: string;
  expenseDate: string;
  paymentMethod?: string;
  referenceNumber?: string;
}

export interface DashboardData {
  totalOrders: number;
  totalRevenue: number;
  totalPayments: number;
  netProfit: number;
  recentOrders: Order[];
  recentPayments: Payment[];
}

// API Response Wrappers
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  page?: number;
  pageSize?: number;
}

// Type guards
export function isApiError(error: unknown): error is Error {
  return error instanceof Error;
}

// Query Parameters
export interface QueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
  [key: string]: any;
}