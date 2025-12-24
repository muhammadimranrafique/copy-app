import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { api } from '../lib/api-client';
import type {
  Leader,
  Order,
  Product,
  Payment,
  DashboardData,
  QueryParams,
  ApiResponse,
  ListResponse,
} from '../lib/api-types';

// Leaders
export const useLeaders = (
  params?: QueryParams,
  options?: UseQueryOptions<ListResponse<Leader>>
) => {
  return useQuery({
    queryKey: ['leaders', params],
    queryFn: () => api.getLeaders(params),
    ...options,
  });
};

export const useCreateLeader = (
  options?: UseMutationOptions<ApiResponse<Leader>, Error, Partial<Leader>>
) => {
  return useMutation({
    mutationFn: (data) => api.createLeader(data),
    ...options,
  });
};

// Orders
export const useOrders = (
  params?: QueryParams,
  options?: UseQueryOptions<ListResponse<Order>>
) => {
  return useQuery({
    queryKey: ['orders', params],
    queryFn: () => api.getOrders(params),
    ...options,
  });
};

export const useCreateOrder = (
  options?: UseMutationOptions<ApiResponse<Order>, Error, Partial<Order>>
) => {
  return useMutation({
    mutationFn: (data) => api.createOrder(data),
    ...options,
  });
};

// Products
export const useProducts = (
  params?: QueryParams,
  options?: UseQueryOptions<ListResponse<Product>>
) => {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => api.getProducts(params),
    ...options,
  });
};

export const useCreateProduct = (
  options?: UseMutationOptions<ApiResponse<Product>, Error, Partial<Product>>
) => {
  return useMutation({
    mutationFn: (data) => api.createProduct(data),
    ...options,
  });
};

// Payments
export const usePayments = (
  params?: QueryParams,
  options?: UseQueryOptions<ListResponse<Payment>>
) => {
  return useQuery({
    queryKey: ['payments', params],
    queryFn: () => api.getPayments(params),
    ...options,
  });
};

export const useCreatePayment = (
  options?: UseMutationOptions<ApiResponse<Payment>, Error, Partial<Payment>>
) => {
  return useMutation({
    mutationFn: (data) => api.createPayment(data),
    ...options,
  });
};

// Dashboard
export const useDashboard = (
  params?: QueryParams,
  options?: UseQueryOptions<DashboardData>
) => {
  return useQuery({
    queryKey: ['dashboard', params],
    queryFn: () => api.getDashboardData(params),
    ...options,
  });
};