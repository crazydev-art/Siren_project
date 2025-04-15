from pydantic import BaseModel
from datetime import datetime

class UniteLegaleBase(BaseModel):
    siren: str
    datecreationunitelegale: datetime | None = None
    trancheeffectifsunitelegale: str | None = None
    anneeeffectifsunitelegale: str | None = None
    datederniertraitementunitelegale: datetime | None = None
    categorieentreprise: str | None = None
    anneecategorieentreprise: str | None = None
    etatadministratifunitelegale: str | None = None
    nomunitelegale: str | None = None
    nomusageunitelegale: str | None = None
    denominationunitelegale: str | None = None
    categoriejuridiqueunitelegale: str | None = None
    activiteprincipaleunitelegale: str | None = None
    nicsiegeunitelegale: str | None = None

class UniteLegaleResponse(UniteLegaleBase):
    class Config:
        from_attributes = True  # ORM Compatibility
