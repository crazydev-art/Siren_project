"""Module pour charger et mettre à jour les données dans PostgreSQL."""
import io
import os
from datetime import datetime
import psycopg2
from app.src.database.connection import DatabaseConnectionPool
from app.src.utils.logger import DatabaseLogger




def create_log_table():
    """Crée la table de log si elle n'existe pas."""
    db_pool = DatabaseConnectionPool()
    
    try:
        with db_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS updates_log (
                        id SERIAL PRIMARY KEY,
                        entity_type VARCHAR(20),  -- 'etablissement' ou 'unitelegale'
                        entity_id VARCHAR(14),    -- siret ou siren
                        update_type VARCHAR(10),  -- 'INSERT' ou 'UPDATE'
                        update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_log_entity ON updates_log(entity_type, entity_id);
                    CREATE INDEX IF NOT EXISTS idx_log_date ON updates_log(update_date);
                """)
                conn.commit()
    except psycopg2.Error as e:
        print(f"❌ Erreur lors de la création de la table de log: {e}")

def load_data_to_staging(csv_data, table_type):
    """
    Charge les données CSV dans la table staging appropriée.
    
    Args:
        csv_data (str): Données CSV à charger
        table_type (str): 'etablissement' ou 'unitelegale'
    """
    db_pool = DatabaseConnectionPool()
    logger = DatabaseLogger()
    
    # Configuration des tables et colonnes
    table_config = {
        'etablissement': {
            'staging_table': 'staging_etablissement',
            'key_field': 'siret',
            'etat_administratif': 'etatAdministratifEtablissement',
            'columns': """(
                siret, nic, siren, datecreationetablissement,
                trancheeffectifsetablissement, anneeffectifsetablissement,
                activiteprincipaleetablissement, datederniertraitementetablissement,
                etatadministratifetablissement, etablissementsiege,
                enseigne1etablissement, enseigne2etablissement, enseigne3etablissement,
                denominationusuelleetablissement
            )"""
        },
        'unitelegale': {
            'staging_table': 'staging_unite_legale',
            'key_field': 'siren',
            'etat_administratif': 'etatAdministratifUniteLegale',
            'columns': """(
                siren, datecreationunitelegale, trancheeffectifsunitelegale,
                anneeffectifsunitelegale, datederniertraitementunitelegale,
                categorieentreprise, anneecategorieentreprise,
                etatadministratifunitelegale, nomunitelegale,
                nomusageunitelegale, denominationunitelegale,
                categoriejuridiqueunitelegale, activiteprincipaleunitelegale,
                nicsiegeunitelegale
            )"""
        },
        'adresse': {
            'staging_table': 'staging_adresse',
            'key_field': 'siret',
            'columns': """(
                siret, complementadresseetablissement, numerovoieetablissement,
                indicerepetitionetablissement, typevoieetablissement,
                libellevoieetablissement, codepostaletablissement,
                libellecommuneetablissement, codecommuneetablissement
            )"""
        }
    }
    
    config = table_config.get(table_type)
    if not config:
        logger.log_error("STAGING_INSERT", f"Type de table inconnu: {table_type}")
        return False
    
    try:
        with db_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                # Création table temporaire
                cursor.execute(f"""
                CREATE TEMP TABLE temp_staging (LIKE {config['staging_table']})
                ON COMMIT DROP;
                """)

                # Copie des données
                buffer = io.StringIO(csv_data)
                cursor.copy_expert(
                    f"""
                    COPY temp_staging {config['columns']}
                    FROM STDIN WITH (FORMAT CSV, HEADER)
                    """,
                    buffer
                )

                # Insertion données uniques dans la table staging
                cursor.execute(f"""
                INSERT INTO {config['staging_table']}
                SELECT DISTINCT ON ({config['key_field']}) *
                FROM temp_staging;
                """)
                
                rows_affected = cursor.rowcount
                logger.log_staging_operation(f"INSERT_{table_type.upper()}", rows_affected)
            conn.commit()
            print(f"🗄️ Données {table_type} stockées dans staging ({rows_affected} lignes)")
            return True

    except (psycopg2.Error, IOError) as e:
        logger.log_error(f"STAGING_INSERT_{table_type.upper()}", str(e))
        if 'conn' in locals():
            conn.rollback()
        return False

def dump_and_clear_staging(table_type):
    """
    Vide la table staging spécifiée.
    
    Args:
        table_type (str): 'etablissement', 'unitelegale' ou 'adresse'
        
    Returns:
        bool: True si succès, False si échec
    """
    table_mapping = {
        'etablissement': 'staging_etablissement',
        'unitelegale': 'staging_unite_legale',
        'adresse': 'staging_adresse'
    }
    
    staging_table = table_mapping.get(table_type)
    if not staging_table:
        print(f"❌ Type de table inconnu: {table_type}")
        return False
    
    db_pool = DatabaseConnectionPool()
    
    try:
        with db_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {staging_table}")
                conn.commit()
                print(f"🧹 Table {staging_table} vidée")
                return True
            
    except psycopg2.Error as e:
        print(f"❌ Erreur lors du nettoyage de la table staging: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

def update_from_staging(table_type):
    """
    Met à jour la table principale depuis la staging.
    
    Args:
        table_type (str): 'etablissement' ou 'unitelegale'
    Returns:
        tuple: (success: bool, rows_affected: int)
    """
    create_log_table()  # S'assure que la table de log existe
    
    db_pool = DatabaseConnectionPool()
    logger = DatabaseLogger()
    
    table_config = {
        'etablissement': {
            'main_table': 'etablissement',
            'staging_table': 'staging_etablissement',
            'key_field': 'siret',
            'update_champs': """
                datecreationetablissement = s.datecreationetablissement,
                trancheeffectifsetablissement = s.trancheeffectifsetablissement,
                anneeffectifsetablissement = s.anneeffectifsetablissement,
                datederniertraitementetablissement = s.datederniertraitementetablissement,
                etablissementsiege = s.etablissementsiege,
                etatadministratifetablissement = s.etatadministratifetablissement,
                enseigne1etablissement = s.enseigne1etablissement,
                enseigne2etablissement = s.enseigne2etablissement,
                enseigne3etablissement = s.enseigne3etablissement,
                denominationusuelleetablissement = s.denominationusuelleetablissement,
                activiteprincipaleetablissement = s.activiteprincipaleetablissement
            """
        },
        'unitelegale': {
            'main_table': 'unitelegale',
            'staging_table': 'staging_unite_legale',
            'key_field': 'siren',
            'update_champs': """
                datecreationunitelegale = s.datecreationunitelegale,
                trancheeffectifsunitelegale = s.trancheeffectifsunitelegale,
                anneeffectifsunitelegale = s.anneeffectifsunitelegale,
                datederniertraitementunitelegale = s.datederniertraitementunitelegale,
                categorieentreprise = s.categorieentreprise,
                anneecategorieentreprise = s.anneecategorieentreprise,
                etatadministratifunitelegale = s.etatadministratifunitelegale,
                nomunitelegale = s.nomunitelegale,
                nomusageunitelegale = s.nomusageunitelegale,
                denominationunitelegale = s.denominationunitelegale,
                categoriejuridiqueunitelegale = s.categoriejuridiqueunitelegale,
                activiteprincipaleunitelegale = s.activiteprincipaleunitelegale,
                nicsiegeunitelegale = s.nicsiegeunitelegale
            """
        },
        'adresse': {
            'main_table': 'adresse',
            'staging_table': 'staging_adresse',
            'key_field': 'siret',
            'update_champs': """
                complementadresseetablissement = s.complementadresseetablissement,
                numerovoieetablissement = s.numerovoieetablissement,
                indicerepetitionetablissement = s.indicerepetitionetablissement,
                typevoieetablissement = s.typevoieetablissement,
                libellevoieetablissement = s.libellevoieetablissement,
                codepostaletablissement = s.codepostaletablissement,
                libellecommuneetablissement = s.libellecommuneetablissement,
                codecommuneetablissement = s.codecommuneetablissement
            """
        }
    }
    
    config = table_config.get(table_type)
    if not config:
        return (False, 0)
    
    try:
        with db_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                if table_type == 'etablissement':
                    # Identifier et supprimer les établissements qui passent à l'état 'F'
                    cursor.execute("""
                        WITH to_delete AS (
                            DELETE FROM etablissement e
                            USING staging_etablissement s
                            WHERE e.siret = s.siret 
                            AND s.etatadministratifetablissement = 'F'
                            AND e.etatadministratifetablissement = 'A'
                            RETURNING e.siret
                        )
                        INSERT INTO updates_log (entity_type, entity_id, update_type)
                        SELECT 'etablissement', siret, 'DELETE' 
                        FROM to_delete;
                    """)
                    deleted_rows = cursor.rowcount
                else:
                    deleted_rows = 0

                # Mise à jour uniquement pour les établissements actifs
                cursor.execute(f"""
                    WITH updated AS (
                        UPDATE {config['main_table']} e
                        SET {config['update_champs']}
                        FROM {config['staging_table']} s
                        WHERE e.{config['key_field']} = s.{config['key_field']}
                        {" AND s.etatadministratifetablissement = 'A'" if table_type == 'etablissement' else ""}
                        RETURNING e.{config['key_field']}
                    )
                    INSERT INTO updates_log (entity_type, entity_id, update_type)
                    SELECT '{table_type}', {config['key_field']}, 'UPDATE' 
                    FROM updated;
                """)
                
                updated_rows = cursor.rowcount
                
                # Insertion uniquement pour les nouveaux établissements actifs
                cursor.execute(f"""
                    WITH inserted AS (
                        INSERT INTO {config['main_table']}
                        SELECT s.*
                        FROM {config['staging_table']} s
                        WHERE NOT EXISTS (
                            SELECT 1 
                            FROM {config['main_table']} e 
                            WHERE e.{config['key_field']} = s.{config['key_field']}
                        )
                        {" AND s.etatadministratifetablissement = 'A'" if table_type == 'etablissement' else ""}
                        RETURNING {config['key_field']}
                    )
                    INSERT INTO updates_log (entity_type, entity_id, update_type)
                    SELECT '{table_type}', {config['key_field']}, 'INSERT' 
                    FROM inserted;
                """)
                
                inserted_rows = cursor.rowcount
                
            conn.commit()
            if table_type == 'etablissement':
                print(f"✅ {table_type}: {deleted_rows} supprimés (passés à F), {updated_rows} mis à jour, {inserted_rows} insérés")
            else:
                print(f"✅ {table_type}: {updated_rows} mis à jour, {inserted_rows} insérés")
            return (True, updated_rows + inserted_rows)

    except Exception as e:
        logger.log_error(f"MAIN_UPDATE_{table_type.upper()}", str(e))
        if 'conn' in locals():
            conn.rollback()
        return (False, 0)