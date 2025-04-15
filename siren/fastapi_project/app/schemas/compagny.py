from pydantic import BaseModel

class CompanySchema(BaseModel):
    siret: str
    x: float
    y: float

    class Config:
        orm_mode = True

class SearchFilters(BaseModel):
    activityCode: str  # NAF code (e.g., "08.11Z")
    latitude: float   # Latitude (e.g., 48.8490995)
    longitude: float  # Longitude (e.g., 2.3388232)
    radius: float     # Radius in kilometers (e.g., 10)