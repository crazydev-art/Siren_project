import React from 'react';
import { NavLink } from 'react-router-dom';
import { Search, Map, Home } from 'lucide-react';

export default function Navigation() {
  const linkClasses = "flex items-center px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors";
  const activeLinkClasses = "text-blue-600 font-medium";

  return (
    <nav className="flex items-center space-x-4">
      <NavLink 
        to="/" 
        className={({ isActive }) => `${linkClasses} ${isActive ? activeLinkClasses : ''}`}
      >
        <Home className="w-5 h-5 mr-2" />
        Accueil
      </NavLink>
      <NavLink 
        to="/search" 
        className={({ isActive }) => `${linkClasses} ${isActive ? activeLinkClasses : ''}`}
      >
        <Search className="w-5 h-5 mr-2" />
        Recherche
      </NavLink>
      <NavLink 
        to="/map" 
        className={({ isActive }) => `${linkClasses} ${isActive ? activeLinkClasses : ''}`}
      >
        <Map className="w-5 h-5 mr-2" />
        Carte
      </NavLink>
    </nav>
  );
}