import os
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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
        logger.error(f"Erreur de connexion à la base de données : {e}")
        raise

def read_large_table(chunksize=500000):
    """Lit une grande table PostgreSQL en morceaux et retourne un DataFrame."""
    engine = get_db_connection()
    query = """
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

    # query = """
    # WITH etab AS (
    #     SELECT 
    #         siret, siren, nic, 
    #         statutdiffusionetablissement, 
    #         etablissementsiege, 
    #         activiteprincipaleetablissement, 
    #         datederniertraitementetablissement,
    #         trancheeffectifsetablissement, 
    #         datecreationetablissement,
    #         etablissementsiege,
    #         etatadministratifetablissement
    #     FROM etablissement
    # ),
    # unite AS (
    #     SELECT 
    #         siren, 
    #         statutdiffusionunitelegale,
    #         unitepurgeeunitelegale,
    #         datederniertraitementunitelegale,
    #         categoriejuridiqueunitelegale,
    #         activiteprincipaleunitelegale,
    #         economiessocialesolidaireunitelegale,
    #         caractereemployeurunitelegale,
    #         trancheeffectifsunitelegale,
    #         anneecategorieentreprise,
    #         datecreationunitelegale,
    #         etatadministratifunitelegale,
    #         nomunitelegale,
    #         denominationunitelegale,
    #         categorieentreprise
    #     FROM unitelegale 
    #     WHERE siren IN (SELECT siren FROM etab)
    # ),
    # geo AS (
    #     SELECT 
    #         siret,
    #         longitude, 
    #         latitude, 
    #         codeCommuneEtablissement,
    #         codePostalEtablissement,
    #         libelleCommuneEtablissement
    #     FROM geolocalisation 
    #     WHERE siret IN (SELECT siret FROM etab)
    # )
    # SELECT 
    #     e.siret, e.siren, e.nic, 
    #     e.etablissementsiege, 
    #     e.activiteprincipaleetablissement,
    #     e.trancheeffectifsetablissement,
    #     e.datecreationetablissement,
    #     e.etatadministratifetablissement,
    #     u.statutdiffusionunitelegale,
    #     u.categoriejuridiqueunitelegale,
    #     u.activiteprincipaleunitelegale,
    #     u.economiessocialesolidaireunitelegale,
    #     u.caractereemployeurunitelegale,
    #     u.trancheeffectifsunitelegale,
    #     u.anneecategorieentreprise,
    #     u.datecreationunitelegale,
    #     u.etatadministratifunitelegale,
    #     u.categorieentreprise,
    #     g.longitude, g.latitude,
    #     g.codeCommuneEtablissement,
    #     g.codePostalEtablissement
    # FROM etab e
    # JOIN unite u ON e.siren = u.siren
    # JOIN geo g ON e.siret = g.siret
    # -- Limiter aux entreprises avec un état administratif connu
    # WHERE e.etatadministratifetablissement IS NOT NULL;
    # """
   
    all_chunks = []
    total_rows = 0
    
    logger.info("Exécution query en chunks...")
    
    # Lecture par chunks avec pd.read_sql
    for chunk in pd.read_sql(query, engine, chunksize=chunksize):
        all_chunks.append(chunk)
        total_rows += len(chunk)
        logger.info(f"Morceau chargé : {len(chunk)} lignes. Total actuel : {total_rows} lignes.")
    
    # Concaténation des morceaux en un seul DataFrame
    df = pd.concat(all_chunks, ignore_index=True)
    
    logger.info(f"Lecture terminée : {total_rows} lignes chargées.")
    return df




def analyze_data(df):
    """Effectue une analyse approfondie des données."""
    logger.info("Analyse des données en cours...")
    
    # Informations générales sur le DataFrame
    logger.info(f"Dimensions du DataFrame: {df.shape}")
    logger.info(f"Types de données:\n{df.dtypes}")
    
    # Résumé statistique
    logger.info("Résumé statistique pour les colonnes numériques:")
    print(df.describe())
    
    # Analyse des valeurs manquantes
    missing_values = df.isnull().sum()
    missing_percent = (missing_values / len(df)) * 100
    missing_data = pd.DataFrame({'Valeurs manquantes': missing_values, 
                                 'Pourcentage (%)': missing_percent})
    missing_data = missing_data[missing_data['Valeurs manquantes'] > 0].sort_values(
                                'Pourcentage (%)', ascending=False)
    logger.info("Analyse des valeurs manquantes:")
    print(missing_data)
    
    # Analyse des valeurs uniques
    unique_values = df.nunique()
    unique_data = pd.DataFrame({'Valeurs uniques': unique_values})
    logger.info("Analyse des valeurs uniques:")
    print(unique_data)
    
    # Identification des colonnes catégorielles et numériques
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    logger.info(f"Colonnes catégorielles ({len(categorical_cols)}): {categorical_cols[:10]}...")
    logger.info(f"Colonnes numériques ({len(numerical_cols)}): {numerical_cols[:10]}...")
    
    # Analyse des distributions pour les colonnes numériques (limité aux 5 premières)
    if len(numerical_cols) > 0:
        plt.figure(figsize=(15, 10))
        for i, col in enumerate(numerical_cols[:5]):
            plt.subplot(2, 3, i+1)
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f'Distribution de {col}')
        plt.tight_layout()
        plt.savefig('numerical_distributions.png')
        logger.info("Graphiques de distribution enregistrés")
    
    # Analyse des distributions pour les colonnes catégorielles (limité aux 5 premières)
    if len(categorical_cols) > 0:
        for i, col in enumerate(categorical_cols[:5]):
            plt.figure(figsize=(10, 6))
            value_counts = df[col].value_counts().head(10)
            value_counts.plot(kind='bar')
            plt.title(f'Top 10 valeurs pour {col}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'categorical_{col}.png')
        logger.info("Graphiques des catégories enregistrés")
    
    # Matrice de corrélation pour les colonnes numériques
    if len(numerical_cols) > 1:
        plt.figure(figsize=(12, 10))
        correlation_matrix = df[numerical_cols].corr()
        sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
        plt.title('Matrice de corrélation')
        plt.tight_layout()
        plt.savefig('correlation_matrix.png')
        logger.info("Matrice de corrélation enregistrée")
    
    return {
        'categorical_cols': categorical_cols,
        'numerical_cols': numerical_cols,
        'missing_data': missing_data
    }

def prepare_data_for_ml(df, analysis_results, target_column=None):
    """Prépare les données pour le machine learning."""
    logger.info("Préparation des données pour le ML...")
    
    # Si aucune colonne cible n'est spécifiée, on essaie de définir une cible basée sur les données
    if target_column is None or target_column not in df.columns:
        # On peut chercher des colonnes potentielles qui pourraient servir de cible
        # Par exemple, une colonne avec peu de valeurs uniques pourrait être une bonne cible
        unique_counts = df.nunique()
        potential_targets = unique_counts[(unique_counts > 1) & (unique_counts < 10)].index.tolist()
        
        if potential_targets:
            target_column = potential_targets[0]
            logger.info(f"Aucune cible spécifiée. Utilisation de '{target_column}' comme cible.")
        else:
            # Si aucune cible potentielle n'est trouvée, on crée une cible synthétique pour démonstration
            logger.info("Création d'une cible synthétique pour démonstration.")
            # Par exemple, on peut créer une classification binaire basée sur une colonne numérique
            num_cols = analysis_results['numerical_cols']
            if num_cols:
                df['target_synthetic'] = np.where(df[num_cols[0]] > df[num_cols[0]].median(), 1, 0)
                target_column = 'target_synthetic'
            else:
                raise ValueError("Impossible de créer une cible pour le ML. Veuillez spécifier une colonne cible.")
    
    # Vérification de la cible
    logger.info(f"Utilisation de '{target_column}' comme variable cible.")
    logger.info(f"Distribution de la cible:\n{df[target_column].value_counts(dropna=False)}")
    
    # Suppression des lignes où la cible est nulle
    df = df.dropna(subset=[target_column])
    
    # Séparation des features et de la cible
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Division en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    logger.info(f"Dimensions de X_train: {X_train.shape}, X_test: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test, target_column

def create_preprocessing_pipeline(categorical_cols, numerical_cols):
    """Crée un pipeline de prétraitement pour les données."""
    # Préprocessing pour les colonnes numériques
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Préprocessing pour les colonnes catégorielles
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # Combinaison des préprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])
    
    return preprocessor

def train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor):
    """Entraîne et évalue plusieurs modèles de ML."""
    logger.info("Entraînement et évaluation des modèles...")
    
    # Vérification si nous avons affaire à une classification ou une régression
    unique_y = np.unique(y_train)
    is_classification = len(unique_y) <= 10  # Seuil arbitraire pour déterminer si c'est une classification
    
    if is_classification:
        logger.info(f"Tâche de classification détectée. Classes: {unique_y}")
        
        # Modèles pour la classification
        models = {
            "Régression Logistique": LogisticRegression(max_iter=1000),
            "K Plus Proches Voisins": KNeighborsClassifier(),
            "Naive Bayes": GaussianNB(),
            "Arbre de Décision": DecisionTreeClassifier(random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(random_state=42)
        }
        
        # Pour SVM, on l'ajoute seulement si le dataset n'est pas trop grand
        if X_train.shape[0] < 10000:
            models["SVM"] = SVC(probability=True)
    else:
        logger.info("Tâche de régression détectée.")
        # Pour la régression, on ajouterait ici des modèles de régression
        # Ce qui n'est pas implémenté dans cet exemple
    
    results = {}
    for name, model in models.items():
        logger.info(f"Entraînement du modèle: {name}")
        
        # Création du pipeline complet
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('selector', SelectKBest(f_classif, k=min(50, X_train.shape[1]))),
            ('classifier', model)
        ])
        
        # Entraînement
        pipeline.fit(X_train, y_train)
        
        # Prédictions
        y_pred = pipeline.predict(X_test)
        
        # Évaluation
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = accuracy
        
        logger.info(f"{name} - Accuracy: {accuracy:.4f}")
        logger.info(f"Rapport de classification:\n{classification_report(y_test, y_pred)}")
        
        # Matrice de confusion
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Matrice de confusion - {name}')
        plt.xlabel('Prédit')
        plt.ylabel('Réel')
        plt.savefig(f'confusion_matrix_{name}.png')
    
    # Affichage des résultats comparatifs
    plt.figure(figsize=(10, 6))
    plt.bar(results.keys(), results.values())
    plt.title('Comparaison des performances des modèles')
    plt.xlabel('Modèle')
    plt.ylabel('Accuracy')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('model_comparison.png')
    
    # Identification du meilleur modèle
    best_model = max(results, key=results.get)
    logger.info(f"Meilleur modèle: {best_model} avec une accuracy de {results[best_model]:.4f}")
    
    return results, best_model

def main():
    """Runs the ML analysis pipeline."""
    logger.info("Démarrage du processus d'analyse ML...")
    
    try:
        # Chargement des données
        df = read_large_table()
        
        # Analyse exploratoire des données
        analysis_results = analyze_data(df)
        
        # À ce stade, vous devriez spécifier votre colonne cible
        # Si vous ne la connaissez pas, la fonction prepare_data_for_ml essaiera d'en définir une
        target_column = None  # Remplacer par le nom de votre colonne cible si vous la connaissez
        
        # Préparation des données pour le ML
        X_train, X_test, y_train, y_test, actual_target = prepare_data_for_ml(df, analysis_results, target_column)
        
        # Sélection des colonnes à utiliser (pour limiter la complexité)
        categorical_cols = analysis_results['categorical_cols']
        numerical_cols = analysis_results['numerical_cols']
        
        # Limitation du nombre de colonnes pour les grandes tables
        max_cols = 100  # Limite arbitraire
        if len(categorical_cols) > max_cols // 2:
            categorical_cols = categorical_cols[:max_cols // 2]
        if len(numerical_cols) > max_cols // 2:
            numerical_cols = numerical_cols[:max_cols // 2]
        
        logger.info(f"Utilisation de {len(categorical_cols)} colonnes catégorielles et {len(numerical_cols)} colonnes numériques")
        
        # Création du pipeline de prétraitement
        preprocessor = create_preprocessing_pipeline(categorical_cols, numerical_cols)
        
        # Entraînement et évaluation des modèles
        results, best_model = train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor)
        
        logger.info("Analyse ML terminée avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur pendant l'analyse ML: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()