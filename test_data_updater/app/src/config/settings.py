"""Configuration de l'application."""

import os
from datetime import timedelta

# Intervalles de mise à jour
UPDATE_INTERVAL = timedelta(hours=24)  # Vérifie toutes les 12 heures

# Configuration API
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 60  # secondes

# Configuration Base de données
DB_BATCH_SIZE = 100000  # Taille max du batch pour staging

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
DUMPS_DIR = os.path.join(BASE_DIR, 'dumps')

# Créer les répertoires nécessaires - test
for directory in [LOGS_DIR, DUMPS_DIR]:os.makedirs(directory, exist_ok=True) 