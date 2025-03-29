from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_siren_db
from app.models.unitelegale import UniteLegale
from app.schemas.unitelegale import UniteLegaleResponse
from typing import List

router = APIRouter()

@router.get("/siren", response_model=List[UniteLegaleResponse])
def search_by_siren(
    siren: str = Query(..., min_length=9, max_length=9, regex="^\d{9}$"),
    db: Session = Depends(get_siren_db)
):
    """ Search company by SIREN number (9 digits) """
    
    results = db.query(UniteLegale).filter(UniteLegale.siren == siren).all()

    if not results:
        raise HTTPException(status_code=404, detail="No company found with this SIREN")

    return results
