import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  CpuChipIcon,
  ArrowRightIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  MapPinIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';

const IntelligentRouting = () => {
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
      title: 'ML-Powered Routing',
      icon: CpuChipIcon,
      description: 'Intelligent routing that learns and adapts to optimize performance and cost',
      details: [
        'Real-time performance monitoring across all providers',
        'Dynamic routing based on request complexity',
        'Cost optimization with intelligent provider selection',
        'Geographic routing for latency optimization',
        'Automatic failover and load balancing'
      ],
      competitive: 'Basic load balancing vs. our ML-powered routing that optimizes for performance and cost.',
      technical: 'Uses machine learning models to analyze request patterns, implements real-time performance monitoring, and provides dynamic routing based on multiple factors including cost, latency, and provider performance.'
    },
    {
      title: 'Intelligent Request Analysis',
      icon: ChartBarIcon,
      description: 'Advanced request analysis to determine optimal routing strategy',
      details: [
        'Request complexity analysis',
        'Content type classification',
        'Performance prediction',
        'Cost estimation',
        'Provider capability matching'
      ],
      competitive: 'Simple routing vs. our intelligent request analysis that considers multiple factors.',
      technical: 'Implements NLP-based request analysis, uses performance prediction models, and provides intelligent provider matching based on request characteristics.'
    },
    {
      title: 'Dynamic Performance Optimization',
      icon: ArrowTrendingUpIcon,
      description: 'Real-time performance optimization with automatic adjustments',
      details: [
        'Real-time performance monitoring',
        'Automatic provider switching',
        'Performance trend analysis',
        'Predictive optimization',
        'Continuous improvement'
      ],
      competitive: 'Static routing vs. our dynamic performance optimization with real-time adjustments.',
      technical: 'Uses real-time performance monitoring with sub-second latency tracking, implements automatic provider switching, and provides predictive optimization using ML models.'
    },
    {
      title: 'Geographic Optimization',
      icon: MapPinIcon,
      description: 'Intelligent geographic routing for optimal latency and performance',
      details: [
        'Geographic proximity analysis',
        'Latency-based routing',
        'Regional provider selection',
        'Global load distribution',
        'Edge computing integration'
      ],
      competitive: 'Global routing vs. our geographic optimization for reduced latency.',
      technical: 'Implements geographic proximity analysis, uses latency-based routing algorithms, and provides regional provider selection for optimal performance.'
    },
    {
      title: 'Cost-Aware Routing',
      icon: SparklesIcon,
      description: 'Intelligent cost optimization without sacrificing performance',
      details: [
        'Real-time cost monitoring',
        'Cost-per-token optimization',
        'Provider cost comparison',
        'Budget-aware routing',
        'ROI optimization'
      ],
      competitive: 'Fixed pricing vs. our cost-aware routing that optimizes for both performance and cost.',
      technical: 'Uses real-time cost monitoring with per-request cost analysis, implements cost-per-token optimization, and provides budget-aware routing with ROI optimization.'
    },
    {
      title: 'Adaptive Learning',
      icon: ArrowRightIcon,
      description: 'Continuous learning and adaptation to changing conditions',
      details: [
        'Performance pattern learning',
        'Provider behavior analysis',
        'Request pattern recognition',
        'Automatic rule generation',
        'Continuous optimization'
      ],
      competitive: 'Static rules vs. our adaptive learning that continuously improves routing decisions.',
      technical: 'Uses machine learning for pattern recognition, implements automatic rule generation, and provides continuous optimization based on performance data.'
    }
  ];

  const competitiveComparison = [
    {
      feature: 'Routing Intelligence',
      basic: 'Simple load balancing',
      modelBridge: 'ML-powered intelligent routing',
      advantage: 'Optimized performance and cost'
    },
    {
      feature: 'Request Analysis',
      basic: 'No request analysis',
      modelBridge: 'Intelligent request analysis',
      advantage: 'Better provider matching'
    },
    {
      feature: 'Performance Optimization',
      basic: 'Static routing rules',
      modelBridge: 'Dynamic performance optimization',
      advantage: 'Real-time optimization'
    },
    {
      feature: 'Geographic Routing',
      basic: 'Global routing only',
      modelBridge: 'Intelligent geographic optimization',
      advantage: 'Reduced latency'
    },
    {
      feature: 'Cost Optimization',
      basic: 'Fixed pricing',
      modelBridge: 'Cost-aware routing',
      advantage: 'Lower costs'
    },
    {
      feature: 'Learning Capability',
      basic: 'Static rules',
      modelBridge: 'Adaptive learning',
      advantage: 'Continuous improvement'
    }
  ];

  const technicalArchitecture = [
    {
      component: 'Request Analyzer',
      description: 'Intelligent request analysis',
      technology: 'NLP and ML models',
      performance: 'Sub-second analysis'
    },
    {
      component: 'Performance Monitor',
      description: 'Real-time performance tracking',
      technology: 'Distributed monitoring',
      performance: 'Real-time optimization'
    },
    {
      component: 'Routing Engine',
      description: 'Intelligent routing decisions',
      technology: 'ML-powered algorithms',
      performance: 'Dynamic routing'
    },
    {
      component: 'Cost Optimizer',
      description: 'Cost-aware optimization',
      technology: 'Real-time cost analysis',
      performance: 'Budget optimization'
    },
    {
      component: 'Geographic Router',
      description: 'Geographic optimization',
      technology: 'Latency-based algorithms',
      performance: 'Reduced latency'
    },
    {
      component: 'Learning Engine',
      description: 'Continuous improvement',
      technology: 'Adaptive ML models',
      performance: 'Self-optimizing'
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
              <CpuChipIcon className="h-4 w-4 mr-2" />
              ML-Powered Intelligent Routing
            </div>
            <h1 className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <span className="block text-gray-900">The Perplexity</span>
              <span className="block text-gray-900">
                Killer
              </span>
            </h1>
            <p className={`text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              Experience routing that thinks for you. Model Bridge's ML-powered intelligent routing 
              optimizes performance, reduces costs, and adapts to changing conditions automatically.
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
                      Pause Routing Demo
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Routing Demo
                    </>
                  )}
                </span>
              </button>
            </div>
            
            {/* Animated Stats Grid with gray/black theme */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">20-40%</div>
                <div className="text-sm text-gray-600">Better Routing Accuracy</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">99.9%</div>
                <div className="text-sm text-gray-600">Uptime</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">40-60%</div>
                <div className="text-sm text-gray-600">Latency Reduction</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">&lt;20ms</div>
                <div className="text-sm text-gray-600">Prediction Time</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Statement with Clean Design */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              The Routing Problem
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Most AI platforms use simple load balancing that treats all requests the same. 
              This leads to poor performance, high costs, and missed opportunities.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white border border-gray-200 rounded-2xl p-6 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-start mb-4">
                <XCircleIcon className="h-6 w-6 text-gray-400 mr-3 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900">Dumb Load Balancing</h3>
                  <p className="text-gray-600">Simple round-robin distribution that doesn't consider performance, cost, or request complexity.</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-6 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-start mb-4">
                <XCircleIcon className="h-6 w-6 text-gray-400 mr-3 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900">No Intelligence</h3>
                  <p className="text-gray-600">Treats all requests the same, regardless of whether it's coding, creative writing, or analysis.</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-6 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-start mb-4">
                <XCircleIcon className="h-6 w-6 text-gray-400 mr-3 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900">Global Routing Only</h3>
                  <p className="text-gray-600">Routes all requests globally, ignoring geographic proximity and latency optimization.</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-6 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-start mb-4">
                <XCircleIcon className="h-6 w-6 text-gray-400 mr-3 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900">Static Configuration</h3>
                  <p className="text-gray-600">Fixed weights and rules that don't adapt to changing provider performance.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-12 bg-white border border-gray-200 rounded-2xl p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">The Result?</h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-center">
                <XCircleIcon className="h-4 w-4 text-gray-400 mr-2" />
                Poor performance with high latency
              </li>
              <li className="flex items-center">
                <XCircleIcon className="h-4 w-4 text-gray-400 mr-2" />
                Unnecessary costs from inefficient routing
              </li>
              <li className="flex items-center">
                <XCircleIcon className="h-4 w-4 text-gray-400 mr-2" />
                No adaptation to changing conditions
              </li>
              <li className="flex items-center">
                <XCircleIcon className="h-4 w-4 text-gray-400 mr-2" />
                Missed opportunities for optimization
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Interactive Features Section with Advanced Animations */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Intelligent Routing Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience routing that thinks for you. Our ML-powered features don't just route—they optimize, learn, and improve.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm hover:shadow-lg transform hover:scale-105 transition-all duration-300">
                <div className="bg-gray-100 rounded-lg p-3 w-fit mb-6">
                  <feature.icon className="h-6 w-6 text-gray-700" />
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 mb-6">{feature.description}</p>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <CheckCircleIcon className="h-4 w-4 text-gray-500 mr-2" />
                      Key Features
                    </h4>
                    <ul className="space-y-2">
                      {feature.details.map((detail, detailIndex) => (
                        <li key={detailIndex} className="text-sm text-gray-600 flex items-start">
                          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                          {detail}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Competitive Advantage</h4>
                    <p className="text-sm text-gray-700">{feature.competitive}</p>
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

      {/* Competitive Comparison with Clean Design */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Why Model Bridge Routing Wins
            </h2>
            <p className="text-xl text-gray-600">
              See how our intelligent routing outperforms traditional solutions.
            </p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Feature
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Basic Routing
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
                {competitiveComparison.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.feature}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.basic}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {item.modelBridge}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {item.advantage}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Technical Architecture with Clean Design */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Technical Architecture
            </h2>
            <p className="text-xl text-gray-600">
              Built on cutting-edge routing technology for maximum performance and efficiency.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {technicalArchitecture.map((component, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-lg transform hover:scale-105 transition-transform duration-300">
                <div className="flex items-center mb-4">
                  <div className="bg-gray-100 rounded-lg p-2 mr-4">
                    <CpuChipIcon className="h-6 w-6 text-gray-700" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">{component.component}</h3>
                </div>
                
                <p className="text-gray-600 mb-4">{component.description}</p>
                
                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold text-gray-900 text-sm">Technology</h4>
                    <p className="text-sm text-gray-600">{component.technology}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 text-sm">Performance</h4>
                    <p className="text-sm text-gray-600">{component.performance}</p>
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
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Route Intelligently?
          </h2>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Join thousands of teams who've transformed their routing with Model Bridge. 
            Start routing with intelligence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="bg-white text-gray-900 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Start Free Trial
            </Link>
            <Link
              to="/product/orchestration"
              className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Explore Other Features
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default IntelligentRouting; 