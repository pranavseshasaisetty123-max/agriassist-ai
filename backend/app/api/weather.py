from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.schemas.weather import WeatherCurrentResponse, WeatherForecastResponse, AIAdvisoryResponse
from app.services.weather import weather_intelligence_service, smart_advisory_service

router = APIRouter()


@router.get("/current", response_model=WeatherCurrentResponse)
def get_current_weather(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve current weather status for the logged-in farmer's location."""
    location = current_farmer.location or "Delhi, India"
    lat, lon, temp, condition, _ = weather_intelligence_service.get_weather_data(db, location)
    
    return {
        "location": location,
        "latitude": lat,
        "longitude": lon,
        "current_temp": temp,
        "current_condition": condition
    }


@router.get("/forecast", response_model=WeatherForecastResponse)
def get_weather_forecast(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve 7-day daily weather forecast ranges for the farmer's location."""
    location = current_farmer.location or "Delhi, India"
    lat, lon, _, _, forecast = weather_intelligence_service.get_weather_data(db, location)
    
    return {
        "location": location,
        "latitude": lat,
        "longitude": lon,
        "forecast": forecast
    }


@router.get("/advisory", response_model=AIAdvisoryResponse)
def get_farming_advisory(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Generate crop-specific farming suggestions based on latest soil health and weather forecasts."""
    return smart_advisory_service.generate_farming_advisory(db, farmer=current_farmer)
