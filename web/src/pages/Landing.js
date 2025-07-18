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
  XMarkIcon,
  PlayIcon,
  ArrowRightIcon,
  PhoneIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';
import Logo from '../components/Logo';

const Landing = () => {
  const [stats, setStats] = useState({
    totalModels: 0,
    providers: 0,
    uptime: '99.9%'
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    company: '',
    message: ''
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/v1/models/public');
      const modelCount = response.data.total_models || Object.values(response.data.models || {}).reduce((sum, models) => sum + models.length, 0);
      const providerCount = response.data.total_providers || Object.keys(response.data.models || {}).length;
      
      setStats({
        totalModels: modelCount,
        providers: providerCount,
        uptime: '99.9%'
      });
    } catch (error) {
      setStats({
        totalModels: 80,
        providers: 12,
        uptime: '99.9%'
      });
    }
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    try {
      // Send email via your backend API
      await api.post('/v1/contact', contactForm);
      alert('Thank you! Your message has been sent. We\'ll get back to you soon.');
      setContactForm({ name: '', email: '', company: '', message: '' });
      setContactModalOpen(false);
    } catch (error) {
      alert('Sorry, there was an error sending your message. Please try again.');
    }
  };

  const features = [
    {
      icon: CpuChipIcon,
      title: 'Unified Model Access',
      description: 'Access 80+ AI models from OpenAI, Anthropic, Google, and 12+ providers through a single, consistent API.',
      highlight: 'One API for everything'
    },
    {
      icon: BoltIcon,
      title: 'Intelligent Routing',
      description: 'Smart algorithm automatically selects the optimal model for each request, balancing cost, speed, and quality.',
      highlight: 'Save 50-80% on costs'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Enterprise Security',
      description: 'SOC 2 compliant infrastructure with secure key management, rate limiting, and comprehensive audit logs.',
      highlight: 'Bank-level security'
    },
    {
      icon: CloudIcon,
      title: 'High Availability',
      description: 'Automatic failover across multiple providers ensures 99.9% uptime for mission-critical applications.',
      highlight: 'Never goes down'
    }
  ];

  const providers = [
    { name: 'OpenAI', models: 'GPT-4o, GPT-4, GPT-3.5', category: 'General Purpose', icon: `${process.env.PUBLIC_URL}/images/openaiiconq.png` },
    { name: 'Anthropic', models: 'Claude 3.5 Sonnet, Claude 3 Opus', category: 'Reasoning', icon: `${process.env.PUBLIC_URL}/images/icons8-anthropic-48.png` },
    { name: 'Google', models: 'Gemini 1.5 Pro, Gemini Ultra', category: 'Multimodal', icon: `${process.env.PUBLIC_URL}/images/google-color.png` },
    { name: 'Groq', models: 'Llama 3, Mixtral (Ultra-fast)', category: 'Speed', icon: `${process.env.PUBLIC_URL}/images/icons8-grok-48.png` },
    { name: 'Cohere', models: 'Command R+, Command R', category: 'Enterprise', icon: `${process.env.PUBLIC_URL}/images/cohere-color.png` },
    { name: 'DeepSeek', models: 'DeepSeek R1 (Reasoning)', category: 'Specialized', icon: `${process.env.PUBLIC_URL}/images/deepseek-color.png` },
    { name: 'Mistral', models: 'Mistral Large, Medium', category: 'Open Source', icon: `${process.env.PUBLIC_URL}/images/mistral-color.png` },
    { name: 'Meta', models: 'Llama 3, Llama 2', category: 'Open Source', icon: `${process.env.PUBLIC_URL}/images/meta-color.png` },
    { name: 'Ollama', models: 'Local Models (Free)', category: 'Local', icon: `${process.env.PUBLIC_URL}/images/ollama.png` }
  ];

  const companyLogos = [
    { name: 'TechCorp', logo: '🏢' },
    { name: 'StartupXYZ', logo: '🚀' },
    { name: 'Enterprise Inc', logo: '🏛️' },
    { name: 'Innovation Labs', logo: '🔬' },
    { name: 'Global Systems', logo: '🌐' },
    { name: 'Future Tech', logo: '⚡' }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm border-b border-gray-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
                <Logo size="large" showText={true} />
              <div className="hidden md:block ml-12">
                <div className="flex items-center space-x-8">
                  <a href="#features" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                    Features
                  </a>
                  <Link to="/models" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                    Models
                  </Link>
                  <Link to="/pricing" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                    Pricing
                  </Link>
                  <Link to="/docs" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                    Docs
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="hidden md:flex items-center space-x-4">
              <button
                onClick={() => setContactModalOpen(true)}
                className="flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                <PhoneIcon className="h-4 w-4 mr-1" />
                Contact Sales
              </button>
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>

            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-600 hover:text-gray-900 p-2"
              >
                {mobileMenuOpen ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100">
            <div className="px-4 pt-2 pb-3 space-y-1">
              <a href="#features" className="block text-gray-600 hover:text-gray-900 px-3 py-2 font-medium">
                Features
              </a>
              <Link to="/models" className="block text-gray-600 hover:text-gray-900 px-3 py-2 font-medium">
                Models
              </Link>
              <Link to="/pricing" className="block text-gray-600 hover:text-gray-900 px-3 py-2 font-medium">
                Pricing
              </Link>
                              <Link to="/docs" className="block text-gray-600 hover:text-gray-900 px-3 py-2 font-medium">
                  Docs
                </Link>
                <div className="pt-4 border-t border-gray-100">
                  <button
                    onClick={() => setContactModalOpen(true)}
                    className="flex items-center text-gray-600 hover:text-gray-900 px-3 py-2 font-medium"
                  >
                    <PhoneIcon className="h-4 w-4 mr-1" />
                    Contact Sales
                  </button>
                  <Link to="/login" className="block text-gray-600 hover:text-gray-900 px-3 py-2 font-medium">
                    Sign In
                  </Link>
                  <Link to="/register" className="block bg-gray-900 text-white px-3 py-2 rounded-lg font-medium mt-2">
                    Get Started
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section with Video */}
      <section className="pt-24 pb-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-5xl mx-auto mb-16">
            {/* Enterprise Badge with Advanced Styling */}
            <div className="relative inline-flex items-center justify-center mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-green-600/20 rounded-full blur-xl"></div>
              <div className="relative bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-full px-6 py-2 shadow-lg">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">
                    Where AI-First Companies Scale
                  </span>
                  <div className="w-2 h-2 bg-gradient-to-r from-green-500 to-blue-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Main Title with Advanced Typography */}
            <h1 className="relative text-5xl md:text-7xl font-bold mb-8 leading-tight">
              <span className="text-gray-900">One API for</span>
              <span className="block relative mt-2">
                <span className="absolute inset-0 bg-gradient-to-r from-yellow-700 via-yellow-800 to-gray-900 bg-clip-text text-transparent blur-sm opacity-40">
                  Every AI Model
                </span>
                <span className="relative bg-gradient-to-r from-yellow-800 via-amber-900 to-black bg-clip-text text-transparent">
                  Every AI Model
                </span>
              </span>
            </h1>

            {/* Decorative Elements */}
            <div className="flex items-center justify-center mb-8">
              <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent w-20"></div>
              <div className="mx-4 w-3 h-3 bg-gradient-to-r from-blue-500 to-green-500 rounded-full animate-spin" style={{ animationDuration: '8s' }}></div>
              <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent w-20"></div>
            </div>
            
            <p className="text-xl text-gray-600 mb-12 leading-relaxed max-w-3xl mx-auto">
              Watch how Model Bridge connects your application to 80+ AI models through intelligent routing, 
              automatic failover, and enterprise-grade security.
            </p>
          </div>
          
          {/* Video with story around it */}
          <div className="grid grid-cols-1 lg:grid-cols-10 gap-6 items-center mb-20">
            {/* Left side story */}
            <div className="lg:col-span-2 space-y-12">
              <div className="text-center lg:text-right p-3 transform hover:scale-105 transition-all duration-300 hover:bg-white hover:shadow-lg rounded-xl animate-bounce" style={{ animationDuration: '6s', animationDelay: '0s' }}>
                <div className="inline-flex items-center px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm font-medium mb-4 animate-pulse">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-ping"></span>
                  Your App
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">Single Request</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Send one API call to our unified endpoint</p>
              </div>
              
              <div className="text-center lg:text-right p-3 transform hover:scale-105 transition-all duration-300 hover:bg-white hover:shadow-lg rounded-xl animate-bounce" style={{ animationDuration: '6s', animationDelay: '1s' }}>
                <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-4 animate-pulse">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-ping"></span>
                  Smart Routing
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">AI Decides</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Our system picks the best model for your specific task</p>
              </div>
            </div>
            
            {/* Center video - bigger */}
            <div className="lg:col-span-6">
              <div className="relative mx-auto">
                <video 
                  src="/images/Untitled1.mp4" 
                  autoPlay 
                  loop 
                  muted 
                  playsInline
                  className="w-full h-auto rounded-lg"
                  style={{ maxHeight: '600px' }}
                >
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
            
            {/* Right side story */}
            <div className="lg:col-span-2 space-y-12">
              <div className="text-center lg:text-left p-3 transform hover:scale-105 transition-all duration-300 hover:bg-white hover:shadow-lg rounded-xl animate-bounce" style={{ animationDuration: '6s', animationDelay: '2s' }}>
                <div className="inline-flex items-center px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm font-medium mb-4 animate-pulse">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2 animate-ping"></span>
                  Multiple Providers
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">80+ Models</h3>
                <p className="text-gray-600 text-sm leading-relaxed">OpenAI, Anthropic, Google, and 9+ more providers</p>
              </div>
              
              <div className="text-center lg:text-left p-3 transform hover:scale-105 transition-all duration-300 hover:bg-white hover:shadow-lg rounded-xl animate-bounce" style={{ animationDuration: '6s', animationDelay: '3s' }}>
                <div className="inline-flex items-center px-4 py-2 bg-orange-50 text-orange-700 rounded-full text-sm font-medium mb-4 animate-pulse">
                  <span className="w-2 h-2 bg-orange-500 rounded-full mr-2 animate-ping"></span>
                  Best Response
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">Optimized Result</h3>
                <p className="text-gray-600 text-sm leading-relaxed">Get the perfect balance of cost, speed, and quality</p>
              </div>
            </div>
          </div>
          
          {/* CTA below video */}
          <div className="text-center">
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link
                to="/register"
                className="group bg-gray-900 hover:bg-gray-800 text-white px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center"
              >
                Start Building Free
                <ArrowRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/docs"
                className="group border border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center"
              >
                <PlayIcon className="mr-2 h-5 w-5" />
                View Demo
              </Link>
            </div>
            
            <p className="text-sm text-gray-500">
              Free tier • 1,000 requests/month • No credit card required
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">{stats.totalModels}+</div>
              <div className="text-gray-600 font-medium">AI Models</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">{stats.providers}+</div>
              <div className="text-gray-600 font-medium">Providers</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">{stats.uptime}</div>
              <div className="text-gray-600 font-medium">Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">80%</div>
              <div className="text-gray-600 font-medium">Cost Savings</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Built for Enterprise
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Production-ready infrastructure that scales with your business
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200 hover:shadow-lg transition-shadow duration-300">
                <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-6">
                  <feature.icon className="h-6 w-6 text-gray-600" />
                </div>
                
                <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 mb-4 leading-relaxed">{feature.description}</p>
                
                <div className="inline-flex items-center px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium">
                  <CheckIcon className="h-4 w-4 mr-1" />
                  {feature.highlight}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Models Section */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Leading AI Providers
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Access models from the world's top AI companies through one unified interface
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {providers.map((provider, index) => (
              <div key={index} className="group bg-gray-50 hover:bg-white rounded-2xl p-6 border border-transparent hover:border-gray-200 hover:shadow-lg transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <img 
                      src={provider.icon} 
                      alt={`${provider.name} logo`}
                      className="w-8 h-8 object-contain"
                      onError={(e) => {
                        console.log(`Failed to load icon for ${provider.name}:`, provider.icon);
                        e.target.style.display = 'none';
                        // Show fallback text
                        const fallback = document.createElement('div');
                        fallback.textContent = provider.name.charAt(0);
                        fallback.className = 'w-8 h-8 bg-gray-100 rounded flex items-center justify-center text-gray-600 font-bold';
                        e.target.parentNode.insertBefore(fallback, e.target);
                      }}
                    />
                    <h3 className="text-xl font-bold text-gray-900">{provider.name}</h3>
                  </div>
                  <div className="flex items-center text-green-600 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Online
                  </div>
                </div>
                
                <p className="text-gray-600 mb-3">{provider.models}</p>
                
                <div className="inline-flex items-center px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                  {provider.category}
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <Link
              to="/models"
              className="group inline-flex items-center px-8 py-4 bg-gray-900 hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors duration-300"
            >
                View All Models
                <ChevronRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>





      {/* CTA Section */}
      <section className="py-24 bg-white text-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Join thousands of developers building the next generation of AI applications
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="group bg-gray-900 text-white hover:bg-gray-800 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center"
            >
                Start Free Trial
              <ArrowRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            
            <Link
              to="/contact"
              className="group border border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white py-16 border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
                <Logo size="default" showText={true} />
              <p className="text-gray-600 mt-4 leading-relaxed">
                Enterprise-grade AI infrastructure for modern applications.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Product</h4>
              <ul className="space-y-3 text-gray-600">
                <li><a href="#features" className="hover:text-gray-900 transition-colors">Features</a></li>
                <li><Link to="/models" className="hover:text-gray-900 transition-colors">Models</Link></li>
                <li><Link to="/pricing" className="hover:text-gray-900 transition-colors">Pricing</Link></li>
                <li><Link to="/dashboard/analytics" className="hover:text-gray-900 transition-colors">Analytics</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Resources</h4>
              <ul className="space-y-3 text-gray-600">
                <li><Link to="/docs" className="hover:text-gray-900 transition-colors">Documentation</Link></li>
                <li><Link to="/guides" className="hover:text-gray-900 transition-colors">API Reference</Link></li>
                <li><Link to="/support" className="hover:text-gray-900 transition-colors">Support</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Company</h4>
              <ul className="space-y-3 text-gray-600">
                <li><Link to="/about" className="hover:text-gray-900 transition-colors">About</Link></li>
                <li><Link to="/careers" className="hover:text-gray-900 transition-colors">Careers</Link></li>
                <li><Link to="/contact" className="hover:text-gray-900 transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-8 text-center text-gray-500">
            <p>&copy; 2024 Model Bridge. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Contact Modal */}
      {contactModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">Contact Sales</h3>
                <button
                  onClick={() => setContactModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <form onSubmit={handleContactSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={contactForm.name}
                    onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Your name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    required
                    value={contactForm.email}
                    onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your@email.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    value={contactForm.company}
                    onChange={(e) => setContactForm({ ...contactForm, company: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Your company name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message *
                  </label>
                  <textarea
                    required
                    rows="4"
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Tell us about your AI needs..."
                  />
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setContactModalOpen(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    Send Message
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Landing;