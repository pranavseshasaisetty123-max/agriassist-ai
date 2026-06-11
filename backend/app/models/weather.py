from sqlalchemy import Column, Integer, Float, String, DateTime, Text, func
from app.core.database import Base


class WeatherCache(Base):
    __tablename__ = "weather_caches"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    current_temp = Column(Float, nullable=False)
    current_condition = Column(String(100), nullable=False)
    forecast_json = Column(Text, nullable=False)  # JSON-encoded forecast details
    cached_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
