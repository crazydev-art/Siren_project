# tests/test_db_cleaner.py
import pytest
from unittest.mock import patch, MagicMock
from app.db_cleaner import DBCleaner
import psycopg2
import os

@pytest.fixture
def db_cleaner():
    return DBCleaner()

@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn

def test_get_env_variable_success(db_cleaner):
    with patch.dict(os.environ, {'POSTGRES_DB': 'test_db'}):
        assert db_cleaner.get_env_variable('POSTGRES_DB') == 'test_db'

def test_get_env_variable_missing(db_cleaner):
    with pytest.raises(EnvironmentError):
        db_cleaner.get_env_variable('NON_EXISTENT_VAR')

def test_get_db_connection_success(db_cleaner):
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = 'connection'
        with patch.dict(os.environ, {
            'POSTGRES_DB': 'db',
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'pass',
            'IPHOST': 'host'
        }):
            conn = db_cleaner.get_db_connection()
            assert conn == 'connection'

def test_delete_orphaned_records(db_cleaner, mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.fetchall.side_effect = [[1, 2, 3], []]

    db_cleaner.delete_orphaned_records(
        mock_db_connection,
        'test_table',
        'foreign_table',
        'test_id'
    )

    assert mock_cursor.execute.call_count == 2
    mock_db_connection.commit.assert_called()
    mock_db_connection.rollback.assert_not_called()

def test_vacuum_analyze(db_cleaner):
    with patch('app.db_cleaner.DBCleaner.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        db_cleaner._vacuum_analyze()
        mock_cursor.execute.assert_called_with("VACUUM ANALYZE;")

def test_run_cleanup_sequential(db_cleaner):
    with patch('app.db_cleaner.DBCleaner._run_sequential') as mock_seq, \
         patch('app.db_cleaner.DBCleaner._vacuum_analyze') as mock_vacuum:
        db_cleaner.run_cleanup()
        mock_seq.assert_called_once()
        mock_vacuum.assert_called_once()

@patch('app.db_cleaner.ProcessPoolExecutor')
def test_run_cleanup_parallel(mock_executor, db_cleaner):
    db_cleaner.run_cleanup(parallel=True)
    mock_executor.return_value.__enter__.return_value.submit.assert_called()