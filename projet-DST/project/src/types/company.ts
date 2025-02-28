export interface Company {
  siren: string;
  siret: string;
  name: string;
  activity: string;
  activityCode: string;
  location: {
    address: string;
    city: string;
    department: string;
    region: string;
    coordinates: {
      lat: number;
      lng: number;
    };
  };
  size: string;
  employees: number;
  status: 'active' | 'closed';
  creationDate: string;
}

export interface SearchFilters {
  query: string;
  type: 'siren' | 'name' | 'activity';
  region?: string;
  department?: string;
  city?: string;
  activityCode?: string;
  size?: string;
}