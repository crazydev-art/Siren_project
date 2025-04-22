import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search as SearchIcon } from 'lucide-react';
import type { SearchFilters, Company } from '../types/company';
import { searchCompanies, searchCompanyBySiren, searchCompanyBySiret } from '../api/company'; // Import all API functions

export default function SearchPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    type: 'name'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null); // New state for query error

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setQueryError(null); // Clear previous query error
    setError(null); // Clear previous error

    if (!filters.query.trim()) {
      setQueryError('Veuillez entrer une valeur dans le champ de recherche.');
      return; // Stop form submission
    }

    // Siren/Siret Length and Numeric Validation
    if (filters.type === 'siren') {
      if (filters.query.length !== 9) {
        setQueryError('Le Siren doit contenir 9 chiffres.');
        return;
      }
      if (!/^\d+$/.test(filters.query)) {
        setQueryError('Le Siren doit contenir uniquement des chiffres.');
        return;
      }
    }
    if (filters.type === 'siret') {
      if (filters.query.length !== 14) {
        setQueryError('Le Siret doit contenir 14 chiffres.');
        return;
      }
      if (!/^\d+$/.test(filters.query)) {
        setQueryError('Le Siret doit contenir uniquement des chiffres.');
        return;
      }
    }

    setLoading(true);

    try {
      let companies: Company[] = [];
      if (filters.type === 'siren') {
        const company = await searchCompanyBySiren(filters.query);
        if (company) {
          companies = [company];
        } else {
          setError('Aucune entreprise trouvée avec ce Siren.'); // API "not found"
        }
      } else if (filters.type === 'siret') {
        const company = await searchCompanyBySiret(filters.query);
        if (company) {
          companies = [company];
        } else {
          setError('Aucun établissement trouvé avec ce Siret.'); // API "not found"
        }
      } else {
        companies = await searchCompanies(filters);
        if (companies.length === 0) {
          setError('Aucune entreprise trouvée correspondant à vos critères.');
        }
      }
      if (companies.length > 0) {
        navigate('/results', { state: { filters, companies } });
      }
    } catch (err) {
      setError('Failed to fetch companies. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Recherche Approfondie en Ile-De-France</h2>

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
                onChange={(e) => setFilters({ ...filters, type: e.target.value as 'siren' | 'name' | 'activity' | 'siret' })}
              >
                {/*<option value="name">Nom d'entreprise</option>*/}
                <option value="siren">Siren</option>
                <option value="siret">Siret</option>
                {/*<option value="activity">Code APE(activité principale exercée)</option>*/}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recherche
              </label>
              <div className="relative">
                <input
                  type="text"
                  className={`w-full px-4 py-3 pl-12 rounded-lg border ${queryError ? 'border-red-500' : 'border-gray-300'} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                  placeholder="Entrez votre recherche..."
                  value={filters.query}
                  onChange={(e) => setFilters({ ...filters, query: e.target.value })}
                />
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              </div>
              {queryError && <p className="text-red-500 text-sm mt-1">{queryError}</p>} {/* Display query error */}
            </div>
          </div>
        </div>
        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Lancer la recherche'}
          </button>
        </div>
        {/* Error Message */}
        {error && <div className="text-red-500">{error}</div>}
      </form>
    </div>
  );
}
