import React, { useState, useEffect } from 'react';
import { 
  CogIcon, 
  ChartBarIcon, 
  ClockIcon, 
  CpuChipIcon, 
  CircleStackIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  SignalIcon,
  BeakerIcon,
  SparklesIcon,
  LightBulbIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import api from '../services/api';
import toast from 'react-hot-toast';

const AdvancedRouting = () => {
  const [loading, setLoading] = useState(true);
  const [routingData, setRoutingData] = useState(null);
  const [predictiveData, setPredictiveData] = useState(null);
  const [weightData, setWeightData] = useState(null);
  const [geoData, setGeoData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchRoutingData();
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchRoutingData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchRoutingData = async () => {
    try {
      console.log('Fetching advanced routing data...');
      const [routingResponse, predictiveResponse, weightResponse, geoResponse] = await Promise.all([
        api.get('/dashboard/advanced-routing'),
        api.get('/dashboard/predictive-routing'),
        api.get('/v1/weight-management/stats'),
        api.get('/v1/geo-routing/stats')
      ]);
      
      console.log('Advanced routing response:', routingResponse.data);
      console.log('Predictive routing response:', predictiveResponse.data);
      console.log('Weight management response:', weightResponse.data);
      console.log('Geographic routing response:', geoResponse.data);
      
      setRoutingData(routingResponse.data);
      setPredictiveData(predictiveResponse.data);
      setWeightData(weightResponse.data);
      setGeoData(geoResponse.data);
    } catch (error) {
      console.error('Error fetching routing data:', error);
      // Don't show toast for connection errors to avoid spam
      if (error.response?.status !== 401 && error.response?.status !== 403) {
        console.log('Advanced routing backend not available - showing empty data');
      }
      
      // Set empty/zero data - no fake data
      setRoutingData({
        load_balancer_enabled: false,
        routing_status: {
          load_balancer_enabled: false,
          load_balancer_available: false,
          predictive_routing_enabled: false,
          intelligent_routing_enabled: false,
          fallback_enabled: false,
          performance_tracking: false
        },
        load_balancer_stats: {
          strategy: 'none',
          total_providers: 0,
          available_providers: 0,
          provider_weights: {},
          connection_pools: {},
          health_summary: {
            total_providers: 0,
            healthy_providers: 0,
            degraded_providers: 0,
            unhealthy_providers: 0,
            availability_percentage: 0,
            avg_response_time: 0,
            monitoring_active: false
          }
        },
        health_metrics: {
          overall_status: 'unknown',
          healthy_providers: 0,
          total_providers: 0,
          providers: {}
        }
      });
      
      // Set empty predictive data - no fake data
      setPredictiveData({
        predictive_routing_enabled: false,
        prediction_analytics: {
          model_stats: {
            providers_with_models: 0,
            total_training_data: 0,
            feature_stats: {}
          },
          patterns_summary: {
            total_patterns: 0,
            total_requests_analyzed: 0,
            patterns: []
          },
          cache_stats: {
            cached_predictions: 0,
            cache_ttl_minutes: 0
          },
          confidence_threshold: 0
        },
        model_performance: {
          providers_with_models: 0,
          total_training_data: 0,
          feature_stats: {}
        },
        pattern_insights: {
          total_patterns: 0,
          requests_analyzed: 0,
          top_patterns: []
        },
        confidence_metrics: {
          cached_predictions: 0,
          cache_hit_rate: 0,
          average_confidence: 0,
          confidence_threshold: 0
        }
      });
      
      // Set empty weight management data - no fake data
      setWeightData({
        enabled: false,
        stats: {
          total_adjustments: 0,
          recent_adjustments: 0,
          adjustment_types: {},
          provider_stats: {},
          configuration: {
            min_weight: 0,
            max_weight: 0,
            adjustment_sensitivity: 0,
            rebalance_threshold: 0,
            trend_window: 0,
            performance_weight: 0,
            availability_weight: 0,
            cost_weight: 0,
            response_time_weight: 0,
            load_balance_weight: 0
          },
          triggers: {},
          last_adjustment_time: null,
          ema_values: {
            response_time: {},
            success_rate: {},
            cost: {},
            availability: {}
          }
        }
      });
      
      // Set empty geographic routing data - no fake data
      setGeoData({
        enabled: false,
        configuration: {
          max_latency_threshold_ms: 0,
          latency_weight: 0,
          region_preference_weight: 0,
          performance_weight: 0,
          availability_weight: 0,
          fallback_enabled: false,
          max_providers_per_request: 0,
          confidence_threshold: 0
        },
        provider_regions: {},
        region_preferences: {},
        routing_rules: [],
        latency_stats: {},
        analytics: {
          total_routing_rules: 0,
          enabled_routing_rules: 0,
          geoip_available: false,
          latency_monitor_active: false,
          recent_routing_decisions: []
        }
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchRoutingData();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircleIcon className="w-5 h-5" />;
      case 'degraded': return <ExclamationTriangleIcon className="w-5 h-5" />;
      case 'unhealthy': return <XCircleIcon className="w-5 h-5" />;
      default: return <CircleStackIcon className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CogIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Load Balancer</p>
              <p className="text-2xl font-semibold text-gray-900">
                {routingData?.load_balancer_enabled ? 'Enabled' : 'Disabled'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <SignalIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Available Providers</p>
              <p className="text-2xl font-semibold text-gray-900">
                {routingData?.load_balancer_stats?.available_providers || 0} / {routingData?.load_balancer_stats?.total_providers || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg Response Time</p>
              <p className="text-2xl font-semibold text-gray-900">
                {routingData?.load_balancer_stats?.health_summary?.avg_response_time?.toFixed(2) || '0.00'}s
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Availability</p>
              <p className="text-2xl font-semibold text-gray-900">
                {routingData?.load_balancer_stats?.health_summary?.availability_percentage?.toFixed(1) || '0.0'}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Health Status */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Provider Health Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {routingData?.health_metrics?.providers && Object.entries(routingData.health_metrics.providers).map(([provider, metrics]) => (
              <div key={provider} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 capitalize">{provider}</h4>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(metrics.status)}`}>
                    {getStatusIcon(metrics.status)}
                    <span className="ml-1 capitalize">{metrics.status}</span>
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Response Time: {metrics.response_time?.toFixed(2) || 'N/A'}s
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderLoadBalancer = () => (
    <div className="space-y-6">
      {/* Load Balancer Configuration */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Load Balancer Configuration</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Settings</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Strategy:</span>
                  <span className="text-sm font-medium capitalize">{routingData?.load_balancer_stats?.strategy || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Intelligent Routing:</span>
                  <span className="text-sm font-medium">{routingData?.routing_status?.intelligent_routing_enabled ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Fallback:</span>
                  <span className="text-sm font-medium">{routingData?.routing_status?.fallback_enabled ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Performance Tracking:</span>
                  <span className="text-sm font-medium">{routingData?.routing_status?.performance_tracking ? 'Enabled' : 'Disabled'}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Health Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Monitoring Active:</span>
                  <span className="text-sm font-medium">{routingData?.load_balancer_stats?.health_summary?.monitoring_active ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Healthy Providers:</span>
                  <span className="text-sm font-medium">{routingData?.load_balancer_stats?.health_summary?.healthy_providers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Degraded Providers:</span>
                  <span className="text-sm font-medium">{routingData?.load_balancer_stats?.health_summary?.degraded_providers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Unhealthy Providers:</span>
                  <span className="text-sm font-medium">{routingData?.load_balancer_stats?.health_summary?.unhealthy_providers || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Weights */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Provider Weights</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {routingData?.provider_weights && Object.entries(routingData.provider_weights).map(([provider, weight]) => (
              <div key={provider} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 capitalize">{provider}</h4>
                  <span className="text-lg font-semibold text-blue-600">
                    {weight.current_weight?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Performance:</span>
                    <div className="font-medium">{weight.performance_multiplier?.toFixed(2) || '0.00'}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Health:</span>
                    <div className="font-medium">{weight.health_multiplier?.toFixed(2) || '0.00'}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Base:</span>
                    <div className="font-medium">{weight.base_weight?.toFixed(2) || '0.00'}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Connection Pools */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Connection Pools</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {routingData?.connection_pools && Object.entries(routingData.connection_pools).map(([provider, pool]) => (
              <div key={provider} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 capitalize mb-2">{provider}</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Active:</span>
                    <span className="font-medium">{pool.active_connections || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Max:</span>
                    <span className="font-medium">{pool.max_connections || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Usage:</span>
                    <span className="font-medium">{((pool.utilization || 0) * 100).toFixed(1)}%</span>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(pool.utilization || 0) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderPredictiveRouting = () => (
    <div className="space-y-6">
      {/* Predictive Routing Status */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Predictive Routing Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <BeakerIcon className="w-8 h-8 text-purple-600" />
              </div>
              <div className="text-sm text-gray-500">ML Models</div>
              <div className="text-2xl font-semibold text-gray-900">
                {predictiveData?.model_performance?.providers_with_models || 0}
              </div>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <SparklesIcon className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-sm text-gray-500">Training Data</div>
              <div className="text-2xl font-semibold text-gray-900">
                {predictiveData?.model_performance?.total_training_data || 0}
              </div>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <LightBulbIcon className="w-8 h-8 text-orange-600" />
              </div>
              <div className="text-sm text-gray-500">Patterns</div>
              <div className="text-2xl font-semibold text-gray-900">
                {predictiveData?.pattern_insights?.total_patterns || 0}
              </div>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <EyeIcon className="w-8 h-8 text-blue-600" />
              </div>
              <div className="text-sm text-gray-500">Avg Confidence</div>
              <div className="text-2xl font-semibold text-gray-900">
                {((predictiveData?.confidence_metrics?.average_confidence || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Request Patterns */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Request Patterns</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {predictiveData?.pattern_insights?.top_patterns?.map((pattern, index) => (
              <div key={pattern.pattern_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{pattern.pattern_id.replace(/_/g, ' ')}</h4>
                  <span className="text-sm text-gray-500">#{index + 1}</span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Frequency:</span>
                    <div className="font-medium">{pattern.frequency}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Success Rate:</span>
                    <div className="font-medium">{(pattern.success_rate * 100).toFixed(1)}%</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Confidence:</span>
                    <div className="font-medium">{(pattern.confidence_score * 100).toFixed(1)}%</div>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${pattern.confidence_score * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Model Performance */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Model Performance</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {predictiveData?.model_performance?.feature_stats && Object.entries(predictiveData.model_performance.feature_stats).map(([provider, stats]) => (
              <div key={provider} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 capitalize mb-3">{provider}</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Response Time:</span>
                    <span className="text-sm font-medium">{stats.avg_response_time?.toFixed(2) || 'N/A'}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Success Rate:</span>
                    <span className="text-sm font-medium">{((stats.success_rate || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Error Rate:</span>
                    <span className="text-sm font-medium">{((stats.recent_error_rate || 0) * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Prediction Cache */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Prediction Cache</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-900">
                {predictiveData?.confidence_metrics?.cached_predictions || 0}
              </div>
              <div className="text-sm text-gray-500">Cached Predictions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-900">
                {((predictiveData?.confidence_metrics?.cache_hit_rate || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500">Cache Hit Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-900">
                {((predictiveData?.confidence_metrics?.confidence_threshold || 0) * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-500">Confidence Threshold</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderWeightManagement = () => (
    <div className="space-y-6">
      {/* Weight Management Status */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Weight Management Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <ChartBarIcon className="w-8 h-8 text-blue-600" />
              </div>
              <div className="text-sm text-gray-500">Total Adjustments</div>
              <div className="text-2xl font-semibold text-gray-900">
                {weightData?.stats?.total_adjustments || 0}
              </div>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <ClockIcon className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-sm text-gray-500">Recent Adjustments</div>
              <div className="text-2xl font-semibold text-gray-900">
                {weightData?.stats?.recent_adjustments || 0}
              </div>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <CogIcon className="w-8 h-8 text-purple-600" />
              </div>
              <div className="text-sm text-gray-500">Active Providers</div>
              <div className="text-2xl font-semibold text-gray-900">
                {weightData?.stats?.provider_stats ? Object.keys(weightData.stats.provider_stats).length : 0}
              </div>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-2">
                <SignalIcon className="w-8 h-8 text-orange-600" />
              </div>
              <div className="text-sm text-gray-500">Avg Performance</div>
              <div className="text-2xl font-semibold text-gray-900">
                {weightData?.stats?.provider_stats ? 
                  (Object.values(weightData.stats.provider_stats).reduce((sum, p) => sum + p.performance_score, 0) / 
                   Object.values(weightData.stats.provider_stats).length * 100).toFixed(1) : 0}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Weight Metrics */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Provider Weight Metrics</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {weightData?.stats?.provider_stats && Object.entries(weightData.stats.provider_stats).map(([provider, stats]) => (
              <div key={provider} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-medium text-gray-900 capitalize">{provider}</h4>
                  <span className="text-lg font-semibold text-blue-600">
                    {stats.current_weight?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Performance Score</span>
                    <span className="text-sm font-medium">{(stats.performance_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${stats.performance_score * 100}%` }}
                    ></div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Base Weight:</span>
                      <div className="font-medium">{stats.base_weight?.toFixed(2) || '0.00'}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Weight Ratio:</span>
                      <div className="font-medium">{stats.weight_ratio?.toFixed(2) || '0.00'}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Adjustments:</span>
                      <div className="font-medium">{stats.adjustment_count || 0}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Last Updated:</span>
                      <div className="font-medium text-xs">
                        {stats.last_updated ? new Date(stats.last_updated).toLocaleTimeString() : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Adjustment Types Distribution */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Adjustment Types Distribution</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {weightData?.stats?.adjustment_types && Object.entries(weightData.stats.adjustment_types).map(([type, count]) => (
              <div key={type} className="border rounded-lg p-4 text-center">
                <div className="text-2xl font-semibold text-gray-900">{count}</div>
                <div className="text-sm text-gray-500 capitalize">{type.replace(/_/g, ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* EMA Values */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Exponential Moving Averages</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Response Time EMA */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Response Time (seconds)</h4>
              <div className="space-y-2">
                {weightData?.stats?.ema_values?.response_time && Object.entries(weightData.stats.ema_values.response_time).map(([provider, value]) => (
                  <div key={provider} className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 capitalize">{provider}</span>
                    <span className="text-sm font-medium">{value?.toFixed(2) || '0.00'}s</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Success Rate EMA */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Success Rate</h4>
              <div className="space-y-2">
                {weightData?.stats?.ema_values?.success_rate && Object.entries(weightData.stats.ema_values.success_rate).map(([provider, value]) => (
                  <div key={provider} className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 capitalize">{provider}</span>
                    <span className="text-sm font-medium">{(value * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Cost EMA */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Cost per 1K Tokens</h4>
              <div className="space-y-2">
                {weightData?.stats?.ema_values?.cost && Object.entries(weightData.stats.ema_values.cost).map(([provider, value]) => (
                  <div key={provider} className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 capitalize">{provider}</span>
                    <span className="text-sm font-medium">${value?.toFixed(3) || '0.000'}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Availability EMA */}
            <div className="border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Availability</h4>
              <div className="space-y-2">
                {weightData?.stats?.ema_values?.availability && Object.entries(weightData.stats.ema_values.availability).map(([provider, value]) => (
                  <div key={provider} className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 capitalize">{provider}</span>
                    <span className="text-sm font-medium">{(value * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Weight Configuration */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Weight Configuration</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Weight Settings</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Min Weight:</span>
                  <span className="text-sm font-medium">{weightData?.stats?.configuration?.min_weight || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Max Weight:</span>
                  <span className="text-sm font-medium">{weightData?.stats?.configuration?.max_weight || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Adjustment Sensitivity:</span>
                  <span className="text-sm font-medium">{weightData?.stats?.configuration?.adjustment_sensitivity || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Rebalance Threshold:</span>
                  <span className="text-sm font-medium">{weightData?.stats?.configuration?.rebalance_threshold || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Trend Window:</span>
                  <span className="text-sm font-medium">{weightData?.stats?.configuration?.trend_window || 0}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Weight Factors</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Performance Weight:</span>
                  <span className="text-sm font-medium">{((weightData?.stats?.configuration?.performance_weight || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Availability Weight:</span>
                  <span className="text-sm font-medium">{((weightData?.stats?.configuration?.availability_weight || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Cost Weight:</span>
                  <span className="text-sm font-medium">{((weightData?.stats?.configuration?.cost_weight || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Response Time Weight:</span>
                  <span className="text-sm font-medium">{((weightData?.stats?.configuration?.response_time_weight || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Load Balance Weight:</span>
                  <span className="text-sm font-medium">{((weightData?.stats?.configuration?.load_balance_weight || 0) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Adjustment Triggers */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Adjustment Triggers</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {weightData?.stats?.triggers && Object.entries(weightData.stats.triggers).map(([trigger, config]) => (
              <div key={trigger} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 capitalize">{trigger.replace(/_/g, ' ')}</h4>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    config.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {config.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  Threshold: {(config.threshold * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderGeographicRouting = () => (
    <div className="space-y-6">
      {/* Geographic Routing Configuration */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Geographic Routing Configuration</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Status</h4>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  geoData?.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {geoData?.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <p className="text-sm text-gray-600">Geographic routing system status</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">GeoIP Database</h4>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  geoData?.analytics?.geoip_available ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {geoData?.analytics?.geoip_available ? 'Available' : 'Fallback'}
                </span>
              </div>
              <p className="text-sm text-gray-600">Location detection system</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Latency Monitor</h4>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  geoData?.analytics?.latency_monitor_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {geoData?.analytics?.latency_monitor_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="text-sm text-gray-600">Real-time latency tracking</p>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Regions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Provider Regional Coverage</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {geoData?.provider_regions && Object.entries(geoData.provider_regions).map(([provider, regions]) => (
              <div key={provider} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 capitalize mb-2">{provider}</h4>
                <div className="space-y-1">
                  {regions.map((region) => (
                    <span key={region} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2 mb-1">
                      {region}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Latency Statistics */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Regional Latency Statistics</h3>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">North America</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Europe</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asia Pacific</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {geoData?.latency_stats && Object.entries(geoData.latency_stats).map(([provider, regions]) => (
                  <tr key={provider}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">{provider}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {regions['North America'] ? `${regions['North America'].avg_latency_ms}ms` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {regions['Europe'] ? `${regions['Europe'].avg_latency_ms}ms` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {regions['Asia Pacific'] ? `${regions['Asia Pacific'].avg_latency_ms}ms` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Routing Rules */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Routing Rules</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {geoData?.routing_rules && geoData.routing_rules.map((rule) => (
              <div key={rule.rule_id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h4 className="font-medium text-gray-900">{rule.name}</h4>
                    <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      rule.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {rule.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                </div>
                <div className="text-sm text-gray-500">
                  Priority: {rule.priority}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Routing Decisions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Routing Decisions</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {geoData?.analytics?.recent_routing_decisions && geoData.analytics.recent_routing_decisions.map((decision, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-900">
                      {decision.client_location.country}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({decision.client_location.region})
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(decision.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">Providers:</span>
                    {decision.selected_providers.map((provider) => (
                      <span key={provider} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {provider}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">
                      Confidence: {(decision.confidence_score * 100).toFixed(1)}%
                    </span>
                    <span className="text-sm text-gray-600">
                      Reason: {decision.routing_reason}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Advanced Routing</h1>
            <p className="text-gray-600 mt-1">Monitor and manage intelligent load balancing and provider routing</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <ArrowPathIcon className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <nav className="flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('load-balancer')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'load-balancer'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Load Balancer
          </button>
          <button
            onClick={() => setActiveTab('predictive')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'predictive'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Predictive Routing
          </button>
          <button
            onClick={() => setActiveTab('weight-management')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'weight-management'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Weight Management
          </button>
          <button
            onClick={() => setActiveTab('geographic-routing')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'geographic-routing'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Geographic Routing
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'load-balancer' && renderLoadBalancer()}
      {activeTab === 'predictive' && renderPredictiveRouting()}
      {activeTab === 'weight-management' && renderWeightManagement()}
      {activeTab === 'geographic-routing' && renderGeographicRouting()}
    </div>
  );
};

export default AdvancedRouting;