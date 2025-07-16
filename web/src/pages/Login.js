import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(email, password);
      toast.success('Successfully logged in!');
      navigate('/dashboard');
    } catch (error) {
      let message = error.response?.data?.detail;
      if (!message && error.response?.data && typeof error.response.data === 'object') {
        // If it's a validation error array, join the messages
        if (Array.isArray(error.response.data)) {
          message = error.response.data.map(e => e.msg || JSON.stringify(e)).join(', ');
        } else if (error.response.data.detail) {
          message = error.response.data.detail;
        } else {
          // If it's a validation error object, try to extract 'msg' or fallback to string
          message = error.response.data.msg || JSON.stringify(error.response.data);
        }
      }
      // Always ensure message is a string
      if (typeof message !== 'string') {
        message = JSON.stringify(message);
      }
      toast.error(message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" 
         style={{background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'}}>
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-4xl font-bold gradient-text mb-3">
            Welcome Back
          </h2>
          <p className="text-gray-600">
            Sign in to your Model Bridge account
          </p>
          <p className="mt-4 text-sm text-gray-500">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-medium text-blue-700 hover:text-indigo-600 px-1 py-0.5 rounded transition-colors"
            >
              Create one here
            </Link>
          </p>
        </div>
        <div className="clean-card rounded-2xl p-8 mt-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="form-input"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="form-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary text-lg disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-300"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="text-center space-y-3">
            <Link 
              to="/forgot-password" 
              className="block text-[#9B5967] hover:text-[#8a4d5a] font-medium transition-colors"
            >
              Forgot your password?
            </Link>
            <div>
              <span className="text-gray-600">Don't have an account?</span>
              <Link to="/register" className="ml-2 text-[#9B5967] hover:text-[#8a4d5a] font-medium transition-colors">
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;