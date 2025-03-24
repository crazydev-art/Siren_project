import React, { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import type { SearchFilters } from '../types/company';

interface SearchBarProps {
  onSearch: (filters: SearchFilters) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    type: 'name',
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters({ ...filters, query: e.target.value });
  };

  const handleSearchTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters({ ...filters, type: e.target.value as 'siren' | 'name' | 'activity' | 'siret' });
  };

  const handleFilterChange = (
    e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>,
    filterKey: keyof Omit<SearchFilters, 'query' | 'type'>
  ) => {
    setFilters({ ...filters, [filterKey]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md">
      <div className="flex items-center space-x-4">
        {/* Search Input */}
        <div className="relative flex-grow">
          <input
            type="text"
            className="w-full px-4 py-3 pl-12 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Entrez votre recherche..."
            value={filters.query}
            onChange={handleInputChange}
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>

        {/* Filter Button */}
        <button
          type="button"
          className="p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="text-gray-600" size={20} />
        </button>
      </div>

      {/* Filter Dropdown */}
      {showFilters && (
        <div className="mt-4 space-y-4">
          {/* Search Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type de recherche
            </label>
            <select
              className="w-full rounded-lg border border-gray-300 p-3"
              value={filters.type}
              onChange={handleSearchTypeChange}
            >
              <option value="name">Nom d'entreprise</option>
              <option value="siren">Siren</option>
              <option value="siret">Siret</option>
              <option value="activity">Code APE</option>
            </select>
          </div>
          {/* Region */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Région
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 p-3"
              value={filters.region || ''}
              onChange={(e) => handleFilterChange(e, 'region')}
            />
          </div>
          {/* Department */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Département
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 p-3"
              value={filters.department || ''}
              onChange={(e) => handleFilterChange(e, 'department')}
            />
          </div>
          {/* City */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ville
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 p-3"
              value={filters.city || ''}
              onChange={(e) => handleFilterChange(e, 'city')}
            />
          </div>
          {/* Activity Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code APE
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 p-3"
              value={filters.activityCode || ''}
              onChange={(e) => handleFilterChange(e, 'activityCode')}
            />
          </div>
          {/* Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Taille
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 p-3"
              value={filters.size || ''}
              onChange={(e) => handleFilterChange(e, 'size')}
            />
          </div>
        </div>
      )}
      {showFilters && (
        <div className="flex justify-end mt-4">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Rechercher
          </button>
        </div>
      )}
    </form>
  );
};

export default SearchBar;
