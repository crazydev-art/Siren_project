import os
import logging
import psycopg2
from psycopg2 import sql
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 10000  # Taille de lot optimisée

def get_env_variable(var_name, default=None, required=True):
    """Fetch an environment variable or raise an error if it's required and not set."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

def get_db_connection():
    """Returns a new database connection."""
    return psycopg2.connect(
        dbname=get_env_variable('POSTGRES_DB'),
        user=get_env_variable('POSTGRES_USER'),
        password=get_env_variable('POSTGRES_PASSWORD'),
        host=get_env_variable('IPHOST'),
        port=get_env_variable('POSTGRES_PORT', '5432', required=False)
    )

def get_valid_siren_and_siret(conn):
    """Creates a temporary table with valid siren and siret from etablissement."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_valid_siren_siret AS
                SELECT siren, siret FROM etablissement;
            """)
            conn.commit()
            logger.info("Table temporaire 'temp_valid_siren_siret' créée.")
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la création de la table temporaire: {e}")
        raise

def delete_orphaned_records_unitelegale(conn):
    """Deletes orphaned records in unitelegale where siren doesn't exist in etablissement."""
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

                logger.info(f"{len(deleted_rows)} enregistrements supprimés de unitelegale.")
                time.sleep(0.05)  # Short pause for optimization
    except psycopg2.Error as e:
        logger.error(f"Erreur suppression unitelegale: {e}")

def delete_orphaned_records_geolocalisation(conn):
    """Deletes orphaned records in geolocalisation where siret doesn't exist in etablissement."""
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

                logger.info(f"{len(deleted_rows)} enregistrements supprimés de geolocalisation.")
                time.sleep(0.05)  # Short pause for optimization
    except psycopg2.Error as e:
        logger.error(f"Erreur suppression geolocalisation: {e}")

def vacuum_analyze():
    """Executes VACUUM ANALYZE to optimize the database after deletion."""
    try:
        conn = get_db_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Required for VACUUM
        with conn.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE;")
            logger.info("VACUUM ANALYZE exécuté avec succès.")
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de VACUUM ANALYZE : {e}")

def clean_orphan_records_parallel():
    """Runs cleanup in parallel using 4 processes and 10 threads per process."""
    with ProcessPoolExecutor(max_workers=4) as process_executor:
        tasks = [process_executor.submit(process_cleanup_task) for _ in range(2)]

        for task in tasks:
            task.result()

    vacuum_analyze()

def process_cleanup_task():
    """Handles orphaned record cleanup in a session."""
    conn = get_db_connection()

    try:
        get_valid_siren_and_siret(conn)
        delete_orphaned_records_unitelegale(conn)
        delete_orphaned_records_geolocalisation(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    clean_orphan_records_parallel()

# import os
# import logging
# import psycopg2
# from psycopg2 import sql
# from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# import bcrypt
# import time
# import functools

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# BATCH_SIZE = 10000  # Taille de lot optimisée

# def get_env_variable(var_name, default=None, required=True):
#     """Fetch an environment variable or raise an error if it's required and not set."""
#     value = os.getenv(var_name, default)
#     if required and value is None:
#         raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
#     return value

# def get_valid_siren_and_siret(conn):
#     """
#     Crée la table temporaire avec les siren et siret valides depuis etablissement.
#     Cette fonction doit être appelée dans chaque connexion, car les tables temporaires
#     sont spécifiques à chaque session.
#     """
#     try:
#         cursor = conn.cursor()

#         # Créer la table temporaire avec les siren et siret valides depuis etablissement
#         cursor.execute("""
#             CREATE TEMPORARY TABLE IF NOT EXISTS temp_valid_siren_siret AS
#             SELECT siren, siret FROM etablissement;
#         """)
#         conn.commit()
#         print("Table temporaire 'temp_valid_siren_siret' créée.")
#     except psycopg2.Error as e:
#         print(f"Erreur lors de la création de la table temporaire: {e}")
#         raise
#     finally:
#         cursor.close()

# def delete_orphaned_records_unitelegale(conn):
#     """Supprime les enregistrements orphelins de unitelegale où le siren n'existe pas dans etablissement."""
#     try:
#         cursor = conn.cursor()

#         while True:
#             # Suppression des enregistrements orphelins dans unitelegale où siren n'existe pas dans etablissement
#             cursor.execute("""
#                 DELETE FROM unitelegale AS u
#                 WHERE NOT EXISTS (
#                     SELECT 1 FROM etablissement AS e
#                     WHERE u.siren = e.siren
#                 )
#                 RETURNING u.siren;
#             """)
            
#             deleted_rows = cursor.fetchall()
#             conn.commit()

#             if not deleted_rows:
#                 break  # Fin du nettoyage
            
#             print(f" {len(deleted_rows)} enregistrements supprimés de unitelegale.")
#             time.sleep(0.05)  # Pause ultra courte pour optimiser
        
#     except psycopg2.Error as e:
#         print(f" Erreur suppression unitelegale: {e}")
#     finally:
#         cursor.close()

# def delete_orphaned_records_geolocalisation(conn):
#     """Supprime les enregistrements orphelins de geolocalisation où le siret n'existe pas dans etablissement."""
#     try:
#         cursor = conn.cursor()

#         while True:
#             # Suppression des enregistrements orphelins dans geolocalisation où siret n'existe pas dans etablissement
#             cursor.execute("""
#                 DELETE FROM geolocalisation AS g
#                 WHERE NOT EXISTS (
#                     SELECT 1 FROM etablissement AS e
#                     WHERE g.siret = e.siret
#                 )
#                 RETURNING g.siret;
#             """)
            
#             deleted_rows = cursor.fetchall()
#             conn.commit()

#             if not deleted_rows:
#                 break  # Fin du nettoyage
            
#             print(f" {len(deleted_rows)} enregistrements supprimés de geolocalisation.")
#             time.sleep(0.05)  # Pause ultra courte pour optimiser
        
#     except psycopg2.Error as e:
#         print(f" Erreur suppression geolocalisation: {e}")
#     finally:
#         cursor.close()

# def vacuum_analyze(conn):
#     """Exécute un VACUUM ANALYZE pour optimiser la base après suppression."""
#     try:
#         cursor = conn.cursor()
#         cursor.execute("VACUUM ANALYZE;")
#         conn.commit()
#         print(" VACUUM ANALYZE exécuté avec succès.")
#     except psycopg2.Error as e:
#         print(f" Erreur lors de VACUUM ANALYZE : {e}")
#     finally:
#         cursor.close()

# def clean_orphan_records_parallel():
#     """Lance la suppression en paquets avec 4 processus et 40 threads au total avec cache."""
#     with ProcessPoolExecutor(max_workers=4) as process_executor:
#         with ThreadPoolExecutor(max_workers=10) as thread_executor:
#             tasks = []
#             for _ in range(2):  # 2 tables à nettoyer : unitelegale et geolocalisation
#                 tasks.append(process_executor.submit(process_cleanup_task))

#             for task in tasks:
#                 task.result()

#     # Connexion globale pour Vacuum
#     conn = psycopg2.connect(
#         dbname=os.getenv('POSTGRES_DB', 'default_user_db'),
#         user=os.getenv('POSTGRES_USER', 'postgres'),
#         password=os.getenv('POSTGRES_PASSWORD', 'password'),
#         host=os.getenv('IPHOST', 'localhost'),
#         port=os.getenv('POSTGRES_PORT', '5432')
#     )
#     vacuum_analyze(conn)
#     conn.close()

# def process_cleanup_task():
#     """Gère la suppression des enregistrements orphelins dans une session."""
#     conn = psycopg2.connect(
#         dbname=os.getenv('POSTGRES_DB', 'default_user_db'),
#         user=os.getenv('POSTGRES_USER', 'postgres'),
#         password=os.getenv('POSTGRES_PASSWORD', 'password'),
#         host=os.getenv('IPHOST', 'localhost'),
#         port=os.getenv('POSTGRES_PORT', '5432')
#     )

#     # Créer la table temporaire
#     get_valid_siren_and_siret(conn)

#     # Suppression des enregistrements orphelins dans `unitelegale`
#     delete_orphaned_records_unitelegale(conn)

#     # Suppression des enregistrements orphelins dans `geolocalisation`
#     delete_orphaned_records_geolocalisation(conn)

#     conn.close()

# if __name__ == "__main__":
#     clean_orphan_records_parallel()
