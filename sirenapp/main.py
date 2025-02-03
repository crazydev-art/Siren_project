#pip install fastapi[all] asyncpg databases psycopg2

from fastapi import FastAPI, Form, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
from databases import Database
import logging
from datetime import datetime, timedelta
import bcrypt
# from dotenv import load_dotenv  # if load_dotenv()
from uuid import UUID
import jwt

logging.basicConfig(level=logging.DEBUG)

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'user')}:" \
               f"{os.getenv('POSTGRES_PASSWORD', 'password')}@" \
               f"{os.getenv('POSTGRES_HOST', 'localhost')}:" \
               f"{os.getenv('POSTGRES_PORT', '5432')}/" \
               f"{os.getenv('POSTGRES_DB', 'mydatabase')}"

USERS_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:" \
               f"{os.getenv('POSTGRES_PASSWORD', 'password')}@" \
               f"{os.getenv('POSTGRES_HOST', 'localhost')}:" \
               f"{os.getenv('POSTGRES_PORT', '5432')}/" \
               f"{os.getenv('POSTGRES_DB_USER')}"

# Initialize database connection
database = Database(DATABASE_URL)
users = Database(USERS_URL)
app = FastAPI()

class Adresse(BaseModel):
    adresse_id: UUID
    numerovoieetablissement: str
    complementadresseetablissement: Optional[str] = None
    indicerepetitionetablissement: Optional[str] = None
    typevoieetablissement: str
    libellevoieetablissement: str
    codepostaletablissement: str
    libellecommuneetablissement: str
    codecommuneetablissement: str


class Etablissement(BaseModel):
    siren: str
    nic: str
    siret: str
    trancheeffectifsetablissement: Optional[str] = None
    anneeeffectifsetablissement: Optional[str] = None
    activiteprincipaleregistremetiersetablissement: Optional[str] = None
    datederniertraitementetablissement: datetime
    etablissementsiege: bool
    adresse_id: UUID

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.on_event("startup")
async def startup():
    try:
        # Connect to both databases
        await database.connect()  # Main database connection
        await users.connect()  # Users database connection
        logging.info("Successfully connected to both databases")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to one or more databases")

@app.post("/add new user to database users/")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Register a new user with encrypted password.
    """
    if not users:
        raise HTTPException(status_code=500, detail="Database is not configured. Please configure it first.")

    try:
        # Check if username or email already exists
        query = "SELECT username, email FROM users WHERE username = :username OR email = :email"
        existing_user = await users.fetch_one(query, values={"username": username, "email": email})

        if existing_user:
            # If username already exists
            if existing_user["username"] == username:
                raise HTTPException(status_code=400, detail="Username already exists")
            # If email already exists
            if existing_user["email"] == email:
                raise HTTPException(status_code=400, detail="Email already exists")

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Insert new user
        insert_query = """
        INSERT INTO users (username, email, password)
        VALUES (:username, :email, :password)
        """
        await users.execute(insert_query, values={"username": username, "email": email, "password": hashed_password})

        return {"message": "User registered successfully"}
    
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login/")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    ):
    """
    Authenticate a user by checking their username and password from the database.
    """
    query = "SELECT username, password FROM users WHERE username = :username"
    user_record = await users.fetch_one(query, values={"username": username})

    if not user_record:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    stored_password = user_record["password"]
    
    if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful"}
   

@app.get("/etablissements/", response_model=List[Etablissement])
async def list_etablissements(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Number of records to retrieve")
):
    try:
        query = "SELECT * FROM etablissement ORDER BY siret OFFSET :skip LIMIT :limit"
        result = await database.fetch_all(query, values={"skip": skip, "limit": limit})
        return [Etablissement(**row) for row in result]
    except Exception as e:
        logging.error(f"Error fetching etablissements: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data.")




