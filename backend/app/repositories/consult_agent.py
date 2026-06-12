import json
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.consult_agent import ConsultationHistory


class ConsultationHistoryRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        question: str,
        answer: str,
        context_snapshot: dict
    ) -> ConsultationHistory:
        db_obj = ConsultationHistory(
            farmer_id=farmer_id,
            question=question,
            answer=answer,
            context_snapshot_json=json.dumps(context_snapshot)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, consult_id: int) -> Optional[ConsultationHistory]:
        return db.query(ConsultationHistory).filter(ConsultationHistory.id == consult_id).first()

    def list_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 100, offset: int = 0
    ) -> List[ConsultationHistory]:
        return (
            db.query(ConsultationHistory)
            .filter(ConsultationHistory.farmer_id == farmer_id)
            .order_by(ConsultationHistory.created_at.desc(), ConsultationHistory.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


consultation_history_repo = ConsultationHistoryRepository()
