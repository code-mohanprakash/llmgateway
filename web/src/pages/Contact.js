import React from 'react';
import { 
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  UserIcon,
  AcademicCapIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const Contact = () => {
  const contactMethods = [
    {
      title: "Email Support",
      description: "Get help with technical questions and API usage",
      icon: EnvelopeIcon,
      value: "mohanprakash462@gmail.com",
      responseTime: "24 hours",
      color: "blue"
    },
    {
      title: "GitHub Issues",
      description: "Report bugs and request features on our repository",
      icon: AcademicCapIcon,
      value: "github.com/modelbridge",
      responseTime: "48 hours",
      color: "green"
    },
    {
      title: "General Inquiries",
      description: "Questions about our project and development",
      icon: ChatBubbleLeftRightIcon,
      value: "mohanprakash462@gmail.com",
      responseTime: "24 hours",
      color: "purple"
    }
  ];



  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
            Contact Us
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Have questions about our shuttle-themed AI gateway? We're here to help with 
            technical support, feature requests, or general inquiries.
          </p>
        </div>

        {/* Contact Methods */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Get in Touch</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {contactMethods.map((method, index) => (
              <div 
                key={index}
                className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white"
              >
                <div className={`w-12 h-12 bg-gradient-to-br from-${method.color}-100 to-${method.color}-200 rounded-lg flex items-center justify-center mb-4`}>
                  <method.icon className={`h-6 w-6 text-${method.color}-600`} />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{method.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{method.description}</p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm">
                    <span className="text-gray-900 font-medium">{method.value}</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    Response time: {method.responseTime}
                  </div>
                </div>
                
                <a
                  href={method.title.includes("Email") ? `mailto:${method.value}` : `https://${method.value}`}
                  className={`inline-flex items-center px-4 py-2 bg-${method.color}-600 text-white rounded-lg hover:bg-${method.color}-700 transition-colors duration-200 text-sm font-medium`}
                >
                  Contact {method.title.split(" ")[0]}
                </a>
              </div>
            ))}
          </div>
        </div>



        {/* Contact Form */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-gray-50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Send us a Message</h2>
            <p className="text-gray-600 mb-8 text-center">
              Fill out the form below and we'll get back to you as soon as possible.
            </p>
            
            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                  placeholder="Enter your email address"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent">
                  <option>General Inquiry</option>
                  <option>Technical Support</option>
                  <option>Feature Request</option>
                  <option>Bug Report</option>
                  <option>Contribution</option>
                  <option>Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                <textarea
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#9B5967] focus:border-transparent"
                  placeholder="Tell us how we can help you..."
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="newsletter"
                  className="h-4 w-4 text-[#9B5967] focus:ring-[#9B5967] border-gray-300 rounded"
                />
                <label htmlFor="newsletter" className="ml-2 text-sm text-gray-600">
                  Subscribe to our newsletter for project updates and insights
                </label>
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

        {/* FAQ Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h2>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-4">
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Is this a real company?</h3>
                <p className="text-gray-600 text-sm">
                  No, this is a student project built for learning purposes. It demonstrates 
                  AI infrastructure concepts with a shuttle/space theme.
                </p>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Can I contribute to the project?</h3>
                <p className="text-gray-600 text-sm">
                  Yes! This is an open-source project and we welcome contributions, 
                  bug reports, and feature requests through GitHub.
                </p>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">What's the shuttle theme about?</h3>
                <p className="text-gray-600 text-sm">
                  The shuttle theme represents how our platform bridges different AI models, 
                  just like shuttles connect different destinations in space.
                </p>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Is the API functional?</h3>
                <p className="text-gray-600 text-sm">
                  The API is functional for demonstration purposes, but it's designed as a 
                  learning project rather than a production service.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact; 