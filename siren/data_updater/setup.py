from setuptools import setup, find_packages

setup(
    name="siren_project",
    version="0.1",
    description="Projet de récupération et traitement des données SIRENE/SIRET",
    author="Yassine",
    packages=find_packages(where="app/src"),
    package_dir={'': 'app/src'},
    install_requires=[
        'requests',      # Pour les appels API
        'python-dotenv', # Pour gérer les variables d'environnement
        'pandas',        # Pour la manipulation des données
        'psycopg2',      # Pour PostgreSQL
    ],
    python_requires='>=3.8',  # Version minimale de Python requise
)
