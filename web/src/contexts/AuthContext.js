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

  useEffect(() => {
    const token = Cookies.get('access_token');
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    // Send as form data for OAuth2PasswordRequestForm compatibility
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token, refresh_token } = response.data;
    
    Cookies.set('access_token', access_token, { expires: 1 });
    Cookies.set('refresh_token', refresh_token, { expires: 7 });
    
    await checkAuth();
    
    return response.data;
  };

  const register = async (userData) => {
    const response = await api.post('/auth/register', userData);
    
    const { access_token, refresh_token } = response.data;
    
    Cookies.set('access_token', access_token, { expires: 1 });
    Cookies.set('refresh_token', refresh_token, { expires: 7 });
    
    await checkAuth();
    
    return response.data;
  };

  const logout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};