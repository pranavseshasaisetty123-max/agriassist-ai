from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.farm_analytics import FarmAnalyticsSnapshot


class FarmAnalyticsRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        health_score: float,
        risk_score: float,
        projected_profit: float,
        projected_yield: float,
        active_crop_count: int,
        active_alert_count: int,
        snapshot_json: str,
        farm_id: Optional[int] = None
    ) -> FarmAnalyticsSnapshot:
        db_obj = FarmAnalyticsSnapshot(
            farmer_id=farmer_id,
            farm_id=farm_id,
            health_score=health_score,
            risk_score=risk_score,
            projected_profit=projected_profit,
            projected_yield=projected_yield,
            active_crop_count=active_crop_count,
            active_alert_count=active_alert_count,
            snapshot_json=snapshot_json
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 50, farm_id: Optional[int] = None
    ) -> List[FarmAnalyticsSnapshot]:
        query = db.query(FarmAnalyticsSnapshot).filter(FarmAnalyticsSnapshot.farmer_id == farmer_id)
        if farm_id is not None:
            query = query.filter(FarmAnalyticsSnapshot.farm_id == farm_id)
        return (
            query
            .order_by(FarmAnalyticsSnapshot.created_at.asc())
            .limit(limit)
            .all()
        )

    def get_latest(self, db: Session, farmer_id: int, farm_id: Optional[int] = None) -> Optional[FarmAnalyticsSnapshot]:
        query = db.query(FarmAnalyticsSnapshot).filter(FarmAnalyticsSnapshot.farmer_id == farmer_id)
        if farm_id is not None:
            query = query.filter(FarmAnalyticsSnapshot.farm_id == farm_id)
        return (
            query
            .order_by(FarmAnalyticsSnapshot.created_at.desc())
            .first()
        )


    def delete(self, db: Session, snapshot: FarmAnalyticsSnapshot) -> None:
        db.delete(snapshot)
        db.commit()


farm_analytics_repo = FarmAnalyticsRepository()
