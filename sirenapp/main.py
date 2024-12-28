from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Any, Dict, Optional
import os
import logging
from datetime import datetime

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# MongoDB Configuration
mongo_config = {
    'IPHOST': os.getenv('IPHOST', 'localhost'),
    'PORT': 27017,
    'DATABASE': 'siren',
    'USERNAME': os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    'PASSWORD': os.getenv('MONGO_INITDB_ROOT_PASSWORD')
}

# MongoDB Configuration
MONGO_URL = f"mongodb://{mongo_config['USERNAME']}:{mongo_config['PASSWORD']}@" \
            f"{mongo_config['IPHOST']}:{mongo_config['PORT']}/{mongo_config['DATABASE']}?authSource=admin"
        
# DB_NAME = f"{mongo_config['DATABASE']}"

# MongoDB Client Initialization
client = AsyncIOMotorClient(MONGO_URL)
db = client[mongo_config['DATABASE']]

# Declare Multiple Collections
etablissement_collection = db["etablissement"]
adresse_collection = db["adresse"]
unitelegale_collection = db["unitelegale"]
geolocalisation_collection = db["geolocalisation"]
nafv2_collection = db["nafv2"]
categorie_juridique_collection = db["categorie_juridique"]

# Pydantic Model for Etablissement with Specific Fields
class Adresse(BaseModel):
    id: str = Field(..., alias="_id")
    adresse_id: str
    numerovoieetablissement: str
    complementadresseetablissement: str
    indicerepetitionetablissement: str
    typevoieetablissement: str
    libellevoieetablissement: str
    codepostaletablissement: str
    libellecommuneetablissement: str
    codecommuneetablissement: str

    class Config:
        schema_extra = {
            "example": {
                "_id": "676c608eb6c41debaccafdb5",
                "adresse_id": "f88fd199-db9d-4bc8-a38f-ef0bcb583882",
                "numerovoieetablissement": "36",
                "complementadresseetablissement": "",
                "indicerepetitionetablissement": "",
                "typevoieetablissement": "AVENUE",
                "libellevoieetablissement": "JUNOT",
                "codepostaletablissement": "75018",
                "libellecommuneetablissement": "PARIS",
                "codecommuneetablissement": "75118",
            }
        }

    @classmethod
    def from_mongo(cls, mongo_obj: dict) -> "Adresse":
        mongo_obj["_id"] = str(mongo_obj["_id"]) if "_id" in mongo_obj else None
        return cls(**mongo_obj)

class EtablissementResponse(BaseModel):
    id: str = Field(..., alias="_id")
    siren: str
    nic: str
    siret: str
    trancheeffectifsetablissement: str
    anneeeffectifsetablissement: str
    activiteprincipaleregistremetiersetablissement: str
    datederniertraitementetablissement: datetime
    etablissementsiege: str
    adresse_id: str
    adresse: Optional[Adresse] = None  # Adresse is optional for routes that don’t need it - NewLine to manage etabl/Adres response

    class Config:
        schema_extra = {
            "example": {
                "_id": "676c60e7b6c41debacf90dc6",
                "siren": "005520325",
                "nic": "00027",
                "siret": "00552032500027",
                "trancheeffectifsetablissement": "",
                "anneeeffectifsetablissement": "",
                "activiteprincipaleregistremetiersetablissement": "",
                "datederniertraitementetablissement": "2024-03-30T14:22:10.000Z",
                "etablissementsiege": "true",
                "adresse_id": "f88fd199-db9d-4bc8-a38f-ef0bcb583882",
                "adresse": { # # Adresse is optional for routes that don’t need it - NewLine to manage etabl/Adres response
                    "_id": "676c608eb6c41debaccafdb5",
                    "adresse_id": "f88fd199-db9d-4bc8-a38f-ef0bcb583882",
                    "numerovoieetablissement": "36",
                    "complementadresseetablissement": "",
                    "indicerepetitionetablissement": "",
                    "typevoieetablissement": "AVENUE",
                    "libellevoieetablissement": "JUNOT",
                    "codepostaletablissement": "75018",
                    "libellecommuneetablissement": "PARIS",
                    "codecommuneetablissement": "75118"
                }
            }
        }

    @classmethod
    def from_mongo(cls, mongo_obj: dict) -> "EtablissementResponse":
        # Convert MongoDB ObjectId to string for Pydantic model
        mongo_obj["_id"] = str(mongo_obj["_id"]) if "_id" in mongo_obj else None
        # If adresse exists, we need to create an Adresse model
        if 'adresse' in mongo_obj and mongo_obj['adresse']:
            adresse_data = mongo_obj['adresse']
            # Convert ObjectId to string in adresse data
            if "_id" in adresse_data and isinstance(adresse_data["_id"], ObjectId):
                adresse_data["_id"] = str(adresse_data["_id"])
            # Create Adresse object from the data
            mongo_obj['adresse'] = Adresse(**adresse_data)  # Create Adresse object from the data
        return cls(**mongo_obj)




# Endpoint /
@app.get("/", tags=["Health Check"])
def verify():
    return {"message": "L'API est fonctionnelle."}

# Route to Retrieve All Etablissements with Specified Fields
@app.get("/etablissements/", response_model=List[EtablissementResponse], tags=["Etablissements"])
async def list_etablissements(
    limit: int = Query(100, description="Maximum number of documents to retrieve", example=50),
    skip: int = Query(0, description="Number of documents to skip", example=10),
):
    try:
        cursor = etablissement_collection.find({}, {
            "_id": 1,
            "siren": 1,
            "nic": 1,
            "siret": 1,
            "trancheeffectifsetablissement": 1,
            "anneeeffectifsetablissement": 1,
            "activiteprincipaleregistremetiersetablissement": 1,
            "datederniertraitementetablissement": 1,
            "etablissementsiege": 1,
            "adresse_id": 1
        }).skip(skip).limit(limit)
        
        etablissements = await cursor.to_list(length=limit)
                
        return [EtablissementResponse.from_mongo(etablissement) for etablissement in etablissements]
    
    except Exception as e:
        logging.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# # Endpoint with aggregation
# @app.get("/etablissements-with-adresse/", response_model=List[EtablissementResponse])
# async def get_etablissements_with_adresse():
#     pipeline = [
#         {
#             "$lookup": {
#                 "from": "adresse",  # Collection to join
#                 "localField": "adresse_id",  # Field in etablissement
#                 "foreignField": "adresse_id",  # Field in adresse
#                 "as": "adresse"  # Resulting field
#             }
#         },
#         {
#             "$unwind": "$adresse"  # Flatten the joined array
#         },
#         {
#             "$project": {  # Project specific fields
#                 "_id": 1,
#                 "siren": 1,
#                 "nic": 1,
#                 "siret": 1,
#                 "trancheeffectifsetablissement": 1,
#                 "anneeeffectifsetablissement": 1,
#                 "activiteprincipaleregistremetiersetablissement": 1,
#                 "datederniertraitementetablissement": 1,
#                 "etablissementsiege": 1,
#                 "adresse.numerovoieetablissement": 1,
#                 "adresse.complementadresseetablissement": 1,
#                 "adresse.indicerepetitionetablissement": 1,
#                 "adresse.typevoieetablissement": 1,
#                 "adresse.libellevoieetablissement": 1,
#                 "adresse.codepostaletablissement": 1,
#                 "adresse.libellecommuneetablissement": 1,
#                 "adresse.codecommuneetablissement": 1
#             }
#         }
#     ]

#     cursor = etablissement_collection.aggregate(pipeline)
#     results = await cursor.to_list(length=100)  # Limit the results for now
#     return [EtablissementResponse.from_mongo(doc) for doc in results]
   

@app.get("/etablissements-with-adresse-filter/", response_model=List[EtablissementResponse])
async def get_etablissements_with_adresse_filter(
    siren: Optional[str] = None,
    siret: Optional[str] = None,
    etablissementsiege: Optional[bool] = None,
    limit: int = Query(100, description="Maximum number of documents to retrieve", example=50),
    skip: int = Query(0, description="Number of documents to skip", example=10)
):
    # Build dynamic match criteria
    match_criteria = {}
    if siren:
        match_criteria["siren"] = siren
    if siret:
        match_criteria["siret"] = siret
    if etablissementsiege is not None:
        match_criteria["etablissementsiege"] = str(etablissementsiege).lower()  # Convert to string "true"/"false"

    pipeline = [
        {
            "$match": match_criteria  # Apply filters
        },
        {
            "$lookup": {
                "from": "adresse",  # Collection to join
                "localField": "adresse_id",  # Field in etablissement
                "foreignField": "adresse_id",  # Field in adresse
                "as": "adresse"  # Resulting field
            }
        },
        {
            "$unwind": "$adresse"  # Flatten the joined array
        },
        {
            "$project": {  # Project specific fields
                "_id": 1,
                "siren": 1,
                "nic": 1,
                "siret": 1,
                "trancheeffectifsetablissement": 1,
                "anneeeffectifsetablissement": 1,
                "activiteprincipaleregistremetiersetablissement": 1,
                "datederniertraitementetablissement": 1,
                "etablissementsiege": 1,
                "adresse_id": 1,
                "adresse._id": 1,
                "adresse.adresse_id": 1,
                "adresse.numerovoieetablissement": 1,
                "adresse.complementadresseetablissement": 1,
                "adresse.indicerepetitionetablissement": 1,
                "adresse.typevoieetablissement": 1,
                "adresse.libellevoieetablissement": 1,
                "adresse.codepostaletablissement": 1,
                "adresse.libellecommuneetablissement": 1,
                "adresse.codecommuneetablissement": 1
            }
        }
    ]

    cursor = etablissement_collection.aggregate(pipeline)
    results = await cursor.to_list(length=limit)  # Limit the results for now
    # return [serialize_mongo_object(doc) for doc in results]
    return [EtablissementResponse.from_mongo(doc) for doc in results]
