/**
 * Enterprise Authentication Service
 * Handles all authentication logic with proper error handling
 */
import api from '../../web/src/services/api';
import Cookies from 'js-cookie';

class AuthService {
  /**
   * Login user with email and password
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<Object>} Authentication response
   */
  static async login(email, password) {
    try {
      // Send as form data for OAuth2PasswordRequestForm compatibility
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      if (response.data.success) {
        const { access_token, refresh_token, user } = response.data;
        
        // Store tokens in cookies
        Cookies.set('access_token', access_token, { expires: 1 });
        Cookies.set('refresh_token', refresh_token, { expires: 7 });
        
        return {
          success: true,
          user: user,
          tokens: {
            access_token,
            refresh_token
          }
        };
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Extract error message from response
      let message = 'Login failed';
      
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      } else if (error.message) {
        message = error.message;
      }
      
      throw new Error(message);
    }
  }

  /**
   * Register new user
   * @param {Object} userData User registration data
   * @returns {Promise<Object>} Authentication response
   */
  static async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      
      if (response.data.success) {
        const { access_token, refresh_token, user } = response.data;
        
        // Store tokens in cookies
        Cookies.set('access_token', access_token, { expires: 1 });
        Cookies.set('refresh_token', refresh_token, { expires: 7 });
        
        return {
          success: true,
          user: user,
          tokens: {
            access_token,
            refresh_token
          }
        };
      } else {
        throw new Error(response.data.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      // Extract error message from response
      let message = 'Registration failed';
      
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      } else if (error.message) {
        message = error.message;
      }
      
      throw new Error(message);
    }
  }

  /**
   * Send forgot password email
   * @param {string} email 
   * @returns {Promise<Object>} Response
   */
  static async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      
      return {
        success: response.data.success || true,
        message: response.data.message || 'Password reset email sent'
      };
    } catch (error) {
      console.error('Forgot password error:', error);
      
      let message = 'Failed to send reset email';
      
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      }
      
      throw new Error(message);
    }
  }

  /**
   * Reset password with token
   * @param {string} token 
   * @param {string} newPassword 
   * @returns {Promise<Object>} Response
   */
  static async resetPassword(token, newPassword) {
    try {
      const response = await api.post('/auth/reset-password', {
        token,
        new_password: newPassword
      });
      
      return {
        success: response.data.success || true,
        message: response.data.message || 'Password reset successful'
      };
    } catch (error) {
      console.error('Reset password error:', error);
      
      let message = 'Password reset failed';
      
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      }
      
      throw new Error(message);
    }
  }

  /**
   * Refresh access token
   * @returns {Promise<Object>} New tokens
   */
  static async refreshToken() {
    try {
      const refreshToken = Cookies.get('refresh_token');
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      });
      
      if (response.data.success) {
        const { access_token, refresh_token } = response.data;
        
        // Update tokens in cookies
        Cookies.set('access_token', access_token, { expires: 1 });
        Cookies.set('refresh_token', refresh_token, { expires: 7 });
        
        return {
          success: true,
          tokens: {
            access_token,
            refresh_token
          }
        };
      } else {
        throw new Error(response.data.message || 'Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      
      // Clear tokens on refresh failure
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      
      throw error;
    }
  }

  /**
   * Logout user
   */
  static logout() {
    try {
      // Clear tokens from cookies
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      
      // Optional: Call logout endpoint
      api.post('/auth/logout').catch(() => {
        // Ignore logout endpoint errors
      });
      
      return { success: true, message: 'Logged out successfully' };
    } catch (error) {
      console.error('Logout error:', error);
      // Still return success as local logout should always work
      return { success: true, message: 'Logged out successfully' };
    }
  }

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  static isAuthenticated() {
    const token = Cookies.get('access_token');
    return !!token;
  }

  /**
   * Get current access token
   * @returns {string|null}
   */
  static getAccessToken() {
    return Cookies.get('access_token') || null;
  }

  /**
   * Get current refresh token
   * @returns {string|null}
   */
  static getRefreshToken() {
    return Cookies.get('refresh_token') || null;
  }
}

export default AuthService;