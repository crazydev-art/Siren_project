from sqlalchemy import Column, String, Integer, Date, TIMESTAMP, func,Boolean
from app.database import Base  

class Etablissement(Base):
    __tablename__ = "etablissement"

    siret = Column(String(14), primary_key=True, index=True)  # ✅ SIRET (14 digits)
    nic = Column(String, nullable=True)
    siren = Column(String(9), nullable=False)  # ✅ Linked SIREN number
    datecreationetablissement = Column(Date, nullable=True)  # ✅ Date Type
    trancheeffectifsetablissement = Column(String, nullable=True)
    anneeeffectifsetablissement = Column(String, nullable=True)
    activiteprincipaleetablissement = Column(String, nullable=True)
    datederniertraitementetablissement = Column(TIMESTAMP, server_default=func.now(), nullable=False)  # ✅ TIMESTAMP
    etatadministratifetablissement = Column(String, nullable=True)
    etablissementsiege = Column(Boolean, nullable=True)
    enseigne1etablissement = Column(String, nullable=True)
    enseigne2etablissement = Column(String, nullable=True)
    enseigne3etablissement = Column(String, nullable=True)
    denominationusuelleetablissement = Column(String, nullable=True)
