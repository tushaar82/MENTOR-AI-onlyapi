'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { User, AuthState, LoginCredentials, RegisterCredentials } from '@/types/auth';
import { apiClient } from '@/lib/auth/api';
import { 
  setAuthTokens, 
  getAccessToken, 
  getRefreshToken, 
  clearAuthTokens, 
  setUser, 
  getUser, 
  isAuthenticated,
  shouldRefreshToken
} from '@/lib/auth/utils';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (credentials: RegisterCredentials) => Promise<boolean>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
  });

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  const setUserState = useCallback((user: User | null) => {
    setState(prev => ({ ...prev, user }));
  }, []);

  const login = useCallback(async (credentials: LoginCredentials): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.login(credentials);
      
      if (response.success && response.data) {
        const { user, token, refreshToken } = response.data;
        
        // Store tokens and user data
        setAuthTokens(token, refreshToken);
        setUser(user);
        setUserState(user);
        
        return true;
      } else {
        setError(response.error || 'Login failed');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (credentials: RegisterCredentials): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.register(credentials);
      
      if (response.success && response.data) {
        const { user, token, refreshToken } = response.data;
        
        // Store tokens and user data
        setAuthTokens(token, refreshToken);
        setUser(user);
        setUserState(user);
        
        return true;
      } else {
        setError(response.error || 'Registration failed');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    // Call API to logout (optional)
    apiClient.logout().catch(console.error);
    
    // Clear local storage and state
    clearAuthTokens();
    setUserState(null);
    setError(null);
  }, []);

  const refreshAuthToken = useCallback(async (): Promise<boolean> => {
    const refreshTk = getRefreshToken();
    if (!refreshTk) {
      logout();
      return false;
    }

    try {
      const response = await apiClient.refreshToken();
      
      if (response.success && response.data) {
        const { token } = response.data;
        localStorage.setItem('access_token', token);
        return true;
      } else {
        logout();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return false;
    }
  }, []);

  const checkAuth = useCallback(async () => {
    const token = getAccessToken();
    const user = getUser();

    if (!token || !user) {
      setLoading(false);
      return;
    }

    // Check if token needs refresh
    if (shouldRefreshToken()) {
      const refreshed = await refreshAuthToken();
      if (!refreshed) {
        setLoading(false);
        return;
      }
    }

    setUserState(user);
    setLoading(false);
  }, [refreshAuthToken]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Set up token refresh interval
  useEffect(() => {
    const interval = setInterval(() => {
      if (isAuthenticated() && shouldRefreshToken()) {
        refreshAuthToken();
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [refreshAuthToken]);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken: refreshAuthToken,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};