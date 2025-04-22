export interface UniteLegale {
  siren: string;
  datecreationunitelegale: string;
  trancheeffectifsunitelegale: string;
  anneeffectifsunitelegale: string;
  datederniertraitementunitelegale: string;
  categorieentreprise: string;
  anneecategorieentreprise: string;
  etatadministratifunitelegale: string;
  nomunitelegale: string | null;
  nomusageunitelegale: string | null;
  denominationunitelegale: string;
  categoriejuridiqueunitelegale: string;
  activiteprincipaleunitelegale: string;
  nicsiegeunitelegale: string;
}

export interface Etablissement {
  siret: string;
  nic: string;
  siren: string;
  datecreationetablissement: string;
  trancheeffectifsetablissement: string;
  anneeffectifsetablissement: string;
  activiteprincipaleetablissement: string;
  datederniertraitementetablissement: string;
  etatadministratifetablissement: string;
  etablissementsiege: boolean;
  enseigne1etablissement: string;
  enseigne2etablissement: string;
  enseigne3etablissement: string;
  denominationusuelleetablissement: string;
}

export type Company = UniteLegale | Etablissement;

export interface SearchFilters {
  query: string; // Add the query property
  type: 'siren' | 'name' | 'activity' | 'siret'; // Add the type property with its possible values

  // Keep these if they are used elsewhere or for other types of searches
  // If they are completely unused for this search form, you might consider removing them
  // or creating a separate type for geo-based searches.
  activityCode?: string; // Made optional if not always present
  latitude?: number;   // Made optional
  longitude?: number;  // Made optional
  radius?: number;     // Made optional
}
export interface GeocodedAddress {
  siret: string;
  latitude: number;
  longitude: number;
}

export interface Geo {
  siret: string;
  x: number; // Longitude
  y: number; // Latitude
}

export interface Activity {
  codenaf: string;
  nafvfinale: string;
}
export type CompanyType = 'UniteLegale' | 'Etablissement';
