"""Tests des fonctions de base de données."""

from unittest.mock import Mock, patch

import pytest

from app.src.database.loader import load_data_to_staging, update_from_staging


@pytest.fixture
def mock_db_pool():
    """Fixture pour simuler le pool de connexions."""
    with patch("app.src.database.connection.DatabaseConnectionPool") as mock:
        pool = Mock()
        mock.return_value = pool
        yield pool


def test_load_data_to_staging():
    """Test le chargement des données dans la table staging."""
    test_data = [{
        "siret": "12345678901234",
        "nic": "12345"
    }]
    
    # Mock complet avec context manager
    mock_conn = Mock()
    mock_cursor = Mock()
    
    with patch('app.src.database.connection.DatabaseConnectionPool') as mock_pool:
        # Configuration du mock pour le context manager
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        mock_pool_instance.get_connection.return_value = mock_conn
        
        # Setup du context manager pour la connexion
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        
        # Setup du cursor avec context manager
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        
        result = load_data_to_staging(test_data)
        assert result is True


def test_update_from_staging():
    """Test la mise à jour depuis la table staging."""
    mock_conn = Mock()
    mock_cursor = Mock()
    
    with patch('app.src.database.connection.DatabaseConnectionPool') as mock_pool:
        # Configuration complète du mock
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        mock_pool_instance.get_connection.return_value = mock_conn
        
        # Setup des context managers
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        
        # Simuler une mise à jour réussie
        mock_cursor.rowcount = 10
        
        success, count = update_from_staging()
        assert success is True
        assert count == 10
