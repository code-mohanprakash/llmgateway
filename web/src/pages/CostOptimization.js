import React from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { 
  CurrencyDollarIcon,
  ChartPieIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  CalculatorIcon,
  ChartBarIcon,
  CogIcon,
  SparklesIcon,
  BrainIcon,
  ShieldCheckIcon,
  TrendingUpIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

const CostOptimization = () => {
  const features = [
    {
      title: 'Token-Level Cost Prediction',
      icon: CalculatorIcon,
      description: 'Predict costs before making requests and optimize for the most cost-effective provider',
      details: [
        'Pre-request cost estimation with 95% accuracy',
        'Token counting and pricing calculation',
        'Real-time pricing updates from all providers',
        'Cost prediction accuracy tracking',
        'Budget-aware routing decisions'
      ],
      competitive: 'Other platforms charge you after the fact. We predict and optimize costs before each request, saving 30-50% on average.',
      technical: 'Uses tiktoken for accurate token counting, maintains real-time pricing database, and implements linear regression for cost prediction with confidence intervals.'
    },
    {
      title: 'Budget Management System',
      icon: ChartPieIcon,
      description: 'Comprehensive budget tracking with alerts, projections, and automatic throttling',
      details: [
        'Multi-period budget tracking (daily, weekly, monthly)',
        'Alert thresholds with configurable percentages',
        'Burn rate calculation and projections',
        'Automatic throttling when limits approached',
        'Department and model allocation tracking'
      ],
      competitive: 'Basic cost tracking vs. our enterprise-grade budget management with predictive analytics and automatic controls.',
      technical: 'Implements exponential moving averages for burn rate calculation, uses statistical forecasting for projections, and maintains hierarchical budget structures with role-based access.'
    },
    {
      title: 'Provider Cost Arbitrage',
      icon: ArrowTrendingUpIcon,
      description: 'Automatically switch between providers to find the best price for each request type',
      details: [
        'Real-time price comparison across providers',
        'Task-specific cost optimization',
        'Quality vs. cost trade-off analysis',
        'Historical cost trend analysis',
        'Automated provider switching'
      ],
      competitive: 'Manual provider selection vs. our intelligent arbitrage that finds the best deal automatically while maintaining quality.',
      technical: 'Uses dynamic programming for optimal provider selection, implements multi-objective optimization considering cost, quality, and speed, with real-time price monitoring.'
    },
    {
      title: 'Cost-Aware Caching',
      icon: CogIcon,
      description: 'Intelligent caching that considers both performance and cost savings',
      details: [
        'Cost-aware cache eviction policies',
        'Provider-specific caching strategies',
        'Cache hit rate optimization',
        'Cost savings tracking',
        'Intelligent cache warming'
      ],
      competitive: 'Basic caching vs. our cost-aware system that optimizes for both performance and cost savings, achieving 70% cache hit rates.',
      technical: 'Implements LRU with cost-weighted eviction, uses Redis for distributed caching, and maintains cache effectiveness metrics with automatic optimization.'
    },
    {
      title: 'Budget Alerts & Controls',
      icon: ExclamationTriangleIcon,
      description: 'Proactive budget monitoring with automatic controls and alerts',
      details: [
        'Multi-level alert thresholds (75%, 90%, 95%)',
        'Automatic throttling at budget limits',
        'Real-time spending notifications',
        'Projection-based early warnings',
        'Custom alert rules and actions'
      ],
      competitive: 'Reactive budget management vs. our proactive system that prevents overspending before it happens.',
      technical: 'Uses sliding window algorithms for real-time monitoring, implements circuit breakers for automatic throttling, and maintains alert history with escalation policies.'
    },
    {
      title: 'Cost Analytics & Insights',
      icon: ChartBarIcon,
      description: 'Deep cost analytics with actionable insights and optimization recommendations',
      details: [
        'Cost breakdown by model, provider, and usage',
        'Trend analysis and forecasting',
        'Optimization recommendations',
        'ROI calculation and reporting',
        'Cost center allocation'
      ],
      competitive: 'Basic cost reports vs. our ML-powered analytics that provide actionable insights and automated optimization recommendations.',
      technical: 'Uses time-series analysis for trend detection, implements anomaly detection for cost spikes, and provides automated optimization suggestions based on historical patterns.'
    }
  ];

  const competitiveComparison = [
    {
      feature: 'Cost Prediction',
      basic: 'Post-request cost tracking only',
      modelBridge: 'Pre-request cost prediction with 95% accuracy',
      advantage: '30-50% cost savings'
    },
    {
      feature: 'Budget Management',
      basic: 'Simple spending limits',
      modelBridge: 'Multi-period budgets with projections and alerts',
      advantage: 'Prevent overspending'
    },
    {
      feature: 'Provider Selection',
      basic: 'Manual provider choice',
      modelBridge: 'Automatic arbitrage and optimization',
      advantage: 'Always best price'
    },
    {
      feature: 'Caching Strategy',
      basic: 'Basic response caching',
      modelBridge: 'Cost-aware caching with 70% hit rate',
      advantage: 'Performance + savings'
    },
    {
      feature: 'Alerts & Controls',
      basic: 'Simple threshold alerts',
      modelBridge: 'Proactive controls with automatic throttling',
      advantage: 'Zero budget surprises'
    },
    {
      feature: 'Analytics',
      basic: 'Basic cost reports',
      modelBridge: 'ML-powered insights and recommendations',
      advantage: 'Actionable optimization'
    }
  ];

  const costSavings = [
    {
      metric: 'Average Cost Reduction',
      value: '50-80%',
      description: 'Through intelligent provider selection and optimization'
    },
    {
      metric: 'Cache Hit Rate',
      value: '70%',
      description: 'Cost-aware caching reduces redundant requests'
    },
    {
      metric: 'Budget Compliance',
      value: '99%',
      description: 'Proactive controls prevent overspending'
    },
    {
      metric: 'Prediction Accuracy',
      value: '95%',
      description: 'Accurate cost prediction before requests'
    },
    {
      metric: 'Provider Utilization',
      value: 'Optimized',
      description: 'Intelligent routing maximizes cost efficiency'
    },
    {
      metric: 'ROI Improvement',
      value: '3-5x',
      description: 'Better cost management increases returns'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <Navigation />
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-800 rounded-full text-sm font-medium mb-6">
              <CurrencyDollarIcon className="h-4 w-4 mr-2" />
              Cost Optimization Engine
            </div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="block text-gray-900">Intelligent Cost</span>
              <span className="block bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">
                Optimization
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              While others track costs after the fact, we predict and optimize costs before each request. 
              Our intelligent cost optimization engine saves enterprises 50-80% on AI costs while maintaining 
              or improving performance and quality.
            </p>
            
            {/* Key Stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-12">
          <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">50-80%</div>
            <div className="text-sm text-gray-600">Cost Savings</div>
          </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">95%</div>
                <div className="text-sm text-gray-600">Prediction Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">70%</div>
                <div className="text-sm text-gray-600">Cache Hit Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">99%</div>
                <div className="text-sm text-gray-600">Budget Compliance</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">3-5x</div>
                <div className="text-sm text-gray-600">ROI Improvement</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">&lt;1s</div>
                <div className="text-sm text-gray-600">Optimization Time</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                The Cost Problem in AI
              </h2>
              <div className="space-y-4">
                <div className="flex items-start">
                  <XCircleIcon className="h-6 w-6 text-gray-500 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Post-Fact Cost Tracking</h3>
                    <p className="text-gray-600">You only know the cost after the request is made, with no way to optimize beforehand.</p>
            </div>
          </div>
                <div className="flex items-start">
                  <XCircleIcon className="h-6 w-6 text-gray-500 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-gray-900">No Budget Controls</h3>
                    <p className="text-gray-600">Simple spending limits that don't prevent overspending or provide early warnings.</p>
            </div>
          </div>
                <div className="flex items-start">
                  <XCircleIcon className="h-6 w-6 text-gray-500 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Manual Provider Selection</h3>
                    <p className="text-gray-600">You have to manually choose providers without knowing real-time pricing or performance.</p>
            </div>
          </div>
                <div className="flex items-start">
                  <XCircleIcon className="h-6 w-6 text-gray-500 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-gray-900">No Cost Intelligence</h3>
                    <p className="text-gray-600">Basic cost reports without actionable insights or optimization recommendations.</p>
          </div>
        </div>
      </div>
            </div>
            <div className="bg-gray-50 rounded-xl p-8">
              <h3 className="text-xl font-bold text-gray-800 mb-4">The Result?</h3>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-center">
                  <XCircleIcon className="h-5 w-5 mr-2" />
                  Unpredictable costs and budget overruns
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-5 w-5 mr-2" />
                  No optimization or cost savings
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-5 w-5 mr-2" />
                  Manual provider management
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-5 w-5 mr-2" />
                  Reactive cost management
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Our Solution Section */}
      <section className="py-16 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Our Intelligent Cost Solution
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We've built the world's most sophisticated cost optimization engine that predicts costs, 
              optimizes provider selection, and provides enterprise-grade budget management.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-8 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                <div className="bg-gradient-to-r from-gray-600 to-gray-800 rounded-lg p-3 w-fit mb-6">
                  <feature.icon className="h-8 w-8 text-white" />
            </div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 mb-6">{feature.description}</p>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <CheckCircleIcon className="h-4 w-4 text-gray-600 mr-2" />
                      Key Features
                    </h4>
                    <ul className="space-y-2">
                      {feature.details.map((detail, detailIndex) => (
                        <li key={detailIndex} className="text-sm text-gray-600 flex items-start">
                          <div className="w-1.5 h-1.5 bg-gray-600 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                          {detail}
                        </li>
                      ))}
                    </ul>
                    </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Competitive Advantage</h4>
                    <p className="text-sm text-gray-800">{feature.competitive}</p>
                    </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Technical Implementation</h4>
                    <p className="text-sm text-gray-700">{feature.technical}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Cost Savings Metrics */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Proven Cost Savings
            </h2>
            <p className="text-xl text-gray-600">
              Real metrics from enterprises using our cost optimization engine
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {costSavings.map((metric, index) => (
              <div key={index} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-8 text-center">
                <div className="text-4xl font-bold text-gray-700 mb-4">{metric.value}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{metric.metric}</h3>
                <p className="text-gray-600">{metric.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Competitive Comparison */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              How We Compare
            </h2>
            <p className="text-xl text-gray-600">
              See the difference between basic cost tracking and our intelligent optimization
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Feature
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Basic Cost Tracking
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Model Bridge
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Advantage
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {competitiveComparison.map((row, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {row.feature}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {row.basic}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {row.modelBridge}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {row.advantage}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
        </div>
      </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-gray-600 to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Optimize Your AI Costs?
          </h2>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Join the enterprises that are already saving 50-80% on their AI costs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-gray-900 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Start Free Trial
            </Link>
            <Link
              to="/product"
              className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Explore Other Modules
            </Link>
      </div>
      </div>
      </section>
    </div>
  );
};

export default CostOptimization;