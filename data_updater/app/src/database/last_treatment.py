"""Module pour récupérer la dernière date de traitement depuis la base de données."""

import psycopg2
from app.src.database.connection import DatabaseConnectionPool

def get_latest_treatment_date(table_name: str):
    """
    Récupère la dernière date de traitement depuis la table spécifiée.
    
    Args:
        table_name (str): 'etablissement' ou ''
        
    Returns:
        str: Date au format 'YYYY-MM-DD' ou None si erreur
    """
    if not table_name:
        print("Erreur : Le nom de la table n'est pas spécifié.")
        return None
            
    # Mapping des colonnes de date selon le type de table
    date_columns = {
        'etablissement': 'datederniertraitementetablissement',
        'unitelegale': 'datederniertraitementunitelegale'
    }
    
    if table_name not in date_columns:
        print(f"Erreur : Type de table inconnu '{table_name}'")
        return None
    
    db_pool = DatabaseConnectionPool()
    
    try:
        with db_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                # Requête pour obtenir la dernière date
                query = f"""
                    SELECT {date_columns[table_name]}
                    FROM {table_name}
                    ORDER BY {date_columns[table_name]} DESC 
                    LIMIT 1
                """
                cursor.execute(query)
                result = cursor.fetchone()
                
                if result and result[0]:
                    return result[0].strftime("%Y-%m-%d")
                return None
                
    except psycopg2.Error as e:
        print(f"Erreur de base de données: {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return None



