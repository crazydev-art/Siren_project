from sqlalchemy import Column, String, Integer,TIMESTAMP,Date
from app.database import Base
class UniteLegale(Base):
    __tablename__ = "unitelegale"

    siren = Column(String(9), primary_key=True, index=True)  # SIREN (9 digits)
    datecreationunitelegale = Column(Date, nullable=True)  
    trancheeffectifsunitelegale = Column(String, nullable=True)
    anneeffectifsunitelegale = Column(String, nullable=True)
    datederniertraitementunitelegale = Column(TIMESTAMP, nullable=True)
    categorieentreprise = Column(String, nullable=True)
    anneecategorieentreprise = Column(String, nullable=True)
    etatadministratifunitelegale = Column(String, nullable=True)
    nomunitelegale = Column(String, nullable=True)
    nomusageunitelegale = Column(String, nullable=True)
    denominationunitelegale = Column(String, nullable=True)
    categoriejuridiqueunitelegale = Column(String, nullable=True)
    activiteprincipaleunitelegale = Column(String, nullable=True)
    nicsiegeunitelegale = Column(String, nullable=True)
