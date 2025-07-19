import React, { useState, useEffect } from 'react';
import { ChartBarIcon, ClockIcon, CurrencyDollarIcon, DocumentTextIcon, ArrowTrendingUpIcon, UsersIcon, LightBulbIcon, CogIcon, BoltIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import api from '../services/api';
import toast from 'react-hot-toast';

const Analytics = () => {
  console.log('Analytics component rendering');
  const [timeRange, setTimeRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [recentRequests, setRecentRequests] = useState([]);
  const [intelligentRouting, setIntelligentRouting] = useState(null);
  const [providerPerformance, setProviderPerformance] = useState(null);
  const [routingInsights, setRoutingInsights] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    console.log('Analytics useEffect triggered');
    // Disable API call until working auth integration is complete
    // fetchAnalytics();
    
    // Set empty/default states for now
    setAnalytics(null);
    setRecentRequests([]);
    setIntelligentRouting(null);
    setProviderPerformance([]);
    setRoutingInsights(null);
    setLoading(false);
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      console.log('Fetching analytics data...');
      const days = timeRange === '24h' ? 1 : 
                   timeRange === '7d' ? 7 : 
                   timeRange === '30d' ? 30 : 90;
      
      const [analyticsRes, recentRes, intelligentRes, performanceRes, insightsRes] = await Promise.all([
        api.get(`/dashboard/analytics?days=${days}`),
        api.get('/dashboard/recent-requests?limit=10'),
        api.get('/dashboard/intelligent-routing'),
        api.get('/dashboard/provider-performance'),
        api.get('/dashboard/routing-insights')
      ]);
      
      console.log('Analytics response:', analyticsRes.data);
      console.log('Recent requests response:', recentRes.data);
      console.log('Intelligent routing response:', intelligentRes.data);
      console.log('Provider performance response:', performanceRes.data);
      console.log('Routing insights response:', insightsRes.data);
      
      setAnalytics(analyticsRes.data);
      setRecentRequests(recentRes.data);
      setIntelligentRouting(intelligentRes.data);
      setProviderPerformance(performanceRes.data);
      setRoutingInsights(insightsRes.data);
    } catch (error) {
      let message = error.response?.data?.detail;
      if (!message && error.response?.data && typeof error.response.data === 'object') {
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
      toast.error(message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, trend, color = 'blue' }) => (
    <div className="stat-card hover-lift">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <div className="flex items-center mt-2">
              <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm font-medium text-green-600">
                {trend > 0 ? '+' : ''}{trend}%
              </span>
              <span className="text-sm text-gray-500 ml-1">vs last period</span>
            </div>
          )}
        </div>
        <div className="ml-4">
          <div className={`w-12 h-12 bg-gradient-to-br from-${color}-100 to-${color}-200 rounded-xl flex items-center justify-center`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
      </div>
    </div>
  );

  const InsightCard = ({ title, description, icon: Icon, color = 'blue', children }) => (
    <div className="clean-card p-6 hover-lift">
      <div className="flex items-center mb-4">
        <div className={`w-10 h-10 bg-gradient-to-br from-${color}-100 to-${color}-200 rounded-lg flex items-center justify-center mr-3`}>
          <Icon className={`h-5 w-5 text-${color}-600`} />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>
      {children}
    </div>
  );

  const ProviderCard = ({ provider, stats, rank }) => (
    <div className="clean-card p-4 hover-lift">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center mr-3">
            <span className="text-sm font-bold text-blue-600">{rank}</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 capitalize">{provider}</h4>
            <p className="text-sm text-gray-600">Success Rate: {(stats.success_rate * 100).toFixed(1)}%</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-900">${stats.avg_cost?.toFixed(4) || '0.0000'}</p>
          <p className="text-xs text-gray-600">avg cost</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <p className="text-gray-600">Response Time</p>
          <p className="font-medium">{(stats.avg_response_time || 0).toFixed(1)}ms</p>
        </div>
        <div>
          <p className="text-gray-600">Requests</p>
          <p className="font-medium">{stats.total_requests || 0}</p>
        </div>
      </div>
    </div>
  );

  const EmptyChart = ({ title, description, icon }) => (
    <div className="clean-card p-6 hover-lift">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="chart-placeholder">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">{icon}</span>
          </div>
          <h4 className="text-lg font-semibold text-gray-700 mb-2">No Data Yet</h4>
          <p className="text-gray-500 text-sm max-w-xs mx-auto">{description}</p>
        </div>
        {/* Beautiful chart skeleton */}
        <div className="absolute inset-0 p-8">
          <div className="flex items-end justify-between h-full opacity-20">
            {[...Array(7)].map((_, i) => (
              <div
                key={i}
                className="bg-gradient-to-t from-blue-200 to-blue-300 rounded-t"
                style={{ 
                  height: `${Math.random() * 60 + 20}%`,
                  width: '8%'
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const formatTimeAgo = (isoString) => {
    const now = new Date();
    const date = new Date(isoString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  // Default analytics fallback
  const defaultAnalytics = {
    total_requests: 0,
    total_tokens: 0,
    total_cost: 0,
    success_rate: 0,
    avg_response_time: 0,
    top_models: [],
    usage_by_day: [],
    cost_by_provider: []
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'intelligent-routing', name: 'Intelligent Routing', icon: LightBulbIcon },
    { id: 'provider-performance', name: 'Provider Performance', icon: CogIcon },
    { id: 'routing-insights', name: 'Routing Insights', icon: BoltIcon }
  ];

  if (loading) {
    console.log('Analytics: Showing loading state');
    return (
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Analytics</h1>
            <p className="text-gray-600 mt-2">Track your API usage and performance</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Time Range:</span>
            <div className="flex bg-gray-100 rounded-lg p-1 opacity-50">
              {[
                { value: '24h', label: '24h' },
                { value: '7d', label: '7d' },
                { value: '30d', label: '30d' },
                { value: '90d', label: '90d' }
              ].map((option) => (
                <button
                  key={option.value}
                  disabled
                  className="px-3 py-1 text-sm font-medium rounded-md text-gray-400"
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="stat-card animate-pulse">
              <div className="h-20 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
        
        <div className="flex items-center justify-center h-64">
          <div className="spinner w-12 h-12"></div>
        </div>
      </div>
    );
  }

  console.log('Analytics: Rendering main content, analytics:', analytics, 'recentRequests:', recentRequests);
  // Use fallback if analytics is null/undefined
  const analyticsSafe = analytics || defaultAnalytics;
  const hasData = analyticsSafe && (analyticsSafe.total_requests > 0 || recentRequests.length > 0);

  const renderOverview = () => (
    <>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Requests"
          value={analyticsSafe.total_requests?.toLocaleString() || '0'}
          icon={DocumentTextIcon}
          color="blue"
        />
        <StatCard
          title="Success Rate"
          value={`${analyticsSafe.success_rate?.toFixed(1) || '0'}%`}
          icon={ShieldCheckIcon}
          color="green"
        />
        <StatCard
          title="Total Cost"
          value={`$${analyticsSafe.total_cost?.toFixed(2) || '0.00'}`}
          icon={CurrencyDollarIcon}
          color="yellow"
        />
        <StatCard
          title="Avg Response Time"
          value={`${analyticsSafe.avg_response_time?.toFixed(0) || '0'}ms`}
          icon={ClockIcon}
          color="purple"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Over Time */}
        {analyticsSafe.usage_by_day && analyticsSafe.usage_by_day.length > 0 ? (
          <div className="clean-card p-6 hover-lift">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analyticsSafe.usage_by_day}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="requests" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <EmptyChart
            title="Usage Over Time"
            description="Your API usage will appear here once you start making requests"
            icon="📊"
          />
        )}

        {/* Cost by Provider */}
        {analyticsSafe.cost_by_provider && analyticsSafe.cost_by_provider.length > 0 ? (
          <div className="clean-card p-6 hover-lift">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost by Provider</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsSafe.cost_by_provider}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="cost"
                >
                  {analyticsSafe.cost_by_provider.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][index % 5]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <EmptyChart
            title="Cost by Provider"
            description="Provider cost breakdown will appear here"
            icon="💰"
          />
        )}
      </div>

      {/* Recent Requests */}
      <div className="clean-card p-6 hover-lift">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Requests</h3>
        {recentRequests && recentRequests.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Request ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Provider</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Model</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Tokens</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Cost</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Time</th>
                </tr>
              </thead>
              <tbody>
                {recentRequests.map((request) => (
                  <tr key={request.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-900 font-mono">{request.request_id?.slice(0, 8)}...</td>
                    <td className="py-3 px-4 text-sm text-gray-700 capitalize">{request.provider}</td>
                    <td className="py-3 px-4 text-sm text-gray-700">{request.model_id}</td>
                    <td className="py-3 px-4 text-sm text-gray-700">{request.total_tokens?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-sm text-gray-700">${request.cost_usd?.toFixed(4)}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        request.success 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {request.success ? 'Success' : 'Failed'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-500">{formatTimeAgo(request.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            </div>
            <h4 className="text-lg font-semibold text-gray-700 mb-2">No Requests Yet</h4>
            <p className="text-gray-500 text-sm">Your API requests will appear here once you start using the service</p>
          </div>
        )}
      </div>
    </>
  );

  const renderIntelligentRouting = () => (
    <div className="space-y-6">
      {/* Routing Recommendations */}
      {intelligentRouting && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <InsightCard
            title="Top Performers"
            description="Best performing providers based on success rate and speed"
            icon={BoltIcon}
            color="green"
          >
            {intelligentRouting.routing_recommendations?.top_performers?.length > 0 ? (
              <div className="space-y-3">
                {intelligentRouting.routing_recommendations.top_performers.map((provider, index) => (
                  <div key={provider.provider} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                        <span className="text-sm font-bold text-green-600">{index + 1}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 capitalize">{provider.provider}</p>
                        <p className="text-sm text-gray-600">{(provider.success_rate * 100).toFixed(1)}% success rate</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{(provider.avg_response_time || 0).toFixed(1)}ms</p>
                      <p className="text-xs text-gray-600">avg response</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No performance data available yet</p>
            )}
          </InsightCard>

          <InsightCard
            title="Cost Optimizers"
            description="Most cost-effective providers for your requests"
            icon={CurrencyDollarIcon}
            color="yellow"
          >
            {intelligentRouting.routing_recommendations?.cost_optimizers?.length > 0 ? (
              <div className="space-y-3">
                {intelligentRouting.routing_recommendations.cost_optimizers.map((provider, index) => (
                  <div key={provider.provider} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
                        <span className="text-sm font-bold text-yellow-600">{index + 1}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 capitalize">{provider.provider}</p>
                        <p className="text-sm text-gray-600">${(provider.avg_cost || 0).toFixed(4)} per request</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{(provider.success_rate * 100).toFixed(1)}%</p>
                      <p className="text-xs text-gray-600">success rate</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No cost data available yet</p>
            )}
          </InsightCard>
        </div>
      )}

      {/* Cost Optimization Insights */}
      {intelligentRouting?.cost_optimization && (
        <InsightCard
          title="Cost Optimization"
          description="Potential savings and recommendations"
          icon={CurrencyDollarIcon}
          color="green"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Potential Savings</p>
              <p className="text-2xl font-bold text-green-600">
                ${intelligentRouting.cost_optimization.potential_savings?.toFixed(2) || '0.00'}
              </p>
              <p className="text-xs text-gray-500">by switching to optimal providers</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Recommended Providers</p>
              <div className="space-y-1">
                {intelligentRouting.cost_optimization.recommended_providers?.slice(0, 3).map((provider, index) => (
                  <div key={provider.provider} className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{provider.provider}</span>
                    <span className="text-xs text-gray-600">${provider.avg_cost?.toFixed(4)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </InsightCard>
      )}
    </div>
  );

  const renderProviderPerformance = () => (
    <div className="space-y-6">
      {providerPerformance?.providers && Object.keys(providerPerformance.providers).length > 0 ? (
        <>
          {/* Performance Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {providerPerformance.summary.best_performer && (
              <InsightCard
                title="Best Performer"
                description="Highest efficiency score"
                icon={BoltIcon}
                color="green"
              >
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600 capitalize">
                    {providerPerformance.summary.best_performer}
                  </p>
                  <p className="text-sm text-gray-600">
                    Efficiency: {(providerPerformance.providers[providerPerformance.summary.best_performer]?.efficiency_score * 100).toFixed(1)}%
                  </p>
                </div>
              </InsightCard>
            )}

            {providerPerformance.summary.most_cost_efficient && (
              <InsightCard
                title="Most Cost Efficient"
                description="Best value for money"
                icon={CurrencyDollarIcon}
                color="yellow"
              >
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600 capitalize">
                    {providerPerformance.summary.most_cost_efficient}
                  </p>
                  <p className="text-sm text-gray-600">
                    Cost Efficiency: {providerPerformance.providers[providerPerformance.summary.most_cost_efficient]?.cost_efficiency?.toFixed(2) || '0.00'}
                  </p>
                </div>
              </InsightCard>
            )}

            {providerPerformance.summary.most_reliable && (
              <InsightCard
                title="Most Reliable"
                description="Highest reliability score"
                icon={ShieldCheckIcon}
                color="blue"
              >
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600 capitalize">
                    {providerPerformance.summary.most_reliable}
                  </p>
                  <p className="text-sm text-gray-600">
                    Reliability: {(providerPerformance.providers[providerPerformance.summary.most_reliable]?.reliability_score * 100).toFixed(1)}%
                  </p>
                </div>
              </InsightCard>
            )}
          </div>

          {/* Provider Performance Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(providerPerformance.providers)
              .sort(([,a], [,b]) => b.efficiency_score - a.efficiency_score)
              .map(([provider, stats], index) => (
                <ProviderCard
                  key={provider}
                  provider={provider}
                  stats={stats}
                  rank={index + 1}
                />
              ))}
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <CogIcon className="h-8 w-8 text-blue-600" />
          </div>
          <h4 className="text-lg font-semibold text-gray-700 mb-2">No Performance Data</h4>
          <p className="text-gray-500 text-sm">Provider performance data will appear here once you start making requests</p>
        </div>
      )}
    </div>
  );

  const renderRoutingInsights = () => (
    <div className="space-y-6">
      {routingInsights && (
        <>
          {/* Optimal Strategy */}
          <InsightCard
            title="Optimal Routing Strategy"
            description="Current best routing approach for your usage patterns"
            icon={LightBulbIcon}
            color="purple"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Current Strategy</p>
                <p className="text-xl font-bold text-purple-600 capitalize">
                  {routingInsights.optimal_routing_strategy}
                </p>
                <p className="text-xs text-gray-500">Based on performance analysis</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Recommended Providers</p>
                <div className="space-y-1">
                  {routingInsights.recommended_providers?.slice(0, 3).map((provider, index) => (
                    <div key={provider.provider} className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize">{provider.provider}</span>
                      <span className="text-xs text-gray-600">{(provider.success_rate * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </InsightCard>

          {/* Health Alerts */}
          {routingInsights.health_alerts && routingInsights.health_alerts.length > 0 && (
            <InsightCard
              title="Health Alerts"
              description="Providers that may need attention"
              icon={ShieldCheckIcon}
              color="red"
            >
              <div className="space-y-3">
                {routingInsights.health_alerts.map((alert, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center mr-3">
                        <span className="text-sm font-bold text-red-600">!</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 capitalize">{alert.provider}</p>
                        <p className="text-sm text-red-600">{alert.error}</p>
                      </div>
                    </div>
                    <span className="text-xs text-red-600 capitalize">{alert.status}</span>
                  </div>
                ))}
              </div>
            </InsightCard>
          )}

          {/* Performance Insights */}
          {routingInsights.performance_insights && routingInsights.performance_insights.length > 0 && (
            <InsightCard
              title="Performance Insights"
              description="Key insights about your routing performance"
              icon={BoltIcon}
              color="green"
            >
              <div className="space-y-3">
                {routingInsights.performance_insights.map((insight, index) => (
                  <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-xs font-bold text-green-600">✓</span>
                    </div>
                    <p className="text-sm text-gray-700">{insight.message}</p>
                  </div>
                ))}
              </div>
            </InsightCard>
          )}
        </>
      )}
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Header with Compact Time Filter */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Analytics</h1>
          <p className="text-gray-600 mt-2">Track your API usage and intelligent routing performance</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Time Range:</span>
          <div className="flex bg-gray-100 rounded-lg p-1">
            {[
              { value: '24h', label: '24h' },
              { value: '7d', label: '7d' },
              { value: '30d', label: '30d' },
              { value: '90d', label: '90d' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setTimeRange(option.value)}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-all duration-200 ${
                  timeRange === option.value
                    ? 'bg-white text-[#000000] shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center">
                <tab.icon className="h-4 w-4 mr-2" />
                {tab.name}
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'intelligent-routing' && renderIntelligentRouting()}
      {activeTab === 'provider-performance' && renderProviderPerformance()}
      {activeTab === 'routing-insights' && renderRoutingInsights()}
    </div>
  );
};

export default Analytics;