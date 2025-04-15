import os
import logging
#import psycopg2
#from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
from sqlalchemy import create_engine # to use with pandas
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_env_variable(var_name, default=None, required=True):
    """Fetch an environment variable or raise an error if it's required and not set."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

def get_db_connection():
    """Returns a new database connection."""
    try:
    #     conn = psycopg2.connect(
    #         dbname=get_env_variable('POSTGRES_DB'),
    #         user=get_env_variable('POSTGRES_USER'),
    #         password=get_env_variable('POSTGRES_PASSWORD'),
    #         host=get_env_variable('IPHOST'),
    #         port=get_env_variable('POSTGRES_PORT', '5432', required=False)
    #     )
    #     return conn
    # except psycopg2.Error as e:
    #     #db_connection_errors.inc()
    #     logger.error(f"Database connection error: {e}")
    #     raise
        # Construire l'URL de connexion à partir des variables d'environnement
        db_url = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('IPHOST')}:{os.getenv('POSTGRES_PORT', '5432')}"
            f"/{os.getenv('POSTGRES_DB')}"
        )
        # Créer un moteur SQLAlchemy
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        raise

# def pandas_df(test, chunksize=500000):
#     """Step 0: Read Data from python"""
#     #logger.info("Step : Creating staging tables.")
    
#     conn = get_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT *FROM etablissement;")
#             conn.commit()
#             logger.info("Génèration Dataframe Pandas.")
#         logger.info("Step completed successfully.")
#     except psycopg2.Error as e:
#         logger.error(f"Error creating Dataframe: {e}")
#         # cleanup_errors_total.inc()
#         conn.rollback()
#     finally:
#         conn.close()

# def read_large_table(etablissement, chunksize=500000):
#     """Lit une grande table PostgreSQL en chunks et les concatène dans un DataFrame."""
#     engine = get_db_connection()
#     query = f"SELECT * FROM {etablissement};"
    
#     all_chunks = []  # Liste pour stocker les chunks temporairement
#     total_rows = 0  # Compteur d'enregistrements
    
#     logger.info(f"Lecture de la table {etablissement} en chunks de {chunksize} lignes...")
    
#     for chunk in pd.read_sql(query, engine, chunksize=chunksize):
#         all_chunks.append(chunk)  # Stockage en mémoire
#         total_rows += len(chunk)
#         logger.info(f"Chunk chargé : {len(chunk)} lignes. Total actuel : {total_rows} lignes.")

#     df = pd.concat(all_chunks, ignore_index=True)  # Concaténation finale

#     logger.info(f"Lecture terminée : {total_rows} lignes chargées.")
#     return df



def read_large_table(chunksize=500000):
# def read_large_table(table_name, chunksize=500000):
    """Lit une grande table PostgreSQL en morceaux et retourne un DataFrame."""
    engine = get_db_connection()
    # query = f"SELECT * FROM {table_name};"
    query ="""
    WITH etab AS (
        SELECT * FROM etablissement
    ),
    unite AS (
        SELECT * FROM unitelegale 
        WHERE siren IN (SELECT siren FROM etab)
    ),
    geo AS (
        SELECT * FROM geolocalisation 
        WHERE siret IN (SELECT siret FROM etab)
    )
    SELECT e.*, u.*, g.*
    FROM etab e
    JOIN unite u ON e.siren = u.siren
    JOIN geo g ON e.siret = g.siret;
    """
   
    # Liste pour stocker les morceaux
    all_chunks = []
    total_rows = 0
    
    #print(f"Lecture de la table {table_name} en morceaux de {chunksize} lignes...")
    print("Exécution query en chunks ...")
    
    # Lecture par chunks avec pd.read_sql
    for chunk in pd.read_sql(query, engine, chunksize=chunksize):
        all_chunks.append(chunk)
        total_rows += len(chunk)
        print(f"Morceau chargé : {len(chunk)} lignes. Total actuel : {total_rows} lignes.")
    
    # Concaténation des morceaux en un seul DataFrame
    df = pd.concat(all_chunks, ignore_index=True)
    
    print(f"Lecture terminée : {total_rows} lignes chargées.")
    return df

def preprocess_data(df):
    df = df.dropna()
    X = df.drop(columns=['target_column'])  # Replace with actual target column
    y = df['target_column']
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    models = {
       # "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        # "Logistic Regression": LogisticRegression(max_iter=1000),
        "Support Vector Machine": SVC(),
        "K-Nearest Neighbors": KNeighborsClassifier(),
       # "Decision Tree": DecisionTreeClassifier(),
        "Naive Bayes": GaussianNB(),
        "Gradient Boosting": GradientBoostingClassifier()
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = accuracy
        logger.info(f"{name} Accuracy: {accuracy:.4f}")
        logger.info(f"{name} Classification Report:\n{classification_report(y_test, y_pred)}")

def main():
    
    """Runs the orphaned record deletion followed by database optimization."""
    logger.info("Starting ML process with df load...")
    # Pandas dataframe without any corrections
    df = read_large_table()
    print(df)
    # Analyze Dataframe before applicate Machine Learning
    print(df.columns)
    for col in df.columns:
        unique_values = df[col].nunique()
    
    print(f"{col}: {unique_values} unique values")
    print(df.isnull().sum())  # Count missing values per column
    missing_values = df.isnull().sum()
    unique_values = df.nunique()
    summary = pd.DataFrame({'Unique Values': unique_values, 'Missing Values': missing_values})
    print(summary)
    
if __name__ == "__main__":
    main()