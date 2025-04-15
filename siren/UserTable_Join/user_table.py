import os
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt
from prometheus_client import Counter, Histogram, start_http_server
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Prometheus Metrics
DB_CREATE_COUNTER = Counter("db_create_attempts", "Number of attempts to create database")
TABLE_CREATE_COUNTER = Counter("table_create_attempts", "Number of attempts to create admin_users table")
ADMIN_CREATE_COUNTER = Counter("admin_create_attempts", "Number of attempts to create admin user")

DB_CREATE_DURATION = Histogram("db_create_duration_seconds", "Time taken to create database")
TABLE_CREATE_DURATION = Histogram("table_create_duration_seconds", "Time taken to create admin_users table")
ADMIN_CREATE_DURATION = Histogram("admin_create_duration_seconds", "Time taken to create admin user")

def start_metrics_server(port=9000):
    """Starts Prometheus metrics server on the given port."""
    start_http_server(port)
    logger.info(f"Metrics server running on port {port}")

# Utility function to get environment variables
def get_env_variable(var_name, default=None, required=True):
    """Fetch an environment variable or raise an error if it's required and not set."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

@DB_CREATE_DURATION.time()
def create_user_db():
    DB_CREATE_COUNTER.inc()
    db_name = get_env_variable('POSTGRES_DB_USER')
    db_host = get_env_variable('IPHOST')
    db_user = get_env_variable('POSTGRES_USER')
    db_password = get_env_variable('POSTGRES_PASSWORD')
    db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

    try:
        conn = psycopg2.connect(
            dbname="postgres", user=db_user, password=db_password, host=db_host, port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            logger.info(f"Database '{db_name}' created successfully.")
        
        conn.close()
    except psycopg2.errors.DuplicateDatabase:
        logger.info(f"Database '{db_name}' already exists.")
    except psycopg2.Error as e:
        logger.error(f"An error occurred while creating the database: {e}")
    finally:
        if conn:
            conn.close()

@TABLE_CREATE_DURATION.time()
def create_users_table():
    TABLE_CREATE_COUNTER.inc()
    db_name = get_env_variable('POSTGRES_DB_USER')
    db_host = get_env_variable('IPHOST')
    db_user = get_env_variable('POSTGRES_USER')
    db_password = get_env_variable('POSTGRES_PASSWORD')
    db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

    try:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        hashed_password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("Table 'admin_users' created successfully.")
    except psycopg2.Error as e:
        logger.error(f"An error occurred while creating the table: {e}")

@ADMIN_CREATE_DURATION.time()
def create_admin_user():
    ADMIN_CREATE_COUNTER.inc()
    db_name = get_env_variable('POSTGRES_DB_USER')
    db_host = get_env_variable('IPHOST')
    db_user = get_env_variable('POSTGRES_USER')
    db_password = get_env_variable('POSTGRES_PASSWORD')
    db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

    admin_username = get_env_variable('ADMIN_USERNAME', 'admin', required=False)
    admin_email = get_env_variable('ADMIN_EMAIL', 'admin@gmail.com', required=False)
    admin_password = get_env_variable('ADMIN_PASSWORD', 'admin_password', required=False)

    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO admin_users (username, email, password)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                """, (admin_username, admin_email, hashed_password))
                conn.commit()
                logger.info("Admin user created successfully (or already exists).")
    except psycopg2.Error as e:
        logger.error(f"An error occurred while creating the admin user: {e}")

if __name__ == "__main__":
    # Start Prometheus metrics server in a separate thread
    metrics_thread = threading.Thread(target=start_metrics_server, args=(9000,), daemon=True)
    metrics_thread.start()

    create_user_db()
    create_users_table()
    create_admin_user()