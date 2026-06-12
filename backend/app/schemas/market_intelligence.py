from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class MarketPriceItem(BaseModel):
    market_name: str
    state: str
    price_per_kg: float
    recorded_date: date

    class Config:
        from_attributes = True


class StateAverageItem(BaseModel):
    state: str
    price_per_kg: float


class CropMarketPricesResponse(BaseModel):
    crop_name: str
    average_price: float
    recorded_date: date
    top_markets: List[MarketPriceItem]
    state_averages: List[StateAverageItem]
    markets: List[MarketPriceItem]


class PriceTrendResponse(BaseModel):
    recorded_date: date
    price_per_kg: float


class ProfitCalculationRequest(BaseModel):
    crop_name: str
    expected_yield: float = Field(..., ge=0)
    cultivation_cost: float = Field(..., ge=0)
    market_price_per_kg: Optional[float] = Field(None, ge=0)


class ProfitabilityAnalysisResponse(BaseModel):
    id: int
    farmer_id: int
    crop_name: str
    expected_yield: float
    cultivation_cost: float
    market_price_per_kg: float
    estimated_revenue: float
    estimated_profit: float
    profit_margin: float
    created_at: datetime

    class Config:
        from_attributes = True


class TrendPoint(BaseModel):
    recorded_date: date
    price_per_kg: float


class ExplainTrendsRequest(BaseModel):
    crop_name: str
    trends: List[TrendPoint]


class ExplainTrendsResponse(BaseModel):
    explanation: str
