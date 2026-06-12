import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.farmer import Farmer
from app.models.notification import Notification
from app.repositories.notification import notification_repo
from app.repositories.soil import soil_report_repo
from app.services.weather import weather_intelligence_service
from app.services.risk_intelligence import risk_intelligence_service
from app.repositories.risk_intelligence import risk_alert_repo
from app.repositories.farm_planner import farm_task_repo
from app.repositories.yield_prediction import yield_prediction_repo
from app.repositories.disease import disease_scan_repo
from app.repositories.consult_agent import consultation_history_repo

logger = logging.getLogger("agriassist.notification_service")


class NotificationService:
    def _create_if_not_exists(
        self,
        db: Session,
        farmer_id: int,
        title: str,
        message: str,
        notification_type: str,
        priority: str,
        source_module: str,
    ) -> bool:
        exists = notification_repo.check_exists(
            db=db,
            farmer_id=farmer_id,
            notification_type=notification_type,
            source_module=source_module,
            title=title
        )
        if not exists:
            notification_repo.create(
                db=db,
                farmer_id=farmer_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                source_module=source_module
            )
            return True
        return False

    def generate_notifications(self, db: Session, farmer: Farmer) -> int:
        generated_count = 0
        location = farmer.location or "Delhi, India"

        # 1. Weather Forecast Alerts
        try:
            _, _, _, _, forecast = weather_intelligence_service.get_weather_data(db, location)
            for item in forecast[:5]:
                # Severe Rain threshold: WMO codes 65, 82, 95-99
                wcode = item.get("weather_code")
                if wcode in [65, 82, 95, 96, 99] or "heavy rain" in item.get("condition", "").lower() or "thunderstorm" in item.get("condition", "").lower():
                    title = f"Severe Rainfall Forecast: {item.get('date')}"
                    message = f"Heavy rainfall or thunderstorms ({item.get('condition')}) are forecasted for {item.get('date')} in {location}. Postpone fertilizer application or excessive watering."
                    if self._create_if_not_exists(db, farmer.id, title, message, "weather", "critical", "weather"):
                        generated_count += 1
                
                # Heatwave threshold: temp_max > 40
                tmax = item.get("temp_max", 0.0)
                if tmax > 40.0:
                    title = f"Heatwave Alert: {item.get('date')}"
                    message = f"High temperatures forecasted to reach {tmax}°C on {item.get('date')} in {location}. Ensure adequate soil moisture and schedule watering for cooler hours."
                    if self._create_if_not_exists(db, farmer.id, title, message, "weather", "high", "weather"):
                        generated_count += 1
        except Exception as e:
            logger.error(f"Weather notification scan failed: {e}", exc_info=True)

        # 2. Risk Intelligence Alerts
        try:
            # Overall Risk
            assessment = risk_intelligence_service.get_latest_warnings(db, farmer.id)
            score = assessment.get("overall_risk_score", 0)
            if score >= 80:
                title = "Critical Overall Farm Risk"
                message = f"Your overall farm risk assessment has reached a Critical level ({score}/100) due to weather or disease hazards."
                if self._create_if_not_exists(db, farmer.id, title, message, "risk", "critical", "risk"):
                    generated_count += 1

            # Individual High Probability Disease Risks
            latest_alerts = risk_alert_repo.get_latest_run_alerts(db, farmer.id)
            for alert in latest_alerts:
                if alert.category == "disease" and alert.probability >= 80:
                    title = f"High Disease Risk: {alert.alert_title}"
                    message = f"There is a {alert.probability}% probability of '{alert.alert_title}' infection on {alert.crop_name}. {alert.description}"
                    if self._create_if_not_exists(db, farmer.id, title, message, "disease", alert.severity.lower() if alert.severity else "high", "risk"):
                        generated_count += 1
                elif alert.severity.lower() in ["high", "critical"] and alert.probability >= 80:
                    title = f"Urgent Risk Warning: {alert.alert_title}"
                    message = f"A {alert.severity} priority hazard '{alert.alert_title}' has a {alert.probability}% probability of affecting your {alert.crop_name} crop."
                    if self._create_if_not_exists(db, farmer.id, title, message, "risk", alert.severity.lower(), "risk"):
                        generated_count += 1
        except Exception as e:
            logger.error(f"Risk warning notification scan failed: {e}", exc_info=True)

        # 3. Farm Planner Alerts (Upcoming and Overdue)
        try:
            # Overdue Tasks
            overdue_tasks = farm_task_repo.get_overdue_tasks(db, farmer.id)
            for task in overdue_tasks:
                title = f"Overdue Task: {task.title}"
                message = f"The task '{task.title}' was scheduled for {task.planned_date.isoformat()} but is still pending. Please update its status."
                if self._create_if_not_exists(db, farmer.id, title, message, "planner", "high", "planner"):
                    generated_count += 1

            # Upcoming Tasks within 24 hours
            upcoming_tasks = farm_task_repo.get_upcoming_tasks(db, farmer.id, days=1)
            for task in upcoming_tasks:
                title = f"Upcoming Task: {task.title}"
                message = f"This is a reminder to perform task '{task.title}' scheduled for {task.planned_date.isoformat()}: {task.description}"
                if self._create_if_not_exists(db, farmer.id, title, message, "planner", task.priority.lower() if task.priority else "medium", "planner"):
                    generated_count += 1
        except Exception as e:
            logger.error(f"Farm planner notification scan failed: {e}", exc_info=True)

        # 4. Yield Prediction Alerts (Predicted Low Yield)
        try:
            # Get latest yield predictions
            yields = yield_prediction_repo.list_by_farmer(db, farmer_id=farmer.id, limit=5)
            for y in yields:
                if y.yield_category.lower() == "low":
                    title = f"Low Yield Warning: {y.crop_name}"
                    message = f"Our model predicts a Low yield of {y.predicted_yield} kg/acre for {y.crop_name} (Confidence: {y.confidence_score}%). Check agronomist advice."
                    if self._create_if_not_exists(db, farmer.id, title, message, "yield", "high", "yield"):
                        generated_count += 1
        except Exception as e:
            logger.error(f"Yield notification scan failed: {e}", exc_info=True)

        # 5. Disease Detection Alerts (High Severity Scans)
        try:
            scans = disease_scan_repo.list_by_farmer(db, farmer_id=farmer.id, limit=10)
            for scan in scans:
                if scan.severity.lower() in ["high", "critical"] and scan.diagnosis_type == "disease":
                    title = f"Severe Disease Detected: {scan.disease_name}"
                    message = f"A severe case of '{scan.disease_name}' was diagnosed on your field crop (Confidence: {int(scan.confidence * 100)}%). Apply treatments immediately."
                    if self._create_if_not_exists(db, farmer.id, title, message, "disease", scan.severity.lower(), "disease"):
                        generated_count += 1
        except Exception as e:
            logger.error(f"Disease detection notification scan failed: {e}", exc_info=True)

        # 6. Virtual Agronomist Alerts
        try:
            consults = consultation_history_repo.list_by_farmer(db, farmer_id=farmer.id, limit=1)
            if consults:
                latest = consults[0]
                import json
                try:
                    snapshot = json.loads(latest.context_snapshot_json)
                    details = snapshot.get("consultation_details", {})
                    score = details.get("farm_health_score", 100)
                    actions = details.get("recommended_actions", [])
                except Exception:
                    score = 100
                    actions = []

                is_critical = score <= 50 or any(any(word in act.lower() for word in ["reconsider", "critical", "urgent", "danger", "reconsider"]) for act in actions)
                if is_critical:
                    title = "Critical Agronomist Recommendation"
                    message = f"Virtual Agronomist flagged critical operational guidelines for your active crops. Health Score: {score}/100."
                    if self._create_if_not_exists(db, farmer.id, title, message, "agronomist", "high", "agronomist"):
                        generated_count += 1
        except Exception as e:
            logger.error(f"Agronomist notification scan failed: {e}", exc_info=True)

        return generated_count

    def list_notifications(self, db: Session, farmer_id: int, unread_only: bool = False) -> List[Notification]:
        is_read = False if unread_only else None
        return notification_repo.list_by_farmer(db, farmer_id=farmer_id, is_read=is_read)

    def mark_read(self, db: Session, farmer_id: int, notification_id: int) -> Notification:
        n = notification_repo.get_by_id(db, notification_id)
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        if n.farmer_id != farmer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return notification_repo.mark_as_read(db, n)

    def mark_all_read(self, db: Session, farmer_id: int) -> int:
        return notification_repo.mark_all_read(db, farmer_id)

    def delete_notification(self, db: Session, farmer_id: int, notification_id: int) -> None:
        n = notification_repo.get_by_id(db, notification_id)
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        if n.farmer_id != farmer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        notification_repo.delete(db, n)


notification_service = NotificationService()
