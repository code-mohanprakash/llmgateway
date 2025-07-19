import React, { useState, useEffect } from 'react';
import { 
  PlayIcon,
  StopIcon,
  ChartBarIcon,
  CpuChipIcon,
  BeakerIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';

const Orchestration = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      console.log('Fetching orchestration dashboard data...');
      const response = await api.get('/orchestration/dashboard');
      
      console.log('Orchestration dashboard response:', response.data);
      setDashboardData(response.data.dashboard_data);
    } catch (error) {
      console.error('Error fetching orchestration dashboard data:', error);
      
      // Set empty/zero data - no fake data
      setDashboardData({
        orchestration_enabled: false,
        workflow_stats: {
          total_workflows: 0,
          active_workflows: 0,
          executions_today: 0,
          success_rate: 0.0,
          avg_execution_time: 0.0
        },
        ab_testing_stats: {
          active_tests: 0,
          completed_tests: 0,
          total_variants_tested: 0,
          significant_results: 0,
          avg_improvement: 0.0
        },
        evaluation_stats: {
          benchmarks_available: 0,
          models_evaluated: 0,
          evaluations_this_week: 0,
          avg_quality_score: 0.0,
          performance_regressions: 0
        },
        cost_summary: {
          total_orchestration_cost: 0.0,
          workflow_cost: 0.0,
          ab_testing_cost: 0.0,
          evaluation_cost: 0.0
        },
        recent_activity: []
      });
    }
    setLoading(false);
    setRefreshing(false);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const handleCreateWorkflow = async () => {
    try {
      const workflowData = {
        name: "New Workflow",
        description: "A new workflow created from the dashboard",
        steps: [],
        connections: [],
        variables: {}
      };
      
      const response = await api.post('/orchestration/workflows', workflowData);
      
      if (response.data.success) {
        alert('Workflow created successfully!');
        fetchDashboardData(); // Refresh to show new data
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
      alert('Failed to create workflow. Please try again.');
    }
  };

  const handleCreateABTest = async () => {
    try {
      const testData = {
        name: "New A/B Test",
        description: "A new A/B test created from the dashboard",
        test_type: "model_comparison",
        variants: [],
        traffic_split: {},
        duration_days: 7
      };
      
      const response = await api.post('/orchestration/ab-tests', testData);
      
      if (response.data.success) {
        alert('A/B Test created successfully!');
        fetchDashboardData(); // Refresh to show new data
      }
    } catch (error) {
      console.error('Error creating A/B test:', error);
      alert('Failed to create A/B test. Please try again.');
    }
  };

  const handleCreateBenchmark = async () => {
    try {
      const benchmarkData = {
        name: "New Benchmark",
        description: "A new benchmark created from the dashboard",
        test_type: "performance",
        models: [],
        metrics: []
      };
      
      const response = await api.post('/orchestration/benchmarks', benchmarkData);
      
      if (response.data.success) {
        alert('Benchmark created successfully!');
        fetchDashboardData(); // Refresh to show new data
      }
    } catch (error) {
      console.error('Error creating benchmark:', error);
      alert('Failed to create benchmark. Please try again.');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`;
  };

  const getStatusIcon = (type) => {
    switch (type) {
      case 'workflow_completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'ab_test_significant':
        return <ChartBarIcon className="h-5 w-5 text-blue-600" />;
      case 'evaluation_completed':
        return <CpuChipIcon className="h-5 w-5 text-purple-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'workflows', name: 'Workflows', icon: PlayIcon },
    { id: 'ab-testing', name: 'A/B Testing', icon: BeakerIcon },
    { id: 'evaluation', name: 'Model Evaluation', icon: CpuChipIcon }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Workflows</p>
              <p className="text-2xl font-bold text-blue-600">
                {dashboardData?.workflow_stats?.active_workflows || 0}
              </p>
            </div>
            <PlayIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running A/B Tests</p>
              <p className="text-2xl font-bold text-green-600">
                {dashboardData?.ab_testing_stats?.active_tests || 0}
              </p>
            </div>
            <BeakerIcon className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Models Evaluated</p>
              <p className="text-2xl font-bold text-purple-600">
                {dashboardData?.evaluation_stats?.models_evaluated || 0}
              </p>
            </div>
            <CpuChipIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cost</p>
              <p className="text-2xl font-bold text-orange-600">
                {formatCurrency(dashboardData?.cost_summary?.total_orchestration_cost || 0)}
              </p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Workflow Performance</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Success Rate</span>
              <span className="text-sm font-medium text-green-600">
                {formatPercentage(dashboardData?.workflow_stats?.success_rate || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Avg Execution Time</span>
              <span className="text-sm font-medium text-gray-900">
                {dashboardData?.workflow_stats?.avg_execution_time || 0}min
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Executions Today</span>
              <span className="text-sm font-medium text-blue-600">
                {dashboardData?.workflow_stats?.executions_today || 0}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">A/B Testing Insights</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Significant Results</span>
              <span className="text-sm font-medium text-green-600">
                {dashboardData?.ab_testing_stats?.significant_results || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Avg Improvement</span>
              <span className="text-sm font-medium text-purple-600">
                {formatPercentage(dashboardData?.ab_testing_stats?.avg_improvement || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Variants Tested</span>
              <span className="text-sm font-medium text-blue-600">
                {dashboardData?.ab_testing_stats?.total_variants_tested || 0}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Model Evaluation</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Quality Score</span>
              <span className="text-sm font-medium text-green-600">
                {(dashboardData?.evaluation_stats?.avg_quality_score || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Evaluations This Week</span>
              <span className="text-sm font-medium text-blue-600">
                {dashboardData?.evaluation_stats?.evaluations_this_week || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Regressions Detected</span>
              <span className={`text-sm font-medium ${
                (dashboardData?.evaluation_stats?.performance_regressions || 0) > 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {dashboardData?.evaluation_stats?.performance_regressions || 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {dashboardData?.recent_activity?.length > 0 ? (
            dashboardData.recent_activity.map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                {getStatusIcon(activity.type)}
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.name}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
                {activity.improvement && (
                  <span className="text-sm font-medium text-green-600">
                    +{activity.improvement}%
                  </span>
                )}
                {activity.models_tested && (
                  <span className="text-sm font-medium text-blue-600">
                    {activity.models_tested} models
                  </span>
                )}
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {activity.status}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <ClockIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No recent activity</p>
              <p className="text-sm text-gray-500 mt-2">Start creating workflows, A/B tests, or evaluations to see activity here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderWorkflows = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Workflows</h2>
        <button 
          onClick={handleCreateWorkflow}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Create Workflow</span>
        </button>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="text-center py-8">
          <PlayIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No workflows created yet</p>
          <p className="text-sm text-gray-500 mt-2">Create your first workflow to start orchestrating AI operations</p>
          <button 
            onClick={handleCreateWorkflow}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create Your First Workflow
          </button>
        </div>
      </div>
    </div>
  );

  const renderABTesting = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">A/B Testing</h2>
        <button 
          onClick={handleCreateABTest}
          className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Create A/B Test</span>
        </button>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="text-center py-8">
          <BeakerIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No A/B tests running</p>
          <p className="text-sm text-gray-500 mt-2">Start testing model performance and optimize your AI pipeline</p>
          <button 
            onClick={handleCreateABTest}
            className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create Your First A/B Test
          </button>
        </div>
      </div>
    </div>
  );

  const renderEvaluation = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Model Evaluation</h2>
        <button 
          onClick={handleCreateBenchmark}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Create Benchmark</span>
        </button>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="text-center py-8">
          <CpuChipIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No benchmarks available</p>
          <p className="text-sm text-gray-500 mt-2">Create benchmarks to evaluate and compare model performance</p>
          <button 
            onClick={handleCreateBenchmark}
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Create Your First Benchmark
          </button>
        </div>
      </div>
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
            <h1 className="text-2xl font-bold text-gray-900">Orchestration & Evaluation</h1>
            <p className="mt-2 text-sm text-gray-600">
              Advanced workflow orchestration, A/B testing, and model evaluation capabilities
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
        {activeTab === 'workflows' && renderWorkflows()}
        {activeTab === 'ab-testing' && renderABTesting()}
        {activeTab === 'evaluation' && renderEvaluation()}
      </div>
    </div>
  );
};

export default Orchestration;