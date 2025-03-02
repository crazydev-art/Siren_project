import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search as SearchIcon, MapPin, Building2, Briefcase } from 'lucide-react';
import type { SearchFilters } from '../types/company';

export default function SearchPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    type: 'name'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/results', { state: { filters } });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Recherche Approfondie</h2>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Main Search */}
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-xl font-semibold mb-4">Critères Principaux</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type de recherche
              </label>
              <select
                className="w-full rounded-lg border border-gray-300 p-3"
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value as 'siren' | 'name' | 'activity' })}
              >
                <option value="name">Nom d'entreprise</option>
                <option value="siren">SIREN/SIRET</option>
                <option value="activity">Code APE/NAF</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recherche
              </label>
              <div className="relative">
                <input
                  type="text"
                  className="w-full px-4 py-3 pl-12 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Entrez votre recherche..."
                  value={filters.query}
                  onChange={(e) => setFilters({ ...filters, query: e.target.value })}
                />
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              </div>
            </div>
          </div>
        </div>

        {/* Additional Filters */}
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-xl font-semibold mb-4">Filtres Additionnels</h3>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Location */}
            <div className="space-y-4">
              <h4 className="flex items-center text-lg font-medium text-gray-800">
                <MapPin className="w-5 h-5 mr-2" />
                Localisation
              </h4>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Région
                </label>
                <select
                  className="w-full rounded-md border border-gray-300 p-2"
                  value={filters.region}
                  onChange={(e) => setFilters({ ...filters, region: e.target.value })}
                >
                  <option value="">Toutes les régions</option>
                  <option value="IDF">Île-de-France</option>
                  <option value="AURA">Auvergne-Rhône-Alpes</option>
                  <option value="PACA">Provence-Alpes-Côte d'Azur</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Département
                </label>
                <input
                  type="text"
                  className="w-full rounded-md border border-gray-300 p-2"
                  placeholder="Numéro du département"
                  value={filters.department}
                  onChange={(e) => setFilters({ ...filters, department: e.target.value })}
                />
              </div>
            </div>

            {/* Company Details */}
            <div className="space-y-4">
              <h4 className="flex items-center text-lg font-medium text-gray-800">
                <Building2 className="w-5 h-5 mr-2" />
                Caractéristiques
              </h4>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Taille de l'entreprise
                </label>
                <select
                  className="w-full rounded-md border border-gray-300 p-2"
                  value={filters.size}
                  onChange={(e) => setFilters({ ...filters, size: e.target.value })}
                >
                  <option value="">Toutes les tailles</option>
                  <option value="TPE">TPE (0-9 employés)</option>
                  <option value="PME">PME (10-249 employés)</option>
                  <option value="ETI">ETI (250-4999 employés)</option>
                  <option value="GE">Grande Entreprise (5000+ employés)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Secteur d'activité
                </label>
                <input
                  type="text"
                  className="w-full rounded-md border border-gray-300 p-2"
                  placeholder="Code APE/NAF"
                  value={filters.activityCode}
                  onChange={(e) => setFilters({ ...filters, activityCode: e.target.value })}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Lancer la recherche
          </button>
        </div>
      </form>
    </div>
  );
}