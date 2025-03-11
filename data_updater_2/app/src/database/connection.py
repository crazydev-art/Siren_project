"""Module de gestion du pool de connexions à la base de données."""

import os

from contextlib import contextmanager

from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv


class DatabaseConnectionPool:
    """Gestionnaire de pool de connexions à la base de données."""

    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """Initialise le pool de connexions."""
        load_dotenv()

        self._pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

    @contextmanager
    def get_connection(self):
        """
        Récupère une connexion du pool.

        Yields:
            psycopg2.extensions.connection: Une connexion à la base de données
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        finally:
            if conn:
                self._pool.putconn(conn)

    def close_all(self):
        """Ferme toutes les connexions du pool."""
        if self._pool:
            self._pool.closeall()

    @property
    def pool_status(self) -> tuple:
        """
        Retourne le statut actuel du pool.

        Returns:
            tuple: (connexions utilisées, connexions totales)
        """
        if not self._pool:
            return (0, 0)
        return (self._pool.closed, self._pool.maxconn)
