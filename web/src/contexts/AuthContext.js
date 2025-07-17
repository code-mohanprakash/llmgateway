/**
 * Updated AuthContext to use enterprise authentication
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import Cookies from 'js-cookie';

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
      const token = Cookies.get('access_token');
      console.log('AuthContext initializing, token:', token ? 'exists' : 'none');
      
      if (token) {
        console.log('Token found, checking authentication...');
        await checkAuth();
      } else {
        console.log('No token found, user not logged in');
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      // Don't call logout during initialization, just clear the user
      setUser(null);
    } finally {
      setLoading(false);
      setInitialized(true);
      console.log('AuthContext initialization complete');
    }
  };

  const checkAuth = async () => {
    try {
      const token = Cookies.get('access_token');
      if (!token) {
        throw new Error('No access token');
      }
      
      const response = await api.get('/working-auth/me');
      console.log('Auth check successful, user data:', response.data);
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.log('Auth check failed:', error.message);
      // Clear user but don't force logout/redirect
      setUser(null);
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      throw error;
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      
      // Send as form data for OAuth2PasswordRequestForm compatibility
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      console.log('Attempting login for:', email);
      const response = await api.post('/working-auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      const { access_token, refresh_token } = response.data;
      
      console.log('Login successful, tokens received');
      Cookies.set('access_token', access_token, { expires: 1 });
      Cookies.set('refresh_token', refresh_token, { expires: 7 });
      
      console.log('Tokens stored, checking auth...');
      await checkAuth();
      console.log('Login complete, user should be set');
      
      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      setUser(null);
      
      // Extract error message
      let message = 'Login failed';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      } else if (error.message) {
        message = error.message;
      }
      
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      
      console.log('Attempting registration for:', userData.email);
      const response = await api.post('/working-auth/register', userData);
      
      const { access_token, refresh_token } = response.data;
      
      console.log('Registration successful, tokens received');
      Cookies.set('access_token', access_token, { expires: 1 });
      Cookies.set('refresh_token', refresh_token, { expires: 7 });
      
      console.log('Tokens stored, checking auth...');
      await checkAuth();
      console.log('Registration complete, user should be set');
      
      return response.data;
    } catch (error) {
      console.error('Registration failed:', error);
      setUser(null);
      
      // Extract error message
      let message = 'Registration failed';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      } else if (error.message) {
        message = error.message;
      }
      
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const forgotPassword = async (email) => {
    try {
      const response = await api.post('/working-auth/forgot-password', { email });
      return {
        success: true,
        message: response.data.message || 'Password reset email sent'
      };
    } catch (error) {
      console.error('Forgot password failed:', error);
      
      let message = 'Failed to send reset email';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      }
      
      throw new Error(message);
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      const response = await api.post('/auth/reset-password', {
        token,
        new_password: newPassword
      });
      
      return {
        success: true,
        message: response.data.message || 'Password reset successful'
      };
    } catch (error) {
      console.error('Reset password failed:', error);
      
      let message = 'Password reset failed';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      }
      
      throw new Error(message);
    }
  };

  const logout = () => {
    try {
      console.log('Logging out user');
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      setUser(null);
      
      // Optional: Call logout endpoint
      api.post('/auth/logout').catch(() => {
        // Ignore logout endpoint errors
      });
      
      // Don't automatically redirect - let the app handle it
      console.log('Logout complete');
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if there's an error
      setUser(null);
    }
  };

  const refreshToken = async () => {
    try {
      const refreshTokenValue = Cookies.get('refresh_token');
      
      if (!refreshTokenValue) {
        throw new Error('No refresh token available');
      }
      
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshTokenValue
      });
      
      const { access_token, refresh_token } = response.data;
      
      Cookies.set('access_token', access_token, { expires: 1 });
      Cookies.set('refresh_token', refresh_token, { expires: 7 });
      
      return { success: true };
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      throw error;
    }
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
    checkAuth,
    
    // Utilities
    getAccessToken: () => Cookies.get('access_token'),
    getRefreshToken: () => Cookies.get('refresh_token')
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};