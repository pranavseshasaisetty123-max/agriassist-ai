from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class YieldPrediction(Base):
    __tablename__ = "yield_predictions"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String(150), nullable=False)
    predicted_yield = Column(Float, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    yield_category = Column(String(50), nullable=False)  # Low / Medium / High
    prediction_factors = Column(Text, nullable=False)  # Serialized JSON list of factors
    recommendations = Column(Text, nullable=False)  # Serialized JSON list of advice
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="yield_predictions")
