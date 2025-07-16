import React from 'react';

const Debug = () => {
  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Debug Page
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          This is a simple debug page to test routing
        </p>
        <div className="bg-green-100 p-4 rounded-lg">
          <p className="text-green-800">✅ React is working</p>
          <p className="text-green-800">✅ Routing is working</p>
          <p className="text-green-800">✅ Components are rendering</p>
        </div>
      </div>
    </div>
  );
};

export default Debug;