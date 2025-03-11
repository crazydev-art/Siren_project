import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Building } from 'lucide-react';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import SearchResultsPage from './pages/SearchResultsPage';
import MapPage from "./components/Map";


function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <Building className="h-8 w-8 text-blue-600" />
                <h1 className="ml-2 text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  LocaNova
                </h1>
              </div>
              <nav className="hidden md:flex space-x-8">
                <a href="/" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Accueil
                </a>
                <a href="/search" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Recherche
                </a>
                <a href="/map" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Carte
                </a>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/results" element={<SearchResultsPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="text-center text-gray-600">
              <p>Analyse des entreprises d'Île-de-France © 2025</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
