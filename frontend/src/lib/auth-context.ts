import { createContext } from 'react';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  fullName?: string;
  role?: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  loginWithRedirect: (options?: { redirectUrl?: string; email?: string; password?: string }) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
