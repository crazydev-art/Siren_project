from prometheus_client import start_http_server, Counter, Gauge, Histogram
import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
from concurrent.futures import ProcessPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# BATCH_SIZE = 10000  # Batch size for deletions

# Prometheus Metrics
DB_CONNECTION_ERRORS = Counter("db_connection_errors", "Total number of database connection errors")
deleted_unitelegale_total = Counter("deleted_unitelegale_total", "Total orphaned records deleted from unitelegale")
deleted_geolocalisation_total = Counter("deleted_geolocalisation_total", "Total orphaned records deleted from geolocalisation")
vacuum_duration_seconds = Gauge("vacuum_duration_seconds", "Time taken to run VACUUM ANALYZE")
cleanup_errors_total = Counter("cleanup_errors_total", "Total number of cleanup errors")
cleanup_success_total = Counter("cleanup_success_total", "Total number of successful cleanups")
cleanup_step_total = Counter("cleanup_step_total", "Total number of cleanup steps executed", labelnames=["step"])
# REQUESTS_TOTAL = Counter('cleanup_requests_total', 'Total cleanup requests processed')

# Start Prometheus HTTP server on port 9090
start_http_server(9090)

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

def create_staging_tables():
    """Step 0: Create staging tables before cleanup."""
    logger.info("Step : Creating staging tables.")
    cleanup_step_total.labels(step="create_staging").inc()

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS staging_adresse (LIKE adresse);")
            cursor.execute("CREATE TABLE IF NOT EXISTS staging_etablissement (LIKE etablissement);")
            cursor.execute("CREATE TABLE IF NOT EXISTS staging_unite_legale (LIKE unitelegale);")
            conn.commit()
            logger.info("Staging tables created successfully.")
        logger.info("Step completed successfully.")
    except psycopg2.Error as e:
        logger.error(f"Error creating staging tables: {e}")
        cleanup_errors_total.inc()
        conn.rollback()
    finally:
        conn.close()

# Function to delete orphaned records in batches - unitelegale
def delete_orphaned_records_unitelegale(batch_size=10000):
    """Deletes orphaned records from the unitelegale table in batches."""
    conn = get_db_connection()
    total_deleted = 0  # Track total deleted records
    try:
        with conn.cursor() as cursor:
            while True:
                cursor.execute(f"""
                    WITH to_delete AS (
                        SELECT u.siren FROM unitelegale u
                        WHERE NOT EXISTS (
                            SELECT 1 FROM etablissement e WHERE u.siren = e.siren
                        )
                        LIMIT %s  -- ✅ LIMIT is now inside the CTE
                    )
                    DELETE FROM unitelegale
                    WHERE siren IN (SELECT siren FROM to_delete)
                    RETURNING siren;
                """, (batch_size,))
                
                deleted_rows = cursor.fetchall()  # Fetch deleted rows
                conn.commit()  # Commit each batch

                batch_count = len(deleted_rows)
                if batch_count == 0:
                    logger.info("No more orphaned records to delete.")
                    break  # Exit when no more rows are deleted
                
                total_deleted += batch_count
                deleted_unitelegale_total.inc(batch_count)  # Update Prometheus metric
                logger.info(f"Deleted {batch_count} orphaned records (Total: {total_deleted})")

    
    except psycopg2.Error as e:
        logger.error(f"Error during orphaned record deletion: {e}")
        cleanup_errors_total.inc()  # Increment error metric
        conn.rollback()
    finally:
        conn.close()

    
    return total_deleted

def delete_orphaned_records_geolocalisation(batch_size=10000):
    """Deletes orphaned records from the geolocalisation table in batches."""
    conn = get_db_connection()
    total_deleted = 0  # Track total deleted records
    try:
        with conn.cursor() as cursor:
            while True:
                cursor.execute(f"""
                    WITH to_delete AS (
                        SELECT g.siret FROM geolocalisation g
                        WHERE NOT EXISTS (
                            SELECT 1 FROM etablissement e WHERE g.siret = e.siret
                        )
                        LIMIT %s  -- ✅ Uses CTE to limit deletions
                    )
                    DELETE FROM geolocalisation
                    WHERE siret IN (SELECT siret FROM to_delete)
                    RETURNING siret;
                """, (batch_size,))

                deleted_rows = cursor.fetchall()  # Fetch deleted rows
                conn.commit()  # Commit each batch

                batch_count = len(deleted_rows)
                if batch_count == 0:
                    logger.info("No more orphaned records to delete in geolocalisation.")
                    break  # Exit when no more rows are deleted
                    
                total_deleted += batch_count
                deleted_geolocalisation_total.inc(batch_count)  # Update Prometheus metric
                logger.info(f"Deleted {batch_count} orphaned records from geolocalisation (Total: {total_deleted})")

    except psycopg2.Error as e:
        logger.error(f"Error during orphaned record deletion in geolocalisation: {e}")
        cleanup_errors_total.inc()  # Increment error metric
        conn.rollback()
    
    finally:
        conn.close()
        
    return total_deleted


# Function to run VACUUM ANALYZE safely
def vacuum_analyze():
    """Performs VACUUM ANALYZE on the database to optimize performance."""
    conn = get_db_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Ensure VACUUM runs outside a transaction
    start_time = time.time()  # Start timing
    try:
        with conn.cursor() as cursor:
            logger.info("Running VACUUM ANALYZE...")
            cursor.execute("VACUUM ANALYZE;")
            duration = time.time() - start_time  # Calculate duration
            vacuum_duration_seconds.set(duration)  # Update Prometheus metric
            logger.info(f"VACUUM ANALYZE completed in {duration:.2f} seconds.")
    except psycopg2.Error as e:
        logger.error(f"Error during VACUUM ANALYZE: {e}")
        cleanup_errors_total.inc()  # Increment error metric
    finally:
        conn.close()

# Main function to execute the cleanup process
def main():
    
    """Runs the orphaned record deletion followed by database optimization."""
    logger.info("Starting cleanup process...")
    
    deleted_unitelegale = delete_orphaned_records_unitelegale()
    deleted_geolocalisation = delete_orphaned_records_geolocalisation()
    
    create_staging_tables()

    vacuum_analyze()

    if deleted_unitelegale > 0 or deleted_geolocalisation > 0:
        cleanup_success_total.inc()  # Increment success metric
        logger.info(f"Cleanup process completed successfully. Deleted {deleted_unitelegale} from unitelegale and {deleted_geolocalisation} from geolocalisation.")
    else:
        logger.info("Cleanup completed, but no orphaned records were found.")

if __name__ == "__main__":
    main()