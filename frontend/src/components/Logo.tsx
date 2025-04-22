import React from 'react';
import { BookOpenText } from 'lucide-react';

const Logo: React.FC = () => {
  return (
    <div className="flex items-center justify-center group">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-violet-600 rounded-xl blur-xl opacity-75 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="relative bg-gradient-to-r from-blue-600 to-violet-600 p-3 rounded-xl shadow-glow transform transition-all duration-500 group-hover:scale-105">
          <BookOpenText size={36} className="text-white transform transition-transform duration-500 group-hover:rotate-12" />
        </div>
      </div>
      <h1 className="text-3xl md:text-4xl font-bold ml-3 bg-gradient-to-r from-blue-600 via-violet-600 to-purple-600 bg-clip-text text-transparent transform transition-all duration-500 group-hover:scale-105">
        TitleTrail
      </h1>
    </div>
  );
};

export default Logo;