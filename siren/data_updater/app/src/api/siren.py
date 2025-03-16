"""Module pour récupérer les données d'unités légales depuis l'API Sirene."""

import requests
import time
import urllib.parse
from datetime import datetime
from app.src.api.base_client import BaseInseeClient
from app.src.api.last_treatment import fetch_last_treatment_date_siret_api


class UniteLegaleClient(BaseInseeClient):
    """Client pour l'API des unités légales."""
    
    def __init__(self):
        super().__init__("unitelegale", "Unités Légales")
        self.headers = {
            "Accept": "text/csv",
            "X-INSEE-Api-Key-Integration": self.api_key
        }

    def fetch_data(self, url):
        """Effectue la requête à l'API."""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.HTTPError as e:
            self.logger.log_error("API_FETCH", f"Erreur HTTP: {e.response.status_code} - {e.response.text}")
            return None
        except requests.RequestException as e:
            self.logger.log_error("API_FETCH", f"Erreur de requête: {str(e)}")
            return None

def fetch_unitelegale_data(cursor_value, client=None, db_date=None):
    """Récupère les données des unités légales."""
    if client is None:
        client = BaseInseeClient("unitelegale", "Unités Légales")
    
    if db_date is None:
        db_date = client.get_initial_db_date()

    api_date = fetch_last_treatment_date_siret_api("Unités Légales")

    if db_date is None or api_date is None:
        return None, None

    if datetime.strptime(api_date, "%Y-%m-%d") <= datetime.strptime(db_date, "%Y-%m-%d"):
        print("✨ Données unités légales à jour")
        return None, None
            
    print(f"🔄 Traitement unités légales : DB({db_date}) -> API({api_date})")
    
    query = f"dateDernierTraitementUniteLegale:[{db_date} TO {api_date}]"
    encoded_query = urllib.parse.quote(query)
    params = {
        'q': encoded_query,
        'champs': [
            "siren", "dateCreationUniteLegale", "trancheEffectifsUniteLegale",
            "anneeEffectifsUniteLegale", "dateDernierTraitementUniteLegale",
            "categorieEntreprise", "anneeCategorieEntreprise",
            "etatAdministratifUniteLegale", "nomUniteLegale",
            "nomUsageUniteLegale", "denominationUniteLegale",
            "categorieJuridiqueUniteLegale", "activitePrincipaleUniteLegale",
            "nicSiegeUniteLegale"
        ],
        'nombre': 1000,
        'curseur': cursor_value
    }
    
    # URL de base
    base_url = "https://api.insee.fr/api-sirene/3.11/siren"
    
    # Un seul appel API en JSON
    headers_json = {**client.headers, 'Accept': 'application/json'}
    url = client.build_url(base_url, params)
    response = requests.get(url, headers=headers_json, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Erreur API: {response.status_code}")
        return None, None

    try:
        json_data = response.json()
        next_cursor = json_data.get('header', {}).get('curseurSuivant')
        

        csv_header = params['champs']
        
        # Ajout de l'en-tête CSV
        csv_lines = [','.join(csv_header)]
        
        # Conversion des unités légales en lignes CSV
        for unite in json_data.get('unitesLegales', []):
            # On prend la période la plus récente
            periode = unite.get('periodesUniteLegale', [{}])[0]
            
            # Création de la ligne CSV avec les données combinées
            row_data = [
                unite.get('siren', ''),
                unite.get('dateCreationUniteLegale', ''),
                unite.get('trancheEffectifsUniteLegale', ''),
                unite.get('anneeEffectifsUniteLegale', ''),
                unite.get('dateDernierTraitementUniteLegale', ''),
                unite.get('categorieEntreprise', ''),
                unite.get('anneeCategorieEntreprise', ''),
                periode.get('etatAdministratifUniteLegale', ''),
                periode.get('nomUniteLegale', ''),
                periode.get('nomUsageUniteLegale', ''),
                periode.get('denominationUniteLegale', ''),
                periode.get('categorieJuridiqueUniteLegale', ''),
                periode.get('activitePrincipaleUniteLegale', ''),
                periode.get('nicSiegeUniteLegale', '')
            ]
            
            # Échapper les virgules et les guillemets si nécessaire
            escaped_row = []
            for field in row_data:
                if field is None:
                    escaped_row.append('')
                elif ',' in str(field) or '"' in str(field):
                    escaped_row.append('"{0}"'.format(str(field).replace('"', '""')))
                else:
                    escaped_row.append(str(field))
            
            csv_lines.append(','.join(escaped_row))
        
        # Création du CSV final
        csv_output = '\n'.join(csv_lines)
        
        time.sleep(2)  # Pause entre les appels
        return csv_output, next_cursor
        
    except Exception as e:
        print(f"Erreur lors de la conversion JSON->CSV: {str(e)}")
        return None, None   