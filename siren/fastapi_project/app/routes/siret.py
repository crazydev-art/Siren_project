from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_siren_db
from app.models.etablissements import Etablissement
from app.schemas.etablissements import EtablissementResponse
from typing import List

router = APIRouter()

@router.get("/siret", response_model=List[EtablissementResponse])
def search_by_siret(
    siret: str = Query(..., min_length=14, max_length=14, regex="^\d{14}$"),
    db: Session = Depends(get_siren_db)
):
    """ Search for an establishment by SIRET number (14 digits) """
    
    results = db.query(Etablissement).filter(Etablissement.siret == siret).all()

    if not results:
        raise HTTPException(status_code=404, detail="No establishment found with this SIRET")

    return results
