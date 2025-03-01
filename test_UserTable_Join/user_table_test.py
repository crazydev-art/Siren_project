# tests/test_db_setup.py
import pytest
from unittest.mock import patch, MagicMock, call
from app.db_setup import DBCreator
import psycopg2
import bcrypt
import os

@pytest.fixture
def db_creator():
    return DBCreator()

@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = False
    return conn

def test_get_env_var_success(db_creator):
    with patch.dict(os.environ, {'POSTGRES_USER': 'test_user'}):
        assert db_creator.get_env_var('POSTGRES_USER') == 'test_user'

def test_get_env_var_missing(db_creator):
    with pytest.raises(ValueError):
        db_creator.get_env_var('NON_EXISTENT_VAR')

@patch('psycopg2.connect')
def test_create_database_success(mock_connect, db_creator):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.execute.side_effect = None
    
    db_creator.create_database()
    mock_conn.set_isolation_level.assert_called_with(ISOLATION_LEVEL_AUTOCOMMIT)
    mock_conn.cursor.return_value.execute.assert_called()

@patch('psycopg2.connect')
def test_create_database_duplicate(mock_connect, db_creator):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.execute.side_effect = psycopg2.errors.DuplicateDatabase()
    
    db_creator.create_database()  # Should not raise

@patch('bcrypt.hashpw')
def test_create_admin_user(mock_hash, db_creator, mock_db_connection):
    mock_hash.return_value = b'mocked_hash'
    with patch('app.db_setup.DBCreator.create_db_connection', return_value=mock_db_connection):
        db_creator.create_admin_user()
        
    mock_db_connection.cursor.return_value.execute.assert_called_with(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING",
        ('admin', 'admin@example.com', 'mocked_hash')
    )

def test_run_setup(db_creator):
    with patch.object(db_creator, 'start_metrics_server') as mock_metrics, \
         patch.object(db_creator, 'create_database') as mock_db, \
         patch.object(db_creator, 'create_users_table') as mock_table, \
         patch.object(db_creator, 'create_admin_user') as mock_admin:
        
        db_creator.run_setup()
        mock_metrics.assert_called_once()
        mock_db.assert_called_once()
        mock_table.assert_called_once()
        mock_admin.assert_called_once()

def test_metrics_increment(db_creator, mock_db_connection):
    with patch('app.db_setup.DBCreator.create_db_connection', return_value=mock_db_connection):
        db_creator.create_database()
        assert db_creator.metrics['db_create_attempts']._value.get() == 1
        
        db_creator.create_users_table()
        assert db_creator.metrics['table_create_attempts']._value.get() == 1
        
        db_creator.create_admin_user()
        assert db_creator.metrics['admin_create_attempts']._value.get() == 1