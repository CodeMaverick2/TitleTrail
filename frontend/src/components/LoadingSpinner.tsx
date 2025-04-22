import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'blue' | 'white' | 'gray';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = 'blue' 
}) => {
  const sizeClass = {
    small: 'w-5 h-5',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  }[size];

  const colorClass = {
    blue: 'text-primary-600',
    white: 'text-white',
    gray: 'text-gray-600',
  }[color];

  return (
    <div className="flex justify-center items-center">
      <div className={`
        animate-spin rounded-full
        border-t-2 border-b-2 border-current
        ${colorClass} ${sizeClass}
        relative
      `}>
        <div className="absolute inset-0 border-t-2 border-current opacity-20 rounded-full"></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;