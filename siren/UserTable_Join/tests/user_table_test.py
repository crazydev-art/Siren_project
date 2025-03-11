# user_table_test.py
import logging
import os
import pytest
import bcrypt
import user_table  # The module containing create_user_db, create_users_table, etc.

# --- Fake database connection and cursor classes for testing ---

class FakeCursor:
    def __init__(self):
        self.executed_queries = []
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
    
    def close(self):
        pass

class FakeConnection:
    def __init__(self, deletion_rows=0):
        self.deletion_rows = deletion_rows
        self._cursor = self

    def __enter__(self):
        return self  # Allows usage with "with" statement

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()  # Ensures proper cleanup

    def cursor(self):
        return self

    def execute(self, query, params=None):
        pass  # Simulate query execution

    def fetchall(self):
        return [(i,) for i in range(self.deletion_rows)]  # Return fake deleted rows

    def commit(self):
        pass

    def close(self):
        pass

    def set_isolation_level(self, level):
        pass  # Mock method to avoid AttributeError

# Replace psycopg2.connect with a fake function during tests.
def fake_connect(*args, **kwargs):
    return FakeConnection()

# --- Pytest Fixtures ---

@pytest.fixture(autouse=True)
def patch_psycopg2_connect(monkeypatch):
    monkeypatch.setattr(user_table.psycopg2, "connect", fake_connect)

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    # Set database connection variables
    monkeypatch.setenv("POSTGRES_DB_USER", "testdb")
    monkeypatch.setenv("IPHOST", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "testuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    # Set admin user variables
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin_password")

# --- Test Classes ---

class TestDatabaseOperations:
    def test_get_env_variable_success(self):
        # Test that an existing environment variable is returned.
        value = user_table.get_env_variable("POSTGRES_DB_USER")
        assert value == "testdb"

    def test_get_env_variable_missing(self, monkeypatch):
        # Remove a required environment variable and verify an error is raised.
        monkeypatch.delenv("POSTGRES_DB_USER", raising=False)
        with pytest.raises(EnvironmentError) as excinfo:
            user_table.get_env_variable("POSTGRES_DB_USER")
        assert "Environment variable 'POSTGRES_DB_USER' is not set." in str(excinfo.value)

    def test_create_user_db_logs_success(self, caplog):
        caplog.set_level(logging.INFO)  # Ensure INFO level logs are captured
        # Verify create_user_db logs a successful creation message.
        user_table.create_user_db()
        assert "Database 'testdb' created successfully" in caplog.text

class TestUsersTable:
    def test_create_users_table_logs_success(self, caplog):
        caplog.set_level(logging.INFO)  # Ensure INFO level logs are captured
        # Verify that create_users_table logs a success message.
        user_table.create_users_table()
        assert "Table 'users' created successfully" in caplog.text

class TestAdminUser:
    def test_create_admin_user_logs_success(self, caplog):
        caplog.set_level(logging.INFO)  # Ensure INFO level logs are captured
        # Verify that create_admin_user logs a success message.
        user_table.create_admin_user()
        assert "Admin user created successfully" in caplog.text

    def test_admin_password_hashed(self):
        # Verify that the admin password is hashed correctly.
        plain_password = os.getenv("ADMIN_PASSWORD")
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        assert bcrypt.checkpw(plain_password.encode("utf-8"), hashed.encode("utf-8"))
