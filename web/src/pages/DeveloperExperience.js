import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  CodeBracketIcon,
  DocumentTextIcon,
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
  PauseIcon
} from '@heroicons/react/24/outline';

const DeveloperExperience = () => {
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
      title: 'Comprehensive API Documentation',
      icon: DocumentTextIcon,
      description: 'Interactive API documentation with code examples and testing',
      details: [
        'Interactive API playground with real-time testing',
        'Auto-generated documentation from code',
        'Code examples in multiple languages',
        'Request/response examples',
        'API versioning and changelog'
      ],
      competitive: 'Basic docs vs. our interactive API documentation with real-time testing.',
      technical: 'Uses OpenAPI 3.0 specification with auto-generation, implements interactive playground with real-time request testing, and provides multi-language code examples.'
    },
    {
      title: 'SDK & Client Libraries',
      icon: CodeBracketIcon,
      description: 'Production-ready SDKs for popular programming languages',
      details: [
        'SDKs for Python, JavaScript, Java, Go',
        'TypeScript definitions and types',
        'Comprehensive error handling',
        'Async/await support',
        'Built-in retry logic and rate limiting'
      ],
      competitive: 'Basic REST client vs. our production-ready SDKs with comprehensive features.',
      technical: 'Implements language-specific SDKs with idiomatic patterns, uses OpenAPI code generation, and provides comprehensive error handling with retry logic.'
    },
    {
      title: 'Developer Tools & IDE Integration',
      icon: Cog6ToothIcon,
      description: 'Seamless integration with popular development environments',
      details: [
        'VS Code extension with IntelliSense',
        'CLI tools for local development',
        'IDE plugins for popular editors',
        'Debugging and logging tools',
        'Local development environment'
      ],
      competitive: 'Manual setup vs. our integrated developer tools with IDE support.',
      technical: 'Uses Language Server Protocol for IDE integration, implements CLI tools with configuration management, and provides local development environment with Docker.'
    },
    {
      title: 'Testing & Debugging Tools',
      icon: BeakerIcon,
      description: 'Comprehensive testing framework and debugging capabilities',
      details: [
        'Unit testing framework integration',
        'Mock server for testing',
        'Request/response debugging',
        'Performance testing tools',
        'Integration test helpers'
      ],
      competitive: 'Basic testing vs. our comprehensive testing framework with debugging tools.',
      technical: 'Implements mock server with realistic responses, uses request/response logging for debugging, and provides performance testing with load simulation.'
    },
    {
      title: 'Developer Support & Resources',
      icon: AcademicCapIcon,
      description: 'Extensive learning resources and community support',
      details: [
        'Comprehensive tutorials and guides',
        'Video tutorials and webinars',
        'Community forum and Discord',
        'Code samples and templates',
        'Best practices documentation'
      ],
      competitive: 'Basic docs vs. our comprehensive developer support with community resources.',
      technical: 'Uses structured documentation with search capabilities, implements community platform with moderation, and provides interactive learning resources.'
    },
    {
      title: 'Performance & Optimization',
      icon: BoltIcon,
      description: 'Tools for optimizing API performance and efficiency',
      details: [
        'Performance profiling tools',
        'Request optimization suggestions',
        'Caching strategies',
        'Rate limiting guidance',
        'Cost optimization tips'
      ],
      competitive: 'Manual optimization vs. our intelligent performance tools with optimization guidance.',
      technical: 'Uses performance profiling with request analysis, implements caching strategies with Redis, and provides cost optimization with usage analytics.'
    }
  ];

  const testimonials = [
    {
      name: 'Alex Chen',
      role: 'Senior Developer at TechStart',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      quote: 'The interactive API playground saved us hours of development time. The SDKs are production-ready and well-documented.',
      rating: 5
    },
    {
      name: 'Maria Rodriguez',
      role: 'Lead Engineer at DataCorp',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
      quote: 'The VS Code extension with IntelliSense makes development so much faster. The debugging tools are excellent.',
      rating: 5
    },
    {
      name: 'David Kim',
      role: 'CTO at Startup Inc',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      quote: 'The comprehensive documentation and community support helped our team get up to speed quickly. Excellent developer experience.',
      rating: 5
    }
  ];

  const competitiveComparison = [
    {
      feature: 'API Documentation',
      basic: 'Basic markdown docs',
      modelBridge: 'Interactive documentation with playground',
      advantage: 'Real-time testing and examples'
    },
    {
      feature: 'SDK Support',
      basic: 'Basic REST client',
      modelBridge: 'Production-ready SDKs for multiple languages',
      advantage: 'Comprehensive language support'
    },
    {
      feature: 'Developer Tools',
      basic: 'Manual setup',
      modelBridge: 'Integrated IDE tools and CLI',
      advantage: 'Seamless development workflow'
    },
    {
      feature: 'Testing Tools',
      basic: 'Basic unit tests',
      modelBridge: 'Comprehensive testing framework',
      advantage: 'Advanced debugging capabilities'
    },
    {
      feature: 'Support Resources',
      basic: 'Basic documentation',
      modelBridge: 'Comprehensive tutorials and community',
      advantage: 'Extensive learning resources'
    },
    {
      feature: 'Performance Tools',
      basic: 'Manual optimization',
      modelBridge: 'Intelligent performance tools',
      advantage: 'Automated optimization guidance'
    }
  ];

  const technicalArchitecture = [
    {
      component: 'API Documentation',
      description: 'Interactive documentation system',
      technology: 'OpenAPI 3.0 with playground',
      performance: 'Real-time request testing'
    },
    {
      component: 'SDK Generator',
      description: 'Multi-language SDK generation',
      technology: 'OpenAPI code generation',
      performance: 'Type-safe client libraries'
    },
    {
      component: 'IDE Integration',
      description: 'Development environment tools',
      technology: 'Language Server Protocol',
      performance: 'IntelliSense and autocomplete'
    },
    {
      component: 'Testing Framework',
      description: 'Comprehensive testing tools',
      technology: 'Mock server with debugging',
      performance: 'Realistic test scenarios'
    },
    {
      component: 'Developer Portal',
      description: 'Learning and support platform',
      technology: 'Structured documentation system',
      performance: 'Fast search and navigation'
    },
    {
      component: 'Performance Tools',
      description: 'Optimization and profiling',
      technology: 'Request analysis with caching',
      performance: 'Automated optimization'
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
              <CodeBracketIcon className="h-4 w-4 mr-2" />
              Developer-First Experience
            </div>
            <h1 className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <span className="block text-gray-900">Built for</span>
              <span className="block text-gray-900">
                Developers
              </span>
            </h1>
            <p className={`text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              From interactive documentation to production-ready SDKs, Model Bridge provides 
              everything developers need to build, test, and deploy AI applications with confidence.
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
                      Pause Developer Demo
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Developer Demo
                    </>
                  )}
                </span>
              </button>
            </div>
            
            {/* Animated Stats Grid with gray/black theme */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">5+</div>
                <div className="text-sm text-gray-600">Languages</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">Interactive</div>
                <div className="text-sm text-gray-600">Documentation</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">IDE</div>
                <div className="text-sm text-gray-600">Integration</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">24/7</div>
                <div className="text-sm text-gray-600">Support</div>
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
              The Developer Experience Challenge
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              AI development is complex enough without poor developer tools. Most platforms offer 
              basic documentation—we provide a complete developer experience with interactive tools, 
              comprehensive SDKs, and extensive support resources.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <XCircleIcon className="h-8 w-8 text-gray-400 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Basic Developer Tools</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Static documentation only
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Basic REST client
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Manual setup required
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Limited support resources
                </li>
              </ul>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="h-8 w-8 text-gray-900 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Model Bridge Developer Experience</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Interactive API playground
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Production-ready SDKs
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Integrated IDE tools
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Comprehensive support
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
              Comprehensive Developer Tools
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience development that flows naturally. Our developer tools don't just work—they enhance your workflow and accelerate your development.
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
              What Developers Say
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real stories from developers who've transformed their workflow with Model Bridge.
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
              Why Model Bridge Developer Experience Wins
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how our developer-first approach outperforms traditional solutions.
            </p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden">
            <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
              <div className="font-semibold text-gray-900">Feature</div>
              <div className="font-semibold text-gray-900">Basic Tools</div>
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
              Built on cutting-edge developer experience technology for maximum productivity and efficiency.
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
            Ready to Build with Better Tools?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Join thousands of developers who've accelerated their AI development with Model Bridge. 
            Start building with tools designed for developers.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="inline-flex items-center px-8 py-4 bg-white text-gray-900 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              Start Free Trial
            </Link>
            <Link
              to="/product/enterprise-features"
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

export default DeveloperExperience; 