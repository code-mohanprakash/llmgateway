import React from 'react';
import { 
  UserGroupIcon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  HeartIcon,
  StarIcon,
  BoltIcon,
  CogIcon,
  ChartBarIcon,
  AcademicCapIcon,
  LightBulbIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const About = () => {
  const stats = [
    { label: "Models Supported", value: "80+", icon: CogIcon },
    { label: "Providers", value: "12+", icon: BoltIcon },
    { label: "Advanced Routing", value: "Phase 1", icon: LightBulbIcon },
    { label: "Open Source", value: "Yes", icon: ShieldCheckIcon }
  ];

  const values = [
    {
      title: "Developer First",
      description: "We believe AI should be accessible to every developer, regardless of their resources or expertise.",
      icon: AcademicCapIcon,
      color: "blue"
    },
    {
      title: "Open & Transparent",
      description: "Building an open platform that gives developers choice and control over their AI infrastructure.",
      icon: ShieldCheckIcon,
      color: "green"
    },
    {
      title: "Innovation Driven",
      description: "Continuously exploring new ways to make AI integration simpler and more powerful.",
      icon: RocketLaunchIcon,
      color: "purple"
    },
    {
      title: "Community Focused",
      description: "Building with and for the developer community, sharing knowledge and best practices.",
      icon: UserGroupIcon,
      color: "orange"
    }
  ];

  const team = [
    {
      name: "Mohan Prakash",
      role: "Founder & Data Scientist",
      bio: "Passionate about democratizing AI and making it accessible to developers worldwide. Experienced in machine learning, data science, and building scalable AI infrastructure.",
      image: "👨‍💻",
      background: "Data Scientist with expertise in LLMs, MLOps, and AI infrastructure"
    }
  ];

  const timeline = [
    {
      year: "2025",
      title: "Latest Model Integration",
      description: "Added support for Claude 4 series, GPT-4.1, o3/o4-mini reasoning models, and Gemini 2.0 series with dynamic model discovery"
    },
    {
      year: "2024",
      title: "Production Launch",
      description: "Launched production-ready platform with advanced routing, enterprise features, and comprehensive security"
    },
    {
      year: "2024",
      title: "Advanced Routing Engine",
      description: "Developed intelligent routing with real-time load balancing, predictive analytics, and geographic optimization"
    },
    {
      year: "2024",
      title: "Model Bridge Development",
      description: "Started building Model Bridge to solve the fragmentation problem in AI model access"
    },
    {
      year: "2023",
      title: "Problem Identified",
      description: "Recognized the need for a unified API to access multiple AI providers"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-6">
            About Model Bridge
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            We're solving a real problem: the fragmentation of AI model access. 
            Every developer deserves simple, unified access to the world's best AI models.
          </p>
        </div>

        {/* Problem Section */}
        <div className="mb-16">
          <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-2xl p-8 border border-red-200">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center mb-6">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600 mr-3" />
                <h2 className="text-3xl font-bold text-red-900">The Problem We're Solving</h2>
              </div>
              <p className="text-lg text-red-800 mb-6 leading-relaxed">
                As AI adoption grows, developers face a fragmented landscape. Each AI provider has different APIs, 
                authentication methods, rate limits, and pricing models. This creates:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg p-4 border border-red-200">
                  <h3 className="font-semibold text-red-900 mb-2">Complex Integration</h3>
                  <p className="text-red-700 text-sm">Managing multiple API keys, endpoints, and SDKs</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-200">
                  <h3 className="font-semibold text-red-900 mb-2">Vendor Lock-in</h3>
                  <p className="text-red-700 text-sm">Difficult to switch between providers or compare models</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-200">
                  <h3 className="font-semibold text-red-900 mb-2">Inconsistent Experience</h3>
                  <p className="text-red-700 text-sm">Different error handling, response formats, and features</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Solution Section */}
        <div className="mb-16">
          <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-8 border border-green-200">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center mb-6">
                <LightBulbIcon className="h-8 w-8 text-green-600 mr-3" />
                <h2 className="text-3xl font-bold text-green-900">Our Solution</h2>
              </div>
              <p className="text-lg text-green-800 mb-6 leading-relaxed">
                Model Bridge provides a unified API that abstracts away the complexity of multiple AI providers. 
                One API key, one endpoint, access to all models.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <h3 className="font-semibold text-green-900 mb-2">Unified API</h3>
                  <p className="text-green-700 text-sm">Single interface for all AI providers</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <h3 className="font-semibold text-green-900 mb-2">Intelligent Routing</h3>
                  <p className="text-green-700 text-sm">Automatic model selection based on your needs</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <h3 className="font-semibold text-green-900 mb-2">Cost Optimization</h3>
                  <p className="text-green-700 text-sm">Route to the most cost-effective model for your use case</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mb-16">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-[#000000]/10 to-[#14213d]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <stat.icon className="h-8 w-8 text-[#000000]" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Values Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Our Values</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {values.map((value, index) => (
              <div key={index} className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <div className={`w-12 h-12 bg-gradient-to-br from-${value.color}-100 to-${value.color}-200 rounded-lg flex items-center justify-center mb-4`}>
                  <value.icon className={`h-6 w-6 text-${value.color}-600`} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{value.title}</h3>
                <p className="text-gray-600 leading-relaxed">{value.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Team Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Meet Our Team</h2>
          <div className="max-w-2xl mx-auto">
            {team.map((member, index) => (
              <div key={index} className="text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-[#000000]/10 to-[#14213d]/10 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl">
                  {member.image}
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">{member.name}</h3>
                <p className="text-[#000000] font-medium mb-4">{member.role}</p>
                <p className="text-gray-600 mb-4 leading-relaxed">{member.bio}</p>
                <p className="text-sm text-gray-500 italic">{member.background}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Timeline Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Our Journey</h2>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {timeline.map((item, index) => (
                <div key={index} className="flex items-start space-x-6">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-[#000000] to-[#14213d] rounded-full flex items-center justify-center text-white font-bold">
                      {item.year}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Development Status */}
        <div className="mb-16">
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-8">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">🚧 Currently in Development</h2>
              <p className="text-blue-800 mb-6 leading-relaxed">
                Model Bridge is actively being built. We're starting with core functionality and will 
                gradually add more providers, features, and capabilities. This is a passion project 
                born from real developer pain points.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Phase 1</h4>
                  <p className="text-blue-700">Core API and basic provider integration</p>
                </div>
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Phase 2</h4>
                  <p className="text-blue-700">Intelligent routing and cost optimization</p>
                </div>
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Phase 3</h4>
                  <p className="text-blue-700">Advanced features and enterprise capabilities</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="bg-gray-50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Join Us in Building the Future</h2>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Whether you're a developer looking to integrate AI into your applications, 
              or someone who believes in making AI more accessible, we'd love to hear from you.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/docs"
                className="bg-[#000000] text-white px-8 py-3 rounded-lg font-semibold hover:bg-[#14213d] transition-colors duration-200"
              >
                Read Documentation
              </a>
              <a
                href="/contact"
                className="border border-[#000000] text-[#000000] px-8 py-3 rounded-lg font-semibold hover:bg-[#000000] hover:text-white transition-colors duration-200"
              >
                Get in Touch
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About; 