"""Module pour récupérer les données d'établissements depuis l'API Sirene."""

import requests
from app.src.api.base_client import BaseInseeClient
from app.src.api.last_treatment import fetch_last_treatment_date_siret_api
from datetime import datetime
import time
import urllib.parse

class EtablissementClient(BaseInseeClient):
    """Client pour l'API des établissements."""
    
    def __init__(self):
        super().__init__("etablissement", "Établissements")
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

def fetch_etablissement_data(cursor_value, client=None, db_date=None):
    """Récupère les données des établissements."""
    if client is None:
        client = BaseInseeClient("etablissement", "Établissements")
    
    if db_date is None:
        db_date = client.get_initial_db_date()

    api_date = fetch_last_treatment_date_siret_api("Établissements")

    if db_date is None:
        return None, None

    if datetime.strptime(api_date, "%Y-%m-%d") <= datetime.strptime(db_date, "%Y-%m-%d"):
        print("✨ Données établissements à jour")
        return None, None
    
    print(f"🔄 Traitement établissements : DB({db_date}) -> API({api_date})")
    
    # Construction de la requête pour l'Île-de-France
    idf_postal_codes = " OR ".join([
        f"codePostalEtablissement:{dep}*" 
        for dep in ['75', '77', '78', '91', '92', '93', '94', '95']
    ])
    
    query = f"dateDernierTraitementEtablissement:[{db_date} TO {api_date}] AND ({idf_postal_codes}) AND statutDiffusionEtablissement:'O'"
    encoded_query = urllib.parse.quote(query)
    
    # Définition des en-têtes pour chaque type de données
    etab_header = [
        "siret", "nic", "siren", "dateCreationEtablissement",
        "trancheEffectifsEtablissement", "anneeEffectifsEtablissement",
        "activitePrincipaleEtablissement", "dateDernierTraitementEtablissement",
        "etatAdministratifEtablissement", "etablissementSiege",
        "enseigne1Etablissement", "enseigne2Etablissement",
        "enseigne3Etablissement", "denominationUsuelleEtablissement"
    ]
    
    adresse_header = [
        "siret", "complementAdresseEtablissement", "numeroVoieEtablissement",
        "indiceRepetitionEtablissement", "typeVoieEtablissement",
        "libelleVoieEtablissement", "codePostalEtablissement",
        "libelleCommuneEtablissement", "codeCommuneEtablissement"
    ]
    
    params = {
        'q': encoded_query,
        'nombre': 1000,
        'curseur': cursor_value
    }
    
    base_url = "https://api.insee.fr/api-sirene/3.11/siret"
    headers_json = {**client.headers, 'Accept': 'application/json'}
    url = client.build_url(base_url, params)
    response = requests.get(url, headers=headers_json, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Erreur API: {response.status_code}")
        return None, None

    try:
        json_data = response.json()
        next_cursor = json_data.get('header', {}).get('curseurSuivant')
        # Création des CSV pour établissements et adresses
        etab_lines = [','.join(etab_header)]
        adresse_lines = [','.join(adresse_header)]
        
        for etab in json_data.get('etablissements', []):
            periode = etab.get('periodesEtablissement', [{}])[0]
            adresse = etab.get('adresseEtablissement', {})
            
            # Données établissement
            etab_row = [
                etab.get('siret', ''),
                etab.get('nic', ''),
                etab.get('siren', ''),
                etab.get('dateCreationEtablissement', ''),
                etab.get('trancheEffectifsEtablissement', ''),
                etab.get('anneeEffectifsEtablissement', ''),
                periode.get('activitePrincipaleEtablissement', ''),
                etab.get('dateDernierTraitementEtablissement', ''),
                periode.get('etatAdministratifEtablissement', ''),
                etab.get('etablissementSiege', ''),
                periode.get('enseigne1Etablissement', ''),
                periode.get('enseigne2Etablissement', ''),
                periode.get('enseigne3Etablissement', ''),
                periode.get('denominationUsuelleEtablissement', '')
            ]
            
            
            # Données adresse
            adresse_row = [
                etab.get('siret', ''),
                adresse.get('complementAdresseEtablissement', ''),
                adresse.get('numeroVoieEtablissement', ''),
                adresse.get('indiceRepetitionEtablissement', ''),
                adresse.get('typeVoieEtablissement', ''),
                adresse.get('libelleVoieEtablissement', ''),
                adresse.get('codePostalEtablissement', ''),
                adresse.get('libelleCommuneEtablissement', ''),
                adresse.get('codeCommuneEtablissement', '')
            ]
            
            # Échappement des valeurs pour CSV
            escaped_etab = []
            escaped_addr = []
            
            for field in etab_row:
                if field is None:
                    escaped_etab.append('')
                elif ',' in str(field) or '"' in str(field):
                    escaped_etab.append('"{0}"'.format(str(field).replace('"', '""')))
                else:
                    escaped_etab.append(str(field))
                    
            for field in adresse_row:
                if field is None:
                    escaped_addr.append('')
                elif ',' in str(field) or '"' in str(field):
                    escaped_addr.append('"{0}"'.format(str(field).replace('"', '""')))
                else:
                    escaped_addr.append(str(field))
            
            etab_lines.append(','.join(escaped_etab))
            adresse_lines.append(','.join(escaped_addr))
        
        # Création des CSV finaux
        etab_csv = '\n'.join(etab_lines)
        adresse_csv = '\n'.join(adresse_lines)
        
        time.sleep(2)  # Pause entre les appels
        return (etab_csv, adresse_csv), next_cursor
        
    except Exception as e:
        print(f"Erreur lors de la conversion JSON->CSV: {str(e)}")
        return None, None