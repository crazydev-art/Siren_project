import { useLocation } from 'react-router-dom';
import CompanyCard from '../components/CompanyCard';
import type { Company, SearchFilters,UniteLegale, Etablissement } from '../types/company';

function SearchResultsPage() {
  const location = useLocation();
  const filters = location.state?.filters as SearchFilters;
  const companies = location.state?.companies as Company[];

  const handleCompanyClick = (company: Company) => {
    console.log('Company clicked:', company);
    // In a real application, you would navigate to a detailed company page here.
  };

  return (
    <div>
      {/* Results Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Résultats de recherche</h2>
        <div className="flex items-center text-gray-600">
          <p>
            {companies?.length} entreprise{companies?.length > 1 ? 's' : ''} trouvée{companies?.length > 1 ? 's' : ''}
          </p>
          {filters?.query && (
            <p className="ml-2">
              pour "<span className="font-medium">{filters.query}</span>"
            </p>
          )}
        </div>
      </div>
      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {companies?.map((company) => (
    <div key={(company as UniteLegale).siren || (company as Etablissement).siret}>

      <CompanyCard
        company={company}
        onClick={handleCompanyClick}
      />
    </div>
  ))}
</div>


      {/* No Results State */}
      {companies?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">
            Aucune entreprise ne correspond à vos critères de recherche.
          </p>
        </div>
      )}
    </div>
  );
}

export default SearchResultsPage;
