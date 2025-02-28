import React from 'react';
import { Building2, Users, MapPin } from 'lucide-react';
import type { Company } from '../types/company';

interface CompanyCardProps {
  company: Company;
  onClick: (company: Company) => void;
}

export default function CompanyCard({ company, onClick }: CompanyCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => onClick(company)}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">{company.name}</h3>
          <p className="text-sm text-gray-500 mt-1">SIREN: {company.siren}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm ${
          company.status === 'active' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          {company.status === 'active' ? 'Active' : 'Fermée'}
        </span>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center text-gray-600">
          <Building2 size={18} className="mr-2" />
          <span>{company.activity}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <Users size={18} className="mr-2" />
          <span>{company.employees} employés</span>
        </div>
        <div className="flex items-center text-gray-600">
          <MapPin size={18} className="mr-2" />
          <span>{company.location.city}, {company.location.department}</span>
        </div>
      </div>
    </div>
  );
}