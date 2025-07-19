import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  Cog6ToothIcon,
  ArrowPathIcon,
  BoltIcon,
  ServerIcon,
  GlobeAltIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  BeakerIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';

const Orchestration = () => {
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
      title: 'Intelligent Load Balancing',
      icon: Cog6ToothIcon,
      description: 'Smart traffic distribution across multiple AI providers for optimal performance',
      details: [
        'Real-time performance monitoring',
        'Automatic failover and recovery',
        'Cost-optimized routing',
        'Geographic load distribution',
        'Custom routing rules'
      ],
      competitive: 'Basic load balancing vs. our intelligent routing with cost optimization and automatic failover.',
      technical: 'Uses real-time performance metrics with ML-powered routing decisions, implements automatic failover with health checks, and provides cost optimization through intelligent provider selection.'
    },
    {
      title: 'Advanced Rate Limiting',
      icon: ArrowPathIcon,
      description: 'Sophisticated rate limiting with burst handling and priority queuing',
      details: [
        'Organization-level rate limits',
        'Model-specific throttling',
        'Burst handling for emergencies',
        'Priority-based queuing',
        'VIP customer handling'
      ],
      competitive: 'Simple rate limiting vs. our advanced rate limiting with burst handling and priority queuing.',
      technical: 'Implements token bucket algorithms with configurable burst limits, uses priority queues for VIP customers, and provides real-time rate limit monitoring and adjustment.'
    },
    {
      title: 'Cost Optimization',
      icon: CurrencyDollarIcon,
      description: 'Intelligent cost management with automatic provider selection',
      details: [
        'Real-time cost tracking',
        'Automatic provider switching',
        'Budget management and alerts',
        'Cost prediction and forecasting',
        'Usage analytics and reporting'
      ],
      competitive: 'Manual cost management vs. our intelligent cost optimization with automatic provider selection.',
      technical: 'Uses real-time cost tracking with ML-powered provider selection, implements budget management with automated alerts, and provides cost prediction using historical data analysis.'
    },
    {
      title: 'Performance Monitoring',
      icon: BoltIcon,
      description: 'Comprehensive performance monitoring with real-time insights',
      details: [
        'Real-time performance metrics',
        'Response time monitoring',
        'Throughput optimization',
        'Performance alerts',
        'Historical performance analysis'
      ],
      competitive: 'Basic monitoring vs. our comprehensive performance monitoring with real-time optimization.',
      technical: 'Implements real-time performance monitoring with sub-second latency tracking, uses ML for performance prediction, and provides automated performance optimization recommendations.'
    },
    {
      title: 'Global Distribution',
      icon: GlobeAltIcon,
      description: 'Worldwide AI provider distribution for optimal performance',
      details: [
        'Geographic load balancing',
        'Regional provider selection',
        'Latency optimization',
        'Global failover',
        'Edge computing support'
      ],
      competitive: 'Single-region deployment vs. our global distribution with geographic load balancing.',
      technical: 'Uses geographic load balancing with latency-based routing, implements regional provider selection, and provides global failover with edge computing support.'
    },
    {
      title: 'Automated Scaling',
      icon: ServerIcon,
      description: 'Intelligent scaling based on demand and performance',
      details: [
        'Automatic capacity scaling',
        'Demand-based provisioning',
        'Performance-based scaling',
        'Cost-aware scaling',
        'Predictive scaling'
      ],
      competitive: 'Manual scaling vs. our intelligent automated scaling with demand prediction.',
      technical: 'Uses ML-powered demand prediction for proactive scaling, implements performance-based scaling decisions, and provides cost-aware scaling with budget constraints.'
    }
  ];

  const testimonials = [
    {
      name: 'Alex Rivera',
      role: 'Senior Developer at TechStartup',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      quote: 'The intelligent load balancing saved us from major outages. It automatically routes traffic to the best performing providers.',
      rating: 5
    },
    {
      name: 'Maria Chen',
      role: 'Lead Engineer at DataCorp',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
      quote: 'Cost optimization reduced our AI spend by 40% while improving performance. The automatic provider switching is brilliant.',
      rating: 5
    },
    {
      name: 'Tom Johnson',
      role: 'DevOps Engineer at Enterprise Inc',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      quote: 'Global distribution means our users worldwide get consistent performance. The geographic load balancing is seamless.',
      rating: 5
    }
  ];

  const competitiveComparison = [
    {
      feature: 'Load Balancing',
      basic: 'Basic round-robin',
      modelBridge: 'Intelligent load balancing with ML',
      advantage: 'Optimal performance and cost'
    },
    {
      feature: 'Rate Limiting',
      basic: 'Simple rate limits',
      modelBridge: 'Advanced rate limiting with burst handling',
      advantage: 'Better user experience'
    },
    {
      feature: 'Cost Management',
      basic: 'Manual cost tracking',
      modelBridge: 'Intelligent cost optimization',
      advantage: 'Automatic cost savings'
    },
    {
      feature: 'Performance',
      basic: 'Basic monitoring',
      modelBridge: 'Comprehensive performance monitoring',
      advantage: 'Real-time optimization'
    },
    {
      feature: 'Global Reach',
      basic: 'Single region',
      modelBridge: 'Global distribution',
      advantage: 'Worldwide performance'
    },
    {
      feature: 'Scaling',
      basic: 'Manual scaling',
      modelBridge: 'Automated intelligent scaling',
      advantage: 'Predictive scaling'
    }
  ];

  const technicalArchitecture = [
    {
      component: 'Load Balancer',
      description: 'Intelligent traffic distribution',
      technology: 'ML-powered routing decisions',
      performance: 'Sub-second routing'
    },
    {
      component: 'Rate Limiter',
      description: 'Advanced rate limiting',
      technology: 'Token bucket algorithms',
      performance: 'Real-time rate control'
    },
    {
      component: 'Cost Optimizer',
      description: 'Intelligent cost management',
      technology: 'ML-powered provider selection',
      performance: 'Automatic cost savings'
    },
    {
      component: 'Performance Monitor',
      description: 'Real-time performance tracking',
      technology: 'Comprehensive metrics',
      performance: 'Sub-second monitoring'
    },
    {
      component: 'Global Router',
      description: 'Worldwide distribution',
      technology: 'Geographic load balancing',
      performance: 'Global optimization'
    },
    {
      component: 'Auto Scaler',
      description: 'Intelligent scaling',
      technology: 'ML-powered demand prediction',
      performance: 'Predictive scaling'
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
        
        {/* Floating Elements with React-inspired animations */}
        <div className="absolute top-20 left-10 w-20 h-20 border border-gray-200 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-16 h-16 border border-gray-300 rounded-full opacity-20 animate-ping"></div>
        <div className="absolute bottom-20 left-1/4 w-12 h-12 border border-gray-400 rounded-full opacity-20 animate-bounce"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className={`inline-flex items-center px-4 py-2 bg-gray-100 text-gray-800 rounded-full text-sm font-medium mb-6 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <Cog6ToothIcon className="h-4 w-4 mr-2" />
              Intelligent AI Orchestration
            </div>
            <h1 className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <span className="block text-gray-900">Orchestrate Your AI</span>
              <span className="block text-gray-900">
                Like a Symphony
              </span>
            </h1>
            <p className={`text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              Transform chaos into harmony. Model Bridge orchestrates your AI operations with intelligent 
              load balancing, cost optimization, and global distribution for seamless performance.
            </p>
            
            {/* Interactive Demo Button with React-inspired styling */}
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
                      Pause Orchestration Demo
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Orchestration Demo
                    </>
                  )}
                </span>
              </button>
            </div>
            
            {/* Animated Stats Grid with minimal colors */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">99.9%</div>
                <div className="text-sm text-gray-600">Uptime</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">40%</div>
                <div className="text-sm text-gray-600">Cost Savings</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">Global</div>
                <div className="text-sm text-gray-600">Distribution</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">ML</div>
                <div className="text-sm text-gray-600">Powered</div>
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
              The Orchestration Challenge
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Managing multiple AI providers, optimizing costs, and ensuring performance across 
              global deployments is complex. Most solutions offer basic load balancing—we provide 
              intelligent orchestration that thinks for you.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <XCircleIcon className="h-8 w-8 text-gray-400 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Basic Load Balancing</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Simple round-robin routing
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  No cost optimization
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Manual failover
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Single region deployment
                </li>
              </ul>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="h-8 w-8 text-gray-900 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Model Bridge Orchestration</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Intelligent ML-powered routing
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Automatic cost optimization
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Intelligent failover
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Global distribution
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
              Intelligent Orchestration Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience orchestration that thinks for you. Our intelligent features don't just route—they optimize, predict, and adapt.
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
              Real stories from engineers who've transformed their AI operations with Model Bridge.
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
              Why Model Bridge Orchestration Wins
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how our intelligent orchestration outperforms traditional solutions.
            </p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden">
            <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
              <div className="font-semibold text-gray-900">Feature</div>
              <div className="font-semibold text-gray-900">Basic Load Balancing</div>
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
              Built on cutting-edge orchestration technology for maximum performance and reliability.
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
            Ready to Orchestrate Your AI?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Join thousands of teams who've transformed their AI operations with Model Bridge. 
            Start orchestrating your AI like a symphony.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="inline-flex items-center px-8 py-4 bg-white text-gray-900 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              Start Free Trial
            </Link>
            <Link
              to="/product/monitoring"
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

export default Orchestration;