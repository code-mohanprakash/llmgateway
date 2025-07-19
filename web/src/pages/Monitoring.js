import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  EyeIcon,
  ChartBarIcon,
  ServerIcon,
  GlobeAltIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  CheckCircleIcon,
  XCircleIcon,
  Cog6ToothIcon,
  AcademicCapIcon,
  BeakerIcon,
  BoltIcon,
  PlayIcon,
  PauseIcon,
  DocumentTextIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const Monitoring = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 6);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    {
      title: 'Real-Time Performance Monitoring',
      icon: EyeIcon,
      description: 'Comprehensive monitoring with sub-second latency tracking and intelligent alerts',
      details: [
        'Sub-second response time monitoring',
        'Real-time performance metrics',
        'Intelligent alerting system',
        'Performance trend analysis',
        'Automated performance optimization'
      ],
      competitive: 'Basic monitoring vs. our real-time performance monitoring with intelligent optimization.',
      technical: 'Uses real-time performance monitoring with sub-second latency tracking, implements ML for performance prediction, and provides automated performance optimization recommendations.'
    },
    {
      title: 'Advanced Analytics Dashboard',
      icon: ChartBarIcon,
      description: 'Comprehensive analytics with detailed insights and customizable reports',
      details: [
        'Customizable dashboard widgets',
        'Real-time data visualization',
        'Historical trend analysis',
        'Export capabilities',
        'Multi-dimensional analytics'
      ],
      competitive: 'Simple charts vs. our advanced analytics with customizable dashboards and real-time insights.',
      technical: 'Implements real-time data visualization with WebSocket connections, uses D3.js for advanced charts, and provides customizable dashboard with drag-and-drop widgets.'
    },
    {
      title: 'Intelligent Alerting System',
      icon: BoltIcon,
      description: 'Smart alerts that learn from patterns and reduce false positives',
      details: [
        'ML-powered anomaly detection',
        'Customizable alert thresholds',
        'Escalation workflows',
        'Alert correlation',
        'Smart notification routing'
      ],
      competitive: 'Basic alerts vs. our intelligent alerting with ML-powered anomaly detection.',
      technical: 'Uses ML-powered anomaly detection with pattern recognition, implements alert correlation to reduce noise, and provides smart notification routing based on severity.'
    },
    {
      title: 'Comprehensive Logging',
      icon: DocumentTextIcon,
      description: 'Structured logging with full request context and compliance-ready data',
      details: [
        'Structured JSON logging',
        'Full request context',
        'Compliance-ready retention',
        'Search and filtering',
        'Log correlation'
      ],
      competitive: 'Basic logging vs. our comprehensive logging with structured data and compliance features.',
      technical: 'Implements structured logging with full request context, uses Elasticsearch for search capabilities, and provides compliance-ready data retention policies.'
    },
    {
      title: 'Health Monitoring',
      icon: ServerIcon,
      description: 'End-to-end health monitoring with automatic failover detection',
      details: [
        'Service health checks',
        'Dependency monitoring',
        'Automatic failover',
        'Health score calculation',
        'Proactive issue detection'
      ],
      competitive: 'Basic health checks vs. our comprehensive health monitoring with automatic failover.',
      technical: 'Uses health checks with configurable thresholds, implements dependency monitoring with circuit breakers, and provides automatic failover with health score calculation.'
    },
    {
      title: 'Performance Optimization',
      icon: Cog6ToothIcon,
      description: 'Intelligent performance optimization with automated recommendations',
      details: [
        'Performance bottleneck detection',
        'Automated optimization suggestions',
        'Resource utilization monitoring',
        'Capacity planning',
        'Performance forecasting'
      ],
      competitive: 'Manual optimization vs. our intelligent performance optimization with automated recommendations.',
      technical: 'Uses ML for performance bottleneck detection, implements automated optimization suggestions, and provides capacity planning with performance forecasting.'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'DevOps Engineer at TechFlow',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
      quote: 'The real-time monitoring caught a performance issue before it affected users. The intelligent alerting is a game-changer.',
      rating: 5
    },
    {
      name: 'Mike Rodriguez',
      role: 'SRE Lead at DataCorp',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      quote: 'The advanced analytics dashboard gives us insights we never had before. Performance optimization is now data-driven.',
      rating: 5
    },
    {
      name: 'Emily Watson',
      role: 'CTO at Startup Inc',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      quote: 'Health monitoring with automatic failover saved us from major outages. The system is incredibly reliable.',
      rating: 5
    }
  ];

  const competitiveComparison = [
    {
      feature: 'Performance Monitoring',
      basic: 'Basic response time',
      modelBridge: 'Real-time performance with ML optimization',
      advantage: 'Proactive performance management'
    },
    {
      feature: 'Analytics',
      basic: 'Simple charts',
      modelBridge: 'Advanced analytics with customizable dashboards',
      advantage: 'Comprehensive insights'
    },
    {
      feature: 'Alerting',
      basic: 'Basic threshold alerts',
      modelBridge: 'Intelligent alerting with ML anomaly detection',
      advantage: 'Reduced false positives'
    },
    {
      feature: 'Logging',
      basic: 'Basic log files',
      modelBridge: 'Structured logging with compliance features',
      advantage: 'Enterprise-ready logging'
    },
    {
      feature: 'Health Monitoring',
      basic: 'Simple health checks',
      modelBridge: 'Comprehensive health monitoring with failover',
      advantage: 'Automatic issue resolution'
    },
    {
      feature: 'Optimization',
      basic: 'Manual optimization',
      modelBridge: 'Intelligent performance optimization',
      advantage: 'Automated improvements'
    }
  ];

  const technicalArchitecture = [
    {
      component: 'Performance Monitor',
      description: 'Real-time performance tracking',
      technology: 'Sub-second latency monitoring',
      performance: 'Real-time optimization'
    },
    {
      component: 'Analytics Engine',
      description: 'Advanced data analytics',
      technology: 'Real-time data visualization',
      performance: 'Instant insights'
    },
    {
      component: 'Alert Manager',
      description: 'Intelligent alerting system',
      technology: 'ML-powered anomaly detection',
      performance: 'Smart notifications'
    },
    {
      component: 'Log Aggregator',
      description: 'Comprehensive logging',
      technology: 'Structured JSON logging',
      performance: 'Fast search capabilities'
    },
    {
      component: 'Health Checker',
      description: 'Service health monitoring',
      technology: 'Dependency monitoring',
      performance: 'Automatic failover'
    },
    {
      component: 'Optimizer',
      description: 'Performance optimization',
      technology: 'ML-powered recommendations',
      performance: 'Automated improvements'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <Navigation />
      
      {/* Hero Section with Advanced Animations */}
      <section className="relative py-20 overflow-hidden bg-white">
        {/* Animated Background with Mouse Tracking */}
        <div 
          className="absolute inset-0 opacity-5 transition-transform duration-1000 ease-out"
          style={{
            background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0,0,0,0.1), transparent 40%)`,
            transform: `translate(${(mousePosition.x - window.innerWidth / 2) * 0.02}px, ${(mousePosition.y - window.innerHeight / 2) * 0.02}px)`
          }}
        />
        
        {/* Floating Elements with elegant animations */}
        <div className="absolute top-20 left-10 w-20 h-20 border border-gray-200 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-16 h-16 border border-gray-300 rounded-full opacity-20 animate-ping"></div>
        <div className="absolute bottom-20 left-1/4 w-12 h-12 border border-gray-400 rounded-full opacity-20 animate-bounce"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className={`inline-flex items-center px-4 py-2 bg-gray-100 text-gray-800 rounded-full text-sm font-medium mb-6 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <EyeIcon className="h-4 w-4 mr-2" />
              Intelligent Performance Monitoring
            </div>
            <h1 className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <span className="block text-gray-900">Monitor Your AI</span>
              <span className="block text-gray-900">
                Like Never Before
              </span>
            </h1>
            <p className={`text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              See everything, predict problems, optimize performance. Model Bridge provides 
              comprehensive monitoring with intelligent insights that help you stay ahead of issues.
            </p>
            
            {/* Interactive Demo Button with elegant styling */}
            <div className={`mb-12 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="group relative inline-flex items-center px-8 py-4 bg-gray-900 text-white rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 overflow-hidden"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-gray-800 to-gray-900 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                <span className="relative flex items-center">
                  {isPlaying ? (
                    <>
                      <PauseIcon className="h-5 w-5 mr-2" />
                      Pause Monitoring Demo
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Monitoring Demo
                    </>
                  )}
                </span>
              </button>
            </div>
            
            {/* Animated Stats Grid with gray/black theme */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">99.9%</div>
                <div className="text-sm text-gray-600">Uptime</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">Sub-Second</div>
                <div className="text-sm text-gray-600">Latency</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">ML</div>
                <div className="text-sm text-gray-600">Powered</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">Real-Time</div>
                <div className="text-sm text-gray-600">Monitoring</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Statement with Clean Design */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              The Monitoring Challenge
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              AI systems are complex and unpredictable. Most monitoring solutions offer basic metrics—we provide 
              intelligent monitoring that predicts problems before they happen and optimizes performance automatically.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <XCircleIcon className="h-8 w-8 text-gray-400 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Basic Monitoring</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Simple response time tracking
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Basic alerting
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Limited analytics
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Manual optimization
                </li>
              </ul>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="h-8 w-8 text-gray-900 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Model Bridge Monitoring</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Real-time performance monitoring
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Intelligent alerting with ML
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Advanced analytics dashboard
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Automated optimization
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Features Section with Advanced Animations */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              Comprehensive Monitoring Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience monitoring that thinks for you. Our intelligent features don't just watch—they predict, optimize, and improve.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`bg-white border border-gray-200 rounded-2xl p-8 shadow-sm hover:shadow-lg transform hover:scale-105 transition-all duration-300 cursor-pointer ${
                  activeFeature === index ? 'ring-2 ring-gray-300 ring-opacity-50' : ''
                }`}
                onClick={() => setActiveFeature(index)}
                style={{
                  transform: activeFeature === index ? 'scale(1.02)' : 'scale(1)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                <div className="flex items-center mb-4">
                  <div className="p-3 bg-gray-100 rounded-xl mr-4">
                    <feature.icon className="h-6 w-6 text-gray-700" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">{feature.title}</h3>
                </div>
                <p className="text-gray-600 mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.details.slice(0, 3).map((detail, idx) => (
                    <li key={idx} className="flex items-center text-sm text-gray-600">
                      <CheckCircleIcon className="h-4 w-4 text-gray-500 mr-2" />
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Human Testimonials with Clean Design */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              What Engineers Say
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real stories from engineers who've transformed their monitoring with Model Bridge.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
                <div className="flex items-center mb-4">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full mr-4"
                  />
                  <div>
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-700 mb-4 italic">"{testimonial.quote}"</p>
                <div className="flex">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Competitive Comparison with Clean Design */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              Why Model Bridge Monitoring Wins
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how our intelligent monitoring outperforms traditional solutions.
            </p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden">
            <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
              <div className="font-semibold text-gray-900">Feature</div>
              <div className="font-semibold text-gray-900">Basic Monitoring</div>
              <div className="font-semibold text-gray-900">Model Bridge</div>
              <div className="font-semibold text-gray-900">Advantage</div>
            </div>
            
            {competitiveComparison.map((item, index) => (
              <div key={index} className="grid grid-cols-4 gap-4 p-6 border-b last:border-b-0 hover:bg-gray-50 transition-colors">
                <div className="font-medium text-gray-900">{item.feature}</div>
                <div className="text-gray-600">{item.basic}</div>
                <div className="text-gray-900 font-medium">{item.modelBridge}</div>
                <div className="text-gray-700 font-medium">{item.advantage}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Architecture with Clean Design */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              Technical Architecture
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built on cutting-edge monitoring technology for maximum visibility and control.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {technicalArchitecture.map((component, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">{component.component}</h3>
                <p className="text-gray-600 mb-3">{component.description}</p>
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Technology:</span> {component.technology}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Performance:</span> {component.performance}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section with Clean Design */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Monitor Your AI?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Join thousands of teams who've transformed their monitoring with Model Bridge. 
            Start monitoring your AI with intelligence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="inline-flex items-center px-8 py-4 bg-white text-gray-900 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              Start Free Trial
            </Link>
            <Link
              to="/product/security"
              className="inline-flex items-center px-8 py-4 border-2 border-white text-white rounded-full font-semibold text-lg hover:bg-white hover:text-gray-900 transform hover:scale-105 transition-all duration-300"
            >
              Explore Other Features
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Monitoring; 