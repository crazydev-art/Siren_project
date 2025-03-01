from prometheus_client import start_http_server, Counter, Histogram
import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
from concurrent.futures import ProcessPoolExecutor

# Githubaction
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 10000  # Batch size for deletions

# Prometheus Metrics
REQUESTS_TOTAL = Counter("script_requests_total", "Total number of cleanup requests")
DELETION_TIME = Histogram("deletion_duration_seconds", "Time taken to delete orphaned records")
DB_CONNECTION_ERRORS = Counter("db_connection_errors_total", "Total database connection errors")

def get_env_variable(var_name, default=None, required=True):
    """Fetch an environment variable or raise an error if it's required and not set."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

def get_db_connection():
    """Returns a new database connection."""
    try:
        conn = psycopg2.connect(
            dbname=get_env_variable('POSTGRES_DB'),
            user=get_env_variable('POSTGRES_USER'),
            password=get_env_variable('POSTGRES_PASSWORD'),
            host=get_env_variable('IPHOST'),
            port=get_env_variable('POSTGRES_PORT', '5432', required=False)
        )
        return conn
    except psycopg2.Error as e:
        DB_CONNECTION_ERRORS.inc()
        logger.error(f"Database connection error: {e}")
        raise

def delete_orphaned_records_unitelegale(conn):
    """Deletes orphaned records in unitelegale where siren doesn't exist in etablissement."""
    start_time = time.time()
    try:
        with conn.cursor() as cursor:
            while True:
                cursor.execute("""
                    DELETE FROM unitelegale AS u
                    WHERE NOT EXISTS (
                        SELECT 1 FROM etablissement AS e
                        WHERE u.siren = e.siren
                    )
                    RETURNING u.siren;
                """)
                deleted_rows = cursor.fetchall()
                conn.commit()
                if not deleted_rows:
                    break
                logger.info(f"{len(deleted_rows)} orphaned records deleted from unitelegale.")
                time.sleep(0.05)  # Short pause for optimization
    except psycopg2.Error as e:
        logger.error(f"Error deleting orphaned records in unitelegale: {e}")
    finally:
        DELETION_TIME.observe(time.time() - start_time)

def delete_orphaned_records_geolocalisation(conn):
    """Deletes orphaned records in geolocalisation where siret doesn't exist in etablissement."""
    start_time = time.time()
    try:
        with conn.cursor() as cursor:
            while True:
                cursor.execute("""
                    DELETE FROM geolocalisation AS g
                    WHERE NOT EXISTS (
                        SELECT 1 FROM etablissement AS e
                        WHERE g.siret = e.siret
                    )
                    RETURNING g.siret;
                """)
                deleted_rows = cursor.fetchall()
                conn.commit()
                if not deleted_rows:
                    break
                logger.info(f"{len(deleted_rows)} orphaned records deleted from geolocalisation.")
                time.sleep(0.05)
    except psycopg2.Error as e:
        logger.error(f"Error deleting orphaned records in geolocalisation: {e}")
    finally:
        DELETION_TIME.observe(time.time() - start_time)

def vacuum_analyze():
    """Performs a VACUUM ANALYZE on the database to optimize performance."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            logger.info("Running VACUUM ANALYZE...")
            cursor.execute("VACUUM ANALYZE;")
            conn.commit()
            logger.info("VACUUM ANALYZE completed.")
    except psycopg2.Error as e:
        logger.error(f"Error during VACUUM ANALYZE: {e}")
    finally:
        conn.close()

def get_valid_siren_and_siret(conn):
    """Dummy function to validate siren and siret values.
    Replace this with actual validation logic if needed."""
    logger.info("Validating siren and siret values...")
    # Add validation logic here if needed.

def process_cleanup_task():
    """Handles orphaned record cleanup in a session."""
    conn = get_db_connection()
    try:
        get_valid_siren_and_siret(conn)
        delete_orphaned_records_unitelegale(conn)
        delete_orphaned_records_geolocalisation(conn)
    finally:
        conn.close()

def clean_orphan_records_parallel():
    """Runs cleanup in parallel using multiple processes."""
    REQUESTS_TOTAL.inc()  # Track cleanup requests
    with ProcessPoolExecutor(max_workers=4) as process_executor:
        tasks = [process_executor.submit(process_cleanup_task) for _ in range(2)]
        for task in tasks:
            task.result()
    vacuum_analyze()

if __name__ == "__main__":
    # Start Prometheus metrics server on port 9000
    start_http_server(9000)
    logger.info("Prometheus metrics server running on port 9000")
    clean_orphan_records_parallel()
