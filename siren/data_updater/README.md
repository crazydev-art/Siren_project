
# Service de Mise à Jour des Établissements INSEE

## 📋 Description
Service automatisé de mise à jour des données d'établissements depuis l'API Sirene de l'INSEE vers une base de données PostgreSQL. Le service récupère quotidiennement les établissements d'Île-de-France et met à jour la base de données.

## 🏗️ Architecture
```bash
app/
├── src/
│   ├── api/                    # Interactions avec l'API INSEE
│   │   ├── siret.py           # Récupération des données SIRET
│   │   └── last_treatment.py  # Dates de dernier traitement API
│   ├── database/              # Gestion base de données
│   │   ├── connection.py      # Pool de connexions
│   │   ├── loader.py         # Chargement des données
│   │   └── last_treatment.py # Dates de traitement DB
│   ├── utils/                 # Utilitaires
│   │   └── logger.py         # Logging des opérations
│   └── service/              # Services principaux
│       └── updater.py       # Service de mise à jour
├── config/                   # Configuration
│   └── settings.py          # Paramètres globaux
├── logs/                    # Fichiers de logs
├── dumps/                   # Dumps de données
└── run.py                  # Point d'entrée
```

## ⚙️ Installation

### Prérequis
- Python 3.11+
- PostgreSQL
- Accès à l'API INSEE

### Configuration
1. Créer un fichier `.env` :
```bash
# Base de données
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mabase
POSTGRES_USER=monuser
POSTGRES_PASSWORD=monpass

# API INSEE
API_KEY=votre_cle_api_insee
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Démarrage Standard
```bash
python run.py
```

### Docker
```bash
# Construction de l'image
docker build -t insee-updater .

# Lancement du container
docker run --env-file .env insee-updater
```

## 📊 Fonctionnalités

### Mise à jour des données
- Récupération paginée (1000 établissements par appel)
- Gestion des lots volumineux (>100k lignes)
- Mise à jour incrémentale
- Logging détaillé

### Base de données
- Pool de connexions (1-10 connexions)
- Transactions sécurisées
- Gestion des erreurs avec rollback
- Dumps automatiques

## 📝 Logs
Les logs sont stockés dans `logs/db_operations_YYYYMMDD.log` :
```
2024-03-15 10:30:15 | INFO | STAGING | INSERT | Lignes: 1000
2024-03-15 10:30:16 | INFO | MAIN | UPDATE | Lignes: 150
```

## ⚠️ Gestion des Erreurs
- Retry sur erreurs API
- Rollback sur erreurs DB
- Logging des exceptions
- Reprise automatique

## 🛠️ Maintenance

### Vérifications Quotidiennes
1. Consulter les logs : `logs/db_operations_YYYYMMDD.log`
2. Vérifier les dumps : `dumps/`
3. Surveiller l'espace disque

### Résolution des Problèmes
1. Vérifier les logs
2. Contrôler l'API
3. Vérifier la DB
4. Redémarrer si nécessaire

## 📦 Dépendances
```
python-dotenv==1.0.0
requests==2.31.0
psycopg2-binary==2.9.9
```

## 🔒 Sécurité
- Variables d'environnement
- Pool de connexions sécurisé
- Transactions atomiques
- Logging sécurisé

## 📄 Licence
MIT License
```

Ce README fournit :
- 📚 Documentation complète
- 🔧 Instructions d'installation
- 🚀 Guide d'utilisation
- 🏗️ Architecture détaillée
- ⚠️ Gestion des erreurs
- 🛠️ Guide de maintenance
