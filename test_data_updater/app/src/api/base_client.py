"""Module de base pour les clients API INSEE."""

import os
import time
import requests
from dotenv import load_dotenv
from app.src.utils.logger_test import DatabaseLogger
from app.src.database.last_treatment import get_latest_treatment_date

class BaseInseeClient:
    """Client de base pour les API INSEE."""
    
    # Constantes pour les limites API
    API_CALL_DELAY = 2  # secondes entre chaque appel
    
    def __init__(self, table_name, api_route):
        load_dotenv()
        self.api_key = os.getenv("api_key")
        self.table_name = table_name
        self.api_route = api_route
        self.logger = DatabaseLogger()
        
        # Ajout des headers par défaut
        self.headers = {
            "Accept": "text/csv",
            "X-INSEE-Api-Key-Integration": self.api_key
        }
        
        if not self.api_key:
            raise ValueError("La clé API est manquante")
            
        # Initialise la date DB comme variable d'instance
        self._initial_db_date = get_latest_treatment_date(self.table_name)
        print(f"📅 Date initiale DB pour {self.table_name}: {self._initial_db_date}")

    def get_initial_db_date(self):
        return self._initial_db_date

    def build_url(self, base_url, params):
        """Construit l'URL avec les paramètres."""
        query_parts = []
        
        for key, value in params.items():
            if isinstance(value, list):
                query_parts.append(f"{key}=" + "%2C".join(value))
            else:
                query_parts.append(f"{key}={value}")
            
        return f"{base_url}?{'&'.join(query_parts)}"

    def fetch_data(self, url):
        """Effectue la requête à l'API avec délai."""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Pause après chaque appel réussi
            time.sleep(self.API_CALL_DELAY)
            
            return response.text
        except requests.RequestException as e:
            self.logger.log_error("API_FETCH", str(e))
            return None