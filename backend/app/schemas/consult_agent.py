from datetime import datetime
from typing import List
from pydantic import BaseModel


class ConsultationAskRequest(BaseModel):
    question: str


class ConsultationResponse(BaseModel):
    farm_health_score: int
    health_summary: str
    key_findings: List[str]
    recommended_actions: List[str]
    risk_assessment: str
    answer: str
    confidence_score: int

    class Config:
        from_attributes = True


class ConsultationHistoryResponse(BaseModel):
    id: int
    farmer_id: int
    question: str
    answer: str
    created_at: datetime
    farm_health_score: int
    health_summary: str
    key_findings: List[str]
    recommended_actions: List[str]
    risk_assessment: str
    confidence_score: int

    class Config:
        from_attributes = True
