import httpx
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.farmer import Farmer
from app.repositories.weather import weather_cache_repo
from app.repositories.soil import soil_report_repo
from app.services.ai import ai_service

logger = logging.getLogger("agriassist.weather_service")

WMO_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail"
}


class WeatherIntelligenceService:
    def _interpret_wmo_code(self, code: int) -> str:
        return WMO_CODE_MAP.get(code, "Unknown weather")

    def _geocode_location(self, location: str) -> tuple[float, float]:
        """Convert a text location into (latitude, longitude) using Open-Meteo Geocoding API."""
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={httpx.URL(location).raw_path.decode()}&count=1&language=en&format=json"
            response = httpx.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and len(data["results"]) > 0:
                    result = data["results"][0]
                    return float(result["latitude"]), float(result["longitude"])
            logger.warning(f"Geocoding failed for location '{location}'. Falling back to default Delhi coordinates.")
        except Exception as e:
            logger.error(f"Geocoding connection error: {e}")
        
        # Default fallback coordinates: New Delhi, India
        return 28.6139, 77.2090

    def get_weather_data(self, db: Session, location: str) -> tuple[float, float, float, str, list]:
        """
        Check database cache for weather coordinates and forecasts.
        If cache is missing or older than 1 hour, pull new metrics from Open-Meteo.
        """
        # 1. Clean location string
        loc_clean = location.strip()
        if not loc_clean:
            loc_clean = "Delhi, India"

        # 2. Check DB Cache
        cache = weather_cache_repo.get_by_location(db, location=loc_clean)
        if cache and cache.cached_at > datetime.utcnow() - timedelta(hours=1):
            try:
                forecast = json.loads(cache.forecast_json)
                return cache.latitude, cache.longitude, cache.current_temp, cache.current_condition, forecast
            except Exception as e:
                logger.error(f"Failed to parse cached forecast: {e}")

        # 3. Cache Miss / Expired -> Pull live
        logger.info(f"Weather cache miss for '{loc_clean}'. Querying Open-Meteo API...")
        lat, lon = self._geocode_location(loc_clean)

        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
            response = httpx.get(url, timeout=12.0)
            
            if response.status_code != 200:
                raise ValueError(f"Open-Meteo API returned status code {response.status_code}")
                
            data = response.json()
            current = data["current_weather"]
            current_temp = float(current["temperature"])
            current_cond = self._interpret_wmo_code(int(current["weathercode"]))
            
            # Formulate 7-day forecast array
            daily = data["daily"]
            forecast = []
            for i in range(len(daily["time"])):
                wcode = int(daily["weathercode"][i])
                forecast.append({
                    "date": daily["time"][i],
                    "temp_min": float(daily["temperature_2m_min"][i]),
                    "temp_max": float(daily["temperature_2m_max"][i]),
                    "condition": self._interpret_wmo_code(wcode),
                    "weather_code": wcode
                })
                
            # Update cache database entry
            weather_cache_repo.create_or_update(
                db=db,
                location=loc_clean,
                latitude=lat,
                longitude=lon,
                current_temp=current_temp,
                current_condition=current_cond,
                forecast_json=json.dumps(forecast)
            )
            
            return lat, lon, current_temp, current_cond, forecast
            
        except Exception as e:
            logger.error(f"Open-Meteo fetch failed: {e}")
            if cache:
                logger.warning("Returning stale cached data due to API connection failure.")
                forecast = json.loads(cache.forecast_json)
                return cache.latitude, cache.longitude, cache.current_temp, cache.current_condition, forecast
            
            # Hard fallback mock if API is down and no cache exists
            mock_forecast = []
            base_date = datetime.now()
            for i in range(7):
                date_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
                mock_forecast.append({
                    "date": date_str,
                    "temp_min": 22.0,
                    "temp_max": 34.0,
                    "condition": "Partly cloudy",
                    "weather_code": 2
                })
            return lat, lon, 28.5, "Partly cloudy", mock_forecast


weather_intelligence_service = WeatherIntelligenceService()


class SmartAdvisoryService:
    def generate_farming_advisory(self, db: Session, farmer: Farmer) -> dict:
        """
        Evaluate the latest soil report metrics and upcoming weather forecast parameters
        to return crop-tailored agronomist advisories.
        """
        location = farmer.location or "Delhi, India"
        
        # 1. Fetch latest soil report
        reports = soil_report_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1)
        if not reports:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please log a soil test report first to generate personalized agricultural weather advisories."
            )
        report = reports[0]
        
        # 2. Retrieve weather forecast
        _, _, temp, cond, forecast = weather_intelligence_service.get_weather_data(db, location)
        
        # 3. Format a forecast summary for prompt injection
        forecast_summary = ", ".join([
            f"{item['date']}: {item['condition']} (L:{item['temp_min']}°C, H:{item['temp_max']}°C)"
            for item in forecast[:5] # Send next 5 days to keep token payload concise
        ])
        
        # 4. Generate structured advisory from Gemini
        try:
            ai_data = ai_service.generate_weather_advisory(
                crop_planned=report.crop_planned,
                ph=report.ph,
                nitrogen=report.nitrogen,
                phosphorus=report.phosphorus,
                potassium=report.potassium,
                organic_matter=report.organic_matter,
                location=location,
                current_temp=temp,
                current_condition=cond,
                forecast_summary=forecast_summary
            )
            
            return {
                "crop": report.crop_planned,
                "advisory_points": ai_data["advisory_points"],
                "severity": ai_data["severity"],
                "generated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error("Failed to generate smart weather advisory", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI advisory temporarily unavailable. Weather and soil data remain accessible."
            )


smart_advisory_service = SmartAdvisoryService()
