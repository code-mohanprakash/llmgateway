import React from 'react';
import { Link, useLocation } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';
import Logo from './Logo';

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    // The app will handle redirect automatically
  };

  return (
    <nav className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0">
              <Logo size="large" showText={true} />
            </Link>
            <div className="hidden md:block ml-10">
              <div className="flex items-baseline space-x-8">

                <Link 
                  to="/models" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/models') 
                      ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                      : 'text-gray-900 hover:text-[#000000]'
                  }`}
                >
                  Models
                </Link>
                <Link 
                  to="/pricing" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/pricing') 
                      ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                      : 'text-gray-900 hover:text-[#000000]'
                  }`}
                >
                  Pricing
                </Link>
                <Link 
                  to="/docs" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/docs') 
                      ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                      : 'text-gray-900 hover:text-[#000000]'
                  }`}
                >
                  Documentation
                </Link>
                {isAuthenticated && user && (
                  <Link 
                    to="/dashboard" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/dashboard') 
                        ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#000000]'
                    }`}
                  >
                    Dashboard
                  </Link>
                )}
                {isAuthenticated && user && user.role === 'admin' && (
                  <Link 
                    to="/rbac" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/rbac') 
                        ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#000000]'
                    }`}
                  >
                    RBAC
                  </Link>
                )}
                {isAuthenticated && user && (
                  <Link 
                    to="/api-playground" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/api-playground') 
                        ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#000000]'
                    }`}
                  >
                    API Playground
                  </Link>
                )}
                {isAuthenticated && user && user.role === 'admin' && (
                  <Link 
                    to="/ab-testing" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/ab-testing') 
                        ? 'text-[#000000] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#000000]'
                    }`}
                  >
                    A/B Testing
                  </Link>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">


            
            {isAuthenticated && user ? (
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-700">
                  Welcome, {user.email}
                </div>
                <button
                  onClick={handleLogout}
                  className="text-gray-900 hover:text-[#000000] px-3 py-2 text-sm font-medium transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-900 hover:text-[#000000] px-3 py-2 text-sm font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="bg-[#000000] hover:bg-[#14213d] text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 