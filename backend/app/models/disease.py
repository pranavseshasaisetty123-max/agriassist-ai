from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DiseaseScan(Base):
    __tablename__ = "disease_scans"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(500), nullable=False)
    diagnosis_type = Column(String(100), nullable=False)
    disease_name = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False)
    symptoms = Column(Text, nullable=False)             # Serialized JSON list
    treatment = Column(Text, nullable=False)            # Serialized JSON list
    preventive_measures = Column(Text, nullable=False)  # Serialized JSON list
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="disease_scans")
