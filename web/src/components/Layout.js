import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import RoleBasedAccess from './RoleBasedAccess';
import {
  HomeIcon,
  ChartBarIcon,
  KeyIcon,
  CreditCardIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  UsersIcon
} from '@heroicons/react/24/outline';

const Layout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'API Keys', href: '/api-keys', icon: KeyIcon },
    { 
      name: 'Team', 
      href: '/team', 
      icon: UsersIcon,
      requireAdmin: true 
    },
    { name: 'Billing', href: '/billing', icon: CreditCardIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex" style={{background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'}}>
      {/* Sidebar */}
      <div className="w-64 clean-card border-r border-gray-200/50 backdrop-blur-sm">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200/30">
            <h1 className="gradient-text text-xl font-bold tracking-tight">LLM Gateway</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              
              // Check if item requires admin access
              if (item.requireAdmin) {
                return (
                  <RoleBasedAccess key={item.name} requireAdmin={true}>
                    <Link
                      to={item.href}
                      className={`${
                        isActive
                          ? 'bg-blue-50/80 text-blue-900 border-r-2 border-blue-500'
                          : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50/50'
                      } group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200`}
                    >
                      <item.icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </Link>
                  </RoleBasedAccess>
                );
              }
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive
                      ? 'bg-blue-50/80 text-blue-900 border-r-2 border-blue-500'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50/50'
                  } group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User menu */}
          <div className="p-4 border-t border-gray-200/30">
            <div className="flex items-center mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user?.firstName?.[0] || user?.full_name?.[0] || 'U'}
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">
                  {user?.firstName ? `${user.firstName} ${user.lastName}` : user?.full_name}
                </p>
                <p className="text-xs text-gray-500">{user?.email}</p>
                <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg transition-all duration-200"
            >
              <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="clean-card border-b border-gray-200/50 backdrop-blur-sm">
          <div className="px-6 py-5">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold gradient-text">
                {navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
              </h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500 font-medium">
                  {user?.organization?.name}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;