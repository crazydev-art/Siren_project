import React, { useState } from 'react';
import { Search, MapPin } from 'lucide-react';

export default function MapPage() {
  const [activityCode, setActivityCode] = useState('');
  const [radius, setRadius] = useState('10');

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Carte Interactive des Entreprises</h2>
        <p className="text-gray-600">
          Visualisez les entreprises par secteur d'activité dans votre région.
        </p>
      </div>

      {/* Search Controls */}
      <div className="bg-white p-6 rounded-xl shadow-md">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code APE/NAF
            </label>
            <div className="relative">
              <input
                type="text"
                className="w-full px-4 py-2 pl-10 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ex: 6201Z"
                value={activityCode}
                onChange={(e) => setActivityCode(e.target.value)}
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rayon de recherche (km)
            </label>
            <select
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={radius}
              onChange={(e) => setRadius(e.target.value)}
            >
              <option value="5">5 km</option>
              <option value="10">10 km</option>
              <option value="20">20 km</option>
              <option value="50">50 km</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Rechercher
            </button>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="h-[600px] bg-gray-100 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              Sélectionnez un code APE/NAF pour afficher les entreprises sur la carte
            </p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white p-4 rounded-xl shadow-md">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Légende</h3>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">TPE (0-9)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">PME (10-249)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">ETI (250-4999)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">GE (5000+)</span>
          </div>
        </div>
      </div>
    </div>
  );
}