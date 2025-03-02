import React from 'react';
import { useLocation } from 'react-router-dom';
import CompanyCard from '../components/CompanyCard';
import type { Company, SearchFilters } from '../types/company';

// Mock data for demonstration
const mockCompanies: Company[] = [
  {
    siren: "123456789",
    siret: "12345678900001",
    name: "Tech Solutions France",
    activity: "Services informatiques",
    activityCode: "6201Z",
    location: {
      address: "123 Avenue de la République",
      city: "Paris",
      department: "75",
      region: "Île-de-France",
      coordinates: { lat: 48.8566, lng: 2.3522 }
    },
    size: "PME",
    employees: 120,
    status: "active",
    creationDate: "2015-03-15"
  },
  {
    siren: "987654321",
    siret: "98765432100001",
    name: "Eco Innovations",
    activity: "Recherche et développement",
    activityCode: "7219Z",
    location: {
      address: "45 Rue de l'Innovation",
      city: "Lyon",
      department: "69",
      region: "Auvergne-Rhône-Alpes",
      coordinates: { lat: 45.7578, lng: 4.8320 }
    },
    size: "ETI",
    employees: 350,
    status: "active",
    creationDate: "2010-07-22"
  }
];

function SearchResultsPage() {
  const location = useLocation();
  const filters = location.state?.filters as SearchFilters;

  const handleCompanyClick = (company: Company) => {
    console.log('Company clicked:', company);
    // This would navigate to the company detail page in a real application
  };

  return (
    <div>
      {/* Results Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Résultats de recherche</h2>
        <div className="flex items-center text-gray-600">
          <p>
            {mockCompanies.length} entreprise{mockCompanies.length > 1 ? 's' : ''} trouvée{mockCompanies.length > 1 ? 's' : ''}
          </p>
          {filters?.query && (
            <p className="ml-2">
              pour "<span className="font-medium">{filters.query}</span>"
            </p>
          )}
        </div>
      </div>

      {/* Active Filters */}
      {filters && Object.keys(filters).length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Filtres actifs</h3>
          <div className="flex flex-wrap gap-2">
            {filters.region && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Région: {filters.region}
              </span>
            )}
            {filters.size && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Taille: {filters.size}
              </span>
            )}
            {filters.activityCode && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Code APE: {filters.activityCode}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockCompanies.map((company) => (
          <CompanyCard
            key={company.siren}
            company={company}
            onClick={handleCompanyClick}
          />
        ))}
      </div>

      {/* No Results State */}
      {mockCompanies.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">
            Aucune entreprise ne correspond à vos critères de recherche.
          </p>
        </div>
      )}
    </div>
  );
}

export default SearchResultsPage
