import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);



  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsRes, usageRes] = await Promise.all([
        api.get('/dashboard/analytics'),
        api.get('/billing/usage')
      ]);
      
      setAnalytics(analyticsRes.data);
      setUsage(usageRes.data);
    } catch (error) {
      console.error('Dashboard data fetch error:', error);
      let message = error.response?.data?.detail;
      if (!message && error.response?.data && typeof error.response.data === 'object') {
        if (Array.isArray(error.response.data)) {
          message = error.response.data.map(e => e.msg).join(', ');
        } else if (error.response.data.detail) {
          message = error.response.data.detail;
        } else {
          message = JSON.stringify(error.response.data);
        }
      }
      toast.error(message || 'Failed to load dashboard data');
      
      // Set real empty state, not fake data
      setAnalytics({
        total_requests: 0,
        total_tokens: 0,
        total_cost: 0,
        average_response_time: 0,
        success_rate: 0,
        daily_usage: [],
        top_models: []
      });
      setUsage({
        current_period_requests: 0,
        current_period_tokens: 0,
        current_period_cost: 0,
        monthly_token_limit: 0,
        monthly_request_limit: 0,
        plan_type: 'free'
      });
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

  return (
    <div className="space-y-8">
      {/* Dashboard Content */}
      <div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Overview of your Model Bridge usage and performance
        </p>
      </div>

      {/* Usage Stats */}
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
                  {usage?.current_period_requests?.toLocaleString() || '0'}
                </dd>
              </dl>
            </div>
          </div>
          <div className="bg-blue-50/60 px-6 py-3">
            <div className="text-sm">
              <span className="text-gray-600">
                {usage?.request_limit?.toLocaleString() || '∞'} limit
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
                  {usage?.current_period_tokens?.toLocaleString() || '0'}
                </dd>
              </dl>
            </div>
          </div>
          <div className="bg-blue-50/60 px-6 py-3">
            <div className="text-sm">
              <span className="text-gray-600">
                {usage?.token_limit?.toLocaleString() || '∞'} limit
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
                  ${usage?.current_period_cost?.toFixed(2) || '0.00'}
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
                  {analytics?.success_rate?.toFixed(1) || '0.0'}%
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Usage Chart */}
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

      {/* Top Models */}
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
                      {model.request_count.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${model.cost.toFixed(2)}
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