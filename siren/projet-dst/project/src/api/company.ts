import {SearchFilters, UniteLegale, Etablissement, Geo } from '../types/company';
import.meta.env;


const FAST_API_BASE_URL = import.meta.env.VITE_FAST_API_URL || 'http://0.0.0.0:8000';
export const searchCompanies = async (filters: SearchFilters): Promise<Geo[]> => {
  try {
    // Use the base URL variable
    const url = `${FAST_API_BASE_URL}/api/companies/search`;
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
    // Use the base URL variable
    const url = `${FAST_API_BASE_URL}/api/siret?siret=${siret}`;

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
    // Assuming the API returns an array even for a single result
    return data && data.length > 0 ? data[0] as Etablissement : null;
  } catch (error) {
    console.error('Error fetching company by Siret:', error);
    return null; // Return null in case of error
  }
};

export const searchCompanyBySiren = async (siren: string): Promise<UniteLegale | null> => {
    // Note: The original function argument was named 'siret', but the API endpoint uses 'siren'.
    // Changed the argument name to 'siren' for clarity, assuming the API expects a SIREN number here.
  try {
    // Use the base URL variable
    const url = `${FAST_API_BASE_URL}/api/siren?siren=${siren}`;

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
     // Assuming the API returns an array even for a single result
    // Also assuming this endpoint returns UniteLegale data based on the endpoint name
    return data && data.length > 0 ? data[0] as UniteLegale : null;
  } catch (error) {
    console.error('Error fetching company by Siren:', error);
    return null; // Return null in case of error
  }
};