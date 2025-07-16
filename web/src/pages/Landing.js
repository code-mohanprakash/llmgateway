import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ChevronRightIcon, 
  CheckIcon, 
  CpuChipIcon,
  CloudIcon,
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon,
  CogIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';
import BridgeAnimation from '../components/BridgeAnimation';
import Logo from '../components/Logo';

const Landing = () => {
  const [stats, setStats] = useState({
    totalModels: 0,
    providers: 0,
    uptime: '99.9%'
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  console.log('Landing page rendering...');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      console.log('Fetching stats from API...');
      const response = await api.get('/v1/models/public');
      const modelCount = response.data.total_models || Object.values(response.data.models || {}).reduce((sum, models) => sum + models.length, 0);
      const providerCount = response.data.total_providers || Object.keys(response.data.models || {}).length;
      const freeModels = response.data.free_models || 0;
      const paidModels = response.data.paid_models || 0;
      
      setStats({
        totalModels: modelCount,
        providers: providerCount,
        freeModels: freeModels,
        paidModels: paidModels,
        uptime: '99.9%'
      });
      console.log('Stats fetched successfully');
    } catch (error) {
      console.log('API fetch failed, using default stats:', error.message);
      // Use default stats if API is not available
      setStats({
        totalModels: 50,
        providers: 10,
        freeModels: 12,
        paidModels: 38,
        uptime: '99.9%'
      });
    }
  };

  const features = [
    {
      icon: CpuChipIcon,
      title: 'Multi-Provider Access',
      description: 'Access OpenAI, Anthropic, Google, Groq, and 10+ more providers through one unified API'
    },
    {
      icon: BoltIcon,
      title: 'Intelligent Routing',
      description: 'Automatic provider selection based on performance, cost, and availability with smart fallbacks'
    },
    {
      icon: ChartBarIcon,
      title: 'Usage Analytics',
      description: 'Comprehensive analytics, cost tracking, and performance monitoring for all your LLM requests'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Enterprise Security',
      description: 'SOC 2 compliant with API key management, rate limiting, and audit logging'
    },
    {
      icon: CloudIcon,
      title: 'High Availability',
      description: '99.9% uptime with automatic failover between providers and global edge deployment'
    },
    {
      icon: CogIcon,
      title: 'Easy Integration',
      description: 'Drop-in replacement for OpenAI API with enhanced features and multi-provider support'
    }
  ];

  const providers = [
    { name: 'OpenAI', models: 'GPT-4, GPT-4o, GPT-3.5' },
    { name: 'Anthropic', models: 'Claude 3.5, Claude 3 Opus, Claude 3 Sonnet' },
    { name: 'Google', models: 'Gemini Pro, Gemini 1.5, Gemini Ultra' },
    { name: 'Groq', models: 'Llama 3, Mixtral (Ultra-fast)' },
    { name: 'Together AI', models: 'Llama 3, Mistral, Mixtral' },
    { name: 'Mistral AI', models: 'Mistral Large, Medium, Small' },
    { name: 'Cohere', models: 'Command R+, Command R, Command' },
    { name: 'Perplexity', models: 'PPLX 7B, PPLX 70B' },
    { name: 'Ollama', models: 'Local Models (Free)' },
    { name: 'DeepSeek', models: 'DeepSeek R1 (Reasoning)' }
  ];

  const HeroSection = () => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
      setIsVisible(true);
    }, []);

    return (
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-white">
        <div className="relative z-10 text-center px-4 max-w-6xl mx-auto pt-20">
          {/* Main Content */}
          <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="mb-6 flex items-center justify-center relative">
              {/* Animated Text with Neuron Effects */}
              <div className="relative">
                {/* Bigger Text with Gradient and Shining Effect */}
                <div className="relative">
                  <h1 className="text-4xl md:text-6xl font-bold tracking-tight whitespace-nowrap">
                    <span className="text-[#9B5967] drop-shadow-sm">Model</span>
                    <span className="text-black drop-shadow-sm"> Bridge</span>
                  </h1>
                  
                  {/* Shining overlay effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent -skew-x-12 animate-shine"></div>
                  
                  {/* Neuron particles */}
                  <div className="absolute inset-0 overflow-hidden">
                    {/* Neuron 1 - Blue */}
                    <div className="absolute top-1/4 left-0 w-2 h-2 bg-blue-500 rounded-full animate-neuron-1"></div>
                    <div className="absolute top-1/4 left-0 w-1 h-8 bg-gradient-to-b from-blue-500 to-transparent animate-neuron-1"></div>
                    
                    {/* Neuron 2 - Green */}
                    <div className="absolute top-1/2 right-0 w-2 h-2 bg-green-500 rounded-full animate-neuron-2"></div>
                    <div className="absolute top-1/2 right-0 w-1 h-6 bg-gradient-to-b from-green-500 to-transparent animate-neuron-2"></div>
                    
                    {/* Neuron 3 - Purple */}
                    <div className="absolute bottom-1/4 left-1/3 w-2 h-2 bg-purple-500 rounded-full animate-neuron-3"></div>
                    <div className="absolute bottom-1/4 left-1/3 w-1 h-4 bg-gradient-to-b from-purple-500 to-transparent animate-neuron-3"></div>
                  </div>
                </div>
                
                {/* Floating neural network dots */}
                <div className="absolute -top-4 -left-4 w-3 h-3 bg-orange-500/60 rounded-full animate-bounce"></div>
                <div className="absolute -top-2 -right-8 w-2 h-2 bg-pink-500/70 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
                <div className="absolute -bottom-4 -left-8 w-2 h-2 bg-cyan-500/60 rounded-full animate-bounce" style={{animationDelay: '1s'}}></div>
                <div className="absolute -bottom-2 -right-4 w-3 h-3 bg-yellow-500/50 rounded-full animate-bounce" style={{animationDelay: '1.5s'}}></div>
              </div>
            </div>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto">
              We dynamically route requests from devices to the optimal AI model—OpenAI, Anthropic, Google, and more.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
              <Link
                to="/register"
                className="px-8 py-4 bg-[#9B5967] hover:bg-[#8a4d5a] text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                Start Building Free →
              </Link>
              <Link
                to="/docs"
                className="px-8 py-4 border-2 border-[#9B5967] text-[#9B5967] font-semibold rounded-lg hover:bg-[#9B5967]/10 transition-all duration-300"
              >
                View Documentation
              </Link>
            </div>
          </div>

          {/* Advanced Bridge Animation - Moved down with more spacing */}
          <div className="relative h-80 md:h-96 max-w-5xl mx-auto mb-16">
            <BridgeAnimation />
          </div>

          {/* Stats Section - More spacing and better layout */}
          <div className={`grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-20 transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="bg-white rounded-xl p-8 border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-[#9B5967]/10 rounded-lg flex items-center justify-center mr-3">
                  <CpuChipIcon className="w-5 h-5 text-[#9B5967]" />
                </div>
                <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Models</span>
              </div>
              <div className="text-4xl font-bold text-gray-900 mb-2">{stats.totalModels}+</div>
              <div className="text-gray-600">AI Models Available</div>
            </div>
            <div className="bg-white rounded-xl p-8 border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-[#9B5967]/10 rounded-lg flex items-center justify-center mr-3">
                  <CloudIcon className="w-5 h-5 text-[#9B5967]" />
                </div>
                <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Providers</span>
              </div>
              <div className="text-4xl font-bold text-gray-900 mb-2">{stats.providers}+</div>
              <div className="text-gray-600">Integrated Providers</div>
            </div>
            <div className="bg-white rounded-xl p-8 border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Uptime</span>
              </div>
              <div className="text-4xl font-bold text-gray-900 mb-2">{stats.uptime}</div>
              <div className="text-gray-600">System Reliability</div>
            </div>
          </div>
        </div>
      </section>
    );
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Logo size="large" showText={true} />
              </div>
              <div className="hidden md:block ml-10">
                <div className="flex items-baseline space-x-8">
                  <a href="#features" className="text-gray-900 hover:text-[#9B5967] px-3 py-2 text-sm font-medium transition-colors">
                    Features
                  </a>
                  <Link to="/models" className="text-gray-900 hover:text-[#9B5967] px-3 py-2 text-sm font-medium transition-colors">
                    Models
                  </Link>
                  <Link to="/pricing" className="text-gray-900 hover:text-[#9B5967] px-3 py-2 text-sm font-medium transition-colors">
                    Pricing
                  </Link>
                  <Link to="/docs" className="text-gray-900 hover:text-[#9B5967] px-3 py-2 text-sm font-medium transition-colors">
                    Documentation
                  </Link>
                </div>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-900 hover:text-[#9B5967] px-3 py-2 text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-[#9B5967] hover:bg-[#8a4d5a] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Start Free
              </Link>
            </div>
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-900 hover:text-[#9B5967] p-2"
              >
                {mobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" />
                ) : (
                  <Bars3Icon className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#features" className="block text-gray-900 hover:text-[#9B5967] px-3 py-2 text-base font-medium transition-colors">
                Features
              </a>
              <Link to="/models" className="block text-gray-900 hover:text-[#9B5967] px-3 py-2 text-base font-medium transition-colors">
                Models
              </Link>
              <Link to="/pricing" className="block text-gray-900 hover:text-[#9B5967] px-3 py-2 text-base font-medium transition-colors">
                Pricing
              </Link>
              <Link to="/docs" className="block text-gray-900 hover:text-[#9B5967] px-3 py-2 text-base font-medium transition-colors">
                Documentation
              </Link>
              <div className="pt-4 pb-3 border-t border-gray-200">
                <Link
                  to="/login"
                  className="block text-gray-900 hover:text-[#9B5967] px-3 py-2 text-base font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="block bg-[#9B5967] hover:bg-[#8a4d5a] text-white px-3 py-2 rounded-lg text-base font-medium transition-colors mt-2"
                >
                  Start Free
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Stunning Animated Hero Section */}
      <HeroSection />

      {/* Features Section */}
      <section id="features" className="py-20 bg-gradient-to-br from-gray-50 to-white relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, #9B5967 1px, transparent 0)`,
            backgroundSize: '40px 40px'
          }}></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 via-[#9B5967] to-gray-900 bg-clip-text text-transparent">
              Enterprise-Grade AI Infrastructure
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Built for scale, designed for reliability. Everything you need to power your AI applications.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="group relative p-8 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200/50 hover:border-[#9B5967]/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-2 overflow-hidden">
                {/* Gradient overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#9B5967]/5 to-[#8a4d5a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                {/* Icon container */}
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-[#9B5967]/10 to-[#8a4d5a]/10 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <feature.icon className="h-8 w-8 text-[#9B5967] group-hover:rotate-12 transition-transform duration-300" />
                  </div>
                  
                  {/* Floating elements */}
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-[#9B5967]/20 rounded-full opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity duration-300"></div>
                </div>
                
                <div className="relative">
                  <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-[#9B5967] transition-colors duration-300">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                  
                  {/* Hover indicator */}
                  <div className="flex items-center text-[#9B5967] text-sm font-medium mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    Learn more
                    <svg className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Providers Section */}
      <section id="models" className="py-20 bg-gradient-to-br from-white to-gray-50 relative">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-[#9B5967]/5 rounded-full blur-3xl animate-pulse-slow"></div>
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-blue-200/20 rounded-full blur-3xl animate-pulse-slow" style={{animationDelay: '1s'}}></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 via-[#9B5967] to-gray-900 bg-clip-text text-transparent">
              Access All Leading AI Providers
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              One API to rule them all. Switch between providers seamlessly with intelligent routing.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {providers.map((provider, index) => (
              <div key={index} className="group relative bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 hover:border-[#9B5967]/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-2 overflow-hidden">
                {/* Shimmer effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                
                {/* Status indicator */}
                <div className="absolute top-4 right-4">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-lg">
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-ping absolute inset-0"></div>
                  </div>
                </div>
                
                <div className="relative">
                  <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-[#9B5967] transition-colors duration-300">{provider.name}</h3>
                  <p className="text-gray-600 text-sm mb-4 leading-relaxed">{provider.models}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-green-600 text-sm font-medium">
                      <CheckIcon className="h-4 w-4 mr-1" />
                      Available
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                      Online
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <Link
              to="/models"
              className="group relative inline-flex items-center px-8 py-4 bg-gradient-to-r from-[#9B5967] to-[#8a4d5a] text-white text-lg font-semibold rounded-2xl transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl overflow-hidden"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-[#8a4d5a] to-[#9B5967] opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
              <span className="relative flex items-center">
                View All Models
                <ChevronRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-[#9B5967] via-[#8a4d5a] to-[#9B5967] relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-full h-full">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse-slow" style={{animationDelay: '2s'}}></div>
          </div>
          
          {/* Geometric patterns */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-10 left-10 w-20 h-20 border-2 border-white rotate-45 animate-spin-slow"></div>
            <div className="absolute bottom-10 right-10 w-16 h-16 border-2 border-white rounded-full animate-bounce"></div>
            <div className="absolute top-1/2 left-1/4 w-12 h-12 bg-white/20 transform rotate-45 animate-pulse"></div>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
          
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Ready to Transform Your 
            <span className="relative inline-block">
              AI Infrastructure?
              <div className="absolute -bottom-2 left-0 w-full h-1 bg-white/50 transform scale-x-0 animate-pulse"></div>
            </span>
          </h2>
          
          <p className="text-xl text-white/90 mb-12 max-w-3xl mx-auto leading-relaxed">
            Join thousands of developers and companies using Model Bridge to build better AI applications.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="group relative bg-white text-[#9B5967] hover:bg-gray-100 px-8 py-4 rounded-2xl text-lg font-semibold transition-all transform hover:scale-105 inline-flex items-center shadow-xl hover:shadow-2xl overflow-hidden"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-gray-50 to-white opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
              <span className="relative flex items-center">
                Start Free Trial
                <ChevronRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
            
            <Link
              to="/docs"
              className="group border-2 border-white text-white hover:bg-white hover:text-[#9B5967] px-8 py-4 rounded-2xl text-lg font-semibold transition-all inline-flex items-center backdrop-blur-sm bg-white/10"
            >
              <span className="flex items-center">
                <svg className="mr-2 w-5 h-5 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Read Documentation
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="mb-4">
                <Logo size="default" showText={true} variant="white" />
              </div>
              <p className="text-gray-400">
                Enterprise-grade AI infrastructure for modern applications.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-4 text-gray-300">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><Link to="/models" className="hover:text-white transition-colors">Models</Link></li>
                <li><Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link to="/dashboard/analytics" className="hover:text-white transition-colors">Analytics</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-4 text-gray-300">Resources</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/docs" className="hover:text-white transition-colors">Documentation</Link></li>

                <li><Link to="/guides" className="hover:text-white transition-colors">Guides</Link></li>
                <li><Link to="/support" className="hover:text-white transition-colors">Support</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-4 text-gray-300">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>

                <li><Link to="/careers" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Model Bridge. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;