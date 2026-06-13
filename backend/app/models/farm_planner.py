from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FarmPlan(Base):
    __tablename__ = "farm_plans"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=True)
    crop_name = Column(String(150), nullable=False)
    area_acres = Column(Float, nullable=False)
    planned_start_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="active")  # active / completed / deleted
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="farm_plans")
    farm = relationship("Farm", back_populates="farm_plans")
    tasks = relationship("FarmTask", back_populates="farm_plan", cascade="all, delete-orphan")


class FarmTask(Base):
    __tablename__ = "farm_tasks"

    id = Column(Integer, primary_key=True, index=True)
    farm_plan_id = Column(Integer, ForeignKey("farm_plans.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    planned_date = Column(Date, nullable=False)
    priority = Column(String(50), nullable=False)  # low / medium / high
    category = Column(String(100), nullable=False)  # land_preparation / sowing / irrigation / fertilizer / monitoring / disease_control / harvest / post_harvest
    status = Column(String(50), nullable=False, default="pending")  # pending / completed / overdue / cancelled
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    farm_plan = relationship("FarmPlan", back_populates="tasks")
