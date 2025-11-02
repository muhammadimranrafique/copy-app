import { Navigate } from 'react-router-dom';
import { useAuth } from '@/lib/useAuth';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  // on first load, show loading spinner only if we have a token to validate
  const initializing = isLoading && localStorage.getItem('access_token') !== null;
  if (initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // if no loading and no user, or just no token, redirect immediately
  if (!localStorage.getItem('access_token') || !user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
