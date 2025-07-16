import React from 'react';
import Logo from '../components/Logo';

const TestLanding = () => {
  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <div className="mb-4 flex justify-center">
          <Logo size="xl" showText={true} />
        </div>
        <p className="text-xl text-gray-600 mb-8">
          Enterprise-grade AI infrastructure for modern applications
        </p>
        <div className="space-x-4">
          <button className="bg-[#9B5967] text-white px-6 py-3 rounded-lg">
            Get Started
          </button>
          <button className="border border-[#9B5967] text-[#9B5967] px-6 py-3 rounded-lg">
            Learn More
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestLanding;