from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URLs from .env file
SIREN_DATABASE_URL = os.getenv("SIREN_DATABASE_URL")
USER_API_DATABASE_URL = os.getenv("USER_API_DATABASE_URL")

# Create engines for each database
siren_engine = create_engine(SIREN_DATABASE_URL)
user_api_engine = create_engine(USER_API_DATABASE_URL)

Base = declarative_base()

# Create sessions for each database
SirenSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=siren_engine)
UserAPISessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_api_engine)

# Dependency for Siren DB
def get_siren_db():
    db = SirenSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for User API DB
def get_user_api_db():
    db = UserAPISessionLocal()
    try:
        yield db
    finally:
        db.close()
