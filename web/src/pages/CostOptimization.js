import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  CpuChipIcon, 
  CircleStackIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  LightBulbIcon,
  ArrowTrendingUpIcon,
  BanknotesIcon,
  ScaleIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';

const CostOptimization = () => {
  const [loading, setLoading] = useState(true);
  const [costData, setCostData] = useState(null);
  const [budgetData, setBudgetData] = useState(null);
  const [cacheData, setCacheData] = useState(null);
  const [arbitrageData, setArbitrageData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchCostOptimizationData();
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchCostOptimizationData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchCostOptimizationData = async () => {
    try {
      console.log('Fetching cost optimization data...');
      const [costResponse, budgetResponse, cacheResponse, arbitrageResponse] = await Promise.all([
        api.get('/cost-optimization/dashboard'),
        api.get('/cost-optimization/budget-status'),
        api.get('/cost-optimization/cache-stats'),
        api.get('/cost-optimization/arbitrage-opportunities')
      ]);
      
      console.log('Cost optimization response:', costResponse.data);
      console.log('Budget response:', budgetResponse.data);
      console.log('Cache response:', cacheResponse.data);
      console.log('Arbitrage response:', arbitrageResponse.data);
      
      setCostData(costResponse.data);
      setBudgetData(budgetResponse.data);
      setCacheData(cacheResponse.data);
      setArbitrageData(arbitrageResponse.data);
    } catch (error) {
      console.error('Error fetching cost optimization data:', error);
      // Don't show toast for connection errors to avoid spam
      if (error.response?.status !== 401 && error.response?.status !== 403) {
        console.log('Cost optimization backend not available - showing empty data');
      }
      
      // Set empty/zero data - no fake data
      setCostData({
        cost_optimization_enabled: false,
        token_prediction: {
          enabled: false,
          total_predictions: 0,
          accuracy: 0.0,
          cost_savings: 0.0
        },
        budget_management: {
          enabled: false,
          total_budgets: 0,
          active_budgets: 0,
          budget_alerts: 0
        },
        cost_caching: {
          enabled: false,
          cache_hit_rate: 0.0,
          cost_savings: 0.0,
          cache_size: 0
        },
        provider_arbitrage: {
          enabled: false,
          total_opportunities: 0,
          executed_opportunities: 0,
          cost_savings: 0.0
        }
      });
      
      setBudgetData({
        budget_configured: false,
        total_budget: 0.0,
        current_usage: 0.0,
        usage_percentage: 0.0,
        remaining_budget: 0.0,
        status: 'no_budget',
        alerts: []
      });
      
      setCacheData({
        cache_enabled: false,
        hit_rate: 0.0,
        total_requests: 0,
        cache_hits: 0,
        cache_misses: 0,
        cost_savings: 0.0,
        storage_cost: 0.0,
        net_savings: 0.0
      });
      
      setArbitrageData({
        arbitrage_enabled: false,
        active_opportunities: 0,
        total_opportunities: 0,
        executed_opportunities: 0,
        total_savings: 0.0,
        opportunities: []
      });
    }
    setLoading(false);
    setRefreshing(false);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchCostOptimizationData();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };


  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
      case 'exceeded':
        return <XCircleIcon className="h-5 w-5 text-red-600" />;
      default:
        return <CircleStackIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'token-prediction', name: 'Token Prediction', icon: CpuChipIcon },
    { id: 'budget-management', name: 'Budget Management', icon: BanknotesIcon },
    { id: 'cost-caching', name: 'Cost Caching', icon: CircleStackIcon },
    { id: 'provider-arbitrage', name: 'Provider Arbitrage', icon: ScaleIcon }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Savings</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(
                  (costData?.token_prediction?.cost_savings || 0) +
                  (costData?.cost_caching?.cost_savings || 0) +
                  (costData?.provider_arbitrage?.cost_savings || 0)
                )}
              </p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Budget Status</p>
              <p className="text-2xl font-bold text-blue-600">
                {budgetData?.budget_configured ? 
                  `${budgetData.usage_percentage.toFixed(1)}%` : 
                  'Not Set'
                }
              </p>
            </div>
            <BanknotesIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cache Hit Rate</p>
              <p className="text-2xl font-bold text-purple-600">
                {formatPercentage(cacheData?.hit_rate || 0)}
              </p>
            </div>
            <CircleStackIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Arbitrage Opportunities</p>
              <p className="text-2xl font-bold text-orange-600">
                {arbitrageData?.active_opportunities || 0}
              </p>
            </div>
            <ScaleIcon className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Feature Status */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Optimization Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            {costData?.cost_optimization_enabled ? 
              <CheckCircleIcon className="h-5 w-5 text-green-600" /> :
              <XCircleIcon className="h-5 w-5 text-red-600" />
            }
            <span className="text-sm text-gray-700">Cost Optimization Engine</span>
          </div>
          <div className="flex items-center space-x-3">
            {costData?.token_prediction?.enabled ? 
              <CheckCircleIcon className="h-5 w-5 text-green-600" /> :
              <XCircleIcon className="h-5 w-5 text-red-600" />
            }
            <span className="text-sm text-gray-700">Token-level Prediction</span>
          </div>
          <div className="flex items-center space-x-3">
            {costData?.budget_management?.enabled ? 
              <CheckCircleIcon className="h-5 w-5 text-green-600" /> :
              <XCircleIcon className="h-5 w-5 text-red-600" />
            }
            <span className="text-sm text-gray-700">Budget Management</span>
          </div>
          <div className="flex items-center space-x-3">
            {costData?.cost_caching?.enabled ? 
              <CheckCircleIcon className="h-5 w-5 text-green-600" /> :
              <XCircleIcon className="h-5 w-5 text-red-600" />
            }
            <span className="text-sm text-gray-700">Cost-aware Caching</span>
          </div>
          <div className="flex items-center space-x-3">
            {costData?.provider_arbitrage?.enabled ? 
              <CheckCircleIcon className="h-5 w-5 text-green-600" /> :
              <XCircleIcon className="h-5 w-5 text-red-600" />
            }
            <span className="text-sm text-gray-700">Provider Arbitrage</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTokenPrediction = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Token-level Cost Prediction</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {costData?.token_prediction?.total_predictions || 0}
            </div>
            <div className="text-sm text-gray-600">Total Predictions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatPercentage(costData?.token_prediction?.accuracy || 0)}
            </div>
            <div className="text-sm text-gray-600">Prediction Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(costData?.token_prediction?.cost_savings || 0)}
            </div>
            <div className="text-sm text-gray-600">Cost Savings</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">How Token Prediction Works</h4>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <CpuChipIcon className="h-5 w-5 text-blue-600 mt-0.5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Model-specific Tokenization</p>
              <p className="text-sm text-gray-600">Different models use different tokenization methods for accurate counting</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-5 w-5 text-green-600 mt-0.5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Cost Prediction</p>
              <p className="text-sm text-gray-600">Predicts costs based on token counts and provider pricing</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <LightBulbIcon className="h-5 w-5 text-purple-600 mt-0.5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Optimization Recommendations</p>
              <p className="text-sm text-gray-600">Suggests cost-effective alternatives and optimizations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderBudgetManagement = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Budget Overview</h3>
          {getStatusIcon(budgetData?.status)}
        </div>
        
        {budgetData?.budget_configured ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {formatCurrency(budgetData.total_budget)}
                </div>
                <div className="text-sm text-gray-600">Total Budget</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(budgetData.current_usage)}
                </div>
                <div className="text-sm text-gray-600">Current Usage</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {formatCurrency(budgetData.remaining_budget)}
                </div>
                <div className="text-sm text-gray-600">Remaining Budget</div>
              </div>
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Budget Usage</span>
                <span className="text-sm text-gray-500">
                  {budgetData.usage_percentage.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    budgetData.usage_percentage > 90 ? 'bg-red-600' :
                    budgetData.usage_percentage > 75 ? 'bg-yellow-600' :
                    'bg-green-600'
                  }`}
                  style={{width: `${Math.min(budgetData.usage_percentage, 100)}%`}}
                ></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <BanknotesIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No budget configured</p>
            <p className="text-sm text-gray-500 mt-2">Set up a budget to track and control your costs</p>
          </div>
        )}
      </div>

      {budgetData?.alerts && budgetData.alerts.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Budget Alerts</h4>
          <div className="space-y-3">
            {budgetData.alerts.map((alert, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
                <span className="text-sm text-yellow-800">{alert.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderCostCaching = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Cost-aware Caching</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatPercentage(cacheData?.hit_rate || 0)}
            </div>
            <div className="text-sm text-gray-600">Hit Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {cacheData?.total_requests || 0}
            </div>
            <div className="text-sm text-gray-600">Total Requests</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(cacheData?.cost_savings || 0)}
            </div>
            <div className="text-sm text-gray-600">Cost Savings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(cacheData?.net_savings || 0)}
            </div>
            <div className="text-sm text-gray-600">Net Savings</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">Cache Performance</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Cache Hits</span>
              <span className="text-sm font-medium text-green-600">
                {cacheData?.cache_hits || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Cache Misses</span>
              <span className="text-sm font-medium text-red-600">
                {cacheData?.cache_misses || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Storage Cost</span>
              <span className="text-sm font-medium text-gray-900">
                {formatCurrency(cacheData?.storage_cost || 0)}
              </span>
            </div>
          </div>
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {cacheData?.cache_enabled ? 'Enabled' : 'Disabled'}
              </div>
              <div className="text-sm text-gray-600">Cache Status</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderProviderArbitrage = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Provider Arbitrage</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {arbitrageData?.active_opportunities || 0}
            </div>
            <div className="text-sm text-gray-600">Active Opportunities</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {arbitrageData?.executed_opportunities || 0}
            </div>
            <div className="text-sm text-gray-600">Executed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(arbitrageData?.total_savings || 0)}
            </div>
            <div className="text-sm text-gray-600">Total Savings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {arbitrageData?.arbitrage_enabled ? 'Enabled' : 'Disabled'}
            </div>
            <div className="text-sm text-gray-600">Status</div>
          </div>
        </div>
      </div>

      {arbitrageData?.opportunities && arbitrageData.opportunities.length > 0 ? (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Current Opportunities</h4>
          <div className="space-y-3">
            {arbitrageData.opportunities.slice(0, 5).map((opportunity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ScaleIcon className="h-5 w-5 text-green-600" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {opportunity.from_provider} → {opportunity.to_provider}
                    </div>
                    <div className="text-xs text-gray-500">
                      {opportunity.savings_percentage}% savings
                    </div>
                  </div>
                </div>
                <div className="text-sm font-medium text-green-600">
                  {formatCurrency(opportunity.potential_savings)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="text-center py-8">
            <ScaleIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No arbitrage opportunities available</p>
            <p className="text-sm text-gray-500 mt-2">The system is monitoring for cost-saving opportunities</p>
          </div>
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Cost Optimization</h1>
            <p className="mt-2 text-sm text-gray-600">
              Advanced cost optimization with token prediction, budget management, and provider arbitrage
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <ArrowPathIcon className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="bg-gray-50 rounded-lg p-6">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'token-prediction' && renderTokenPrediction()}
        {activeTab === 'budget-management' && renderBudgetManagement()}
        {activeTab === 'cost-caching' && renderCostCaching()}
        {activeTab === 'provider-arbitrage' && renderProviderArbitrage()}
      </div>
    </div>
  );
};

export default CostOptimization;