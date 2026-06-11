from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SoilRecommendationResponse(BaseModel):
    id: int
    report_id: int
    nitrogen_recommendation: str
    phosphorus_recommendation: str
    potassium_recommendation: str
    fertilizer_schedule: str
    ai_raw_analysis: str
    created_at: datetime

    class Config:
        from_attributes = True


class SoilReportBase(BaseModel):
    ph: float = Field(..., ge=0.0, le=14.0, description="Soil pH value")
    nitrogen: float = Field(..., ge=0.0, description="Nitrogen value in mg/kg")
    phosphorus: float = Field(..., ge=0.0, description="Phosphorus value in mg/kg")
    potassium: float = Field(..., ge=0.0, description="Potassium value in mg/kg")
    organic_matter: Optional[float] = Field(None, ge=0.0, le=100.0, description="Organic matter percentage")
    crop_planned: str = Field(..., min_length=1, max_length=150)
    tested_at: date


class SoilReportCreate(SoilReportBase):
    pass


class SoilReportResponse(SoilReportBase):
    id: int
    farmer_id: int
    created_at: datetime
    updated_at: datetime
    recommendation: Optional[SoilRecommendationResponse] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat()
        }
