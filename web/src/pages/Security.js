import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  ShieldCheckIcon,
  LockClosedIcon,
  EyeIcon,
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

const Security = () => {
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
      title: 'Enterprise-Grade Security',
      icon: ShieldCheckIcon,
      description: 'Comprehensive security with threat detection, encryption, and compliance',
      details: [
        'AES-256 encryption at rest and TLS 1.3 in transit',
        'Advanced threat detection and prevention',
        'Security headers and CSP policies',
        'Vulnerability scanning and penetration testing',
        'SOC 2 Type II compliance and audit trails'
      ],
      competitive: 'Basic security vs. our enterprise-grade security with comprehensive threat protection and compliance.',
      technical: 'Implements defense-in-depth security architecture with multiple layers of protection, real-time threat detection using ML models, and comprehensive security monitoring.'
    },
    {
      title: 'Compliance & Governance',
      icon: DocumentTextIcon,
      description: 'Full compliance support for enterprise requirements and regulations',
      details: [
        'SOC 2 Type II compliance with regular audits',
        'GDPR and CCPA privacy compliance',
        'HIPAA compliance for healthcare applications',
        'ISO 27001 security standards',
        'Automated compliance reporting and monitoring'
      ],
      competitive: 'Basic compliance vs. our comprehensive compliance framework with automated monitoring.',
      technical: 'Uses automated compliance monitoring with real-time policy enforcement, automated audit trail generation, and compliance-ready data retention policies.'
    },
    {
      title: 'Data Privacy & Protection',
      icon: LockClosedIcon,
      description: 'Advanced data privacy controls with encryption and access management',
      details: [
        'Data encryption at rest and in transit',
        'Privacy-by-design architecture',
        'Data retention and lifecycle management',
        'Privacy impact assessments',
        'Right to be forgotten implementation'
      ],
      competitive: 'Basic data handling vs. our privacy-by-design architecture with comprehensive data protection.',
      technical: 'Implements zero-knowledge architecture where possible, uses homomorphic encryption for sensitive operations, and provides comprehensive data lifecycle management.'
    },
    {
      title: 'Access Control & Authentication',
      icon: UserGroupIcon,
      description: 'Multi-factor authentication and granular access controls',
      details: [
        'Multi-factor authentication (MFA)',
        'Single sign-on (SSO) integration',
        'Role-based access control (RBAC)',
        'Just-in-time access provisioning',
        'Privileged access management'
      ],
      competitive: 'Basic authentication vs. our enterprise-grade access control with MFA and granular permissions.',
      technical: 'Uses OAuth 2.0/OIDC for modern authentication, implements SAML 2.0 for enterprise SSO, and provides granular RBAC with audit logging.'
    },
    {
      title: 'Security Monitoring & Alerting',
      icon: EyeIcon,
      description: 'Real-time security monitoring with intelligent threat detection',
      details: [
        'Real-time security event monitoring',
        'Intelligent threat detection using ML',
        'Security incident response automation',
        'Comprehensive audit logging',
        'Security metrics and reporting'
      ],
      competitive: 'Basic monitoring vs. our intelligent security monitoring with ML-powered threat detection.',
      technical: 'Uses SIEM-like capabilities with real-time event correlation, implements ML-powered anomaly detection, and provides automated incident response workflows.'
    },
    {
      title: 'Vulnerability Management',
      icon: Cog6ToothIcon,
      description: 'Proactive vulnerability scanning and patch management',
      details: [
        'Automated vulnerability scanning',
        'Dependency vulnerability monitoring',
        'Security patch management',
        'Penetration testing services',
        'Security assessment reports'
      ],
      competitive: 'Manual security vs. our proactive vulnerability management with automated scanning and patching.',
      technical: 'Implements automated vulnerability scanning with dependency analysis, uses automated patch management with rollback capabilities, and provides comprehensive security assessments.'
    }
  ];

  const testimonials = [
    {
      name: 'David Kim',
      role: 'CISO at FinTech Solutions',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      quote: 'Model Bridge\'s security framework helped us achieve SOC 2 compliance in record time. The automated compliance monitoring is a game-changer.',
      rating: 5
    },
    {
      name: 'Lisa Thompson',
      role: 'Security Director at HealthTech',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
      quote: 'The ML-powered threat detection caught a sophisticated attack before it could do damage. Our security team was impressed.',
      rating: 5
    },
    {
      name: 'James Wilson',
      role: 'CTO at Enterprise Corp',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      quote: 'Enterprise-grade security without the enterprise complexity. Model Bridge makes security accessible and effective.',
      rating: 5
    }
  ];

  const competitiveComparison = [
    {
      feature: 'Security Architecture',
      basic: 'Basic HTTPS encryption',
      modelBridge: 'Enterprise-grade security with defense-in-depth',
      advantage: 'Comprehensive threat protection'
    },
    {
      feature: 'Compliance',
      basic: 'Basic privacy policies',
      modelBridge: 'Full compliance framework with automated monitoring',
      advantage: 'Enterprise compliance ready'
    },
    {
      feature: 'Data Privacy',
      basic: 'Basic data handling',
      modelBridge: 'Privacy-by-design with encryption',
      advantage: 'Advanced data protection'
    },
    {
      feature: 'Access Control',
      basic: 'Simple username/password',
      modelBridge: 'MFA with granular RBAC',
      advantage: 'Enterprise-grade access control'
    },
    {
      feature: 'Security Monitoring',
      basic: 'Basic logging',
      modelBridge: 'Intelligent security monitoring with ML',
      advantage: 'Proactive threat detection'
    },
    {
      feature: 'Vulnerability Management',
      basic: 'Manual security updates',
      modelBridge: 'Automated vulnerability management',
      advantage: 'Proactive security maintenance'
    }
  ];

  const technicalArchitecture = [
    {
      component: 'Security Gateway',
      description: 'Enterprise security controls',
      technology: 'Defense-in-depth architecture',
      performance: 'Sub-millisecond security checks'
    },
    {
      component: 'Compliance Engine',
      description: 'Automated compliance monitoring',
      technology: 'Policy enforcement with audit trails',
      performance: 'Real-time compliance validation'
    },
    {
      component: 'Privacy Engine',
      description: 'Data privacy and protection',
      technology: 'Encryption with lifecycle management',
      performance: 'Zero-downtime privacy updates'
    },
    {
      component: 'Access Control',
      description: 'Multi-factor authentication',
      technology: 'OAuth 2.0, SAML 2.0, RBAC',
      performance: 'Sub-second authentication'
    },
    {
      component: 'Security Monitor',
      description: 'Intelligent threat detection',
      technology: 'ML-powered anomaly detection',
      performance: 'Real-time threat response'
    },
    {
      component: 'Vulnerability Scanner',
      description: 'Proactive security scanning',
      technology: 'Automated scanning with patching',
      performance: 'Continuous security assessment'
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
              <ShieldCheckIcon className="h-4 w-4 mr-2" />
              Enterprise-Grade Security & Compliance
            </div>
            <h1 className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <span className="block text-gray-900">Security That</span>
              <span className="block text-gray-900">
                Never Sleeps
              </span>
            </h1>
            <p className={`text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              Built for enterprises that demand the highest security standards. Model Bridge provides 
              comprehensive security, compliance, and threat protection that adapts and evolves with your business.
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
                      Pause Security Demo
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Security Demo
                    </>
                  )}
                </span>
              </button>
            </div>
            
            {/* Animated Stats Grid with gray/black theme */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">SOC 2</div>
                <div className="text-sm text-gray-600">Compliance</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">AES-256</div>
                <div className="text-sm text-gray-600">Encryption</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">24/7</div>
                <div className="text-sm text-gray-600">Monitoring</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">ML</div>
                <div className="text-sm text-gray-600">Threat Detection</div>
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
              The Security Challenge
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              As AI becomes mission-critical, security and compliance requirements become paramount. 
              Most AI platforms offer basic security—we provide enterprise-grade protection 
              with comprehensive compliance and intelligent threat detection.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <XCircleIcon className="h-8 w-8 text-gray-400 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Basic Security</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Simple HTTPS encryption only
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  No compliance framework
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Basic data handling
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Manual security updates
                </li>
              </ul>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-2xl p-8 transform hover:scale-105 transition-transform duration-300 shadow-sm hover:shadow-md">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="h-8 w-8 text-gray-900 mr-3" />
                <h3 className="text-xl font-semibold text-gray-800">Model Bridge Security</h3>
              </div>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Enterprise-grade defense-in-depth
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Automated compliance framework
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Privacy-by-design architecture
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  ML-powered threat detection
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
              Comprehensive Security Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience security that adapts and evolves. Our enterprise-grade protection doesn't just defend—it learns, predicts, and prevents.
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
              Trusted by Security Leaders
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real stories from security professionals who've transformed their protection with Model Bridge.
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
              Why Model Bridge Security Wins
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how our enterprise-grade security outperforms traditional solutions.
            </p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden">
            <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
              <div className="font-semibold text-gray-900">Feature</div>
              <div className="font-semibold text-gray-900">Basic Security</div>
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
              Built on cutting-edge security technology for maximum protection and compliance.
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
            Ready to Secure Your AI Operations?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Join thousands of enterprises who trust Model Bridge with their security. 
            Start protecting your AI operations with enterprise-grade security.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="inline-flex items-center px-8 py-4 bg-white text-gray-900 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              Start Free Trial
            </Link>
            <Link
              to="/product/developer-experience"
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

export default Security; 