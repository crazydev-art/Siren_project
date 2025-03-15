"""Tests du service de mise à jour."""

import pytest

from unittest.mock import patch

from app.src.service.updater import UpdateService


@pytest.fixture
def update_service():
    """Fixture pour le service de mise à jour."""
    return UpdateService()

def test_process_updates():
    """Test le processus complet de mise à jour."""
    with patch('app.src.api.siret.fetch_data_from_api') as mock_fetch:
        # Données de test valides
        mock_fetch.return_value = [
            {
                "siret": "12345678901234",
                "nic": "12345"
            }
        ]
        
        with patch('app.src.database.loader.load_data_to_staging') as mock_load:
            mock_load.return_value = True
            
            with patch('app.src.database.loader.update_from_staging') as mock_update:
                mock_update.return_value = (True, 10)
                
                result = process_updates()
                assert result is True
                
                mock_fetch.assert_called_once()
                mock_load.assert_called_once()
                mock_update.assert_called_once() 