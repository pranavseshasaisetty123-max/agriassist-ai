from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class FarmTaskResponse(BaseModel):
    id: int
    farm_plan_id: int
    title: str
    description: str
    planned_date: date
    priority: str
    category: str
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FarmPlanGenerateRequest(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=150)
    area_acres: float = Field(..., gt=0)
    planned_start_date: date


class FarmPlanResponse(BaseModel):
    id: int
    farmer_id: int
    crop_name: str
    area_acres: float
    planned_start_date: date
    expected_harvest_date: date
    status: str
    created_at: datetime
    tasks: List[FarmTaskResponse] = []

    class Config:
        from_attributes = True


class TaskStatusUpdateRequest(BaseModel):
    status: Literal["pending", "completed", "overdue", "cancelled"]


class ManualTaskCreateRequest(BaseModel):
    farm_plan_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    planned_date: date
    priority: Literal["low", "medium", "high"]
    category: Literal[
        "land_preparation",
        "sowing",
        "irrigation",
        "fertilizer",
        "monitoring",
        "disease_control",
        "harvest",
        "post_harvest",
    ]
