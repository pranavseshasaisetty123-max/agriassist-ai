import logging
import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.models.farmer import Farmer
from app.models.risk_alert import RiskAlert
from app.repositories.farm_planner import farm_plan_repo
from app.repositories.soil import soil_report_repo
from app.repositories.risk_intelligence import risk_alert_repo
from app.services.weather import weather_intelligence_service
from app.services.ai import ai_service
from app.services.farm import farm_service


logger = logging.getLogger("agriassist.risk_intel_service")


class RiskIntelligenceService:
    def _format_alert(self, alert: RiskAlert) -> Dict[str, Any]:
        try:
            prevention_steps = json.loads(alert.prevention_steps)
        except Exception:
            prevention_steps = [alert.prevention_steps] if alert.prevention_steps else []

        try:
            monitoring_advice = json.loads(alert.monitoring_advice)
        except Exception:
            monitoring_advice = [alert.monitoring_advice] if alert.monitoring_advice else []

        return {
            "id": alert.id,
            "farmer_id": alert.farmer_id,
            "crop_name": alert.crop_name,
            "alert_title": alert.alert_title,
            "category": alert.category,
            "severity": alert.severity,
            "probability": alert.probability,
            "description": alert.description,
            "prevention_steps": prevention_steps,
            "monitoring_advice": monitoring_advice,
            "created_at": alert.created_at
        }

    def _calculate_overall_assessment(self, alerts: List[RiskAlert]) -> Dict[str, Any]:
        if not alerts:
            return {
                "overall_risk_score": 0,
                "risk_level": "Low",
                "alerts": []
            }

        weights = {"critical": 1.2, "high": 1.0, "medium": 0.8, "low": 0.5}
        total_weighted = 0.0
        total_weight = 0.0

        for a in alerts:
            prob = a.probability
            sev = a.severity.lower()
            w = weights.get(sev, 0.8)
            total_weighted += prob * w
            total_weight += w

        overall_score = int(total_weighted / total_weight) if total_weight > 0 else 0
        overall_score = min(max(overall_score, 0), 100)

        # Classify severity level
        if overall_score <= 30:
            risk_level = "Low"
        elif overall_score <= 60:
            risk_level = "Medium"
        elif overall_score <= 80:
            risk_level = "High"
        else:
            risk_level = "Critical"

        formatted_alerts = [self._format_alert(a) for a in alerts]

        return {
            "overall_risk_score": overall_score,
            "risk_level": risk_level,
            "alerts": formatted_alerts
        }

    def generate_risk_intelligence(self, db: Session, farmer: Farmer) -> Dict[str, Any]:
        active_farm = farm_service.get_or_create_active_farm(db, farmer)

        # 1. Fetch active crop plans
        plans = farm_plan_repo.list_by_farmer(db, farmer.id, farm_id=active_farm.id)
        active_plans = [p for p in plans if p.status == "active"]
        
        if not active_plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please create a crop plan before generating risk intelligence."
            )

        # 2. Get latest soil metrics
        reports = soil_report_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1, farm_id=active_farm.id)
        if reports:
            report = reports[0]
            soil_metrics = {
                "ph": report.ph,
                "nitrogen": report.nitrogen,
                "phosphorus": report.phosphorus,
                "potassium": report.potassium,
                "organic_matter": report.organic_matter
            }
        else:
            soil_metrics = {
                "ph": 6.5,
                "nitrogen": 40.0,
                "phosphorus": 30.0,
                "potassium": 180.0,
                "organic_matter": 1.5
            }

        # 3. Get weather forecast
        location = farmer.location or "Delhi, India"
        try:
            _, _, temp, condition, forecast = weather_intelligence_service.get_weather_data(db, location)
        except Exception as e:
            logger.error(f"Failed to fetch weather data for risk assessment: {e}", exc_info=True)
            temp = 28.0
            condition = "Sunny"
            forecast = []

        weather_metrics = {
            "temp": temp,
            "condition": condition,
            "forecast_summary": ", ".join([
                f"{item['date']}: {item['condition']} (L:{item['temp_min']}°C, H:{item['temp_max']}°C)"
                for item in forecast[:5]
            ])
        }

        # 4. Active crop names
        crop_names = list(set([p.crop_name for p in active_plans]))

        # 5. Call AI Service
        try:
            ai_data = ai_service.generate_risk_analysis(
                soil_metrics=soil_metrics,
                weather_metrics=weather_metrics,
                crop_names=crop_names,
                location=location
            )
        except Exception as e:
            logger.error(f"Gemini risk warnings generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini risk warning engine is temporarily unavailable. Please try again later."
            )

        # 6. Save risk alerts in DB in a single transaction
        created_alerts = []
        ai_alerts = ai_data.get("alerts", [])
        
        for alert in ai_alerts:
            db_obj = risk_alert_repo.create(
                db=db,
                farmer_id=farmer.id,
                farm_id=active_farm.id,
                crop_name=alert.get("crop_name", crop_names[0]),
                alert_title=alert.get("title", "Disease Risk Alert"),
                category=alert.get("category", "disease"),
                severity=alert.get("risk_level", "medium"),
                probability=alert.get("probability", 50),
                description=alert.get("description", ""),
                prevention_steps=alert.get("prevention_steps", []),
                monitoring_advice=alert.get("monitoring_advice", [])
            )
            created_alerts.append(db_obj)

        return self._calculate_overall_assessment(created_alerts)

    def get_latest_warnings(self, db: Session, farmer_id: int, farmer: Optional[Farmer] = None) -> Dict[str, Any]:
        if not farmer:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        alerts = risk_alert_repo.get_latest_run_alerts(db, farmer_id, farm_id=active_farm.id)
        return self._calculate_overall_assessment(alerts)

    def get_history(self, db: Session, farmer_id: int, farmer: Optional[Farmer] = None) -> List[Dict[str, Any]]:
        if not farmer:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        alerts = risk_alert_repo.list_by_farmer(db, farmer_id, farm_id=active_farm.id)
        return [self._format_alert(a) for a in alerts]



risk_intelligence_service = RiskIntelligenceService()
