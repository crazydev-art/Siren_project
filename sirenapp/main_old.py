#pip install fastapi[all] asyncpg databases psycopg2

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import os
from databases import Database
import logging
from datetime import datetime
from uuid import UUID

logging.basicConfig(level=logging.DEBUG)

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'user')}:" \
               f"{os.getenv('POSTGRES_PASSWORD', 'password')}@" \
               f"{os.getenv('POSTGRES_HOST', 'localhost')}:" \
               f"{os.getenv('POSTGRES_PORT', '5432')}/" \
               f"{os.getenv('POSTGRES_DB', 'mydatabase')}"

# Initialize database connection
database = Database(DATABASE_URL)
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


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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

# @app.post("/etablissements/", response_model=Etablissement)
# async def create_etablissement(etablissement: Etablissement):
#     query = """
#     INSERT INTO etablissement (siren, nic, siret, trancheeffectifsetablissement, anneeeffectifsetablissement,
#                                activiteprincipaleregistremetiersetablissement, datederniertraitementetablissement,
#                                etablissementsiege, adresse_id)
#     VALUES (:siren, :nic, :siret, :trancheeffectifsetablissement, :anneeeffectifsetablissement,
#             :activiteprincipaleregistremetiersetablissement, :datederniertraitementetablissement,
#             :etablissementsiege, :adresse_id)
#     RETURNING siret
#     """
#     last_record_id = await database.execute(query=query, values=etablissement.dict())
#     return {**etablissement.dict(), "siret": last_record_id}


