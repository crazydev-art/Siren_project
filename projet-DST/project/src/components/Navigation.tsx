import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Map, Home } from 'lucide-react';

const Navigation = () => {
  const linkClasses = "flex items-center px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors";
  const activeLinkClasses = "text-blue-600 font-medium";

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link 
            to="/" 
            className="flex items-center space-x-2 cursor-pointer hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl font-bold">LocaNova</span>
          </Link>
          
          <div className="flex space-x-4">
            <Link to="/map" className="text-gray-700 hover:text-blue-600">
              Carte
            </Link>
            <Link to="/search" className="text-gray-700 hover:text-blue-600">
              Recherche
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;