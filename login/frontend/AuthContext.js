/**
 * Enterprise Authentication Context
 * Provides authentication state management for the entire application
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import AuthService from './AuthService';
import api from '../../web/src/services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      if (AuthService.isAuthenticated()) {
        await checkAuthStatus();
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      AuthService.logout();
      setUser(null);
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  };

  const checkAuthStatus = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Auth check failed:', error);
      AuthService.logout();
      setUser(null);
      throw error;
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      const result = await AuthService.login(email, password);
      
      if (result.success) {
        setUser(result.user);
        return result;
      } else {
        throw new Error(result.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login failed:', error);
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      const result = await AuthService.register(userData);
      
      if (result.success) {
        setUser(result.user);
        return result;
      } else {
        throw new Error(result.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const forgotPassword = async (email) => {
    try {
      return await AuthService.forgotPassword(email);
    } catch (error) {
      console.error('Forgot password failed:', error);
      throw error;
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      return await AuthService.resetPassword(token, newPassword);
    } catch (error) {
      console.error('Reset password failed:', error);
      throw error;
    }
  };

  const logout = () => {
    try {
      AuthService.logout();
      setUser(null);
      
      // Redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if there's an error
      setUser(null);
      window.location.href = '/login';
    }
  };

  const refreshToken = async () => {
    try {
      const result = await AuthService.refreshToken();
      return result;
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      throw error;
    }
  };

  const updateUser = (userData) => {
    setUser(prevUser => ({
      ...prevUser,
      ...userData
    }));
  };

  const value = {
    // State
    user,
    loading,
    initialized,
    isAuthenticated: !!user,
    
    // Actions
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    refreshToken,
    checkAuthStatus,
    updateUser,
    
    // Utilities
    getAccessToken: AuthService.getAccessToken,
    getRefreshToken: AuthService.getRefreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};