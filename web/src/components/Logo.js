import React from 'react';

const Logo = ({ 
  size = 'default', 
  showText = true, 
  className = '',
  onClick = null,
  variant = 'default' // 'default' or 'white'
}) => {
  const sizeClasses = {
    small: 'h-6 w-6',
    default: 'h-8 w-8',
    large: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  const textSizes = {
    small: 'text-sm',
    default: 'text-lg',
    large: 'text-xl',
    xl: 'text-2xl'
  };

  // Try multiple paths for the image
  const imagePaths = [
    '/images/modelbridge.png',
    process.env.PUBLIC_URL + '/images/modelbridge.png',
    './images/modelbridge.png'
  ];

  return (
    <div 
      className={`flex items-center space-x-2 ${className}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {/* Logo Image */}
      <img 
        src={imagePaths[0]}
        alt="Model Bridge Logo"
        className={`${sizeClasses[size]} flex-shrink-0 object-contain`}
        onError={(e) => {
          console.error('Failed to load logo image:', e.target.src);
          // Try fallback path
          if (e.target.src !== imagePaths[1]) {
            e.target.src = imagePaths[1];
          } else if (e.target.src !== imagePaths[2]) {
            e.target.src = imagePaths[2];
          }
        }}
        onLoad={() => {
          console.log('Logo image loaded successfully');
        }}
      />
      
      {/* Text */}
      {showText && (
        <h1 className={`font-bold tracking-tight whitespace-nowrap ${textSizes[size]} ${
          variant === 'white' ? 'text-white' : ''
        }`}>
          <span className={variant === 'white' ? 'text-white' : 'bg-gradient-to-r from-black via-gray-800 to-green-800 bg-clip-text text-transparent drop-shadow-sm'}>Model</span>
          <span className={variant === 'white' ? 'text-white' : 'bg-gradient-to-r from-green-800 via-gray-800 to-black bg-clip-text text-transparent drop-shadow-sm'}> Bridge</span>
        </h1>
      )}
    </div>
  );
};

export default Logo; 