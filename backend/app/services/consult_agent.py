import logging
import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.models.farmer import Farmer
from app.models.consult_agent import ConsultationHistory
from app.repositories.soil import soil_report_repo
from app.services.weather import weather_intelligence_service
from app.repositories.crop_recommendation import crop_recommendation_repo
from app.repositories.market_intelligence import profitability_analysis_repo
from app.repositories.yield_prediction import yield_prediction_repo
from app.repositories.farm_planner import farm_plan_repo
from app.repositories.risk_intelligence import risk_alert_repo
from app.repositories.consult_agent import consultation_history_repo
from app.services.ai import ai_service

logger = logging.getLogger("agriassist.consult_service")


class ConsultationService:
    def _format_consultation(self, c: ConsultationHistory) -> Dict[str, Any]:
        try:
            snapshot = json.loads(c.context_snapshot_json)
        except Exception:
            snapshot = {}

        details = snapshot.get("consultation_details", {})
        
        return {
            "id": c.id,
            "farmer_id": c.farmer_id,
            "question": c.question,
            "answer": c.answer,
            "created_at": c.created_at,
            "farm_health_score": details.get("farm_health_score", 0),
            "health_summary": details.get("health_summary", ""),
            "key_findings": details.get("key_findings", []),
            "recommended_actions": details.get("recommended_actions", []),
            "risk_assessment": details.get("risk_assessment", ""),
            "confidence_score": details.get("confidence_score", 0)
        }

    def ask_consultant(self, db: Session, farmer: Farmer, question: str) -> Dict[str, Any]:
        # 1. Fetch Latest Soil Report
        soil_data = None
        latest_reports = soil_report_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1)
        if latest_reports:
            r = latest_reports[0]
            soil_data = {
                "ph": r.ph,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "organic_matter": r.organic_matter,
                "crop_planned": r.crop_planned,
                "tested_at": r.tested_at.isoformat() if r.tested_at else None
            }

        # 2. Fetch Weather & 7 Day Forecast
        weather_data = None
        location = farmer.location or "Delhi, India"
        try:
            _, _, temp, condition, forecast = weather_intelligence_service.get_weather_data(db, location)
            weather_data = {
                "temp": temp,
                "condition": condition,
                "forecast": forecast[:7] if forecast else []
            }
        except Exception as e:
            logger.error(f"Failed to load weather context for consultant: {e}")
            weather_data = {
                "temp": 28.0,
                "condition": "Sunny",
                "forecast": []
            }

        # 3. Fetch Crop Recommendations
        crop_recs = []
        latest_recs = crop_recommendation_repo.list_by_farmer(db, farmer_id=farmer.id, limit=5)
        for rec in latest_recs:
            try:
                risk_factors = json.loads(rec.risk_factors)
            except Exception:
                risk_factors = []
            try:
                farming_tips = json.loads(rec.farming_tips)
            except Exception:
                farming_tips = []
            crop_recs.append({
                "crop_name": rec.crop_name,
                "suitability_score": rec.suitability_score,
                "season": rec.season,
                "recommendation_reason": rec.recommendation_reason,
                "risk_factors": risk_factors,
                "farming_tips": farming_tips
            })

        # 4. Fetch Yield Predictions
        yield_preds = []
        latest_preds = yield_prediction_repo.list_by_farmer(db, farmer_id=farmer.id, limit=5)
        for p in latest_preds:
            try:
                factors = json.loads(p.prediction_factors)
            except Exception:
                factors = []
            try:
                recs = json.loads(p.recommendations)
            except Exception:
                recs = []
            yield_preds.append({
                "crop_name": p.crop_name,
                "predicted_yield": p.predicted_yield,
                "confidence_score": p.confidence_score,
                "yield_category": p.yield_category,
                "prediction_factors": factors,
                "recommendations": recs
            })

        # 5. Fetch Market Intelligence (Profitability Analyses)
        market_intel = []
        latest_analyses = profitability_analysis_repo.list_by_farmer(db, farmer_id=farmer.id, limit=5)
        for a in latest_analyses:
            market_intel.append({
                "crop_name": a.crop_name,
                "expected_yield": a.expected_yield,
                "cultivation_cost": a.cultivation_cost,
                "market_price_per_kg": a.market_price_per_kg,
                "estimated_revenue": a.estimated_revenue,
                "estimated_profit": a.estimated_profit,
                "profit_margin": a.profit_margin
            })

        # 6. Fetch Active Farm Plans
        plans_data = []
        plans = farm_plan_repo.list_by_farmer(db, farmer.id)
        active_plans = [p for p in plans if p.status == "active"]
        for p in active_plans:
            plans_data.append({
                "crop_name": p.crop_name,
                "area_acres": p.area_acres,
                "planned_start_date": p.planned_start_date.isoformat() if p.planned_start_date else None,
                "expected_harvest_date": p.expected_harvest_date.isoformat() if p.expected_harvest_date else None
            })

        # 7. Fetch Active Risk Warnings
        active_warnings = []
        alerts = risk_alert_repo.get_latest_run_alerts(db, farmer.id)
        for a in alerts:
            try:
                prev = json.loads(a.prevention_steps)
            except Exception:
                prev = []
            try:
                mon = json.loads(a.monitoring_advice)
            except Exception:
                mon = []
            active_warnings.append({
                "crop_name": a.crop_name,
                "alert_title": a.alert_title,
                "category": a.category,
                "severity": a.severity,
                "probability": a.probability,
                "description": a.description,
                "prevention_steps": prev,
                "monitoring_advice": mon
            })

        # 8. Call AI Service
        try:
            ai_data = ai_service.generate_farm_consultation(
                soil_report=soil_data,
                weather_data=weather_data,
                crop_recommendations=crop_recs,
                yield_predictions=yield_preds,
                market_intelligence=market_intel,
                active_farm_plans=plans_data,
                active_risk_warnings=active_warnings,
                question=question,
                location=location
            )
        except Exception as e:
            logger.error(f"Gemini farm consultation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini virtual agronomist is temporarily unavailable. Please try again later."
            )

        # 9. Create snapshot dictionary
        context_snapshot = {
            "soil_report": soil_data,
            "weather": weather_data,
            "crop_recommendations": crop_recs,
            "yield_predictions": yield_preds,
            "market_intelligence": market_intel,
            "active_farm_plans": plans_data,
            "active_risk_warnings": active_warnings,
            "consultation_details": {
                "farm_health_score": ai_data.get("farm_health_score", 0),
                "health_summary": ai_data.get("health_summary", ""),
                "key_findings": ai_data.get("key_findings", []),
                "recommended_actions": ai_data.get("recommended_actions", []),
                "risk_assessment": ai_data.get("risk_assessment", ""),
                "confidence_score": ai_data.get("confidence_score", 0)
            }
        }

        # 10. Persist consultation history
        db_obj = consultation_history_repo.create(
            db=db,
            farmer_id=farmer.id,
            question=question,
            answer=ai_data.get("answer", ""),
            context_snapshot=context_snapshot
        )

        return self._format_consultation(db_obj)

    def get_history(self, db: Session, farmer_id: int) -> List[Dict[str, Any]]:
        history = consultation_history_repo.list_by_farmer(db, farmer_id)
        return [self._format_consultation(h) for h in history]

    def get_detail(self, db: Session, farmer: Farmer, consult_id: int) -> Dict[str, Any]:
        c = consultation_history_repo.get_by_id(db, consult_id)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation log not found."
            )
        if c.farmer_id != farmer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this consultation log."
            )
        return self._format_consultation(c)


consult_agent_service = ConsultationService()
