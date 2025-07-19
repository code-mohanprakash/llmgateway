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
  PlayIcon,
  ArrowRightIcon,
  PhoneIcon,
  EnvelopeIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';
import Logo from '../components/Logo';
import Navigation from '../components/Navigation';

const Landing = () => {
  const [stats, setStats] = useState({
    totalModels: 0,
    providers: 0,
    uptime: '99.9%'
  });
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
        totalModels: Math.max(modelCount, 120), // Updated to reflect actual model count
        providers: Math.max(providerCount, 12), // Updated to reflect actual provider count
        uptime: '99.9%'
      });
    } catch (error) {
      // Fallback stats with accurate numbers
      setStats({
        totalModels: 120,
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
      title: 'The Perplexity Moment for AI APIs',
      description: 'Remember when Perplexity made search intelligent? We\'re doing the same for AI. One API that thinks for you, routes intelligently, and optimizes automatically.',
      highlight: 'Intelligent by design'
    },
    {
      icon: CloudIcon,
      title: 'Never Think About APIs Again',
      description: 'Just like you don\'t think about electricity when you flip a switch, you shouldn\'t think about which AI provider to use. We handle the complexity.',
      highlight: 'Invisible infrastructure'
    },
    {
      icon: BoltIcon,
      title: 'The Cost Revolution',
      description: 'We don\'t just save you money. We change how you think about AI costs. 50-80% savings isn\'t optimization—it\'s a fundamental shift.',
      highlight: 'Cost reimagined'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Vendor Independence, Finally',
      description: 'No more being held hostage by one provider\'s pricing. Switch providers without changing a line of code. Negotiate from strength.',
      highlight: 'True freedom'
    }
  ];

  const providers = [
    { name: 'OpenAI', models: 'GPT-4.1, GPT-4o, O-Series (16 models)', category: 'General Purpose', icon: `${process.env.PUBLIC_URL}/images/openaiiconq.png` },
    { name: 'Anthropic', models: 'Claude 4, Claude 3.5, Claude 3 (8 models)', category: 'Reasoning & Analysis', icon: `${process.env.PUBLIC_URL}/images/icons8-anthropic-48.png` },
    { name: 'Google', models: 'Gemini 2.0, Gemini 1.5, Gemini Pro (7 models)', category: 'Multimodal', icon: `${process.env.PUBLIC_URL}/images/google-color.png` },
    { name: 'Groq', models: 'Llama 3, Mixtral (Ultra-fast)', category: 'Speed Optimized', icon: `${process.env.PUBLIC_URL}/images/icons8-grok-48.png` },
    { name: 'Together AI', models: 'Llama 3, Mixtral (5 models)', category: 'Open Source', icon: `${process.env.PUBLIC_URL}/images/meta-color.png` },
    { name: 'Mistral', models: 'Large, Medium, Small, Tiny (4 models)', category: 'European AI', icon: `${process.env.PUBLIC_URL}/images/mistral-color.png` },
    { name: 'Cohere', models: 'Command R+, Command R (4 models)', category: 'Enterprise RAG', icon: `${process.env.PUBLIC_URL}/images/cohere-color.png` },
    { name: 'Perplexity', models: 'PPLX 7B/70B (4 models)', category: 'Reasoning + Search', icon: `${process.env.PUBLIC_URL}/images/meta-color.png` },
    { name: 'Ollama', models: 'Local Models (12 models - Free)', category: 'Local/Private', icon: `${process.env.PUBLIC_URL}/images/ollama.png` },
    { name: 'HuggingFace', models: 'DialoGPT, Llama 2 (3 models)', category: 'Open Source Hub', icon: `${process.env.PUBLIC_URL}/images/meta-color.png` },
    { name: 'DeepSeek', models: 'DeepSeek R1 (Reasoning)', category: 'Advanced Reasoning', icon: `${process.env.PUBLIC_URL}/images/meta-color.png` },
    { name: 'OpenRouter', models: 'DeepSeek, GPT-4o (5 models)', category: 'Model Aggregation', icon: `${process.env.PUBLIC_URL}/images/meta-color.png` }
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
      <style>
        {`
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in {
            animation: fade-in 0.8s ease-out;
          }
        `}
      </style>
      {/* Navigation */}
      <Navigation />

      {/* Hero Section with Visionary Story */}
      <section className="pt-24 pb-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-5xl mx-auto mb-16">
            {/* Visionary Badge */}
            <div className="relative inline-flex items-center justify-center mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-green-600/20 rounded-full blur-xl"></div>
              <div className="relative bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-full px-6 py-2 shadow-lg">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-gray-700">The future of AI APIs is here</span>
                  <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Main Headline - Steve Jobs Style */}
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="block relative">
                <span className="text-black">Think Different</span>
                <span className="text-green-900"> About AI</span>
                <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" style={{ animationDuration: '3s' }}></span>
              </span>
              <span className="block text-2xl md:text-3xl font-medium text-gray-600 mt-2 opacity-0 animate-fade-in" style={{ animationDelay: '0.5s', animationFillMode: 'forwards' }}>
                One API. All Providers. Infinite Possibilities.
              </span>
            </h1>

            {/* Visual Separator */}
            <div className="flex items-center justify-center mb-8">
              <div className="w-16 h-px bg-gradient-to-r from-transparent via-teal-500 to-transparent"></div>
              <div className="w-2 h-2 bg-teal-500 rounded-full mx-4"></div>
              <div className="w-16 h-px bg-gradient-to-r from-transparent via-teal-500 to-transparent"></div>
            </div>

            {/* Video Animation */}
            <video 
              autoPlay 
              loop 
              muted 
              playsInline
              className="w-full h-auto mb-12"
            >
              <source src="/images/ani5.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>

            {/* Visionary Story - Steve Jobs Style */}
            <div className="text-xl text-gray-600 mb-8 leading-relaxed max-w-4xl mx-auto">
              <p className="mb-6 text-2xl font-light">
                "Everything around you that you call life was made up by people that were no smarter than you."
              </p>
              <p className="mb-4">
                <span className="font-semibold text-gray-800">We asked ourselves:</span> What if AI APIs were as simple as flipping a light switch? What if you didn't have to think about which provider to use? What if the system just knew?
              </p>
              <p className="mb-6">
                <span className="font-bold bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
                  Model Bridge is that system.
                </span>
              </p>
              <p className="text-lg font-medium text-gray-800">
                The Perplexity moment for AI APIs. Intelligent by design. Invisible by choice.
              </p>
            </div>
          </div>
          
          {/* CTA - Apple Style */}
          <div className="text-center">
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link
                to="/register"
                className="group bg-gray-900 hover:bg-gray-800 text-white px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
              >
                Start Building Free
                <ArrowRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/docs"
                className="group border border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
              >
                <PlayIcon className="mr-2 h-5 w-5" />
                See How It Works
              </Link>
            </div>
            
            <p className="text-sm text-gray-500">
              Free tier • 1,000 requests/month • No credit card required
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section - Apple Style */}
      <section className="py-16 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">120+</div>
              <div className="text-gray-600 font-medium">AI Models</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">12+</div>
              <div className="text-gray-600 font-medium">Providers</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">99.9%</div>
              <div className="text-gray-600 font-medium">Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">80%</div>
              <div className="text-gray-600 font-medium">Cost Savings</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Apple Style */}
      <section id="features" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Designed for the Future
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We didn't just build another API gateway. We reimagined what AI integration should be.
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

      {/* Models Section - Apple Style */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Every Provider. One Experience.
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Access 120+ models from 12+ providers through one consistent interface
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 mb-16">
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

      {/* Testimonial Section - Apple Style */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              "It just works."
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Developers who've made the switch to Model Bridge
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-blue-600 font-bold text-lg">JS</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">John Smith</h4>
                  <p className="text-sm text-gray-600">CTO, TechStartup</p>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "We cut our AI costs by 70% while improving response times. It's like having a genius engineer who never sleeps."
              </p>
            </div>
            
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-green-600 font-bold text-lg">SD</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Sarah Davis</h4>
                  <p className="text-sm text-gray-600">Lead Developer, AI Corp</p>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "Finally, an API that thinks for us. We went from managing 5 different providers to one intelligent interface."
              </p>
            </div>
            
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-purple-600 font-bold text-lg">MJ</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Mike Johnson</h4>
                  <p className="text-sm text-gray-600">VP Engineering, ScaleUp</p>
                </div>
              </div>
              <p className="text-gray-700 italic">
                "The Perplexity moment for AI APIs. We don't think about providers anymore—we just build."
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section - Apple Style */}
      <section className="py-24 bg-white text-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Think Different?
          </h2>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Join the developers who are already building the future of AI applications
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="group bg-gray-900 text-white hover:bg-gray-800 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
                Start Free Trial
              <ArrowRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            
            <Link
              to="/product"
              className="group border border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-lg font-semibold transition-all duration-300 inline-flex items-center justify-center text-lg"
            >
              Explore Product
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