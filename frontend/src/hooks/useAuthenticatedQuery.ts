import { useQuery } from '@tanstack/react-query';

/**
 * A wrapper around React Query's useQuery that handles authentication state
 * and provides a consistent interface for legacy components.
 */
export function useAuthenticatedQuery<T>(
  queryFn: () => Promise<T>,
  options?: {
    onError?: (error: Error) => void;
    onSuccess?: (data: T) => void;
    isReady?: boolean;
    retryCount?: number;
    retryDelay?: (attemptIndex: number) => number;
    enabled?: boolean;
    queryKey?: (string | number | boolean | null | undefined)[];
  }
) {
  // Use provided queryKey or fall back to function string representation
  // Note: When using dynamic parameters (like IDs), always provide a queryKey
  // that includes those parameters to ensure proper cache invalidation
  const queryKey = options?.queryKey ?? [queryFn.toString()];

  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const result = await queryFn();
        options?.onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        options?.onError?.(error);
        throw error;
      }
    },
    enabled: options?.isReady !== false && options?.enabled !== false,
    retry: options?.retryCount ?? 3,
    retryDelay: options?.retryDelay,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });

  return {
    data,
    loading: isLoading,
    error: error as Error | null,
    refetch
  };
}
