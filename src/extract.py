"""Module providing functions to get API siren content and explore it."""

import requests
import json
import os

# Définir la clé API et les en-têtes
API_KEY = "5e242573-0312-333f-88fd-290f4c12138c"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
i = 0
# Critères de la requête
ULNP = "q=-unitePurgeeUniteLegale%3Atrue%20"  # unité légale non purgée
SDUL = "statutDiffusionUniteLegale%3AO%20"  # statut de diffusion unité légale égale à O
CURSEUR = "curseur="
CHAMPS = (
    "champs=siren%2CdenominationUniteLegale%2CactivitePrincipaleUniteLegale"
    "%2CtrancheEffectifsUniteLegale%2CstatutDiffusionUniteLegale"
    "%2CanneeEffectifsUniteLegale%2CetatAdministratifUniteLegale"
    "%2CcategorieJuridiqueUniteLegale%2CdateCreationUniteLegale"
    "%2CdateDernierTraitementUniteLegale%2CcategorieJuridiqueUniteLegale"
)

CRITERIA = f"{ULNP}{SDUL}&{CHAMPS}&nombre=1000&{CURSEUR}"
BASE_URL = f"https://api.insee.fr/entreprises/sirene/V3.11/siren?{CRITERIA}"

OUTPUT_FILE = "/Users/yassineoc/Desktop/DATASCIENTEST/Project Siren_Siret_data/Siren-Siret-DE_Project-/data/processed/Processed_data.json"


def get_content(url, header):
    """Fonction pour récupérer le contenu de l'API."""
    try:
        response = requests.get(url, headers=header, timeout=100)
        if response.status_code == 200:
            content = response.json()
            return content
        else:
            print("error", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None


Curseur_value = "*"
Curseur_suivant = ""

champs = "champs=siren%2CdenominationUniteLegale%2CactivitePrincipaleUniteLegale%2CtrancheEffectifsUniteLegale%2CstatutDiffusionUniteLegale%2CanneeEffectifsUniteLegale%2CetatAdministratifUniteLegale%2CcategorieJuridiqueUniteLegale%2CdateCreationUniteLegale%2CdateDernierTraitementUniteLegale%2CcategorieJuridiqueUniteLegale"


while Curseur_value != Curseur_suivant and i < 5:
    print("en cours d'exe")
    new_url = BASE_URL + Curseur_value
    data = get_content(new_url, header=HEADERS)
    with open(OUTPUT_FILE, "a", encoding="utf -8") as file:
        json.dump(data, file, indent=4)

    Curseur_value = data["header"]["curseurSuivant"]
    Curseur_suivant = get_content(
        f"https://api.insee.fr/entreprises/sirene/V3.11/siren?nombre=1&curseur={Curseur_value}",
        header=HEADERS,
    )["header"]["curseurSuivant"]
    i += 1
