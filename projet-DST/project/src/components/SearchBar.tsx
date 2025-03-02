import React, { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import type { SearchFilters } from '../types/company';

interface SearchBarProps {
  onSearch: (filters: SearchFilters) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    type: 'name',
    region: 'Île-de-France' // Default to Île-de-France
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              className="w-full px-4 py-3 pl-12 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
              placeholder="Rechercher une entreprise..."
              value={filters.query}
              onChange={(e) => setFilters({ ...filters, query: e.target.value })}
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          </div>
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="p-3 rounded-xl border border-gray-300 hover:bg-gray-50 shadow-sm"
          >
            <Filter size={20} className="text-gray-600" />
          </button>
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Rechercher
          </button>
        </div>

        {showFilters && (
          <div className="absolute top-full mt-2 w-full bg-white rounded-xl border border-gray-200 shadow-xl p-6 z-10">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type de recherche
                </label>
                <select
                  className="w-full rounded-lg border border-gray-300 p-2 shadow-sm"
                  value={filters.type}
                  onChange={(e) => setFilters({ ...filters, type: e.target.value as 'siren' | 'name' | 'activity' })}
                >
                  <option value="name">Nom</option>
                  <option value="siren">SIREN/SIRET</option>
                  <option value="activity">Activité</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Département
                </label>
                <select
                  className="w-full rounded-lg border border-gray-300 p-2 shadow-sm"
                  value={filters.department}
                  onChange={(e) => setFilters({ ...filters, department: e.target.value })}
                >
                  <option value="">Tous les départements</option>
                  <option value="75">Paris (75)</option>
                  <option value="77">Seine-et-Marne (77)</option>
                  <option value="78">Yvelines (78)</option>
                  <option value="91">Essonne (91)</option>
                  <option value="92">Hauts-de-Seine (92)</option>
                  <option value="93">Seine-Saint-Denis (93)</option>
                  <option value="94">Val-de-Marne (94)</option>
                  <option value="95">Val-d'Oise (95)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Taille
                </label>
                <select
                  className="w-full rounded-lg border border-gray-300 p-2 shadow-sm"
                  value={filters.size}
                  onChange={(e) => setFilters({ ...filters, size: e.target.value })}
                >
                  <option value="">Toutes les tailles</option>
                  <option value="TPE">TPE (0-9)</option>
                  <option value="PME">PME (10-249)</option>
                  <option value="ETI">ETI (250-4999)</option>
                  <option value="GE">Grande Entreprise (5000+)</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}