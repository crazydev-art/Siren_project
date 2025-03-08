"""Configuration des tests."""

import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def env_setup():
    """Configure l'environnement de test."""
    load_dotenv()
    # Utiliser une base de test
    os.environ['POSTGRES_DB'] = 'test_db' 