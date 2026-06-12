from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CropRecommendation(Base):
    __tablename__ = "crop_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String(150), nullable=False)
    suitability_score = Column(Integer, nullable=False)
    season = Column(String(100), nullable=False)
    recommendation_reason = Column(Text, nullable=False)
    risk_factors = Column(Text, nullable=False)  # Serialized JSON list
    farming_tips = Column(Text, nullable=False)  # Serialized JSON list
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="crop_recommendations")
