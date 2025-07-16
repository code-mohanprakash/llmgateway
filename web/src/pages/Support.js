import React from 'react';
import { 
  ChatBubbleLeftRightIcon,
  EnvelopeIcon,
  PhoneIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  UserGroupIcon,
  CogIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const Support = () => {
  const supportChannels = [
    {
      title: "Email Support",
      description: "Get help via email with detailed responses within 24 hours",
      icon: EnvelopeIcon,
      responseTime: "24 hours",
      availability: "24/7",
      color: "blue",
      action: "Send Email",
      href: "mailto:support@modelbridge.com"
    },
    {
      title: "Live Chat",
      description: "Real-time support from our technical team",
      icon: ChatBubbleLeftRightIcon,
      responseTime: "Instant",
      availability: "9 AM - 6 PM EST",
      color: "green",
      action: "Start Chat",
      href: "#chat"
    },
    {
      title: "Phone Support",
      description: "Speak directly with our support team",
      icon: PhoneIcon,
      responseTime: "Immediate",
      availability: "9 AM - 6 PM EST",
      color: "purple",
      action: "Call Now",
      href: "tel:+1-555-0123"
    }
  ];

  const faqs = [
    {
      question: "How do I get started with Model Bridge?",
      answer: "Sign up for a free account, generate an API key, and make your first request. Check out our Getting Started guide for detailed instructions.",
      category: "Getting Started"
    },
    {
      question: "What models are available?",
      answer: "We support 50+ models from leading providers including OpenAI, Anthropic, Google, and many others. View our complete model list.",
      category: "Models"
    },
    {
      question: "How does billing work?",
      answer: "We charge based on token usage with transparent pricing. Free tier includes 1,000 tokens per month. View our pricing page for details.",
      category: "Billing"
    },
    {
      question: "What's the difference between free and paid plans?",
      answer: "Free plans have limited access to basic models. Paid plans unlock premium models, higher rate limits, and advanced features.",
      category: "Plans"
    },
    {
      question: "How do I handle API errors?",
      answer: "Implement proper error handling with retry logic. Check our Error Handling guide for best practices and code examples.",
      category: "Technical"
    },
    {
      question: "Can I use Model Bridge in production?",
      answer: "Yes! We provide 99.9% uptime SLA for paid plans. Follow our Production Deployment guide for best practices.",
      category: "Production"
    }
  ];

  const resources = [
    {
      title: "Documentation",
      description: "Complete API reference and guides",
      icon: DocumentTextIcon,
      href: "/docs"
    },
    {
      title: "API Reference",
      description: "Detailed endpoint documentation",
      icon: CogIcon,
      href: "/api-reference"
    },
    {
      title: "Guides & Tutorials",
      description: "Step-by-step tutorials and examples",
      icon: AcademicCapIcon,
      href: "/guides"
    },
    {
      title: "Community Forum",
      description: "Connect with other developers",
      icon: UserGroupIcon,
      href: "#community"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
            Support Center
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We're here to help you succeed with Model Bridge. Choose the support channel that works best for you.
          </p>
        </div>

        {/* Support Channels */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Get Help</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {supportChannels.map((channel, index) => (
              <div 
                key={index}
                className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white"
              >
                <div className={`w-12 h-12 bg-gradient-to-br from-${channel.color}-100 to-${channel.color}-200 rounded-lg flex items-center justify-center mb-4`}>
                  <channel.icon className={`h-6 w-6 text-${channel.color}-600`} />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{channel.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{channel.description}</p>
                
                <div className="space-y-2 mb-6">
                  <div className="flex items-center text-sm">
                    <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">Response: {channel.responseTime}</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <CheckCircleIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">Available: {channel.availability}</span>
                  </div>
                </div>
                
                <a
                  href={channel.href}
                  className={`inline-flex items-center px-4 py-2 bg-${channel.color}-600 text-white rounded-lg hover:bg-${channel.color}-700 transition-colors duration-200 text-sm font-medium`}
                >
                  {channel.action}
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h2>
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {faqs.map((faq, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <InformationCircleIcon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">{faq.question}</h3>
                      <p className="text-sm text-gray-600 leading-relaxed">{faq.answer}</p>
                      <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                        {faq.category}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resources Section */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Helpful Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {resources.map((resource, index) => (
              <a
                key={index}
                href={resource.href}
                className="group border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-[#9B5967]/10 to-[#8a4d5a]/10 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <resource.icon className="h-6 w-6 text-[#9B5967]" />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-[#9B5967] transition-colors duration-300">
                  {resource.title}
                </h3>
                
                <p className="text-gray-600 text-sm leading-relaxed">
                  {resource.description}
                </p>
              </a>
            ))}
          </div>
        </div>

        {/* Contact Form */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-gray-50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Still Need Help?</h2>
            <p className="text-gray-600 mb-6 text-center">
              Can't find what you're looking for? Send us a message and we'll get back to you as soon as possible.
            </p>
            
            <form className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent"
                    placeholder="Enter your first name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent"
                    placeholder="Enter your last name"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent"
                  placeholder="Enter your email"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent">
                  <option>General Inquiry</option>
                  <option>Technical Support</option>
                  <option>Billing Question</option>
                  <option>Feature Request</option>
                  <option>Bug Report</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                <textarea
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent"
                  placeholder="Describe your issue or question..."
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-[#9B5967] text-white py-3 px-6 rounded-lg font-semibold hover:bg-[#8a4d5a] transition-colors duration-200"
              >
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Support; 