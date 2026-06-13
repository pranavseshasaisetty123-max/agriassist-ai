from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FarmAnalyticsSnapshot(Base):
    __tablename__ = "farm_analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    health_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    projected_profit = Column(Float, nullable=False)
    projected_yield = Column(Float, nullable=False)
    active_crop_count = Column(Integer, nullable=False)
    active_alert_count = Column(Integer, nullable=False)
    snapshot_json = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="farm_analytics_snapshots")
