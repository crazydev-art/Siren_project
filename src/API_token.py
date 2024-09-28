"""module for function that request the API and get token"""
import requests
from requests.auth import HTTPBasicAuth


def get_token():
    """
    Fetches an access token from the INSEE API using client credentials.

    The function sends a POST request to the INSEE API token URL, providing 
    the client credentials via HTTP Basic Authentication. If successful, 
    the access token is returned. Otherwise, the function prints an error 
    message with the status code and response text.

    Returns:
        str: The access token if the request is successful, or None if it fails.
    """

    url = "https://api.insee.fr/token"
    # Données de la requête
    data = {
        'grant_type': 'client_credentials'
    }

    # Identifiants App
    client_id = 'YOUR CLIENT ID'
    client_secret = 'YOUR CLIENT SECRET PASSWORD'

    # Effectuer la requête POST avec l'authentification Basic
    response = requests.post(url, data=data, auth=HTTPBasicAuth(client_id, client_secret), verify=True,timeout=10)

    # Vérifier le statut de la réponse et extraire le jeton
    if response.status_code == 200:
        token = response.json().get('access_token')
    else:
        print(f"Erreur : {response.status_code}")
        print(response.text)
    
    return token



