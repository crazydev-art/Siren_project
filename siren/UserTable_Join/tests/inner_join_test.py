import pytest
import logging
import os
import time
from unittest.mock import MagicMock, patch
from concurrent.futures import ProcessPoolExecutor
import inner_join  # Import the module under test

# --- Fixtures ---

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    """Mock environment variables required by inner_join.py"""
    env_vars = {
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "testpass",
        "IPHOST": "localhost",
        "POSTGRES_PORT": "5432",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

@pytest.fixture(autouse=True)
def patch_psycopg2_connect(monkeypatch):
    """Mock psycopg2.connect to return a lightweight fake connection"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Simulate a DELETE operation returning 3 affected rows
    fake_cursor.rowcount = 3
    fake_cursor.fetchall.return_value = [("dummy",)] * 3
    
    fake_conn.cursor.return_value = fake_cursor
    fake_conn.commit.return_value = None
    fake_conn.close.return_value = None
    
    monkeypatch.setattr(inner_join.psycopg2, "connect", lambda *args, **kwargs: fake_conn)
    return fake_conn

@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    """Prevent real sleep calls to speed up tests"""
    monkeypatch.setattr(time, "sleep", lambda _: None)


# --- Test Classes ---

class TestGetEnvVariable:
    def test_get_env_variable_success(self):
        """Test that environment variables are fetched correctly"""
        assert inner_join.get_env_variable("POSTGRES_DB") == "testdb"

    def test_get_env_variable_missing(self, monkeypatch):
        """Test error handling when an environment variable is missing"""
        monkeypatch.delenv("POSTGRES_DB", raising=False)
        with pytest.raises(EnvironmentError, match="Environment variable 'POSTGRES_DB' is not set."):
            inner_join.get_env_variable("POSTGRES_DB")


class TestDBConnection:
    def test_get_db_connection_success(self, patch_psycopg2_connect):
        """Test that a database connection is established successfully"""
        conn = inner_join.get_db_connection()
        assert conn is not None
        conn.close.assert_called_once()

    def test_get_db_connection_error(self, monkeypatch):
        """Test handling of database connection failure"""
        monkeypatch.setattr(inner_join.psycopg2, "connect", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Connection failed")))
        with pytest.raises(Exception, match="Connection failed"):
            inner_join.get_db_connection()


class TestCreateStagingTables:
    def test_create_staging_tables(self, patch_psycopg2_connect, caplog):
        """Test staging table creation with logging verification"""
        caplog.set_level(logging.INFO)
        inner_join.create_staging_tables()
        assert "Staging tables created successfully." in caplog.text


class TestDeletionFunctions:
    def test_delete_orphaned_records_unitelegale(self, patch_psycopg2_connect, caplog):
        """Test deletion of orphaned records from unitelegale"""
        caplog.set_level(logging.INFO)
        conn = patch_psycopg2_connect
        inner_join.delete_orphaned_records_unitelegale(conn)
        conn.cursor.return_value.execute.assert_called()
        assert "orphaned records deleted from unitelegale" in caplog.text.lower()

    def test_delete_orphaned_records_geolocalisation(self, patch_psycopg2_connect, caplog):
        """Test deletion of orphaned records from geolocalisation"""
        caplog.set_level(logging.INFO)
        conn = patch_psycopg2_connect
        inner_join.delete_orphaned_records_geolocalisation(conn)
        conn.cursor.return_value.execute.assert_called()
        assert "orphaned records deleted from geolocalisation" in caplog.text.lower()


class TestVacuumAnalyze:
    def test_vacuum_analyze(self, patch_psycopg2_connect, caplog):
        """Test that VACUUM ANALYZE is executed"""
        caplog.set_level(logging.INFO)
        conn = patch_psycopg2_connect
        inner_join.vacuum_analyze()
        conn.cursor.return_value.execute.assert_called_with("VACUUM ANALYZE;")
        assert "vacuum analyze completed" in caplog.text.lower()


class TestProcessCleanupTask:
    def test_process_cleanup_task(self, patch_psycopg2_connect, caplog):
        """Test cleanup task execution and connection closure"""
        caplog.set_level(logging.INFO)
        inner_join.main()
        patch_psycopg2_connect.close.assert_called_once()
        assert "Processing cleanup task" in caplog.text.lower()


class TestCleanOrphanRecordsParallel:
    def test_clean_orphan_records_parallel(self, monkeypatch, caplog):
        """Test parallel execution of cleanup tasks"""
        monkeypatch.setattr(inner_join, "ProcessPoolExecutor", MagicMock())
        monkeypatch.setattr(inner_join, "vacuum_analyze", MagicMock())

        caplog.set_level(logging.INFO)
        inner_join.clean_orphan_records_parallel()

        inner_join.vacuum_analyze.assert_called_once()
        assert "Processing cleanup task" in caplog.text
