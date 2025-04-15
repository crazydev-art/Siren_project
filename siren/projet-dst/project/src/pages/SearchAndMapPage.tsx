import React, { useState, useEffect } from 'react';
import { Combobox } from '@headlessui/react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { GeocodedAddress, Activity, SearchFilters } from '../types/company';
import { searchCompanies } from '../api/company';
import.meta.env;


const FAST_API_BASE_URL = import.meta.env.VITE_FAST_API_URL || 'http://0.0.0.0:8000';

const SearchAndMapPage: React.FC = () => {
  const [address, setAddress] = useState('');
  const [radius, setRadius] = useState(5);
  const [establishments, setEstablishments] = useState<GeocodedAddress[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [query, setQuery] = useState('');
  const [suggestedActivities, setSuggestedActivities] = useState<Activity[]>([]);
  const [mapCenter, setMapCenter] = useState<[number, number]>([48.8584, 2.2945]);
  const [searchedAddress, setSearchedAddress] = useState<GeocodedAddress | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchActivitySuggestions = async () => {
      if (!query.trim()) {
        console.log('Query empty, clearing suggestions');
        setSuggestedActivities([]);
        return;
      }
      try {
        console.log('Fetching activity suggestions for query:', query);

        const url = `${FAST_API_BASE_URL}/activities/suggest?q=${encodeURIComponent(query)}`;
        
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
        const data = await response.json();
        console.log('Activity suggestions received:', data);
        setSuggestedActivities(data);
      } catch (error) {
        console.error('Failed to fetch activity suggestions:', error);
        setSuggestedActivities([]);
      }
    };

    const timeoutId = setTimeout(fetchActivitySuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const fetchNafCode = async (activity: Activity): Promise<string | null> => {
    try {
      console.log('Fetching NAF code for activity:', activity.nafvfinale);
      const url = `${FAST_API_BASE_URL}/activities/get-naf?activity=${encodeURIComponent(activity.nafvfinale)}`
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      const data = await response.json();
      console.log('NAF code received:', data.codenaf);
      return data.codenaf || null;
    } catch (error) {
      console.error('Failed to fetch NAF code:', error);
      return null;
    }
  };

  const geocodeAddress = async (address: string): Promise<{ latitude: number; longitude: number; display_name: string } | null> => {
    try {
      console.log('Geocoding address:', address);
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json&limit=1`
      );
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      const data = await response.json();
      if (data.length === 0) {
        console.log('Address not found');
        return null;
      }
      const { lat, lon, display_name } = data[0];
      console.log('Geocoded address:', { latitude: parseFloat(lat), longitude: parseFloat(lon), display_name });
      return { latitude: parseFloat(lat), longitude: parseFloat(lon), display_name };
    } catch (error) {
      console.error('Failed to geocode address:', error);
      return null;
    }
  };

  const handleSearch = async () => {
    if (!address.trim() || !selectedActivity || !radius) {
      console.log('Validation failed: missing address, activity, or radius');
      alert('Please provide an address, activity, and radius.');
      return;
    }

    setLoading(true);
    try {
      const nafCode = await fetchNafCode(selectedActivity);
      if (!nafCode) {
        console.log('No NAF code found for activity:', selectedActivity.nafvfinale);
        alert('No NAF code found for this activity.');
        return;
      }

      const geocoded = await geocodeAddress(address);
      if (!geocoded) {
        alert('Address not found.');
        return;
      }

      const { latitude, longitude, display_name } = geocoded;
      setMapCenter([latitude, longitude]);
      setSearchedAddress({ latitude, longitude, siret: display_name });

      const searchFilters: SearchFilters = { activityCode: nafCode, latitude, longitude, radius };
      console.log('Searching companies with filters:', searchFilters);

      const companies = await searchCompanies(searchFilters);
      console.log('Companies received:', companies);

      setEstablishments(
        companies.map(c => ({
          siret: c.siret,
          latitude: c.y,
          longitude: c.x,
        }))
      );
    } catch (error) {
      console.error('Search failed:', error);
      alert('An error occurred while searching. Please try again.');
    } finally {
      setLoading(false);
      console.log('Search completed, loading:', false);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="w-1/3 p-6 bg-gray-100 border-r border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Recherche d'établissements</h2>
        <div className="mb-4">
          <input
            type="text"
            className="p-2 w-full border rounded-md"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Entrez une adresse"
          />
        </div>
        <div className="mb-4">
          <Combobox value={selectedActivity} onChange={setSelectedActivity}>
            <div className="relative">
              <Combobox.Input
                className="w-full p-2 border rounded-md"
                displayValue={(activity: Activity) => activity?.nafvfinale || ''}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Entrez une activité"
              />
              <Combobox.Options className="absolute mt-1 w-full bg-white shadow-lg rounded-md max-h-60 overflow-auto z-10">
                {suggestedActivities.length === 0 && query !== '' ? (
                  <div className="p-2 text-gray-500">No activities found</div>
                ) : (
                  suggestedActivities.map((activity) => (
                    <Combobox.Option
                      key={activity.codenaf}
                      value={activity}
                      className={({ active }) => `p-2 cursor-pointer ${active ? 'bg-gray-200' : ''}`}
                    >
                      {activity.nafvfinale}
                    </Combobox.Option>
                  ))
                )}
              </Combobox.Options>
            </div>
          </Combobox>
        </div>
        <div className="mb-4">
          <input
            type="number"
            className="p-2 w-full border rounded-md"
            value={radius}
            onChange={(e) => setRadius(parseInt(e.target.value))}
            min="1"
            placeholder="Radius (km)"
          />
        </div>
        <button
          onClick={handleSearch}
          className="w-full p-2 bg-blue-500 text-white rounded-md"
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Rechercher'}
        </button>
      </div>
      <div className="w-2/3 p-6">
        <MapContainer center={mapCenter} zoom={13} style={{ height: '400px', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="© OpenStreetMap contributors"
          />
          {searchedAddress && (
            <Marker position={[searchedAddress.latitude, searchedAddress.longitude]}>
              <Popup>{searchedAddress.siret}</Popup>
            </Marker>
          )}
          {establishments.map((establishment) => (
            <Marker
              key={establishment.siret}
              position={[establishment.latitude, establishment.longitude]}
            >
              <Popup>{establishment.siret}</Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default SearchAndMapPage;