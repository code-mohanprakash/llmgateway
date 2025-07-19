import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import RoleBasedAccess from './RoleBasedAccess';
import Logo from './Logo';
import {
  HomeIcon,
  ChartBarIcon,
  KeyIcon,
  CreditCardIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  UsersIcon,
  RocketLaunchIcon,
  SparklesIcon,
  TrophyIcon,
  StarIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  BeakerIcon,
  CommandLineIcon,
  BoltIcon,
  CurrencyDollarIcon,
  ServerIcon
} from '@heroicons/react/24/outline';

const Layout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false);
  const [, setCurrentPlan] = useState('free');

  useEffect(() => {
    // Set default plan - disable API call until billing integration is complete
    setCurrentPlan('free');
    
    // TODO: Re-enable billing API call when working auth is integrated
    // const fetchPlan = async () => {
    //   try {
    //     const res = await api.get('/billing/current-plan');
    //     setCurrentPlan(res.data?.plan_id || 'free');
    //   } catch {
    //     setCurrentPlan('free');
    //   }
    // };
    // fetchPlan();
  }, []);

  // Commented out unused functions - can be restored when needed
  // const getPlanIcon = (planId) => {
  //   switch (planId) {
  //     case 'free': return <RocketLaunchIcon className="h-4 w-4 mr-1" />;
  //     case 'starter': return <StarIcon className="h-4 w-4 mr-1" />;
  //     case 'professional': return <SparklesIcon className="h-4 w-4 mr-1" />;
  //     case 'enterprise': return <TrophyIcon className="h-4 w-4 mr-1" />;
  //     default: return <RocketLaunchIcon className="h-4 w-4 mr-1" />;
  //   }
  // };
  
  // const getPlanName = (planId) => {
  //   switch (planId) {
  //     case 'free': return 'Shuttle Launch';
  //     case 'starter': return 'Star Cruiser';
  //     case 'professional': return 'Galaxy Explorer';
  //     case 'enterprise': return 'Cosmic Enterprise';
  //     default: return 'Shuttle Launch';
  //   }
  // };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
    { name: 'API Keys', href: '/dashboard/api-keys', icon: KeyIcon },
    { 
      name: 'Team', 
      href: '/dashboard/team', 
      icon: UsersIcon,
      requireAdmin: true 
    },
    { name: 'Billing', href: '/dashboard/billing', icon: CreditCardIcon },
    { name: 'Settings', href: '/dashboard/settings', icon: CogIcon },
    // Enterprise Features
    { 
      name: 'RBAC', 
      href: '/rbac', 
      icon: ShieldCheckIcon,
      requireAdmin: true 
    },

    { 
      name: 'A/B Testing', 
      href: '/ab-testing', 
      icon: BeakerIcon,
      requireAdmin: true 
    },
    { 
      name: 'API Playground', 
      href: '/api-playground', 
      icon: CommandLineIcon
    },
    { 
      name: 'Advanced Routing', 
      href: '/advanced-routing', 
      icon: BoltIcon,
      requireAdmin: true 
    },
    { 
      name: 'Cost Optimization', 
      href: '/cost-optimization', 
      icon: CurrencyDollarIcon,
      requireAdmin: true 
    },
    { 
      name: 'Orchestration', 
      href: '/orchestration', 
      icon: Cog6ToothIcon,
      requireAdmin: true 
    },
    { 
      name: 'Monitoring', 
      href: '/monitoring', 
      icon: ServerIcon,
      requireAdmin: true 
    },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex" style={{background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'}}>
      {/* Compact Sidebar */}
      <div 
        className={`${
          isSidebarExpanded ? 'w-48' : 'w-16'
        } clean-card border-r border-gray-200/50 backdrop-blur-sm transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0`}
        onMouseEnter={() => setIsSidebarExpanded(true)}
        onMouseLeave={() => setIsSidebarExpanded(false)}
        style={{ height: '100vh' }}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-3 border-b border-gray-200/30 overflow-hidden flex-shrink-0">
            <div className={`transition-all duration-300 ease-in-out ${
              isSidebarExpanded ? 'opacity-100 scale-100' : 'opacity-0 scale-95 absolute'
            }`}>
              <Logo size="default" showText={true} />
            </div>
            <div className={`transition-all duration-300 ease-in-out ${
              isSidebarExpanded ? 'opacity-0 scale-95 absolute' : 'opacity-100 scale-100'
            }`}>
              <Logo size="small" showText={false} />
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 py-6 space-y-1 overflow-y-auto">
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
                          ? 'bg-pink-50/80 text-[#000000] border-r-2 border-[#000000]'
                          : 'text-gray-600 hover:text-[#000000] hover:bg-pink-50/50'
                      } group flex items-center px-2 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                        isSidebarExpanded ? 'justify-start' : 'justify-center'
                      }`}
                      title={!isSidebarExpanded ? item.name : ''}
                    >
                      <item.icon className="h-5 w-5 flex-shrink-0" />
                      <span className={`ml-2 whitespace-nowrap transition-all duration-300 ease-in-out ${
                        isSidebarExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2 absolute'
                      }`}>
                        {item.name}
                      </span>
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
                      ? 'bg-pink-50/80 text-[#000000] border-r-2 border-[#000000]'
                      : 'text-gray-600 hover:text-[#000000] hover:bg-pink-50/50'
                  } group flex items-center px-2 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                    isSidebarExpanded ? 'justify-start' : 'justify-center'
                  }`}
                  title={!isSidebarExpanded ? item.name : ''}
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  <span className={`ml-2 whitespace-nowrap transition-all duration-300 ease-in-out ${
                    isSidebarExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2 absolute'
                  }`}>
                    {item.name}
                  </span>
                </Link>
              );
            })}
          </nav>

          {/* User Profile Section - Always Visible at Bottom */}
          <div className="p-3 border-t border-gray-200/30 flex-shrink-0">
            {/* Expanded State */}
            <div className={`transition-all duration-300 ease-in-out ${
              isSidebarExpanded ? 'opacity-100 scale-100' : 'opacity-0 scale-95 absolute'
            }`}>
              <div className="space-y-3">
                {/* User Info */}
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-gradient-to-br from-[#000000] to-[#14213d] rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-sm font-medium">
                      {user?.firstName?.[0] || user?.full_name?.[0] || 'U'}
                    </span>
                  </div>
                  <div className="ml-3 min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-700 truncate">
                      {user?.firstName ? `${user.firstName} ${user.lastName}` : user?.full_name || 'User'}
                    </p>
                    <p className="text-xs text-gray-500 truncate">{user?.email || 'user@example.com'}</p>
                    <div className="flex items-center mt-1">
                      <span className="text-xs text-gray-400 capitalize">{user?.role || 'user'}</span>
                      {user?.role && (
                        <span className={`ml-2 px-1.5 py-0.5 text-xs rounded-full ${
                          user.role?.toLowerCase() === 'owner' ? 'bg-purple-100 text-purple-800' :
                          user.role?.toLowerCase() === 'admin' ? 'bg-blue-100 text-blue-800' :
                          user.role?.toLowerCase() === 'member' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {user.role?.toLowerCase() === 'owner' ? '👑' :
                           user.role?.toLowerCase() === 'admin' ? '⚡' :
                           user.role?.toLowerCase() === 'member' ? '👤' : '👁️'}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Sign Out Button */}
                <button
                  onClick={handleLogout}
                  className="flex items-center w-full px-3 py-2 text-sm text-gray-600 hover:text-[#000000] hover:bg-pink-50/50 rounded-lg transition-all duration-200"
                >
                  <ArrowRightOnRectangleIcon className="mr-3 h-4 w-4 flex-shrink-0" />
                  <span className="whitespace-nowrap">Sign out</span>
                </button>
              </div>
            </div>
            
            {/* Collapsed State */}
            <div className={`transition-all duration-300 ease-in-out ${
              isSidebarExpanded ? 'opacity-0 scale-95 absolute' : 'opacity-100 scale-100'
            }`}>
              <div className="flex flex-col items-center space-y-3">
                {/* User Avatar */}
                <div className="w-8 h-8 bg-gradient-to-br from-[#000000] to-[#14213d] rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.firstName?.[0] || user?.full_name?.[0] || 'U'}
                  </span>
                </div>
                
                {/* Role Badge */}
                {user?.role && (
                  <div className={`px-1.5 py-0.5 text-xs rounded-full ${
                    user.role?.toLowerCase() === 'owner' ? 'bg-purple-100 text-purple-800' :
                    user.role?.toLowerCase() === 'admin' ? 'bg-blue-100 text-blue-800' :
                    user.role?.toLowerCase() === 'member' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {user.role?.toLowerCase() === 'owner' ? '👑' :
                     user.role?.toLowerCase() === 'admin' ? '⚡' :
                     user.role?.toLowerCase() === 'member' ? '👤' : '👁️'}
                  </div>
                )}
                
                {/* Sign Out Button */}
                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-600 hover:text-[#000000] hover:bg-pink-50/50 rounded-lg transition-all duration-200"
                  title="Sign out"
                >
                  <ArrowRightOnRectangleIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top-right role display */}
        {user?.role && (
          <div className="absolute top-4 right-4 z-10">
            <div className={`px-3 py-1.5 rounded-full text-sm font-medium shadow-sm ${
              user.role?.toLowerCase() === 'owner' ? 'bg-purple-100 text-purple-800 border border-purple-200' :
              user.role?.toLowerCase() === 'admin' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
              user.role?.toLowerCase() === 'member' ? 'bg-green-100 text-green-800 border border-green-200' :
              'bg-gray-100 text-gray-800 border border-gray-200'
            }`}>
              <span className="mr-1">
                {user.role?.toLowerCase() === 'owner' ? '👑' :
                 user.role?.toLowerCase() === 'admin' ? '⚡' :
                 user.role?.toLowerCase() === 'member' ? '👤' : '👁️'}
              </span>
              {user.role?.charAt(0).toUpperCase() + user.role?.slice(1).toLowerCase()}
            </div>
          </div>
        )}
        
        {/* Page content */}
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;