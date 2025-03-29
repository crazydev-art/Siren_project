from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # Store hashed password!
    created_at = Column(TIMESTAMP, server_default=func.now())  # Auto timestamp