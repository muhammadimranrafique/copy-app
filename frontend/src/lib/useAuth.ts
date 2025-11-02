import { useContext } from 'react';
import { AuthContext } from './auth-context';

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  // Don't report loading if there's no token - instant "logged out" state
  const effectivelyLoading = context.isLoading && localStorage.getItem('access_token') !== null;

  return {
    ...context,
    isLoading: effectivelyLoading
  };
}
