"""Module de logging pour suivre les opérations sur la base de données."""

import logging
from datetime import datetime
import os

class DatabaseLogger:
    """Gestionnaire de logs pour les opérations de base de données."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialise le logger avec le format et le fichier de sortie."""
        # Créer le dossier logs s'il n'existe pas
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(current_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Nom du fichier avec la date
        today = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(logs_dir, 'db_operations_%s.log' % today)
        
        # Configuration du logger
        self._logger = logging.getLogger('DatabaseOperations')
        self._logger.setLevel(logging.INFO)
        
        # Formatter pour les logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
    
    def log_staging_operation(self, operation_type: str, rows_affected: int):
        """Log une opération sur la table staging."""
        self._logger.info(
            "table_STAGING | %s | Lignes affectées: %d",
            operation_type, rows_affected
        )
    
    def log_main_operation(self, operation_type: str, rows_affected: int):
        """Log une opération sur la table principale."""
        self._logger.info(
            "table_MAIN | %s | Lignes affectées: %d",
            operation_type, rows_affected
        )
    
    def log_error(self, operation: str, error: str):
        """Log une erreur."""
        self._logger.error("ERREUR | %s | %s", operation, error) 