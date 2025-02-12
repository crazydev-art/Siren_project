import os
import psycopg2
from psycopg2 import sql
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt
import time
import functools

BATCH_SIZE = 10000  # Taille de lot optimisée

def get_valid_siren_and_siret(conn):
    """
    Crée la table temporaire avec les siren et siret valides depuis etablissement.
    Cette fonction doit être appelée dans chaque connexion, car les tables temporaires
    sont spécifiques à chaque session.
    """
    try:
        cursor = conn.cursor()

        # Créer la table temporaire avec les siren et siret valides depuis etablissement
        cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS temp_valid_siren_siret AS
            SELECT siren, siret FROM etablissement;
        """)
        conn.commit()
        print("Table temporaire 'temp_valid_siren_siret' créée.")
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de la table temporaire: {e}")
        raise
    finally:
        cursor.close()

def delete_orphaned_records_unitelegale(conn):
    """Supprime les enregistrements orphelins de unitelegale où le siren n'existe pas dans etablissement."""
    try:
        cursor = conn.cursor()

        while True:
            # Suppression des enregistrements orphelins dans unitelegale où siren n'existe pas dans etablissement
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
                break  # Fin du nettoyage
            
            print(f" {len(deleted_rows)} enregistrements supprimés de unitelegale.")
            time.sleep(0.05)  # Pause ultra courte pour optimiser
        
    except psycopg2.Error as e:
        print(f" Erreur suppression unitelegale: {e}")
    finally:
        cursor.close()

def delete_orphaned_records_geolocalisation(conn):
    """Supprime les enregistrements orphelins de geolocalisation où le siret n'existe pas dans etablissement."""
    try:
        cursor = conn.cursor()

        while True:
            # Suppression des enregistrements orphelins dans geolocalisation où siret n'existe pas dans etablissement
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
                break  # Fin du nettoyage
            
            print(f" {len(deleted_rows)} enregistrements supprimés de geolocalisation.")
            time.sleep(0.05)  # Pause ultra courte pour optimiser
        
    except psycopg2.Error as e:
        print(f" Erreur suppression geolocalisation: {e}")
    finally:
        cursor.close()

def vacuum_analyze(conn):
    """Exécute un VACUUM ANALYZE pour optimiser la base après suppression."""
    try:
        cursor = conn.cursor()
        cursor.execute("VACUUM ANALYZE;")
        conn.commit()
        print(" VACUUM ANALYZE exécuté avec succès.")
    except psycopg2.Error as e:
        print(f" Erreur lors de VACUUM ANALYZE : {e}")
    finally:
        cursor.close()

def clean_orphan_records_parallel():
    """Lance la suppression en paquets avec 4 processus et 40 threads au total avec cache."""
    with ProcessPoolExecutor(max_workers=4) as process_executor:
        with ThreadPoolExecutor(max_workers=10) as thread_executor:
            tasks = []
            for _ in range(2):  # 2 tables à nettoyer : unitelegale et geolocalisation
                tasks.append(process_executor.submit(process_cleanup_task))

            for task in tasks:
                task.result()

    # Connexion globale pour Vacuum
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'default_user_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password'),
        host=os.getenv('IPHOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    vacuum_analyze(conn)
    conn.close()

def process_cleanup_task():
    """Gère la suppression des enregistrements orphelins dans une session."""
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'default_user_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password'),
        host=os.getenv('IPHOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

    # Créer la table temporaire
    get_valid_siren_and_siret(conn)

    # Suppression des enregistrements orphelins dans `unitelegale`
    delete_orphaned_records_unitelegale(conn)

    # Suppression des enregistrements orphelins dans `geolocalisation`
    delete_orphaned_records_geolocalisation(conn)

    conn.close()

if __name__ == "__main__":
    clean_orphan_records_parallel()