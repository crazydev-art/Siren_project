import {SearchFilters, UniteLegale, Etablissement, Geo } from '../types/company';


export const searchCompanies = async (filters: SearchFilters): Promise<Geo[]> => {
  try {
    const url = 'http://141.145.207.10:8000/api/companies/search';
    console.log('Sending request to:', url, 'with body:', JSON.stringify(filters));
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(filters),
    });
    if (!response.ok) {
      const errorData = await response.json();
      console.error('API error response:', errorData);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('API response data:', data);
    return data;
  } catch (error) {
    console.error('Error fetching companies:', error);
    return [];
  }
};

export const searchCompanyBySiret = async (siret: string): Promise<Etablissement | null> => {
  try {
    const url = `http://141.145.207.10:8000/api/siret?siret=${siret}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data[0] as Etablissement;
  } catch (error) {
    console.error('Error fetching company by Siret:', error);
    return null; // Return null in case of error
  }
};

export const searchCompanyBySiren = async (siret: string): Promise<Etablissement | null> => {
  try {
    const url = `http://141.145.207.10:8000/api/siren?siren=${siret}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data[0] as Etablissement;
  } catch (error) {
    console.error('Error fetching company by Siret:', error);
    return null; // Return null in case of error
  }
};
