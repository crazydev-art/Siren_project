from pydantic import BaseModel
from datetime import datetime, date  

class EtablissementBase(BaseModel):
    siret: str
    nic: str | None = None
    siren: str
    datecreationetablissement: date | None = None  
    trancheeffectifsetablissement: str | None = None
    anneeeffectifsetablissement: str | None = None
    activiteprincipaleetablissement: str | None = None
    datederniertraitementetablissement: datetime | None = None  
    etatadministratifetablissement: str | None = None
    etablissementsiege: bool | None = None
    enseigne1etablissement: str | None = None
    enseigne2etablissement: str | None = None
    enseigne3etablissement: str | None = None
    denominationusuelleetablissement: str | None = None

class EtablissementResponse(EtablissementBase):
    class Config:
        from_attributes = True  
