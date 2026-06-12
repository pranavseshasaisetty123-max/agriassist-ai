from datetime import datetime
from typing import List
from pydantic import BaseModel


class RiskAlertResponse(BaseModel):
    id: int
    farmer_id: int
    crop_name: str
    alert_title: str
    category: str  # disease / pest / weather
    severity: str  # low / medium / high / critical
    probability: int  # 0-100
    description: str
    prevention_steps: List[str]
    monitoring_advice: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    overall_risk_score: int
    risk_level: str
    alerts: List[RiskAlertResponse]
