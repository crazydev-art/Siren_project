from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List
from app.schemas.compagny import CompanySchema, SearchFilters
from app.database import get_siren_db 

router = APIRouter()

@router.post("/companies/search", response_model=List[CompanySchema])
def search_companies_in_radius(
    filters: SearchFilters,
    db: Session = Depends(get_siren_db)
):
    print("Received filters:", filters.dict())  # Debug
    activity_code = filters.activityCode
    latitude = filters.latitude
    longitude = filters.longitude
    radius = filters.radius

    radius_meters = radius * 1000

    query = """
        SELECT e.siret, g.x_longitude AS x, g.y_latitude AS y
        FROM geolocalisation g
        JOIN etablissement e ON g.siret = e.siret
        WHERE e.activiteprincipaleetablissement = :activity_code
        AND ST_DWithin(
            g.geog,
            ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
            :radius_meters
        )
    """
    result = db.execute(text(query), {
        "activity_code": activity_code,
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius_meters
    }).fetchall()

    print("Query result:", result)  # Debug
    companies = [{"siret": row[0], "x": row[1], "y": row[2]} for row in result]
    print("Returning companies:", companies)  # Debug
    return companies