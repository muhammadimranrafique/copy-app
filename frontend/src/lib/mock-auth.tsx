import React, { useState, useEffect } from 'react';
import { AuthContext, User } from './auth-context';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080/api/v1';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    // hydrate from localStorage to avoid UI flicker on first paint
    try {
      const raw = localStorage.getItem('current_user');
      return raw ? JSON.parse(raw) as User : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const verify = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        // nothing to verify
        if (mounted) setIsLoading(false);
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          if (mounted) {
            setUser(data);
            localStorage.setItem('current_user', JSON.stringify(data));
          }
        } else if (res.status === 401 || res.status === 403) {
          // invalid token
          localStorage.removeItem('access_token');
          localStorage.removeItem('current_user');
          if (mounted) setUser(null);
        }
      } catch (e) {
        // network error - keep existing user to avoid flicker
        console.warn('Could not verify user session:', e);
      } finally {
        if (mounted) setIsLoading(false);
      }
    };

    verify();

    const onStorage = (e: StorageEvent) => {
      if (e.key === 'access_token' && e.storageArea === localStorage) {
        // when token changes in another tab, re-verify
        verify();
      }
      if (e.key === 'current_user') {
        try {
          setUser(e.newValue ? JSON.parse(e.newValue) : null);
        } catch {
          setUser(null);
        }
      }
    };

    window.addEventListener('storage', onStorage);
    return () => {
      mounted = false;
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  const loginWithRedirect = async (options?: { redirectUrl?: string; email?: string; password?: string }) => {
    setIsLoading(true);
    try {
      // OAuth2PasswordRequestForm expects form-encoded fields: username & password
      const form = new URLSearchParams();
      form.append('username', options?.email || '');
      form.append('password', options?.password || '');

      let res: Response;
      try {
        res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form.toString(),
        });
      } catch (networkError) {
        // This catches CORS errors and network failures
        console.error('Network error during login:', networkError);
        throw new Error(
          'Unable to connect to the server. This may be a network issue or the server may be temporarily unavailable. Please try again later.'
        );
      }

      if (!res.ok) {
        let errorMessage = 'Login failed';
        try {
          const errorData = await res.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          const text = await res.text();
          errorMessage = text || errorMessage;
        }

        if (res.status === 401) {
          throw new Error('Invalid email or password. Please check your credentials and try again.');
        } else if (res.status === 403) {
          throw new Error('Your account has been disabled. Please contact support.');
        } else if (res.status >= 500) {
          throw new Error('Server error. Please try again later.');
        }
        throw new Error(errorMessage);
      }

      const data = await res.json();
      if (data?.access_token) {
        localStorage.setItem('access_token', data.access_token);
        // Some backends return user in response; otherwise call /auth/me
        let me = data.user;
        if (!me) {
          try {
            const meRes = await fetch(`${API_BASE}/auth/me`, {
              headers: { Authorization: `Bearer ${data.access_token}` }
            });
            if (meRes.ok) {
              me = await meRes.json();
            }
          } catch (e) {
            console.warn('Failed to fetch user profile:', e);
          }
        }
        if (me) {
          setUser(me);
          try {
            localStorage.setItem('current_user', JSON.stringify(me));
          } catch (e) {
            console.warn('Failed to persist current_user', e);
          }
        }
      } else {
        throw new Error('Login successful but no access token received.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, loginWithRedirect, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

