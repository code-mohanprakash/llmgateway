import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Only handle auth errors for protected routes
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Check if this is a protected route that requires auth
      const protectedRoutes = ['/auth/me', '/working-auth/me', '/auth/refresh', '/dashboard', '/analytics', '/api-keys', '/billing', '/settings', '/team'];
      const isProtectedRoute = protectedRoutes.some(route => originalRequest.url.includes(route));
      
      if (isProtectedRoute) {
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          try {
            const response = await axios.post('/api/auth/refresh', {
              refresh_token: refreshToken
            });
            
            const { access_token, refresh_token } = response.data;
            Cookies.set('access_token', access_token, { expires: 1 });
            Cookies.set('refresh_token', refresh_token, { expires: 7 });
            
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            // Don't auto-redirect, let the app handle it
            console.log('Tokens cleared due to refresh failure');
          }
        } else {
          console.log('No refresh token available');
          // Don't auto-redirect, let the app handle it
        }
      }
    }
    
    // Don't show error notifications for 401 errors on public routes
    if (error.response?.status === 401) {
      const publicRoutes = ['/auth/login', '/auth/register', '/auth/forgot-password'];
      const isPublicRoute = publicRoutes.some(route => originalRequest.url.includes(route));
      
      if (!isPublicRoute) {
        // Only log the error, don't show notification
        console.log('Authentication required for:', originalRequest.url);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;