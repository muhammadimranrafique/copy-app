import { useEffect, useCallback, useState, useRef } from 'react';

export function useAuthenticatedQuery<T>(
  queryFn: () => Promise<T>,
  options?: {
    onError?: (error: Error) => void;
    onSuccess?: (data: T) => void;
    isReady?: boolean;
    retryCount?: number;
    retryDelay?: (attemptIndex: number) => number;
  }
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const mounted = useRef(true);
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Stabilize the queryFn reference
  const queryFnRef = useRef(queryFn);
  queryFnRef.current = queryFn;

  const execute = useCallback(async () => {
    const currentOptions = optionsRef.current;
    
    if (currentOptions?.isReady === false) {
      if (mounted.current) {
        setLoading(false);
      }
      return;
    }

    try {
      if (mounted.current) {
        setLoading(true);
        setError(null);
      }
      
      const newData = await queryFnRef.current();
      
      // Only update state if component is still mounted
      if (mounted.current) {
        setData(newData);
        currentOptions?.onSuccess?.(newData);
      }
    } catch (e) {
      // Only update error state if component is still mounted
      if (mounted.current) {
        const err = e instanceof Error ? e : new Error(String(e));
        setError(err);
        currentOptions?.onError?.(err);
      }
    } finally {
      // Only update loading state if component is still mounted
      if (mounted.current) {
        setLoading(false);
      }
    }
  }, []); // No dependencies to prevent infinite re-renders

  // Trigger execution when isReady changes
  useEffect(() => {
    if (options?.isReady !== false) {
      execute();
    }
  }, [options?.isReady, execute]);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  return { data, loading, error, refetch: execute };
}