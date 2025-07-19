import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchDashboardData();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch analytics data from the backend
      const analyticsResponse = await api.get('/dashboard/analytics');
      
      // Fetch usage data from the backend
      const usageResponse = await api.get('/billing/usage');
      
      setAnalytics(analyticsResponse.data);
      setUsage(usageResponse.data);
      
    } catch (error) {
      // Don't show toast for 401 errors
      if (error.response?.status !== 401) {
        toast.error('Failed to load dashboard data');
      }
      
      // Don't set any fake data - leave as null
      setAnalytics(null);
      setUsage(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-300 border-t-gray-500"></div>
      </div>
    );
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Dashboard</h1>
          <p className="text-gray-600">
            Please log in to view your Model Bridge usage and performance
          </p>
        </div>
        
        <div className="empty-state-card">
          <div className="empty-state-icon">🔐</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Authentication Required</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            You need to be logged in to view dashboard analytics and usage statistics.
          </p>
          <a 
            href="/login" 
            className="btn-primary"
          >
            Log In
          </a>
        </div>
      </div>
    );
  }

  // If no data available, show empty state
  if (!analytics && !usage) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Dashboard</h1>
          <p className="text-gray-600">
            No data available. Start making API requests to see your usage analytics.
          </p>
        </div>
        
        <div className="empty-state-card">
          <div className="empty-state-icon">📊</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Data Available</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Start making API requests to see your usage analytics and performance metrics here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Dashboard Content */}
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Overview of your Model Bridge usage and performance
        </p>
      </div>

      {/* Usage Stats - Only show if we have usage data */}
      {usage && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="stat-card hover-lift overflow-hidden">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">R</span>
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Requests This Month
                  </dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    {(usage.current_period_requests || 0).toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
            <div className="bg-blue-50/60 px-6 py-3">
              <div className="text-sm">
                <span className="text-gray-600">
                  {usage.request_limit ? usage.request_limit.toLocaleString() : '∞'} limit
                </span>
              </div>
            </div>
          </div>

          <div className="stat-card hover-lift overflow-hidden">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-400 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">T</span>
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Tokens This Month
                  </dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    {(usage.current_period_tokens || 0).toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
            <div className="bg-blue-50/60 px-6 py-3">
              <div className="text-sm">
                <span className="text-gray-600">
                  {usage.token_limit ? usage.token_limit.toLocaleString() : '∞'} limit
                </span>
              </div>
            </div>
          </div>

          <div className="stat-card hover-lift overflow-hidden">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-400 to-blue-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">$</span>
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Cost This Month
                  </dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${(usage.current_period_cost || 0).toFixed(2)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="stat-card hover-lift overflow-hidden">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">%</span>
                </div>
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Success Rate
                  </dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    {(analytics?.success_rate || 0).toFixed(1)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enterprise Features Quick Access */}
      <div className="clean-card hover-lift rounded-xl p-6">
        <h3 className="text-xl font-semibold gradient-text mb-6">Enterprise Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

          <a href="/api-playground" className="feature-card group">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h4 className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">API Playground</h4>
            <p className="text-sm text-gray-600">Test APIs with real-time feedback</p>
          </a>

          <a href="/ab-testing" className="feature-card group">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h4 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">A/B Testing</h4>
            <p className="text-sm text-gray-600">Compare model performance</p>
          </a>

          <a href="/rbac" className="feature-card group">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h4 className="font-semibold text-gray-900 group-hover:text-orange-600 transition-colors">RBAC</h4>
            <p className="text-sm text-gray-600">Role-based access control</p>
          </a>
        </div>
      </div>

      {/* Usage Chart - Only show if we have analytics data */}
      {analytics?.usage_by_day && analytics.usage_by_day.length > 0 ? (
        <div className="clean-card hover-lift rounded-xl p-6">
          <h3 className="text-xl font-semibold gradient-text mb-6">Usage Over Time</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics.usage_by_day}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ef" />
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #e0e7ef',
                    borderRadius: '12px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  name="Requests"
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="cost" 
                  stroke="#6366f1" 
                  strokeWidth={3}
                  name="Cost ($)"
                  dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="empty-state-card">
          <div className="empty-state-icon">📊</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Usage Data Yet</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Start making API requests to see your usage analytics and performance metrics here.
          </p>
        </div>
      )}

      {/* Top Models - Only show if we have analytics data */}
      {analytics?.top_models && analytics.top_models.length > 0 ? (
        <div className="clean-card hover-lift rounded-xl p-6">
          <h3 className="text-xl font-semibold gradient-text mb-6">Top Models</h3>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="table-header">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Model
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Provider
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Requests
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Cost
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {analytics.top_models.slice(0, 5).map((model, index) => (
                  <tr key={index} className="hover-lift">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {model.model_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {model.provider}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {(model.request_count || 0).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${(model.cost || 0).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="empty-state-card">
          <div className="empty-state-icon">🤖</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Model Usage Yet</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Start making requests to different LLM models to see usage statistics and comparisons here.
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;