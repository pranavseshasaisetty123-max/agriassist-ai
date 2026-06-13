from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Dict, Any


class KPIMetricsResponse(BaseModel):
    health_score: float
    risk_score: float
    projected_yield: float
    projected_profit: float
    active_crop_count: int
    active_alert_count: int

    model_config = ConfigDict(from_attributes=True)


class AnalyticsSnapshotResponse(BaseModel):
    id: int
    farmer_id: int
    health_score: float
    risk_score: float
    projected_profit: float
    projected_yield: float
    active_crop_count: int
    active_alert_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrendSnapshotResponse(BaseModel):
    id: int
    health_score: float
    risk_score: float
    projected_profit: float
    projected_yield: float
    active_crop_count: int
    active_alert_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardAnalyticsResponse(BaseModel):
    kpis: KPIMetricsResponse
    trends: List[TrendSnapshotResponse]
    insights: List[str]
    crop_distribution: Dict[str, float]
    alert_distribution: Dict[str, int]


class ReportPayloadResponse(BaseModel):
    kpis: KPIMetricsResponse
    active_risks: List[Dict[str, Any]]
    recommendations: List[str]
    yield_forecasts: List[Dict[str, Any]]
    profit_forecasts: List[Dict[str, Any]]
