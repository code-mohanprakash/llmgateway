import React from 'react';
import { 
  BookOpenIcon,
  CodeBracketIcon,
  PlayIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ChevronRightIcon,
  StarIcon,
  BoltIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CogIcon,
  ServerIcon,
  GlobeAltIcon,
  LightBulbIcon,
  AcademicCapIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const Guides = () => {
  const guides = [
    {
      title: "Getting Started",
      description: "Learn the basics of Model Bridge and make your first API call",
      icon: RocketLaunchIcon,
      difficulty: "Beginner",
      time: "5 min read",
      category: "Basics"
    },
    {
      title: "Authentication & API Keys",
      description: "Set up authentication and manage your API keys securely",
      icon: ShieldCheckIcon,
      difficulty: "Beginner",
      time: "3 min read",
      category: "Security"
    },
    {
      title: "Model Selection & Routing",
      description: "Choose the right model for your use case and understand intelligent routing",
      icon: LightBulbIcon,
      difficulty: "Intermediate",
      time: "8 min read",
      category: "Advanced"
    },
    {
      title: "Error Handling & Retries",
      description: "Implement robust error handling and automatic retry logic",
      icon: ExclamationTriangleIcon,
      difficulty: "Intermediate",
      time: "6 min read",
      category: "Best Practices"
    },
    {
      title: "Streaming Responses",
      description: "Implement real-time streaming for better user experience",
      icon: BoltIcon,
      difficulty: "Intermediate",
      time: "7 min read",
      category: "Advanced"
    },
    {
      title: "Cost Optimization",
      description: "Optimize your API usage to minimize costs while maintaining quality",
      icon: ChartBarIcon,
      difficulty: "Advanced",
      time: "10 min read",
      category: "Optimization"
    },
    {
      title: "Production Deployment",
      description: "Deploy Model Bridge in production with best practices",
      icon: ServerIcon,
      difficulty: "Advanced",
      time: "12 min read",
      category: "Production"
    },
    {
      title: "Integration Examples",
      description: "Real-world examples of integrating Model Bridge into applications",
      icon: CodeBracketIcon,
      difficulty: "Intermediate",
      time: "15 min read",
      category: "Examples"
    }
  ];

  const categories = [
    { name: "All", count: guides.length },
    { name: "Basics", count: guides.filter(g => g.category === "Basics").length },
    { name: "Security", count: guides.filter(g => g.category === "Security").length },
    { name: "Advanced", count: guides.filter(g => g.category === "Advanced").length },
    { name: "Best Practices", count: guides.filter(g => g.category === "Best Practices").length },
    { name: "Optimization", count: guides.filter(g => g.category === "Optimization").length },
    { name: "Production", count: guides.filter(g => g.category === "Production").length },
    { name: "Examples", count: guides.filter(g => g.category === "Examples").length }
  ];

  const [selectedCategory, setSelectedCategory] = React.useState("All");

  const filteredGuides = selectedCategory === "All" 
    ? guides 
    : guides.filter(guide => guide.category === selectedCategory);

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "Beginner": return "bg-green-100 text-green-800";
      case "Intermediate": return "bg-yellow-100 text-yellow-800";
      case "Advanced": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
            Guides & Tutorials
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Learn how to use Model Bridge effectively with our comprehensive guides and tutorials
          </p>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {categories.map((category) => (
              <button
                key={category.name}
                onClick={() => setSelectedCategory(category.name)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  selectedCategory === category.name
                    ? 'bg-[#000000] text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.name} ({category.count})
              </button>
            ))}
          </div>
        </div>

        {/* Guides Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredGuides.map((guide, index) => (
            <div 
              key={index}
              className="group border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-[#000000]/10 to-[#14213d]/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <guide.icon className="h-6 w-6 text-[#000000]" />
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(guide.difficulty)}`}>
                    {guide.difficulty}
                  </span>
                </div>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-[#000000] transition-colors duration-300">
                {guide.title}
              </h3>
              
              <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                {guide.description}
              </p>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{guide.time}</span>
                <div className="flex items-center text-[#000000] text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  Read guide
                  <ChevronRightIcon className="ml-1 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Featured Guide */}
        <div className="mt-16">
          <div className="bg-gradient-to-br from-[#000000] to-[#14213d] rounded-2xl p-8 text-white">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center mb-4">
                <StarIcon className="h-6 w-6 mr-2" />
                <span className="text-sm font-medium">Featured Guide</span>
              </div>
              
              <h2 className="text-3xl font-bold mb-4">
                Complete Model Bridge Integration
              </h2>
              
              <p className="text-lg text-white/90 mb-6 leading-relaxed">
                A comprehensive guide covering everything from initial setup to production deployment. 
                Learn best practices, optimization techniques, and real-world examples.
              </p>
              
              <div className="flex items-center space-x-6 text-sm">
                <span className="flex items-center">
                  <AcademicCapIcon className="h-4 w-4 mr-1" />
                  Advanced
                </span>
                <span className="flex items-center">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  25 min read
                </span>
                <span className="flex items-center">
                  <CodeBracketIcon className="h-4 w-4 mr-1" />
                  Code examples included
                </span>
              </div>
              
              <button className="mt-6 bg-white text-[#000000] px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200 flex items-center">
                Read Complete Guide
                <ChevronRightIcon className="ml-2 h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Quick Start Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-gray-200 rounded-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">1️⃣</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Get API Key</h3>
              <p className="text-gray-600 text-sm">
                Sign up for a free account and generate your first API key
              </p>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">2️⃣</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Make First Request</h3>
              <p className="text-gray-600 text-sm">
                Use our SDK or make a direct API call to test the integration
              </p>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">3️⃣</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Deploy to Production</h3>
              <p className="text-gray-600 text-sm">
                Follow our production deployment guide for best practices
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Guides; 