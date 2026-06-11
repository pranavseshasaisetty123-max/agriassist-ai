from pydantic import BaseModel
from typing import List
from datetime import datetime


class WeatherCurrentResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    current_temp: float
    current_condition: str


class ForecastItem(BaseModel):
    date: str
    temp_min: float
    temp_max: float
    condition: str
    weather_code: int


class WeatherForecastResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    forecast: List[ForecastItem]


class AIAdvisoryResponse(BaseModel):
    crop: str
    advisory_points: List[str]
    severity: str  # "info", "warning", "critical"
    generated_at: datetime

    class Config:
        from_attributes = True
