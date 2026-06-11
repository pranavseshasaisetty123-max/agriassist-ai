from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SoilReport(Base):
    __tablename__ = "soil_reports"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    ph = Column(Float, nullable=False)
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    organic_matter = Column(Float, nullable=True)
    crop_planned = Column(String(150), nullable=False)
    tested_at = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="soil_reports")
    recommendation = relationship(
        "SoilRecommendation",
        back_populates="report",
        uselist=False,
        cascade="all, delete-orphan"
    )


class SoilRecommendation(Base):
    __tablename__ = "soil_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("soil_reports.id", ondelete="CASCADE"), unique=True, nullable=False)
    nitrogen_recommendation = Column(Text, nullable=False)
    phosphorus_recommendation = Column(Text, nullable=False)
    potassium_recommendation = Column(Text, nullable=False)
    fertilizer_schedule = Column(Text, nullable=False)
    ai_raw_analysis = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    report = relationship("SoilReport", back_populates="recommendation")
