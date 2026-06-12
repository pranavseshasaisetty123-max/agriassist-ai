import json
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.risk_alert import RiskAlert


class RiskAlertRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        crop_name: str,
        alert_title: str,
        category: str,
        severity: str,
        probability: int,
        description: str,
        prevention_steps: List[str],
        monitoring_advice: List[str],
    ) -> RiskAlert:
        db_obj = RiskAlert(
            farmer_id=farmer_id,
            crop_name=crop_name,
            alert_title=alert_title,
            category=category,
            severity=severity,
            probability=probability,
            description=description,
            prevention_steps=json.dumps(prevention_steps),
            monitoring_advice=json.dumps(monitoring_advice),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_by_farmer(self, db: Session, farmer_id: int) -> List[RiskAlert]:
        return (
            db.query(RiskAlert)
            .filter(RiskAlert.farmer_id == farmer_id)
            .order_by(RiskAlert.created_at.desc(), RiskAlert.id.desc())
            .all()
        )

    def get_latest_run_alerts(self, db: Session, farmer_id: int) -> List[RiskAlert]:
        # Retrieve the latest alert created by this farmer
        latest_alert = (
            db.query(RiskAlert)
            .filter(RiskAlert.farmer_id == farmer_id)
            .order_by(RiskAlert.created_at.desc())
            .first()
        )
        if not latest_alert:
            return []
        
        # Get all alerts sharing the exact same created_at timestamp
        return (
            db.query(RiskAlert)
            .filter(
                RiskAlert.farmer_id == farmer_id,
                RiskAlert.created_at == latest_alert.created_at
            )
            .all()
        )


risk_alert_repo = RiskAlertRepository()
