import os
import logging
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, precision_recall_curve
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # This loads environment variables from a .env file

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Then check for required variables
required_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.info("Using fallback sample data for testing")

def get_env_variable(var_name, default=None, required=True):
    """Fetch an environment variable or raise an error if it's required and not set."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

def get_db_connection():
    """Returns a new database connection."""
    try:
        # Construire l'URL de connexion à partir des variables d'environnement
        db_url = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('IPHOST')}:{os.getenv('POSTGRES_PORT', '5432')}"
            f"/{os.getenv('POSTGRES_DB')}"
        )

        # Add logging to see the connection string (without password)
        log_url = db_url.replace(os.getenv('POSTGRES_PASSWORD', ''), '******')
        logger.info(f"Attempting to connect with: {log_url}")
        
        # Créer un moteur SQLAlchemy
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données : {e}")
        raise
    
def read_large_table(chunksize=500000, limit=None):
    """Lit une grande table PostgreSQL en morceaux avec les données pertinentes pour l'analyse de viabilité."""
    engine = get_db_connection()
    
     # Ajout d'une limite au nombre de lignes
    limit_clause = f"LIMIT {limit}" if limit else ""

    # Requête SQL optimisée pour extraire des attributs pertinents à la viabilité
    # Tablesample System(10) pour définir un échantillon de 10%.
    query = f"""
    WITH etab AS (
        SELECT * FROM etablissement
        TABLESAMPLE SYSTEM(10)  
        WHERE etatadministratifetablissement IS NOT NULL
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
    JOIN geo g ON e.siret = g.siret
    {limit_clause}
    """
   
    all_chunks = []
    total_rows = 0
    
    logger.info("Exécution query en chunks pour analyse de viabilité...")
    
    # Lecture par chunks avec pd.read_sql
    for chunk in pd.read_sql(query, engine, chunksize=chunksize):
        all_chunks.append(chunk)
        total_rows += len(chunk)
        logger.info(f"Morceau chargé : {len(chunk)} lignes. Total actuel : {total_rows} lignes.")

        # Sortir de la boucle si on a atteint la limite
        if limit and total_rows >= limit:
            break
    
    # Concaténation des morceaux en un seul DataFrame
    df = pd.concat(all_chunks, ignore_index=True)
    
    logger.info(f"Lecture terminée : {total_rows} lignes chargées.")
    return df

def create_viability_features(df):
    """Crée des features pertinentes pour l'analyse de viabilité."""
    logger.info("Création de features pour l'analyse de viabilité...")
    
    # Convertir seulement les colonnes de date nécessaires
    date_columns = ['datecreationunitelegale', 'datecreationetablissement']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Feature 1: Age de l'entreprise en années
    current_date = datetime.now()
    if 'datecreationunitelegale' in df.columns:
        df['age_entreprise'] = ((current_date - df['datecreationunitelegale']).dt.days / 365.25)
    elif 'datecreationetablissement' in df.columns:
        df['age_entreprise'] = ((current_date - df['datecreationetablissement']).dt.days / 365.25)
    
    # Utilisation de méthodes plus performantes pour les transformations
    # Vectorisation au lieu de apply() où possible

    # Feature 2: Conversion des tranches d'effectifs en valeurs numériques (estimation)
    tranche_mapping = {
        'NN': 0,  # Non renseigné
        '00': 0,  # 0 salarié
        '01': 1,  # 1-2 salariés
        '02': 2,  # 3-5 salariés
        '03': 4,  # 6-9 salariés
        '11': 10, # 10-19 salariés
        '12': 20, # 20-49 salariés
        '21': 50, # 50-99 salariés
        '22': 100, # 100-199 salariés
        '31': 250, # 200-249 salariés
        '32': 500, # 250-499 salariés
        '41': 1000, # 500-999 salariés
        '42': 2000, # 1000-1999 salariés
        '51': 5000, # 2000-4999 salariés
        '52': 10000 # 5000+ salariés
    }
    
    if 'trancheeffectifsunitelegale' in df.columns:
        df['effectif_estime'] = df['trancheeffectifsunitelegale'].map(tranche_mapping).fillna(0)
    elif 'trancheeffectifsetablissement' in df.columns:
        df['effectif_estime'] = df['trancheeffectifsetablissement'].map(tranche_mapping).fillna(0)
    
    # Feature 3: Est-ce le siège social?
    # if 'etablissementsiege' in df.columns:
    #     df['est_siege'] = df['etablissementsiege'].apply(lambda x: 1 if x == 'true' or x == True else 0)
    if 'etablissementsiege' in df.columns:
        df['est_siege'] = np.where(df['etablissementsiege'].isin(['true', True]), 1, 0)
    
    # Feature 4: Extraction du secteur d'activité (2 premiers chiffres du code NAF)
    if 'activiteprincipaleunitelegale' in df.columns:
        df['secteur_activite'] = df['activiteprincipaleunitelegale'].astype(str).str[:2]
    elif 'activiteprincipaleetablissement' in df.columns:
        df['secteur_activite'] = df['activiteprincipaleetablissement'].astype(str).str[:2]
    
    # Feature 5: Indice de densité économique basé sur les coordonnées géographiques (clusters)
    # Cette feature utilise le clustering pour estimer si l'entreprise est dans une zone économique dense
    # geo_columns = ['longitude', 'latitude']
    # if all(col in df.columns for col in geo_columns) and df[geo_columns].notna().all(axis=1).sum() > 100:
    #     # On prend un échantillon pour le clustering si le dataset est grand
    #     sample_size = min(10000, len(df))
    #     geo_sample = df[geo_columns].dropna().sample(sample_size)
        
    #     # Création de clusters géographiques
    #     kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
    #     kmeans.fit(geo_sample)
        
    #     # Assigner chaque entreprise à un cluster
    #     geo_data = df[geo_columns].dropna()
    #     df.loc[geo_data.index, 'geo_cluster'] = kmeans.predict(geo_data)
        
    #     # Calculer la densité d'entreprises par cluster
    #     cluster_density = df['geo_cluster'].value_counts().to_dict()
    #     df['densite_zone'] = df['geo_cluster'].map(cluster_density)
        
    #     # Normaliser la densité
    #     max_density = df['densite_zone'].max()
    #     if max_density > 0:
    #         df['densite_zone'] = df['densite_zone'] / max_density
    
     # Utiliser un sous-échantillon plus petit pour le clustering
    geo_columns = ['longitude', 'latitude']
    if all(col in df.columns for col in geo_columns) and df[geo_columns].notna().all(axis=1).sum() > 100:
        # Réduire la taille de l'échantillon pour le clustering
        sample_size = min(5000, len(df))
        geo_sample = df[geo_columns].dropna().sample(sample_size)
        
        # Clustering simplifié
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(geo_sample)
        
        # Appliquer le clustering uniquement aux lignes avec coordonnées valides
        valid_geo_indices = df[geo_columns].dropna().index
        df.loc[valid_geo_indices, 'geo_cluster'] = kmeans.predict(df.loc[valid_geo_indices, geo_columns])
        
        # Calculer la densité de manière optimisée
        cluster_counts = df['geo_cluster'].value_counts()
        df['densite_zone'] = df['geo_cluster'].map(cluster_counts) / cluster_counts.max()

    # Feature 6: Création de variables binaires pour l'état administratif (notre cible potentielle)
    # if 'etatadministratifunitelegale' in df.columns:
    #     # On considère "A" (Actif) comme viable, tout le reste comme non viable
    #     df['est_viable'] = (df['etatadministratifunitelegale'] == 'A').astype(int)
    # elif 'etatadministratifetablissement' in df.columns:
    #     df['est_viable'] = (df['etatadministratifetablissement'] == 'A').astype(int)
    
    # # Feature 7: Économie sociale et solidaire (potentiellement plus résiliente)
    # if 'economiessocialesolidaireunitelegale' in df.columns:
    #     df['est_ess'] = (df['economiessocialesolidaireunitelegale'] == 'O').astype(int)
    
    # # Feature 8: Est employeur
    # if 'caractereemployeurunitelegale' in df.columns:
    #     df['est_employeur'] = (df['caractereemployeurunitelegale'] == 'O').astype(int)
    
    # # Feature 9: Catégorie d'entreprise
    # if 'categorieentreprise' in df.columns:
    #     categorie_map = {
    #         'PME': 1,
    #         'ETI': 2,
    #         'GE': 3,
    #         'TPE': 0
    #     }
    #     df['taille_entreprise'] = df['categorieentreprise'].map(categorie_map).fillna(0)
    
    # # Feature 10: Code postal comme indicateur socio-économique (premiers chiffres)
    # if 'codePostalEtablissement' in df.columns:
    #     df['region_code'] = df['codePostalEtablissement'].astype(str).str[:2]
    
    # logger.info("Features créées avec succès")
    
    # # Affichage des features nouvellement créées
    # new_features = ['age_entreprise', 'effectif_estime', 'est_siege', 'secteur_activite', 
    #                  'est_viable', 'est_ess', 'est_employeur', 'taille_entreprise', 'region_code']
    # existing_features = [f for f in new_features if f in df.columns]
    # logger.info(f"Features disponibles pour analyse: {existing_features}")
    if 'etatadministratifunitelegale' in df.columns:
        df['est_viable'] = (df['etatadministratifunitelegale'] == 'A').astype(int)
    elif 'etatadministratifetablissement' in df.columns:
        df['est_viable'] = (df['etatadministratifetablissement'] == 'A').astype(int)
    
    # Feature 7-9: Features binaires - optimisées
    if 'economiessocialesolidaireunitelegale' in df.columns:
        df['est_ess'] = (df['economiessocialesolidaireunitelegale'] == 'O').astype(int)
    
    if 'caractereemployeurunitelegale' in df.columns:
        df['est_employeur'] = (df['caractereemployeurunitelegale'] == 'O').astype(int)
    
    if 'categorieentreprise' in df.columns:
        categorie_map = {'PME': 1, 'ETI': 2, 'GE': 3, 'TPE': 0}
        df['taille_entreprise'] = df['categorieentreprise'].map(categorie_map).fillna(0)
    
    # Feature 10: Code postal - optimisé
    if 'codePostalEtablissement' in df.columns:
        df['region_code'] = df['codePostalEtablissement'].astype(str).str[:2]
    return df

def analyze_viability_factors(df, generate_plots=True):
    """Analyse les facteurs affectant la viabilité des entreprises."""
    logger.info("Analyse des facteurs de viabilité...")
    
    if 'est_viable' not in df.columns:
        logger.error("Variable cible 'est_viable' non disponible dans les données")
        return
    
    # Résumé de la viabilité
    viability_summary = df['est_viable'].value_counts(normalize=True)
    logger.info(f"Distribution de la viabilité: {viability_summary}")
    
    # Liste des features numériques potentiellement importantes
    numeric_features = ['age_entreprise', 'effectif_estime', 'est_siege', 
                        'est_ess', 'est_employeur', 'taille_entreprise']
    
    # Analyse de corrélation avec la viabilité pour les features numériques
    available_numeric = [f for f in numeric_features if f in df.columns]
    
    if available_numeric:
        correlation = df[available_numeric + ['est_viable']].corr()['est_viable'].sort_values(ascending=False)
        logger.info(f"Corrélation avec la viabilité:\n{correlation}")
        
        # Visualisation des corrélations
        plt.figure(figsize=(10, 6))
        correlation.drop('est_viable').plot(kind='bar')
        plt.title('Corrélation des features avec la viabilité')
        plt.tight_layout()
        plt.savefig('viability_correlation.png')
    
    # Analyse par secteur d'activité
    if 'secteur_activite' in df.columns:
        sector_viability = df.groupby('secteur_activite')['est_viable'].mean().sort_values(ascending=False)
        logger.info(f"Taux de viabilité par secteur d'activité (top 10):\n{sector_viability.head(10)}")
        
        # Visualisation des secteurs les plus viables
        plt.figure(figsize=(12, 6))
        sector_viability.head(15).plot(kind='bar')
        plt.title('Taux de viabilité par secteur d\'activité')
        plt.tight_layout()
        plt.savefig('sector_viability.png')
    
    # Analyse par âge d'entreprise
    if 'age_entreprise' in df.columns:
        # Création de tranches d'âge
        df['tranche_age'] = pd.cut(df['age_entreprise'], 
                                 bins=[0, 1, 3, 5, 10, 20, float('inf')],
                                 labels=['<1 an', '1-3 ans', '3-5 ans', '5-10 ans', '10-20 ans', '>20 ans'])
        age_viability = df.groupby('tranche_age')['est_viable'].mean()
        logger.info(f"Taux de viabilité par âge d'entreprise:\n{age_viability}")
        
        # Visualisation de la viabilité par âge
        plt.figure(figsize=(10, 6))
        age_viability.plot(kind='bar')
        plt.title('Taux de viabilité par âge d\'entreprise')
        plt.tight_layout()
        plt.savefig('age_viability.png')
    
    # Analyse par taille d'entreprise (effectifs)
    if 'effectif_estime' in df.columns:
        # Création de tranches d'effectifs
        df['tranche_effectif'] = pd.cut(df['effectif_estime'], 
                                      bins=[0, 1, 10, 50, 250, float('inf')],
                                      labels=['0', '1-9', '10-49', '50-249', '250+'])
        size_viability = df.groupby('tranche_effectif')['est_viable'].mean()
        logger.info(f"Taux de viabilité par taille d'entreprise:\n{size_viability}")
        
        # Visualisation de la viabilité par taille
        plt.figure(figsize=(10, 6))
        size_viability.plot(kind='bar')
        plt.title('Taux de viabilité par taille d\'entreprise')
        plt.tight_layout()
        plt.savefig('size_viability.png')
    
    # Analyse par région (si disponible)
    if 'region_code' in df.columns:
        region_viability = df.groupby('region_code')['est_viable'].mean().sort_values(ascending=False)
        logger.info(f"Taux de viabilité par région (top 10):\n{region_viability.head(10)}")
        
        # Visualisation des régions les plus viables
        plt.figure(figsize=(12, 6))
        region_viability.head(15).plot(kind='bar')
        plt.title('Taux de viabilité par région')
        plt.tight_layout()
        plt.savefig('region_viability.png')

    if generate_plots:
        # Génération des visualisations
        plt.figure(figsize=(10, 6))
        # ... reste du code de visualisation ...
    else:
        logger.info("Visualisations désactivées pour optimiser les performances")

def prepare_viability_model_data(df):
    """Prépare les données pour le modèle de prédiction de viabilité."""
    logger.info("Préparation des données pour le modèle de viabilité...")
    class_distribution = df['est_viable'].value_counts()
    logger.info(f"Distribution des classes avant modélisation:\n{class_distribution}")
    
    if 'est_viable' not in df.columns:
        logger.error("Variable cible 'est_viable' non disponible dans les données")
        return None, None, None, None, None, None
    
    # Suppression des lignes où la cible est nulle
    df = df.dropna(subset=['est_viable'])
    
    # Liste des features potentielles
    potential_features = [
        'age_entreprise', 'effectif_estime', 'est_siege', 'secteur_activite',
        'est_ess', 'est_employeur', 'taille_entreprise', 'region_code'
    ]
    
    # Identifier les features disponibles
    available_features = [f for f in potential_features if f in df.columns]
    logger.info(f"Features disponibles pour le modèle: {available_features}")
    
    # Séparer les features catégorielles et numériques
    categorical_features = ['secteur_activite', 'region_code']
    categorical_features = [f for f in categorical_features if f in available_features]
    
    numerical_features = [f for f in available_features if f not in categorical_features]
    
    # Vérification des données manquantes
    missing_data = df[available_features].isnull().sum()
    logger.info(f"Valeurs manquantes dans les features:\n{missing_data}")
    
    # Création du dataset pour le ML
    X = df[available_features]
    y = df['est_viable']
    
    # # Division en ensembles d'entraînement et de test, stratifiée pour conserver les proportions de classes
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # logger.info(f"Dimensions de X_train: {X_train.shape}, X_test: {X_test.shape}")
    # logger.info(f"Distribution de la variable cible - Train: {y_train.value_counts(normalize=True)}")
    # logger.info(f"Distribution de la variable cible - Test: {y_test.value_counts(normalize=True)}")
    
    # return X_train, X_test, y_train, y_test, categorical_features, numerical_features
    # Division en ensembles d'entraînement et de test
    # Utiliser stratify seulement si toutes les classes ont au moins 2 échantillons

      # Vérification de la distribution des classes
    class_counts = y.value_counts()
    logger.info(f"Distribution des classes: {class_counts}")
    
    if class_counts.min() >= 2:
        logger.info("Utilisation de la stratification pour la division train/test")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    else:
        logger.warning("Impossible d'utiliser la stratification: certaines classes ont moins de 2 échantillons")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    logger.info(f"Dimensions de X_train: {X_train.shape}, X_test: {X_test.shape}")
    logger.info(f"Distribution de la variable cible - Train: {y_train.value_counts(normalize=True)}")
    logger.info(f"Distribution de la variable cible - Test: {y_test.value_counts(normalize=True)}")
    
    return X_train, X_test, y_train, y_test, categorical_features, numerical_features

def create_viability_model_pipeline(categorical_features, numerical_features):
    """Crée un pipeline de prétraitement et modélisation pour prédire la viabilité."""
    
    # Préprocessing pour les colonnes numériques
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Préprocessing pour les colonnes catégorielles
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # Combinaison des préprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    return preprocessor

def train_viability_models(X_train, X_test, y_train, y_test, preprocessor):
    """Entraîne et évalue des modèles pour prédire la viabilité des entreprises."""
    logger.info("Entraînement des modèles de prédiction de viabilité...")
    
    # if fast_mode:
    #     models = {
    #         "Random Forest": RandomForestClassifier(n_estimators=50, class_weight='balanced', 
    #                                               random_state=42, n_jobs=-1)
    #     }
    # else:
    #     models = {
    #         "Régression Logistique": LogisticRegression(max_iter=500, class_weight='balanced'),
    #         "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', 
    #                                               random_state=42, n_jobs=-1),
    #         "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    #         "K Plus Proches Voisins": KNeighborsClassifier(n_neighbors=5)
    #     }


    # Définition des modèles à tester
    models = {
        "Régression Logistique": LogisticRegression(max_iter=1000, class_weight='balanced'),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "K Plus Proches Voisins": KNeighborsClassifier(n_neighbors=5)
    }
    
    results = {}
    feature_importances = {}
    best_auc = 0
    best_model_name = ""
    best_pipeline = None
    
    for name, model in models.items():
        logger.info(f"Entraînement du modèle: {name}")
        
        # Création du pipeline complet
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('feature_selection', SelectKBest(mutual_info_classif, k='all')),  # On garde toutes les features pour l'instant
            ('classifier', model)
        ])
        
        # Entraînement
        pipeline.fit(X_train, y_train)
        
        # Prédictions
        y_pred = pipeline.predict(X_test)
        
        # Probabilités (pour ROC AUC)
        if hasattr(pipeline[-1], "predict_proba"):
            y_proba = pipeline.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, y_proba)
        else:
            auc = 0
        
        # Évaluation
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = {
            'accuracy': accuracy,
            'auc': auc
        }
        
        if auc > best_auc:
            best_auc = auc
            best_model_name = name
            best_pipeline = pipeline
        
        logger.info(f"{name} - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
        logger.info(f"Rapport de classification:\n{classification_report(y_test, y_pred, zero_division=0)}")
        
        # Matrice de confusion
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f'Matrice de confusion - {name}')
        plt.xlabel('Prédit')
        plt.ylabel('Réel')
        plt.savefig(f'confusion_matrix_viability_{name.replace(" ", "_")}.png')
        
        # Extraction des importances de features (si disponible)
        if hasattr(pipeline[-1], "feature_importances_"):
            feature_names = get_feature_names_from_pipeline(pipeline, X_train.columns)
            importance = pipeline[-1].feature_importances_
            feature_importances[name] = dict(zip(feature_names, importance))
    
    # Affichage des résultats comparatifs
    plt.figure(figsize=(12, 6))
    accuracy_values = [results[model]['accuracy'] for model in models.keys()]
    auc_values = [results[model]['auc'] for model in models.keys()]
    
    x = np.arange(len(models))
    width = 0.35
    
    plt.bar(x - width/2, accuracy_values, width, label='Accuracy')
    plt.bar(x + width/2, auc_values, width, label='AUC')
    
    plt.title('Comparaison des performances des modèles de viabilité')
    plt.xlabel('Modèle')
    plt.ylabel('Score')
    plt.xticks(x, models.keys(), rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('viability_model_comparison.png')
    
    # Visualisation des importances de features pour le meilleur modèle
    if best_model_name in feature_importances:
        plt.figure(figsize=(12, 8))
        importances = feature_importances[best_model_name]
        sorted_indices = np.argsort([v for v in importances.values()])
        
        plt.barh(range(len(sorted_indices)), 
                [list(importances.values())[i] for i in sorted_indices], 
                align='center')
        plt.yticks(range(len(sorted_indices)), 
                [list(importances.keys())[i] for i in sorted_indices])
        plt.title(f'Importance des features - {best_model_name}')
        plt.tight_layout()
        plt.savefig('feature_importance_viability.png')
    
    logger.info(f"Meilleur modèle: {best_model_name} avec un AUC de {best_auc:.4f}")
    
    return results, best_model_name, best_pipeline

def get_feature_names_from_pipeline(pipeline, input_features):
    """Extrait les noms des features après transformation par le pipeline."""
    # Pour les pipelines avec ColumnTransformer
    if hasattr(pipeline[0], 'transformers_'):
        # Extrait les noms de colonnes après one-hot encoding
        preprocessor = pipeline[0]
        cat_cols = []
        num_cols = []
        
        for transformer_name, transformer, column_names in preprocessor.transformers_:
            if transformer_name == 'cat':
                for col in column_names:
                    # Vérifier si le transformer a des catégories
                    if hasattr(transformer.named_steps['encoder'], 'categories_'):
                        for category in transformer.named_steps['encoder'].categories_[column_names.index(col)]:
                            cat_cols.append(f"{col}_{category}")
                    else:
                        # Fallback si les catégories ne sont pas accessibles
                        cat_cols.append(col)
            elif transformer_name == 'num':
                num_cols.extend(column_names)
        
        return num_cols + cat_cols
    else:
        # Fallback pour les pipelines simples
        return input_features

def viability_score_interpretation(model, preprocessor, categorical_features, numerical_features):
    """Interprète le modèle pour fournir des insights sur les facteurs de viabilité."""
    logger.info("Interprétation du modèle de viabilité...")
    
    # Cette fonction va générer des interprétations concrètes des résultats du modèle
    # Par exemple, les seuils critiques pour les variables numériques et les catégories à risque/favorables
    
    if not hasattr(model, 'feature_importances_'):
        logger.info("Le modèle ne fournit pas d'importance de features interprétable")
        return
    
    # Récupération des noms des features après prétraitement
    feature_names = get_feature_names_from_pipeline(
        Pipeline([('preprocessor', preprocessor)]), 
        numerical_features + categorical_features)
    
    # Importance des features
    importances = dict(zip(feature_names, model.feature_importances_))
    sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    
    logger.info("Facteurs influençant la viabilité des entreprises (par ordre d'importance):")
    for feature, importance in sorted_importances[:10]:  # Top 10 features
        logger.info(f"- {feature}: {importance:.4f}")
    
    # Génération d'un rapport de recommandations
    with open('viability_insights.txt', 'w') as f:
        f.write("RAPPORT D'ANALYSE DE VIABILITÉ DES ENTREPRISES\n")
        f.write("===========================================\n\n")
        
        f.write("1. FACTEURS DÉTERMINANTS POUR LA VIABILITÉ\n")
        for i, (feature, importance) in enumerate(sorted_importances[:10], 1):
            f.write(f"   {i}. {feature}: {importance:.4f}\n")
        
        f.write("\n2. INTERPRÉTATION ET RECOMMANDATIONS\n")
        
        # Analyse des features numériques importantes
        numeric_insights = [f for f in sorted_importances if any(nf in f[0] for nf in numerical_features)]
        if numeric_insights:
            f.write("\n   A. Indicateurs quantitatifs clés:\n")
            for feature, importance in numeric_insights[:5]:
                if 'age' in feature.lower():
                    f.write(f"      - L'âge de l'entreprise est un facteur crucial (importance: {importance:.4f})\n")
                    f.write("        Les entreprises bien établies ont généralement plus de résilience.\n")
                elif 'effectif' in feature.lower():
                    f.write(f"      - La taille de l'effectif est significative (importance: {importance:.4f})\n")
                    f.write("        Les entreprises avec un nombre stable d'employés montrent une meilleure viabilité.\n")
                elif 'siege' in feature.lower():
                    f.write(f"      - Le statut de siège social est un indicateur (importance: {importance:.4f})\n")
                    f.write("        Les établissements sièges ont généralement une longévité supérieure.\n")
        
        # Analyse des features catégorielles importantes
        categorical_insights = [f for f in sorted_importances if any(cf in f[0] for cf in categorical_features)]
        if categorical_insights:
            f.write("\n   B. Facteurs catégoriels déterminants:\n")
            for feature, importance in categorical_insights[:5]:
                if 'secteur' in feature.lower():
                    f.write(f"      - Le secteur d'activité est déterminant (importance: {importance:.4f})\n")
                    f.write("        Certains secteurs montrent une résilience supérieure.\n")
                elif 'region' in feature.lower():
                    f.write(f"      - La localisation géographique impacte la viabilité (importance: {importance:.4f})\n")
                    f.write("        Les zones à forte densité économique offrent généralement plus d'opportunités.\n")
        
        f.write("\n3. CONCLUSION\n")
        f.write("   Ce modèle permet d'identifier les entreprises à risque sans recourir au chiffre d'affaires,\n")
        f.write("   en se basant sur des caractéristiques structurelles et géographiques.")
    
    logger.info("Rapport d'insights généré: viability_insights.txt")

def main(sample_size=None, fast_mode=False, generate_plots=True):
    """Exécute le pipeline d'analyse de viabilité des entreprises."""
    logger.info("Démarrage de l'analyse de viabilité des entreprises...")
    
    try:
        # 1. Chargement des données avec une taille d'échantillon spécifiée
        df = read_large_table(limit=sample_size)
        
        # 2. Création des features pertinentes pour l'analyse de viabilité
        df = create_viability_features(df)
        
        # 3. Analyse des facteurs de viabilité
        analyze_viability_factors(df)
        
        # 4. Préparation des données pour le modèle
        X_train, X_test, y_train, y_test, categorical_features, numerical_features = prepare_viability_model_data(df)
        
        if X_train is not None:
            # 5. Création du pipeline de prétraitement
            preprocessor = create_viability_model_pipeline(categorical_features, numerical_features)
            
            # 6. Entraînement et évaluation des modèles
            results, best_model_name, best_pipeline = train_viability_models(X_train, X_test, y_train, y_test, preprocessor)
            
            # 7. Interprétation du modèle
            if best_pipeline is not None:
                viability_score_interpretation(best_pipeline[-1], preprocessor, categorical_features, numerical_features)
                
                # 8. Sauvegarde du meilleur modèle pour utilisation future
                import joblib
                joblib.dump(best_pipeline, 'entreprise_viability_model.pkl')
                logger.info(f"Meilleur modèle sauvegardé: {best_model_name}")
        
        logger.info("Analyse de viabilité terminée avec succès!")
            
    except Exception as e:
        logger.error(f"Erreur pendant l'analyse de viabilité: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description='Analyse de viabilité des entreprises')
    # parser.add_argument('--sample', type=int, default=None, help='Taille de l\'échantillon à utiliser')
    # args = parser.parse_args()
    
    # main(sample_size=args.sample)
    import argparse
    parser = argparse.ArgumentParser(description='Analyse de viabilité des entreprises')
    parser.add_argument('--sample', type=int, default=None, help='Taille de l\'échantillon à utiliser')
    parser.add_argument('--fast', action='store_true', help='Mode rapide avec moins de modèles')
    parser.add_argument('--no-plots', dest='plots', action='store_false', help='Désactiver les visualisations')
    parser.set_defaults(plots=True)
    args = parser.parse_args()
    
    main(sample_size=args.sample, fast_mode=args.fast, generate_plots=args.plots)