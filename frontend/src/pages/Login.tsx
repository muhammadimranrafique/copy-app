import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/useAuth';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Mail, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';

export default function Login() {
  const { user, isLoading, loginWithRedirect } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);

  // Redirect to dashboard if user is authenticated
  // IMPORTANT: Check for valid token to prevent flickering from stale localStorage data
  useEffect(() => {
    const token = localStorage.getItem('access_token');

    // Only redirect if:
    // 1. User object exists
    // 2. Not currently loading
    // 3. Valid token exists in localStorage
    if (user && !isLoading && token) {
      // Small delay to ensure smooth transition
      const timer = setTimeout(() => {
        navigate('/', { replace: true });
      }, 100);

      return () => clearTimeout(timer);
    }
  }, [user, isLoading, navigate]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const errorParam = params.get('error');
    const errorDescription = params.get('error_description');

    if (errorParam) {
      setError(errorDescription || 'Authentication failed. Please try again.');
      setIsAuthenticating(false);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const handleLogin = async () => {
    try {
      setError(null);
      setIsAuthenticating(true);
      const redirectUrl = `${window.location.origin}/`;
      // loginWithRedirect supports email/password options
      await loginWithRedirect({ redirectUrl, email, password });
      if (remember) {
        // keep token in localStorage (default); otherwise token clearing logic would be needed
      }
    } catch (err) {
      console.error('Login error:', err);
      const msg = (err as any)?.message || 'Unable to authenticate. Please try again.';
      setError(msg);
      toast.error(msg);
      setIsAuthenticating(false);
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  // Show loading state while verifying authentication
  // or if user is authenticated and about to redirect
  const token = localStorage.getItem('access_token');
  if (isLoading || (user && token)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-primary/5">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-sm text-muted-foreground">
            {user ? 'Redirecting to dashboard...' : 'Loading authentication...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-primary/5 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-3 text-center">
          <div className="mx-auto w-16 h-16 rounded-full gradient-bg flex items-center justify-center">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <CardTitle className="text-3xl font-bold">SchoolCopy</CardTitle>
          <CardDescription className="text-base">Business Management System</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Authentication Error</AlertTitle>
              <AlertDescription className="mt-2 space-y-2">
                <p>{error}</p>
                <Button variant="outline" size="sm" onClick={handleRefresh} className="mt-2">
                  <RefreshCw className="w-3 h-3 mr-2" />
                  Refresh Page
                </Button>
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <h3 className="font-semibold text-lg">Welcome!</h3>
            <p className="text-sm text-muted-foreground">
              Sign in to access your dashboard and manage orders, products, and payments.
            </p>
          </div>

          <form
            onSubmit={async (e) => {
              e.preventDefault();
              await handleLogin();
            }}
            className="space-y-4"
          >
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@schoolcopy.com"
                required
              />
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                required
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="h-4 w-4 rounded border-muted-foreground"
                />
                <span className="text-sm">Remember me</span>
              </label>
              <button
                type="button"
                className="text-sm text-primary underline"
                onClick={() => toast('Password reset is available via the admin panel.')}
              >
                Forgot password?
              </button>
            </div>

            <Button type="submit" disabled={isAuthenticating} className="w-full h-12 text-base" size="lg">
              {isAuthenticating ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <Mail className="w-5 h-5 mr-2" />
                  Sign in with Email
                </>
              )}
            </Button>
          </form>

          <div className="pt-4 border-t space-y-2">
            <p className="text-xs text-center text-muted-foreground">
              New users will be automatically registered upon first login
            </p>
            <p className="text-xs text-center text-muted-foreground">
              Check your email for a magic link after clicking the button
            </p>
          </div>

          <div className="bg-primary/5 border border-primary/20 p-4 rounded-lg space-y-2">
            <h4 className="font-semibold text-sm flex items-center gap-2">
              <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Key Features
            </h4>
            <ul className="text-xs text-muted-foreground space-y-1.5">
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">✓</span>
                <span>Manage Leaders (Schools & Dealers)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">✓</span>
                <span>Track Products & Inventory</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">✓</span>
                <span>Process Orders & Payments</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">✓</span>
                <span>View Business Analytics</span>
              </li>
            </ul>
          </div>

          <div className="bg-muted/50 p-3 rounded text-xs text-muted-foreground">
            <p className="font-medium mb-1">Having trouble?</p>
            <ul className="space-y-1">
              <li>• Make sure pop-ups are not blocked</li>
              <li>• Check your email for the login link</li>
              <li>• Try refreshing the page if stuck</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
