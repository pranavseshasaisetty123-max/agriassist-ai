from datetime import datetime
from typing import List
from pydantic import BaseModel


class DiseaseScanBase(BaseModel):
    image_path: str
    disease_name: str
    confidence: float
    severity: str
    symptoms: List[str]
    treatment: List[str]
    preventive_measures: List[str]


class DiseaseScanResponse(DiseaseScanBase):
    id: int
    farmer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
