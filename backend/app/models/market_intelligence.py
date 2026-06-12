from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(150), nullable=False, index=True)
    market_name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False)
    price_per_kg = Column(Float, nullable=False)
    recorded_date = Column(Date, nullable=False, index=True)


class ProfitabilityAnalysis(Base):
    __tablename__ = "profitability_analyses"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String(150), nullable=False)
    expected_yield = Column(Float, nullable=False)
    cultivation_cost = Column(Float, nullable=False)
    market_price_per_kg = Column(Float, nullable=False)
    estimated_revenue = Column(Float, nullable=False)
    estimated_profit = Column(Float, nullable=False)
    profit_margin = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="profitability_analyses")
