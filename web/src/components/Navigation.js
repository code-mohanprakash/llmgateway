import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { StarIcon, ChevronDownIcon, PhoneIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import Logo from './Logo';

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [productDropdownOpen, setProductDropdownOpen] = useState(false);
  
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

  const productModules = [
    {
      name: 'Intelligent Routing',
      path: '/product/intelligent-routing',
      description: 'ML-powered routing that thinks for you',
      icon: '⚡'
    },
    {
      name: 'Cost Optimization',
      path: '/product/cost-optimization',
      description: 'Predict and optimize costs before they happen',
      icon: '💰'
    },
    {
      name: 'Enterprise Features',
      path: '/product/enterprise-features',
      description: 'RBAC, SSO, audit logging for large organizations',
      icon: '🏢'
    },
    {
      name: 'Workflow Orchestration',
      path: '/product/orchestration',
      description: 'Multi-step workflows with conditional logic',
      icon: '🔗'
    },
    {
      name: 'Monitoring & Analytics',
      path: '/product/monitoring',
      description: 'ML-powered insights and business intelligence',
      icon: '📊'
    },
    {
      name: 'Security & Compliance',
      path: '/product/security',
      description: 'Enterprise-grade security and compliance',
      icon: '🔒'
    },
    {
      name: 'Developer Experience',
      path: '/product/developer-experience',
      description: 'Interactive playground and enterprise SDKs',
      icon: '🛠️'
    }
  ];

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

                {/* Product Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setProductDropdownOpen(!productDropdownOpen)}
                    className={`flex items-center px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/product') 
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
                    }`}
                  >
                    Product
                    <ChevronDownIcon className="ml-1 h-4 w-4" />
                  </button>
                  
                  {productDropdownOpen && (
                    <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <div className="px-4 py-2 border-b border-gray-100">
                        <Link 
                          to="/product"
                          className="block text-sm font-semibold text-gray-900 hover:text-gray-700"
                          onClick={() => setProductDropdownOpen(false)}
                        >
                          Overview
                        </Link>
                        <p className="text-xs text-gray-500 mt-1">
                          Complete platform overview and competitive analysis
                        </p>
                      </div>
                      
                      <div className="py-2">
                        {productModules.map((module) => (
                          <Link
                            key={module.path}
                            to={module.path}
                            className="flex items-start px-4 py-3 hover:bg-gray-50 transition-colors"
                            onClick={() => setProductDropdownOpen(false)}
                          >
                            <span className="text-lg mr-3">{module.icon}</span>
                            <div>
                              <div className="text-sm font-medium text-gray-900">{module.name}</div>
                              <div className="text-xs text-gray-500 mt-1">{module.description}</div>
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <Link 
                  to="/models" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/models') 
                      ? 'text-gray-900 bg-gray-100 rounded-lg' 
                      : 'text-gray-900 hover:text-gray-700'
                  }`}
                >
                  Models
                </Link>
                <Link 
                  to="/pricing" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/pricing') 
                      ? 'text-gray-900 bg-gray-100 rounded-lg' 
                      : 'text-gray-900 hover:text-gray-700'
                  }`}
                >
                  Pricing
                </Link>
                <Link 
                  to="/docs" 
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/docs') 
                      ? 'text-gray-900 bg-gray-100 rounded-lg' 
                      : 'text-gray-900 hover:text-gray-700'
                  }`}
                >
                  Documentation
                </Link>
                {isAuthenticated && user && (
                  <Link 
                    to="/dashboard" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/dashboard') 
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
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
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
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
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
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
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
                    }`}
                  >
                    A/B Testing
                  </Link>
                )}
                {isAuthenticated && user && (
                  <Link 
                    to="/monitoring" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/monitoring') 
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
                    }`}
                  >
                    Monitoring
                  </Link>
                )}
                {isAuthenticated && user && (
                  <Link 
                    to="/billing" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/billing') 
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
                    }`}
                  >
                    Billing
                  </Link>
                )}
                {isAuthenticated && user && (
                  <Link 
                    to="/settings" 
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive('/settings') 
                        ? 'text-gray-900 bg-gray-100 rounded-lg' 
                        : 'text-gray-900 hover:text-gray-700'
                    }`}
                  >
                    Settings
                  </Link>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {!isAuthenticated ? (
              <>
                <Link
                  to="/login"
                  className="text-gray-900 hover:text-gray-700 px-3 py-2 text-sm font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="bg-gray-900 text-white hover:bg-gray-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Get Started
                </Link>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <div className="relative group">
                  <button className="flex items-center text-sm font-medium text-gray-900 hover:text-gray-700 transition-colors">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 text-sm font-medium">
                        {user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
                      </span>
                    </div>
                    {user.first_name || 'User'}
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <Link
                      to="/settings"
                      className="block px-4 py-2 text-sm text-gray-900 hover:bg-gray-50"
                    >
                      Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-900 hover:bg-gray-50"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 