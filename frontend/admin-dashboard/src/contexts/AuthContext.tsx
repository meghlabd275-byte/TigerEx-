/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AdminUser, LoginCredentials, AuthResponse } from '../types/auth';
import { authService } from '../services/authService';

interface AuthState {
  user: AdminUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: AuthResponse }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: Partial<AdminUser> };

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('admin_token'),
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'LOGIN_SUCCESS':
      localStorage.setItem('admin_token', action.payload.token);
      localStorage.setItem('admin_refresh_token', action.payload.refreshToken);
      localStorage.setItem('admin_user', JSON.stringify(action.payload.user));
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'LOGIN_FAILURE':
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_refresh_token');
      localStorage.removeItem('admin_user');
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_refresh_token');
      localStorage.removeItem('admin_user');
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'UPDATE_USER':
      const updatedUser = state.user ? { ...state.user, ...action.payload } : null;
      if (updatedUser) {
        localStorage.setItem('admin_user', JSON.stringify(updatedUser));
      }
      return {
        ...state,
        user: updatedUser,
      };
    default:
      return state;
  }
};

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  updateUser: (updates: Partial<AdminUser>) => void;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('admin_token');
      const userStr = localStorage.getItem('admin_user');

      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          
          // Verify token is still valid
          const isValid = await authService.verifyToken(token);
          
          if (isValid) {
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: {
                token,
                refreshToken: localStorage.getItem('admin_refresh_token') || '',
                user,
                expiresIn: 0, // Will be set by the service
              },
            });
          } else {
            // Token is invalid, try to refresh
            await refreshToken();
          }
        } catch (error) {
          console.error('Auth initialization error:', error);
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      const response = await authService.login(credentials);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || error.message || 'Login failed';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  const logout = (): void => {
    // Call logout API to invalidate token on server
    authService.logout().catch(console.error);
    dispatch({ type: 'LOGOUT' });
  };

  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const updateUser = (updates: Partial<AdminUser>): void => {
    dispatch({ type: 'UPDATE_USER', payload: updates });
  };

  const hasPermission = (permission: string): boolean => {
    if (!state.user) return false;
    if (state.user.role === 'super_admin') return true;
    return state.user.permissions.includes(permission);
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!state.user) return false;
    if (state.user.role === 'super_admin') return true;
    return permissions.some(permission => state.user!.permissions.includes(permission));
  };

  const refreshToken = async (): Promise<void> => {
    try {
      const refreshTokenStr = localStorage.getItem('admin_refresh_token');
      if (!refreshTokenStr) {
        throw new Error('No refresh token available');
      }

      const response = await authService.refreshToken(refreshTokenStr);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response });
    } catch (error) {
      console.error('Token refresh failed:', error);
      dispatch({ type: 'LOGOUT' });
      throw error;
    }
  };

  // Set up automatic token refresh
  useEffect(() => {
    if (!state.isAuthenticated || !state.token) return;

    const refreshInterval = setInterval(async () => {
      try {
        await refreshToken();
      } catch (error) {
        console.error('Automatic token refresh failed:', error);
        // Token refresh failed, user will be logged out
      }
    }, 15 * 60 * 1000); // Refresh every 15 minutes

    return () => clearInterval(refreshInterval);
  }, [state.isAuthenticated, state.token]);

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    clearError,
    updateUser,
    hasPermission,
    hasAnyPermission,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};