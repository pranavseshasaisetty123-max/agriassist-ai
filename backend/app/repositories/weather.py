from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.models.weather import WeatherCache


class WeatherCacheRepository:
    def get_by_location(self, db: Session, location: str) -> Optional[WeatherCache]:
        """Fetch weather cache entry by location string."""
        return db.query(WeatherCache).filter(WeatherCache.location == location).first()

    def create_or_update(
        self,
        db: Session,
        location: str,
        latitude: float,
        longitude: float,
        current_temp: float,
        current_condition: str,
        forecast_json: str
    ) -> WeatherCache:
        """Create or update a weather cache entry."""
        db_obj = self.get_by_location(db, location)
        
        if db_obj:
            db_obj.latitude = latitude
            db_obj.longitude = longitude
            db_obj.current_temp = current_temp
            db_obj.current_condition = current_condition
            db_obj.forecast_json = forecast_json
            db_obj.cached_at = datetime.utcnow()
        else:
            db_obj = WeatherCache(
                location=location,
                latitude=latitude,
                longitude=longitude,
                current_temp=current_temp,
                current_condition=current_condition,
                forecast_json=forecast_json
            )
            db.add(db_obj)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj


weather_cache_repo = WeatherCacheRepository()
