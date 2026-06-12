import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.farmer import Farmer
from app.models.crop_recommendation import CropRecommendation
from app.repositories.soil import soil_report_repo
from app.repositories.crop_recommendation import crop_recommendation_repo
from app.services.weather import weather_intelligence_service
from app.services.ai import ai_service
from app.schemas.crop_recommendation import CropRecommendationCreate

logger = logging.getLogger("agriassist.crop_rec_service")


class CropRecommendationService:
    def _format_rec_dict(self, rec: CropRecommendation) -> Dict[str, Any]:
        """Convert CropRecommendation model into a dictionary with deserialized lists."""
        try:
            risk_factors = json.loads(rec.risk_factors)
        except Exception:
            risk_factors = [rec.risk_factors] if rec.risk_factors else []

        try:
            farming_tips = json.loads(rec.farming_tips)
        except Exception:
            farming_tips = [rec.farming_tips] if rec.farming_tips else []

        return {
            "id": rec.id,
            "farmer_id": rec.farmer_id,
            "crop_name": rec.crop_name,
            "suitability_score": rec.suitability_score,
            "season": rec.season,
            "recommendation_reason": rec.recommendation_reason,
            "risk_factors": risk_factors,
            "farming_tips": farming_tips,
            "created_at": rec.created_at
        }

    def generate_recommendations(self, db: Session, farmer: Farmer) -> List[Dict[str, Any]]:
        """
        Gathers context from latest Soil Report and current Weather,
        requests top 5 crop recommendations from Gemini, and saves them to the DB.
        """
        # 1. Fetch latest Soil Report
        reports = soil_report_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1)
        if not reports:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please log a soil test report first to generate personalized crop recommendations."
            )
        report = reports[0]

        # 2. Fetch Weather Data (coordinates, temp, condition, forecast)
        location = farmer.location or "Delhi, India"
        try:
            _, _, temp, condition, forecast = weather_intelligence_service.get_weather_data(db, location)
        except Exception as e:
            logger.error(f"Failed to fetch weather data for recommendations: {e}", exc_info=True)
            # Use mock parameters as fallback
            temp = 28.5
            condition = "Partly cloudy"
            forecast = []

        # 3. Format inputs for AI
        soil_metrics = {
            "ph": report.ph,
            "nitrogen": report.nitrogen,
            "phosphorus": report.phosphorus,
            "potassium": report.potassium,
            "organic_matter": report.organic_matter
        }
        current_weather = {
            "temp": temp,
            "condition": condition
        }
        forecast_summary = ", ".join([
            f"{item['date']}: {item['condition']} (L:{item['temp_min']}°C, H:{item['temp_max']}°C)"
            for item in forecast[:5]
        ])

        # 4. Invoke Gemini AI Service
        try:
            ai_data = ai_service.generate_crop_recommendations(
                soil_metrics=soil_metrics,
                current_weather=current_weather,
                forecast_summary=forecast_summary,
                location=location
            )
        except Exception as e:
            logger.error(f"Gemini crop recommendations failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini crop recommendations are temporarily unavailable. Please try again later."
            )

        recommendations_list = ai_data.get("recommendations", [])
        if not recommendations_list:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Received invalid empty crop recommendations from Gemini."
            )

        # 5. Save all recommendations in the batch with a shared created_at timestamp
        created_at_time = datetime.utcnow()
        saved_recs = []
        try:
            for item in recommendations_list:
                create_obj = CropRecommendationCreate(
                    crop_name=item.get("crop_name", "Unknown Crop"),
                    suitability_score=item.get("suitability_score", 0),
                    season=item.get("season", "Unknown Season"),
                    recommendation_reason=item.get("recommendation_reason", ""),
                    risk_factors=item.get("risk_factors", []),
                    farming_tips=item.get("farming_tips", [])
                )
                db_obj = crop_recommendation_repo.create(
                    db=db,
                    farmer_id=farmer.id,
                    obj_in=create_obj,
                    created_at=created_at_time
                )
                saved_recs.append(self._format_rec_dict(db_obj))
            return saved_recs
        except Exception as e:
            logger.error(f"Failed to save crop recommendations to database: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist crop recommendations."
            )

    def list_recommendations(self, db: Session, farmer_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List crop recommendation history records for a farmer."""
        recs = crop_recommendation_repo.list_by_farmer(db, farmer_id=farmer_id, limit=limit, offset=offset)
        return [self._format_rec_dict(r) for r in recs]

    def get_recommendation(self, db: Session, farmer_id: int, rec_id: int) -> Dict[str, Any]:
        """Fetch details of a single crop recommendation after validating ownership."""
        rec = crop_recommendation_repo.get_by_id(db, rec_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crop recommendation not found."
            )
        if rec.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this crop recommendation."
            )
        return self._format_rec_dict(rec)


crop_recommendation_service = CropRecommendationService()
