
import React, { useState, useEffect } from 'react';
import { Building2, Users } from 'lucide-react';
import type { Company, UniteLegale, Etablissement } from '../types/company';
import { searchCompanyBySiren } from '../api/company';

interface CompanyCardProps {
  company: Company;
  onClick: (company: Company) => void;
}

const CompanyCard: React.FC<CompanyCardProps> = ({ company, onClick }) => {
  const [uniteLegale, setUniteLegale] = useState<UniteLegale | null>(null);

  useEffect(() => {
    const fetchUniteLegale = async () => {
      if ((company as Etablissement).siren) {
        const ul = await searchCompanyBySiren((company as Etablissement).siren);
        setUniteLegale(ul);
      }
    };

    fetchUniteLegale();
  }, [company]);

  const getStatus = (company: Company): 'active' | 'inactive' => {
    if ((company as UniteLegale).etatadministratifunitelegale) {
      return (company as UniteLegale).etatadministratifunitelegale === 'A' ? 'active' : 'inactive';
    } else if ((company as Etablissement).etatadministratifetablissement) {
      return (company as Etablissement).etatadministratifetablissement === 'A' ? 'active' : 'inactive';
    }
    return 'inactive'; // Default to inactive if status is not found
  };

  const getCompanyName = (company: Company, uniteLegale: UniteLegale | null): string => {
    if ((company as Etablissement).denominationusuelleetablissement) {
      return (company as Etablissement).denominationusuelleetablissement;
    } else if (uniteLegale) {
      if (uniteLegale.denominationunitelegale) {
        return uniteLegale.denominationunitelegale;
      } else if (uniteLegale.nomusageunitelegale) {
        return uniteLegale.nomusageunitelegale;
      } else if (uniteLegale.nomunitelegale) {
        return uniteLegale.nomunitelegale;
      }
    }
    return "Pas de Nom";
  };

  const getIdentifier = (company: Company): { label: string; value: string } => {
    if ((company as Etablissement).siret) {
      return { label: "SIRET", value: (company as Etablissement).siret };
    } else if ((company as UniteLegale).siren) {
      return { label: "SIREN", value: (company as UniteLegale).siren };
    }
    return { label: "", value: "" };
  };

  const getActivity = (company: Company): string => {
    if ((company as UniteLegale).activiteprincipaleunitelegale) {
      return (company as UniteLegale).activiteprincipaleunitelegale;
    } else if ((company as Etablissement).activiteprincipaleetablissement) {
      return (company as Etablissement).activiteprincipaleetablissement;
    }
    return "";
  };

  const getEmployees = (company: Company): string => {
    if ((company as UniteLegale).trancheeffectifsunitelegale) {
      return (company as UniteLegale).trancheeffectifsunitelegale;
    } else if ((company as Etablissement).trancheeffectifsetablissement) {
      return (company as Etablissement).trancheeffectifsetablissement;
    }
    return "0";
  };

  const companyName = getCompanyName(company, uniteLegale);
  const { label, value } = getIdentifier(company);
  const activity = getActivity(company);
  const employees = getEmployees(company);
  const status = getStatus(company);

  return (
    <div
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => onClick(company)}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-500 text-sm">Dénomination de la société</p>
          <h3 className="text-xl font-semibold text-gray-900">{companyName}</h3>
          <p className="text-sm text-gray-500 mt-1">{label}: {value}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm ${
          status === 'active'
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {status === 'active' ? 'Active' : 'Fermée'}
        </span>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center text-gray-600">
          <Building2 size={18} className="mr-2" />
          <span>{activity}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <Users size={18} className="mr-2" />
          <span>{employees} employés</span>
        </div>
      </div>
    </div>
  );
};

export default CompanyCard;
