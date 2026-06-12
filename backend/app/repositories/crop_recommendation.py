import json
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.crop_recommendation import CropRecommendation
from app.schemas.crop_recommendation import CropRecommendationCreate


class CropRecommendationRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        obj_in: CropRecommendationCreate,
        created_at: datetime
    ) -> CropRecommendation:
        """Create a new crop recommendation entry."""
        db_obj = CropRecommendation(
            farmer_id=farmer_id,
            crop_name=obj_in.crop_name,
            suitability_score=obj_in.suitability_score,
            season=obj_in.season,
            recommendation_reason=obj_in.recommendation_reason,
            risk_factors=json.dumps(obj_in.risk_factors),
            farming_tips=json.dumps(obj_in.farming_tips),
            created_at=created_at
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, rec_id: int) -> Optional[CropRecommendation]:
        """Retrieve a crop recommendation by ID."""
        return db.query(CropRecommendation).filter(CropRecommendation.id == rec_id).first()

    def list_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 100, offset: int = 0
    ) -> List[CropRecommendation]:
        """List all crop recommendations for a farmer sorted by created_at desc."""
        return (
            db.query(CropRecommendation)
            .filter(CropRecommendation.farmer_id == farmer_id)
            .order_by(CropRecommendation.created_at.desc(), CropRecommendation.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


crop_recommendation_repo = CropRecommendationRepository()
