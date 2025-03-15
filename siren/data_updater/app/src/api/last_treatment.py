"""Module pour récupérer les dates de dernier traitement depuis l'API INSEE."""

import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def fetch_last_treatment_date_siret_api(collection_type: str):
    """
    Récupère la date du dernier traitement depuis l'API INSEE.
    
    Args:
        collection_type (str): "Établissements" ou "Unités Légales"
    
    Returns:
        str: Date au format 'YYYY-MM-DD' ou None si erreur
    """
    # Clé API depuis les variables d'environnement
    api_key = os.getenv("api_key")
    if not api_key:
        raise ValueError("La clé API est manquante. Vérifiez votre fichier .env.")

    # URL de l'API
    url = "https://api.insee.fr/api-sirene/3.11/informations"

    # En-têtes de la requête
    headers = {
        "Accept": "application/json",
        "X-INSEE-Api-Key-Integration": api_key
    }

    try:
        # Requête vers l'API
        response = requests.get(url, headers=headers, timeout=30)
        time.sleep(2)
        response.raise_for_status()

        # Conversion de la réponse en JSON
        data = response.json()

        # Parcours des collections pour trouver le type demandé
        for item in data.get("datesDernieresMisesAJourDesDonnees", []):
            if item.get("collection") == collection_type:
                date_str = item.get("dateDernierTraitementMaximum")
                if date_str:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    return date_obj.strftime("%Y-%m-%d")
                else:
                    print(f"⚠️ La date 'dateDernierTraitementMaximum' est manquante pour {collection_type}.")
                    return None

        print(f"⚠️ La collection '{collection_type}' n'a pas été trouvée dans la réponse.")
        return None

    except requests.HTTPError as e:
        print(f"❌ Erreur lors de la requête API: {e.response.status_code} - {e.response.text}")
        return None
    except ValueError as ve:
        print(f"❌ Erreur lors de la conversion de la date: {ve}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return None

