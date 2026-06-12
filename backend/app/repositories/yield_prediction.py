import json
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.yield_prediction import YieldPrediction


class YieldPredictionRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        crop_name: str,
        predicted_yield: float,
        confidence_score: int,
        yield_category: str,
        prediction_factors: List[str],
        recommendations: List[str],
        created_at: Optional[datetime] = None
    ) -> YieldPrediction:
        db_obj = YieldPrediction(
            farmer_id=farmer_id,
            crop_name=crop_name,
            predicted_yield=predicted_yield,
            confidence_score=confidence_score,
            yield_category=yield_category,
            prediction_factors=json.dumps(prediction_factors),
            recommendations=json.dumps(recommendations)
        )
        if created_at:
            db_obj.created_at = created_at
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, pred_id: int) -> Optional[YieldPrediction]:
        return db.query(YieldPrediction).filter(YieldPrediction.id == pred_id).first()

    def list_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 100, offset: int = 0
    ) -> List[YieldPrediction]:
        return (
            db.query(YieldPrediction)
            .filter(YieldPrediction.farmer_id == farmer_id)
            .order_by(YieldPrediction.created_at.desc(), YieldPrediction.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


yield_prediction_repo = YieldPredictionRepository()
