import React from 'react';
import { 
  UserGroupIcon,
  RocketLaunchIcon,
  MapPinIcon,
  ClockIcon,
  CurrencyDollarIcon,
  LightBulbIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

const Careers = () => {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Simple Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Careers
          </h1>
          <p className="text-lg text-gray-600">
            Join our team and help build the future of AI infrastructure
          </p>
        </div>

        {/* Single Job Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-[#9B5967] to-[#8a4d5a] rounded-lg flex items-center justify-center mx-auto mb-4">
              <LightBulbIcon className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Founding Engineer</h2>
            <p className="text-[#9B5967] font-medium">Model Bridge</p>
          </div>

          {/* Job Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="flex items-center justify-center">
              <MapPinIcon className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-gray-600">Remote</span>
            </div>
            <div className="flex items-center justify-center">
              <ClockIcon className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-gray-600">Full-time</span>
            </div>
            <div className="flex items-center justify-center">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-gray-600">Competitive + Equity</span>
            </div>
          </div>

          {/* Description */}
          <div className="text-center mb-8">
            <p className="text-gray-700 leading-relaxed max-w-2xl mx-auto">
              We're looking for a founding engineer with strong AI and development experience 
              to help build our unified AI API platform. You'll work directly with the founder 
              to architect and implement core infrastructure.
            </p>
          </div>

          {/* Requirements */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">Requirements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-start">
                  <span className="text-[#9B5967] mr-2 mt-1">•</span>
                  <span className="text-gray-700">Strong Python and FastAPI experience</span>
                </div>
                <div className="flex items-start">
                  <span className="text-[#9B5967] mr-2 mt-1">•</span>
                  <span className="text-gray-700">Deep understanding of AI/ML infrastructure</span>
                </div>
                <div className="flex items-start">
                  <span className="text-[#9B5967] mr-2 mt-1">•</span>
                  <span className="text-gray-700">Experience with cloud platforms (AWS/GCP/Azure)</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-start">
                  <span className="text-[#9B5967] mr-2 mt-1">•</span>
                  <span className="text-gray-700">Knowledge of LLM architectures and models</span>
                </div>
                <div className="flex items-start">
                  <span className="text-[#9B5967] mr-2 mt-1">•</span>
                  <span className="text-gray-700">Experience with API design and authentication</span>
                </div>
                <div className="flex items-start">
                  <span className="text-[#9B5967] mr-2 mt-1">•</span>
                  <span className="text-gray-700">Strong problem-solving skills</span>
                </div>
              </div>
            </div>
          </div>

          {/* Apply Button */}
          <div className="text-center">
            <button className="bg-[#9B5967] text-white px-8 py-3 rounded-lg font-semibold hover:bg-[#8a4d5a] transition-colors duration-200">
              Apply Now
            </button>
          </div>
        </div>

        {/* Simple Benefits */}
        <div className="mt-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">Benefits</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <GlobeAltIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Remote Work</h4>
              <p className="text-sm text-gray-600">Work from anywhere</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Competitive Pay</h4>
              <p className="text-sm text-gray-600">Salary + equity</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <RocketLaunchIcon className="h-6 w-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Fast Growth</h4>
              <p className="text-sm text-gray-600">Join early stage</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Careers; 