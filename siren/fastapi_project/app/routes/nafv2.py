from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.nafv2 import NafV2
from app.schemas.nafv2 import NafV2Schema
from app.database import get_siren_db


router = APIRouter()

@router.get("/activities/suggest", response_model=List[NafV2Schema])
def get_activity_suggestions(q: str, db: Session = Depends(get_siren_db), limit: int = 10):
    """
    Fetch activity suggestions based on a partial query string.
    
    Args:
        q (str): The partial input from the user (e.g., "rest" to match "Restaurant").
        db (Session): Database session dependency.
        limit (int): Maximum number of suggestions to return (default: 10).
    
    Returns:
        List[NafV2Schema]: A list of matching activities.
    
    Raises:
        HTTPException: If no matches are found or if there's an error.
    """
    if not q or len(q.strip()) < 1:
        return []

    # Search for activities where the label or code matches the query (case-insensitive)
    suggestions = (
        db.query(NafV2)
        .filter(
            (NafV2.nafvfinale.ilike(f"%{q}%")) | (NafV2.codenaf.ilike(f"%{q}%"))
        )
        .limit(limit)
        .all()
    )

    if not suggestions:
        return []  # Return empty list instead of raising an exception for autocomplete

    return suggestions

@router.get("/activities/get-naf", response_model=NafV2Schema)
def get_naf_code(activity: str, db: Session = Depends(get_siren_db)):
    """
    Retrieve the NAF code corresponding to a given activity description.

    Args:
        activity (str): The activity description entered by the user.
        db (Session): Database session dependency.

    Returns:
        NafV2Schema: The matched activity with its NAF code.

    Raises:
        HTTPException: If no matches are found or if there's a database error.
    """
    if not activity or len(activity.strip()) < 2:
        raise HTTPException(status_code=400, detail="Activity input is too short.")

    try:
        # Recherche d'une correspondance exacte ou partielle (priorité à l'exacte)
        naf_entry = (
            db.query(NafV2)
            .filter(NafV2.nafvfinale.ilike(f"{activity}"))
            .first()
        )

        if not naf_entry:
            naf_entry = (
                db.query(NafV2)
                .filter(NafV2.nafvfinale.ilike(f"%{activity}%"))
                .order_by(NafV2.nafvfinale)  # Trie alphabétique pour cohérence
                .first()
            )

        if not naf_entry:
            raise HTTPException(status_code=404, detail="No matching NAF code found.")

        return naf_entry

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
