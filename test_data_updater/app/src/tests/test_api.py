"""Tests des fonctions d'API."""
from unittest.mock import patch, Mock

from datetime import date, datetime

from app.src.api.siret import fetch_data_from_api
from app.src.api.last_treatment import fetch_last_treatment_date_siret_api

def test_fetch_last_treatment_date():
    """Test la récupération de la dernière date de traitement."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "header": {
                "statut": 200,
                "message": "OK"
            },
            "collection": "Établissements",
            "dateDernierTraitement": datetime.now().strftime("%Y-%m-%d")
        }
        mock_get.return_value.status_code = 200
        
        result = fetch_last_treatment_date_siret_api()
        assert result is not None
        assert isinstance(result, date)

def test_fetch_data_from_api():
    """Test la récupération des données de l'API."""
    with patch('app.src.database.last_treatment.get_latest_treatment_date') as mock_db:
        mock_db.return_value = date(2024, 1, 1)
        
        with patch('requests.get') as mock_get:
            # Structure de réponse corrigée
            mock_get.return_value.json.return_value = {
                "header": {
                    "statut": 200,
                    "message": "OK",
                    "total": 1,
                    "curseurSuivant": None
                },
                "etablissements": [{
                    "siret": "12345678901234",
                    "dateTraitement": "2024-03-20"
                }]
            }
            mock_get.return_value.status_code = 200
            
            result = fetch_data_from_api()
            assert isinstance(result, list)

@patch('requests.get')
def test_fetch_last_treatment_date_siret_api(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "header": {
            "statut": 200,
            "message": "OK"
        },
        "collection": "Établissements",
        "derniere_mise_a_jour": "2024-03-20"
    }
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    date_fetched = fetch_last_treatment_date_siret_api("Établissements")
    assert isinstance(date_fetched, date)