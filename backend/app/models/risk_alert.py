from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String(150), nullable=False)
    alert_title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # disease / pest / weather
    severity = Column(String(50), nullable=False)  # low / medium / high / critical
    probability = Column(Integer, nullable=False)  # 0-100
    description = Column(Text, nullable=False)
    prevention_steps = Column(Text, nullable=False)  # Serialized JSON list of strings
    monitoring_advice = Column(Text, nullable=False)  # Serialized JSON list of strings
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="risk_alerts")
