from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # weather, risk, disease, planner, yield, agronomist, system
    priority = Column(String(50), nullable=False)  # low, medium, high, critical
    source_module = Column(String(100), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="notifications")
