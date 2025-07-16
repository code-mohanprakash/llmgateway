import React from 'react';

const BridgeAnimation = () => {
  return (
    <div className="relative mt-12 flex h-[400px] max-w-6xl mx-auto items-center justify-center p-10 bg-white">
      {/* Left Input Node - Computer Monitor */}
      <div className="absolute left-8 top-1/2 -translate-y-1/2 z-10">
        <div className="w-16 h-16 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <div className="relative">
            <svg className="w-8 h-8 text-gray-700" fill="currentColor" viewBox="0 0 24 24">
              <path d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7l-2 3v1h8v-1l-2-3h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H3V4h18v10z"/>
            </svg>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-gray-700 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* Center Bridge Node - Icon */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-5">
        <img 
          src={process.env.PUBLIC_URL + '/images/icon.png'}
          alt="Bridge Icon"
          className="w-80 h-80 object-contain"
        />
      </div>

      {/* Right Provider Nodes - Vertical Column */}
      <div className="absolute right-8 top-1/2 -translate-y-1/2 flex flex-col items-center justify-center gap-4 z-10">
        {/* 1. ChatGPT-like "C" icon */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">C</span>
          </div>
        </div>

        {/* 2. Reddish-brown asterisk/starburst */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <svg className="w-6 h-6 text-[#9B5967]" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        </div>

        {/* 3. Blue bar chart/building blocks */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
          </svg>
        </div>

        {/* 4. Black "XI" or "Xl" */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <span className="text-gray-700 font-bold text-sm">XI</span>
        </div>

        {/* 5. Three horizontal dots "..." */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <div className="flex space-x-1">
            <div className="w-1.5 h-1.5 bg-gray-600 rounded-full"></div>
            <div className="w-1.5 h-1.5 bg-gray-600 rounded-full"></div>
            <div className="w-1.5 h-1.5 bg-gray-600 rounded-full"></div>
          </div>
        </div>

        {/* 6. Blue hexagonal gear/snowflake */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>

        {/* 7. Question mark */}
        <div className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center">
          <span className="text-gray-700 font-bold text-lg">?</span>
        </div>
      </div>

      {/* Connection Lines */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 20 }}>
        <defs>
          <linearGradient id="mainLineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#000000" />
            <stop offset="100%" stopColor="#333333" />
          </linearGradient>
          <linearGradient id="fanGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#000000" />
            <stop offset="100%" stopColor="#333333" />
          </linearGradient>
          
          {/* Shining light effect */}
          <linearGradient id="shiningLight" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0">
              <animate attributeName="stop-opacity" values="0;1;0" dur="3s" repeatCount="indefinite" />
            </stop>
            <stop offset="50%" stopColor="#ffffff" stopOpacity="0">
              <animate attributeName="stop-opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="1.5s" />
            </stop>
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0">
              <animate attributeName="stop-opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="3s" />
            </stop>
          </linearGradient>
        </defs>
        
        {/* Main connection line from input to bridge center */}
        <line 
          x1="12%" 
          y1="50%" 
          x2="34%" 
          y2="50%" 
          stroke="url(#mainLineGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on main line */}
        <line 
          x1="12%" 
          y1="50%" 
          x2="34%" 
          y2="50%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.8"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2s" repeatCount="indefinite" />
        </line>
        
        {/* Additional line from computer to left side of bridge image */}
        <line 
          x1="12%" 
          y1="50%" 
          x2="37%" 
          y2="50%" 
          stroke="#000000" 
          strokeWidth="0.5"
          strokeDasharray="2,2"
          opacity="0.9"
        >
          <animate attributeName="stroke-dashoffset" values="0;6;0" dur="3s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on additional line */}
        <line 
          x1="12%" 
          y1="50%" 
          x2="37%" 
          y2="50%" 
          stroke="url(#shiningLight)" 
          strokeWidth="1.5"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;6;0" dur="3s" repeatCount="indefinite" />
        </line>
        
        {/* Fanning out lines from bridge center to providers */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="15%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.2s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 1 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="15%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.2s" repeatCount="indefinite" />
        </line>
        
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="25%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.4s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 2 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="25%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.4s" repeatCount="indefinite" />
        </line>
        
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="35%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.1s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 3 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="35%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.1s" repeatCount="indefinite" />
        </line>
        
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="45%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.3s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 4 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="45%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.3s" repeatCount="indefinite" />
        </line>
        
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="55%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 5 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="55%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2s" repeatCount="indefinite" />
        </line>
        
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="65%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.5s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 6 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="65%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="2.5s" repeatCount="indefinite" />
        </line>
        
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="75%" 
          stroke="url(#fanGradient)" 
          strokeWidth="1"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="1.9s" repeatCount="indefinite" />
        </line>
        
        {/* Shining light on fan line 7 */}
        <line 
          x1="66%" 
          y1="50%" 
          x2="82%" 
          y2="75%" 
          stroke="url(#shiningLight)" 
          strokeWidth="2"
          strokeDasharray="2,2"
          opacity="0.6"
        >
          <animate attributeName="stroke-dashoffset" values="0;4;0" dur="1.9s" repeatCount="indefinite" />
        </line>
      </svg>

      {/* Animated data flow dots */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 25 }}>
        {/* Main path dot */}
        <circle r="2" fill="#000000" opacity="0.7">
          <animateMotion dur="2s" repeatCount="indefinite" path="M 12% 50% L 34% 50%" />
        </circle>
        
        {/* Provider path dots with staggered timing */}
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="1.8s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="2.2s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="1.9s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="2.1s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="2s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="1.7s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
        <circle r="1.5" fill="#000000" opacity="0.5">
          <animateMotion dur="2.3s" repeatCount="indefinite" path="M 66% 50% L 82% 15%" />
        </circle>
      </svg>

      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px,rgb(201, 197, 198) 1px, transparent 0)`,
          backgroundSize: '20px 20px'
        }}></div>
      </div>
    </div>
  );
};

export default BridgeAnimation;