from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class YieldPredictionRequest(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=150)


class YieldPredictionResponse(BaseModel):
    id: int
    farmer_id: int
    crop_name: str
    predicted_yield: float
    confidence_score: int = Field(..., ge=0, le=100)
    yield_category: str
    prediction_factors: List[str]
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
