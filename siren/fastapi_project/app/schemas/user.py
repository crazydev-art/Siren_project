from pydantic import BaseModel, EmailStr
from datetime import datetime

class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # For ORM compatibility

class UniteLegaleBase(BaseModel):
    siren: str
    datecreationunitelegale: str | None = None
    trancheeffectifsunitelegale: str | None = None
    anneeeffectifsunitelegale: str | None = None
    daderniertraitementunitelegale: str | None = None
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
