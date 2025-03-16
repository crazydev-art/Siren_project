# pytest inner join
import logging
import os
import time
import pytest
from concurrent.futures import ProcessPoolExecutor

import inner_join  # The module with functions like get_env_variable, get_db_connection, etc.

# --- Database Fake Classes for simulating database interactions ---

class DatabaseFake:
    """Simulate a DB cursor for deletion functions.
    On the first call to fetchall, it returns a non-empty list;
    subsequent calls return an empty list to exit the loop.
    """
    def __init__(self, deletion_rows=3):
        self.deletion_rows = deletion_rows
        self.call_count = 0
        self.queries = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        pass

    def execute(self, query, params=None):
        self.queries.append(query)
        self.call_count += 1
        # Simulate deletion rows on first call, then 0
        if self.call_count == 1:
            self.rowcount = self.deletion_rows
        else:
            self.rowcount = 0

    def fetchall(self):
        if "SELECT" in self.queries[-1][0].upper():
            if self._fetch_state == 0:
                self._fetch_state = 1
                return [('dummy',)] * self.deletion_rows
            else:
                return []
        return []
    # def fetchall(self):
    #     if self.call_count == 1:
    #         # Simulate deletion: return a list with deletion_rows items
    #         return [('dummy',)] * self.deletion_rows
    #     else:
    #         # No more rows to delete
    #         return []

    def close(self):
        pass


class FakeConnection:
    """Simulate a DB connection for deletion and vacuum functions."""
    def __init__(self, deletion_rows=3):
        self.deletion_rows = deletion_rows
        self.closed = False
        self._cursor = DatabaseFake(deletion_rows=self.deletion_rows)

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def close(self):
        self.closed = True


# Dummy Future and Executor for parallel processing tests
class DummyFuture:
    def __init__(self, result):
        self._result = result

    def result(self):
        return self._result


class DummyExecutor:
    def __init__(self, max_workers):
        self.max_workers = max_workers

    def submit(self, func, *args, **kwargs):
        return DummyFuture(func(*args, **kwargs))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# --- Pytest Fixtures ---

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    # Set environment variables required by inner_join.py functions.
    monkeypatch.setenv("POSTGRES_DB", "testdb")
    monkeypatch.setenv("POSTGRES_USER", "testuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")
    monkeypatch.setenv("IPHOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    yield


@pytest.fixture(autouse=True)
def patch_psycopg2_connect(monkeypatch):
    # Override psycopg2.connect to return a FakeConnection.
    monkeypatch.setattr(inner_join.psycopg2, "connect", lambda *args, **kwargs: FakeConnection(deletion_rows=3))


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    # Override time.sleep to avoid actual delays in tests.
    monkeypatch.setattr(time, "sleep", lambda x: None)


# --- Test Classes ---

class TestGetEnvVariable:
    def test_get_env_variable_success(self):
        value = inner_join.get_env_variable("POSTGRES_DB")
        assert value == "testdb"

    def test_get_env_variable_missing(self, monkeypatch):
        monkeypatch.delenv("POSTGRES_DB", raising=False)
        with pytest.raises(EnvironmentError) as excinfo:
            inner_join.get_env_variable("POSTGRES_DB")
        assert "Environment variable 'POSTGRES_DB' is not set." in str(excinfo.value)


class TestDBConnection:
    def test_get_db_connection_success(self):
        conn = inner_join.get_db_connection()
        # Verify that our fake connection was returned.
        assert isinstance(conn, FakeConnection)
        conn.close()

    def test_get_db_connection_error(self, monkeypatch, caplog):
        # Patch psycopg2.connect to raise an error.
        def fake_error(*args, **kwargs):
            raise inner_join.psycopg2.Error("Connection failed")
        monkeypatch.setattr(inner_join.psycopg2, "connect", fake_error)
        with pytest.raises(inner_join.psycopg2.Error):
            inner_join.get_db_connection()
        assert "Database connection error: " in caplog.text
        # Check that the DB_CONNECTION_ERRORS counter was incremented.
        assert inner_join.DB_CONNECTION_ERRORS._value.get() > 0

class TestCreateStagingTables:
    def test_create_staging_tables(self, monkeypatch, caplog):
        caplog.set_level(logging.INFO)
        fake_conn = FakeConnection()
        monkeypatch.setattr(inner_join, "get_db_connection", lambda: fake_conn)
        inner_join.create_staging_tables()
        assert "Staging tables created successfully." in caplog.text

class TestDeletionFunctions:
    def test_delete_orphaned_records_unitelegale(self, caplog):
        caplog.set_level(logging.INFO)  # Ensure INFO level logs are captured
        fake_conn = FakeConnection(deletion_rows=5)
        inner_join.delete_orphaned_records_unitelegale(fake_conn)
        # The DatabaseFake should have been used at least twice (one with rows, one empty).
        assert fake_conn._cursor.call_count >= 2
        # Check that a log message indicates deletion from unitelegale.
        assert "orphaned records deleted from unitelegale" in caplog.text.lower()

    def test_delete_orphaned_records_geolocalisation(self, caplog):
        caplog.set_level(logging.INFO)  # Ensure INFO level logs are captured
        fake_conn = FakeConnection(deletion_rows=4)
        inner_join.delete_orphaned_records_geolocalisation(fake_conn)
        assert fake_conn._cursor.call_count >= 2
        assert "orphaned records deleted from geolocalisation" in caplog.text.lower()


class TestVacuumAnalyze:
    def test_vacuum_analyze(self, monkeypatch, caplog):
        caplog.set_level(logging.INFO)  # Ensure INFO level logs are captured
        # Create a FakeConnection that records executed queries.
        class DatabaseFakeVacuum:
            def __init__(self):
                self.queries = []

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, traceback):
                pass

            def execute(self, query, params=None):
                self.queries.append(query)

            def close(self):
                pass

        class FakeConnectionVacuum:
            def __init__(self):
                self._cursor = DatabaseFakeVacuum()
                self.closed = False

            def cursor(self):
                return self._cursor

            def commit(self):
                pass

            def close(self):
                self.closed = True
            
            def set_isolation_level(self, level):  # 👈 Add this function
                pass  # No real implementation needed for a fake DB

        fake_conn = FakeConnectionVacuum()
        monkeypatch.setattr(inner_join, "get_db_connection", lambda: fake_conn)
        inner_join.vacuum_analyze()
        # Verify that a VACUUM ANALYZE query was executed.
        assert any("VACUUM ANALYZE" in query for query in fake_conn._cursor.queries)
        assert "vacuum analyze completed" in caplog.text.lower()


class TestProcessCleanupTask:
    def test_process_cleanup_task(self, monkeypatch, caplog):
        fake_conn = FakeConnection(deletion_rows=3)
        # Override get_db_connection to always return our fake connection.
        def fake_get_db_connection():
            return fake_conn
        original_get_db_connection = inner_join.get_db_connection
        monkeypatch.setattr(inner_join, "get_db_connection", fake_get_db_connection)
        inner_join.main()
        # Verify that the fake connection was closed after task execution.
        assert fake_conn.closed
        # Restore the original get_db_connection function.
        monkeypatch.setattr(inner_join, "get_db_connection", original_get_db_connection)


class TestCleanOrphanRecordsParallel:
    def test_clean_orphan_records_parallel(self, monkeypatch, caplog):
        # Replace ProcessPoolExecutor with our DummyExecutor.
        monkeypatch.setattr(inner_join, "ProcessPoolExecutor", DummyExecutor)
        # Patch vacuum_analyze to record if it gets called.
        vacuum_called = False

        def fake_vacuum():
            nonlocal vacuum_called
            vacuum_called = True

       
        monkeypatch.setattr(inner_join, "vacuum_analyze", fake_vacuum)
        # Reset the cleanup cleanup_success_total counter.
        inner_join.cleanup_success_total._value.set(0)
       # inner_join.clean_orphan_records_parallel()
        # Check that the REQUESTS_TOTAL counter was incremented.
        assert inner_join.cleanup_success_total._value.get() > 0
        # Verify that vacuum_analyze was called.
        assert vacuum_called
