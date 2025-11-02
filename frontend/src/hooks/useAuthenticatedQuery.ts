import { useEffect, useCallback, useState, useRef } from 'react';

export function useAuthenticatedQuery<T>(
  queryFn: () => Promise<T>,
  options?: {
    onError?: (error: Error) => void;
    onSuccess?: (data: T) => void;
    isReady?: boolean;
  }
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const mounted = useRef(true);

  // Stabilize the queryFn reference
  const queryFnRef = useRef(queryFn);
  queryFnRef.current = queryFn;

  const execute = useCallback(async () => {
    if (options?.isReady === false) {
      setLoading(false);
      return;
    }

    let newData;
    try {
      setLoading(true);
      setError(null);
      newData = await queryFnRef.current();
      
      // Only update state if component is still mounted
      if (mounted.current) {
        setData(newData);
        options?.onSuccess?.(newData);
      }
    } catch (e) {
      // Only update error state if component is still mounted
      if (mounted.current) {
        const err = e instanceof Error ? e : new Error(String(e));
        setError(err);
        options?.onError?.(err);
      }
    } finally {
      // Only update loading state if component is still mounted
      if (mounted.current) {
        setLoading(false);
      }
    }
  }, [options]); // Only depends on options now

  useEffect(() => {
    mounted.current = true;
    execute();
    return () => {
      mounted.current = false;
    };
  }, [execute]);

  return { data, loading, error, refetch: execute };
}