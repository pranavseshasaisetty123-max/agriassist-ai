from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class FarmBase(BaseModel):
    name: str
    location: str
    total_area_acres: float
    soil_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    total_area_acres: Optional[float] = None
    soil_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmResponse(FarmBase):
    id: int
    farmer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PortfolioResponse(BaseModel):
    total_farms: int
    total_area: float
    portfolio_profit: float
    portfolio_yield: float
    portfolio_risk: float
    active_crop_plans: int
