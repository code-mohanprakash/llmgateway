import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  CpuChipIcon,
  CloudIcon,
  BoltIcon,
  ChartBarIcon,
  CogIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  CurrencyDollarIcon,
  ClockIcon,
  UserGroupIcon,
  BeakerIcon,
  PuzzlePieceIcon,
  RocketLaunchIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  ServerIcon,
  WrenchScrewdriverIcon,
  CommandLineIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  BuildingOfficeIcon,
  LockClosedIcon,
  EyeIcon,
  ChartPieIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const Product = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalModels: 120,
    providers: 12,
    uptime: '99.9%',
    costSavings: '50-80%',
    responseTime: '<200ms',
    accuracy: '99.5%'
  });

  const tabs = [
    { id: 'overview', name: 'Overview', icon: SparklesIcon },
    { id: 'intelligent-routing', name: 'Intelligent Routing', icon: BoltIcon },
    { id: 'cost-optimization', name: 'Cost Optimization', icon: CurrencyDollarIcon },
    { id: 'enterprise-features', name: 'Enterprise Features', icon: BuildingOfficeIcon },
    { id: 'orchestration', name: 'Workflow Orchestration', icon: PuzzlePieceIcon },
    { id: 'monitoring', name: 'Monitoring & Analytics', icon: ChartBarIcon },
    { id: 'security', name: 'Security & Compliance', icon: ShieldCheckIcon },
    { id: 'developer-experience', name: 'Developer Experience', icon: CommandLineIcon }
  ];

  const features = {
    'intelligent-routing': [
      {
        title: 'Predictive Routing Engine',
        description: 'ML-powered routing that predicts the optimal provider for each request based on historical performance, current load, and request patterns.',
        icon: BeakerIcon,
        details: [
          'Real-time pattern analysis with clustering algorithms',
          'Confidence scoring for routing decisions',
          'Geographic optimization based on latency',
          'Dynamic weight adjustment using exponential moving averages',
          'Request complexity analysis for intelligent model selection'
        ],
        competitive: 'Unlike basic load balancers, our ML engine learns from every request to continuously improve routing accuracy.'
      },
      {
        title: 'Advanced Load Balancing',
        description: 'Enterprise-grade load balancing with circuit breakers, health monitoring, and intelligent failover mechanisms.',
        icon: ServerIcon,
        details: [
          'Circuit breaker pattern for fault tolerance',
          'Connection pooling for optimal performance',
          'Real-time health monitoring with 30-second intervals',
          'Weighted round-robin with performance adjustment',
          'Automatic failover with zero downtime'
        ],
        competitive: 'Traditional load balancers only distribute traffic. Ours intelligently routes based on performance, cost, and reliability.'
      },
      {
        title: 'Geographic Routing',
        description: 'Route requests to the closest provider based on geographic location and latency measurements.',
        icon: GlobeAltIcon,
        details: [
          'IP-based geographic detection',
          'Latency measurement and monitoring',
          'Regional provider preferences',
          'Fallback mechanisms for reliability',
          'Real-time latency statistics'
        ],
        competitive: 'Most competitors route globally. We route locally for optimal performance and cost.'
      }
    ],
    'cost-optimization': [
      {
        title: 'Token-Level Cost Prediction',
        description: 'Predict costs before making requests and optimize for the most cost-effective provider.',
        icon: CurrencyDollarIcon,
        details: [
          'Pre-request cost estimation',
          'Token counting and pricing calculation',
          'Cost prediction accuracy tracking',
          'Real-time pricing updates',
          'Budget-aware routing decisions'
        ],
        competitive: 'Other platforms charge you after the fact. We predict and optimize costs before each request.'
      },
      {
        title: 'Budget Management System',
        description: 'Comprehensive budget tracking with alerts, projections, and automatic throttling.',
        icon: ChartPieIcon,
        details: [
          'Multi-period budget tracking (daily, weekly, monthly)',
          'Alert thresholds with configurable percentages',
          'Burn rate calculation and projections',
          'Automatic throttling when limits approached',
          'Department and model allocation tracking'
        ],
        competitive: 'Basic cost tracking vs. our enterprise-grade budget management with predictive analytics.'
      },
      {
        title: 'Provider Cost Arbitrage',
        description: 'Automatically switch between providers to find the best price for each request type.',
        icon: ArrowTrendingUpIcon,
        details: [
          'Real-time price comparison across providers',
          'Task-specific cost optimization',
          'Quality vs. cost trade-off analysis',
          'Historical cost trend analysis',
          'Automated provider switching'
        ],
        competitive: 'Manual provider selection vs. our intelligent arbitrage that finds the best deal automatically.'
      }
    ],
    'enterprise-features': [
      {
        title: 'Role-Based Access Control (RBAC)',
        description: 'Granular permission system with hierarchical roles and organization-level isolation.',
        icon: UserGroupIcon,
        details: [
          'Hierarchical role system (Owner, Admin, Member, Viewer)',
          'Granular permissions for every feature',
          'Organization-level data isolation',
          'Custom role creation and delegation',
          'Audit logging for all access events'
        ],
        competitive: 'Basic user management vs. our enterprise-grade RBAC with full audit trails.'
      },
      {
        title: 'Advanced Rate Limiting',
        description: 'Sophisticated rate limiting with burst handling and priority-based queuing.',
        icon: Cog6ToothIcon,
        details: [
          'Organization-level rate limits',
          'Model-specific rate limits',
          'Burst handling for traffic spikes',
          'Priority-based request queuing',
          'VIP customer handling'
        ],
        competitive: 'Simple rate limits vs. our intelligent rate management with priority handling.'
      },
      {
        title: 'SSO & Enterprise Authentication',
        description: 'Enterprise-grade authentication with SAML, OAuth, and Active Directory integration.',
        icon: LockClosedIcon,
        details: [
          'SAML 2.0 integration',
          'OAuth 2.0/OIDC support',
          'Active Directory integration',
          'Multi-factor authentication (MFA)',
          'Enterprise user provisioning'
        ],
        competitive: 'Basic authentication vs. our enterprise SSO with full compliance support.'
      }
    ],
    'orchestration': [
      {
        title: 'Multi-Step Workflow Builder',
        description: 'Visual workflow designer for complex AI applications with conditional logic and parallel execution.',
        icon: PuzzlePieceIcon,
        details: [
          'Visual workflow designer',
          'Conditional logic and branching',
          'Parallel execution capabilities',
          'Error handling and retry mechanisms',
          'Performance monitoring and optimization'
        ],
        competitive: 'Single API calls vs. our sophisticated workflow orchestration for complex AI applications.'
      },
      {
        title: 'A/B Testing Framework',
        description: 'Statistical A/B testing for model comparison with confidence intervals and performance metrics.',
        icon: BeakerIcon,
        details: [
          'Statistical significance testing',
          'Confidence interval calculation',
          'Performance metrics comparison',
          'Cost analysis for each variant',
          'Automated winner selection'
        ],
        competitive: 'Manual model testing vs. our statistical A/B testing with automated insights.'
      },
      {
        title: 'Chain-of-Thought Optimization',
        description: 'Advanced reasoning optimization for complex problem-solving workflows.',
        icon: AcademicCapIcon,
        details: [
          'Multi-step reasoning chains',
          'Intermediate result validation',
          'Error recovery mechanisms',
          'Performance optimization',
          'Quality scoring system'
        ],
        competitive: 'Simple prompts vs. our sophisticated reasoning chains for complex problem solving.'
      }
    ],
    'monitoring': [
      {
        title: 'Real-Time Health Monitoring',
        description: 'Comprehensive system monitoring with alerts, SLA tracking, and performance optimization.',
        icon: EyeIcon,
        details: [
          'System health dashboard',
          'Performance metrics tracking',
          'Automated alerting system',
          'SLA monitoring and reporting',
          'Incident management'
        ],
        competitive: 'Basic uptime monitoring vs. our comprehensive health monitoring with predictive alerts.'
      },
      {
        title: 'Advanced Analytics',
        description: 'Enterprise-grade analytics with cost analysis, usage patterns, and business intelligence.',
        icon: ChartBarIcon,
        details: [
          'Cost center allocation',
          'Usage pattern analysis',
          'Performance optimization insights',
          'ROI calculation tools',
          'Business intelligence dashboards'
        ],
        competitive: 'Simple usage stats vs. our enterprise analytics with business intelligence.'
      },
      {
        title: 'ML-Powered Insights',
        description: 'Machine learning-driven insights for cost optimization and performance recommendations.',
        icon: SparklesIcon,
        details: [
          'Usage pattern analysis',
          'Cost optimization recommendations',
          'Performance anomaly detection',
          'Predictive analytics',
          'Automated optimization suggestions'
        ],
        competitive: 'Static reports vs. our ML-powered insights that continuously improve your operations.'
      }
    ],
    'security': [
      {
        title: 'Comprehensive Audit Logging',
        description: 'Complete audit trail with full request context for compliance and security.',
        icon: DocumentTextIcon,
        details: [
          'Full request context logging',
          'User action tracking',
          'Data access audit trails',
          'Compliance-ready reporting',
          'Security event monitoring'
        ],
        competitive: 'Basic logging vs. our compliance-ready audit system with full context.'
      },
      {
        title: 'Data Governance',
        description: 'Enterprise data governance with privacy controls and compliance policies.',
        icon: ShieldCheckIcon,
        details: [
          'Data privacy controls',
          'Compliance policy enforcement',
          'Data retention management',
          'Privacy impact assessments',
          'Regulatory compliance support'
        ],
        competitive: 'Basic data handling vs. our enterprise-grade data governance.'
      },
      {
        title: 'Security Middleware',
        description: 'Advanced security middleware with threat detection and prevention.',
        icon: LockClosedIcon,
        details: [
          'Threat detection and prevention',
          'Rate limiting and DDoS protection',
          'Input validation and sanitization',
          'Security headers management',
          'Vulnerability scanning'
        ],
        competitive: 'Basic security vs. our comprehensive security middleware with threat prevention.'
      }
    ],
    'developer-experience': [
      {
        title: 'Interactive API Playground',
        description: 'Real-time API testing and exploration with instant feedback and documentation.',
        icon: CommandLineIcon,
        details: [
          'Real-time API testing',
          'Instant feedback and validation',
          'Interactive documentation',
          'Code snippet generation',
          'Request/response inspection'
        ],
        competitive: 'Static documentation vs. our interactive playground for instant API exploration.'
      },
      {
        title: 'Enterprise SDKs',
        description: 'Comprehensive SDKs for Python and JavaScript with enterprise features.',
        icon: Cog6ToothIcon,
        details: [
          'Python SDK with enterprise features',
          'JavaScript SDK with enterprise features',
          'TypeScript support',
          'Enterprise integration examples',
          'Comprehensive documentation'
        ],
        competitive: 'Basic SDKs vs. our enterprise-grade SDKs with full feature support.'
      },
      {
        title: 'Developer Tools',
        description: 'Advanced developer tools for debugging, testing, and optimization.',
        icon: WrenchScrewdriverIcon,
        details: [
          'Request debugging tools',
          'Performance profiling',
          'Cost analysis tools',
          'Integration testing framework',
          'Deployment automation'
        ],
        competitive: 'Basic tools vs. our comprehensive developer toolkit for enterprise development.'
      }
    ]
  };

  const competitiveAdvantages = [
    {
      title: 'The Perplexity Moment for AI APIs',
      description: 'Just like Perplexity revolutionized search by intelligently routing queries to the best sources, we\'re doing the same for AI. No more guessing which provider to use.',
      icon: SparklesIcon,
      color: 'from-gray-600 to-gray-800'
    },
    {
      title: 'Enterprise-Grade Intelligence',
      description: 'While competitors offer basic API aggregation, we provide ML-powered routing, predictive analytics, and enterprise-grade features that scale with your business.',
      icon: CpuChipIcon,
      color: 'from-gray-700 to-gray-900'
    },
    {
      title: 'Cost Intelligence, Not Just Tracking',
      description: 'Others track costs after the fact. We predict and optimize costs before each request, saving 50-80% while maintaining quality.',
      icon: CurrencyDollarIcon,
      color: 'from-gray-800 to-gray-900'
    },
    {
      title: 'Workflow Orchestration',
      description: 'While competitors focus on single API calls, we provide sophisticated workflow orchestration for complex AI applications.',
      icon: PuzzlePieceIcon,
      color: 'from-gray-600 to-gray-800'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <Navigation />
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="block text-gray-900">The Complete</span>
              <span className="block bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">
                AI Platform
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              Model Bridge isn't just another API gateway. We're the intelligent layer that transforms 
              how enterprises build, deploy, and scale AI applications. Think of us as the "Perplexity for AI APIs."
            </p>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-12">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">{stats.totalModels}+</div>
                <div className="text-sm text-gray-600">AI Models</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">{stats.providers}+</div>
                <div className="text-sm text-gray-600">Providers</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">{stats.uptime}</div>
                <div className="text-sm text-gray-600">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">{stats.costSavings}</div>
                <div className="text-sm text-gray-600">Cost Savings</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">{stats.responseTime}</div>
                <div className="text-sm text-gray-600">Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">{stats.accuracy}</div>
                <div className="text-sm text-gray-600">Routing Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Navigation Tabs */}
      <section className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-gray-500 text-gray-700'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Content Sections */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-16">
              {/* Competitive Advantages */}
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                  Why We're Different
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {competitiveAdvantages.map((advantage, index) => (
                    <div key={index} className="bg-white rounded-xl p-8 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                      <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${advantage.color} mb-6`}>
                        <advantage.icon className="h-8 w-8 text-white" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-4">{advantage.title}</h3>
                      <p className="text-gray-600 leading-relaxed">{advantage.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Technical Architecture */}
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                  Technical Architecture
                </h2>
                <div className="bg-gray-50 rounded-xl p-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="text-center">
                      <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                        <CpuChipIcon className="h-8 w-8 text-gray-700" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Intelligent Core</h3>
                      <p className="text-gray-600 text-sm">
                        ML-powered routing engine with predictive analytics and real-time optimization
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                        <CloudIcon className="h-8 w-8 text-gray-700" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Multi-Provider</h3>
                      <p className="text-gray-600 text-sm">
                        12+ providers with automatic failover, health monitoring, and performance tracking
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                        <ShieldCheckIcon className="h-8 w-8 text-gray-700" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Enterprise Ready</h3>
                      <p className="text-gray-600 text-sm">
                        RBAC, SSO, audit logging, compliance, and enterprise-grade security
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Feature Comparison */}
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                  How We Compare
                </h2>
                <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Feature
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Basic API Gateways
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Model Bridge
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            Routing Intelligence
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            Basic load balancing
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              ML-powered predictive routing
                            </span>
                          </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            Cost Optimization
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            Post-request cost tracking
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              Pre-request cost prediction & arbitrage
                            </span>
                          </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            Enterprise Features
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            Basic authentication
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              Full RBAC, SSO, audit logging
                            </span>
                          </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            Workflow Orchestration
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            Single API calls
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              Multi-step workflows with conditional logic
                            </span>
                          </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            Monitoring & Analytics
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            Basic usage stats
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              ML-powered insights & business intelligence
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Feature Tabs */}
          {activeTab !== 'overview' && features[activeTab] && (
            <div className="space-y-12">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  {tabs.find(tab => tab.id === activeTab)?.name}
                </h2>
                <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                  {activeTab === 'intelligent-routing' && 'ML-powered routing that thinks for you, optimizing for performance, cost, and reliability.'}
                  {activeTab === 'cost-optimization' && 'Intelligent cost management that predicts and optimizes expenses before they happen.'}
                  {activeTab === 'enterprise-features' && 'Enterprise-grade security, compliance, and governance for large organizations.'}
                  {activeTab === 'orchestration' && 'Sophisticated workflow orchestration for complex AI applications.'}
                  {activeTab === 'monitoring' && 'Comprehensive monitoring and analytics with ML-powered insights.'}
                  {activeTab === 'security' && 'Advanced security and compliance features for enterprise deployments.'}
                  {activeTab === 'developer-experience' && 'Developer-first tools and SDKs for rapid AI application development.'}
                </p>
              </div>

              <div className="space-y-8">
                {features[activeTab].map((feature, index) => (
                  <div key={index} className="bg-white rounded-xl p-8 shadow-lg border border-gray-100">
                    <div className="flex items-start space-x-6">
                      <div className="bg-gray-100 rounded-lg p-3">
                        <feature.icon className="h-8 w-8 text-gray-700" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                        <p className="text-gray-600 mb-6 leading-relaxed">{feature.description}</p>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                              <CheckCircleIcon className="h-5 w-5 text-gray-600 mr-2" />
                              Key Features
                            </h4>
                            <ul className="space-y-3">
                              {feature.details.map((detail, detailIndex) => (
                                <li key={detailIndex} className="flex items-start">
                                  <div className="flex-shrink-0 w-2 h-2 bg-gray-600 rounded-full mt-2 mr-3"></div>
                                  <span className="text-gray-700">{detail}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                          
                          <div className="bg-gray-50 rounded-lg p-6">
                            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                              <ArrowTrendingUpIcon className="h-5 w-5 text-gray-600 mr-2" />
                              Competitive Advantage
                            </h4>
                            <p className="text-gray-700 leading-relaxed">{feature.competitive}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-gray-700 to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your AI Strategy?
          </h2>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Join the enterprises that are already building the future of AI applications with Model Bridge.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-gray-900 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Start Free Trial
            </Link>
            <Link
              to="/contact"
              className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Schedule Demo
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Product; 