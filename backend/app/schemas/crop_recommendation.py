from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CropRecommendationBase(BaseModel):
    crop_name: str
    suitability_score: int = Field(..., ge=0, le=100)
    season: str
    recommendation_reason: str
    risk_factors: List[str]
    farming_tips: List[str]


class CropRecommendationCreate(CropRecommendationBase):
    pass


class CropRecommendationResponse(CropRecommendationBase):
    id: int
    farmer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
