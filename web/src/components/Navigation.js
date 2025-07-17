import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { StarIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import Logo from './Logo';

const Navigation = () => {
  const location = useLocation();
  const { user } = useAuth();
  
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
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
                      ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                      : 'text-gray-900 hover:text-[#9B5967]'
                  }`}
                >
                  Models
                </Link>
                <Link 
                  to="/pricing" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/pricing') 
                      ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                      : 'text-gray-900 hover:text-[#9B5967]'
                  }`}
                >
                  Pricing
                </Link>
                <Link 
                  to="/docs" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/docs') 
                      ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                      : 'text-gray-900 hover:text-[#9B5967]'
                  }`}
                >
                  Documentation
                </Link>
                {user && (
                  <Link 
                    to="/dashboard" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/dashboard') 
                        ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#9B5967]'
                    }`}
                  >
                    Dashboard
                  </Link>
                )}
                {user && user.role === 'admin' && (
                  <Link 
                    to="/rbac" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/rbac') 
                        ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#9B5967]'
                    }`}
                  >
                    RBAC
                  </Link>
                )}
                {user && (
                  <Link 
                    to="/workflow" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/workflow') 
                        ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#9B5967]'
                    }`}
                  >
                    Workflows
                  </Link>
                )}
                {user && (
                  <Link 
                    to="/api-playground" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/api-playground') 
                        ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#9B5967]'
                    }`}
                  >
                    API Playground
                  </Link>
                )}
                {user && user.role === 'admin' && (
                  <Link 
                    to="/ab-testing" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/ab-testing') 
                        ? 'text-[#9B5967] bg-pink-50/50 rounded-lg' 
                        : 'text-gray-900 hover:text-[#9B5967]'
                    }`}
                  >
                    A/B Testing
                  </Link>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">

            
            <button className="flex items-center space-x-2 text-gray-600 hover:text-[#9B5967] transition-colors">
              <StarIcon className="h-4 w-4" />
              <span className="text-sm font-medium">227</span>
            </button>
            <Link
              to="/login"
              className="text-gray-900 hover:text-[#9B5967] px-3 py-2 text-sm font-medium transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="bg-[#9B5967] hover:bg-[#8a4d5a] text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 