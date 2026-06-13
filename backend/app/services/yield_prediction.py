import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.yield_prediction import YieldPrediction
from app.repositories.soil import soil_report_repo
from app.repositories.yield_prediction import yield_prediction_repo
from app.services.weather import weather_intelligence_service
from app.services.ai import ai_service
from app.services.farm import farm_service

logger = logging.getLogger("agriassist.yield_pred_service")


class YieldPredictionService:
    def _format_pred_dict(self, pred: YieldPrediction) -> Dict[str, Any]:
        """Convert YieldPrediction model into a dictionary with deserialized lists."""
        try:
            prediction_factors = json.loads(pred.prediction_factors)
        except Exception:
            prediction_factors = [pred.prediction_factors] if pred.prediction_factors else []

        try:
            recommendations = json.loads(pred.recommendations)
        except Exception:
            recommendations = [pred.recommendations] if pred.recommendations else []

        return {
            "id": pred.id,
            "farmer_id": pred.farmer_id,
            "crop_name": pred.crop_name,
            "predicted_yield": pred.predicted_yield,
            "confidence_score": pred.confidence_score,
            "yield_category": pred.yield_category,
            "prediction_factors": prediction_factors,
            "recommendations": recommendations,
            "created_at": pred.created_at
        }

    def generate_yield_prediction(self, db: Session, farmer: Farmer, crop_name: str) -> Dict[str, Any]:
        """
        Gathers latest Soil Report and current Weather data,
        invokes Gemini AI to estimate expected yield, and persists results.
        """
        active_farm = farm_service.get_or_create_active_farm(db, farmer)

        # 1. Fetch latest Soil Report
        reports = soil_report_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1, farm_id=active_farm.id)
        if not reports:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please log a soil test report first to predict crop yield."
            )
        report = reports[0]

        # 2. Fetch Weather Data (coordinates, temp, condition, forecast)
        location = farmer.location or "Delhi, India"
        try:
            _, _, temp, condition, forecast = weather_intelligence_service.get_weather_data(db, location)
        except Exception as e:
            logger.error(f"Failed to fetch weather data for yield prediction: {e}", exc_info=True)
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
        weather_metrics = {
            "temp": temp,
            "condition": condition,
            "forecast_summary": ", ".join([
                f"{item['date']}: {item['condition']} (L:{item['temp_min']}°C, H:{item['temp_max']}°C)"
                for item in forecast[:5]
            ])
        }

        # 4. Invoke Gemini AI Service
        try:
            ai_data = ai_service.generate_yield_prediction(
                soil_metrics=soil_metrics,
                weather_metrics=weather_metrics,
                crop_name=crop_name,
                location=location
            )
        except Exception as e:
            logger.error(f"Gemini yield prediction failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini yield prediction engine is temporarily unavailable. Please try again later."
            )

        # 5. Persist prediction
        try:
            db_obj = yield_prediction_repo.create(
                db=db,
                farmer_id=farmer.id,
                farm_id=active_farm.id,
                crop_name=crop_name,
                predicted_yield=ai_data.get("predicted_yield", 0.0),
                confidence_score=ai_data.get("confidence_score", 0),
                yield_category=ai_data.get("yield_category", "Medium"),
                prediction_factors=ai_data.get("prediction_factors", []),
                recommendations=ai_data.get("recommendations", [])
            )
            return self._format_pred_dict(db_obj)
        except Exception as e:
            logger.error(f"Failed to save yield prediction to database: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist crop yield prediction metrics."
            )

    def list_predictions(self, db: Session, farmer_id: int, limit: int = 100, offset: int = 0, farmer: Optional[Farmer] = None) -> List[Dict[str, Any]]:
        """List historical yield predictions run by the farmer."""
        if not farmer:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        preds = yield_prediction_repo.list_by_farmer(db, farmer_id=farmer_id, limit=limit, offset=offset, farm_id=active_farm.id)
        return [self._format_pred_dict(p) for p in preds]


    def get_prediction(self, db: Session, farmer_id: int, pred_id: int) -> Dict[str, Any]:
        """Fetch details of a specific yield prediction after checking ownership."""
        pred = yield_prediction_repo.get_by_id(db, pred_id)
        if not pred:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yield prediction record not found."
            )
        if pred.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this yield prediction."
            )
        return self._format_pred_dict(pred)


yield_prediction_service = YieldPredictionService()
