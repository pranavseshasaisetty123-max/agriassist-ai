from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(255), nullable=False)
    total_area_acres = Column(Float, nullable=False)
    soil_type = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="farms", foreign_keys=[farmer_id])
    
    # Context relationships
    soil_reports = relationship("SoilReport", back_populates="farm", cascade="all, delete-orphan")
    yield_predictions = relationship("YieldPrediction", back_populates="farm", cascade="all, delete-orphan")
    farm_plans = relationship("FarmPlan", back_populates="farm", cascade="all, delete-orphan")
    risk_alerts = relationship("RiskAlert", back_populates="farm", cascade="all, delete-orphan")
    farm_analytics_snapshots = relationship("FarmAnalyticsSnapshot", back_populates="farm", cascade="all, delete-orphan")
