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
        farm_id: Optional[int] = None,
    ) -> RiskAlert:
        db_obj = RiskAlert(
            farmer_id=farmer_id,
            farm_id=farm_id,
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

    def list_by_farmer(self, db: Session, farmer_id: int, farm_id: Optional[int] = None) -> List[RiskAlert]:
        query = db.query(RiskAlert).filter(RiskAlert.farmer_id == farmer_id)
        if farm_id is not None:
            query = query.filter(RiskAlert.farm_id == farm_id)
        return (
            query
            .order_by(RiskAlert.created_at.desc(), RiskAlert.id.desc())
            .all()
        )

    def get_latest_run_alerts(self, db: Session, farmer_id: int, farm_id: Optional[int] = None) -> List[RiskAlert]:
        # Retrieve the latest alert created by this farmer
        query = db.query(RiskAlert).filter(RiskAlert.farmer_id == farmer_id)
        if farm_id is not None:
            query = query.filter(RiskAlert.farm_id == farm_id)
        latest_alert = (
            query
            .order_by(RiskAlert.created_at.desc())
            .first()
        )
        if not latest_alert:
            return []
        
        # Get all alerts sharing the exact same created_at timestamp
        query = db.query(RiskAlert).filter(
            RiskAlert.farmer_id == farmer_id,
            RiskAlert.created_at == latest_alert.created_at
        )
        if farm_id is not None:
            query = query.filter(RiskAlert.farm_id == farm_id)
        return query.all()



risk_alert_repo = RiskAlertRepository()
