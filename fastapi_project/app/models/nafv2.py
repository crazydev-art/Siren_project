from sqlalchemy import Column, String
from app.database import Base

class NafV2(Base):
    __tablename__ = "nafv2"

    codenaf = Column(String(9), primary_key=True, index=True)  # Primary Key
    nafvfinale = Column(String(255), nullable=True)  # Can be NULL
