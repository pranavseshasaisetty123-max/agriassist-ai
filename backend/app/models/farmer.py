from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)
    contact_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    sessions = relationship("ChatSession", back_populates="farmer", cascade="all, delete-orphan")
    soil_reports = relationship("SoilReport", back_populates="farmer", cascade="all, delete-orphan")
    disease_scans = relationship("DiseaseScan", back_populates="farmer", cascade="all, delete-orphan")
