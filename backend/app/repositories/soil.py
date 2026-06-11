from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.soil import SoilReport, SoilRecommendation
from app.schemas.soil import SoilReportCreate


class SoilReportRepository:
    def create(self, db: Session, farmer_id: int, obj_in: SoilReportCreate) -> SoilReport:
        """Create a new soil report entry."""
        db_obj = SoilReport(
            farmer_id=farmer_id,
            ph=obj_in.ph,
            nitrogen=obj_in.nitrogen,
            phosphorus=obj_in.phosphorus,
            potassium=obj_in.potassium,
            organic_matter=obj_in.organic_matter,
            crop_planned=obj_in.crop_planned,
            tested_at=obj_in.tested_at
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, report_id: int) -> Optional[SoilReport]:
        """Retrieve a soil report by ID."""
        return db.query(SoilReport).filter(SoilReport.id == report_id).first()

    def list_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 50, offset: int = 0
    ) -> List[SoilReport]:
        """Retrieve all historical soil reports logged by a farmer."""
        return (
            db.query(SoilReport)
            .filter(SoilReport.farmer_id == farmer_id)
            .order_by(SoilReport.tested_at.desc(), SoilReport.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, db_obj: SoilReport) -> None:
        """Delete a soil report from database."""
        db.delete(db_obj)
        db.commit()


class SoilRecommendationRepository:
    def create(
        self,
        db: Session,
        report_id: int,
        nitrogen_rec: str,
        phosphorus_rec: str,
        potassium_rec: str,
        schedule: str,
        raw_ai: str
    ) -> SoilRecommendation:
        """Persist a new AI recommendation linked to a report."""
        db_obj = SoilRecommendation(
            report_id=report_id,
            nitrogen_recommendation=nitrogen_rec,
            phosphorus_recommendation=phosphorus_rec,
            potassium_recommendation=potassium_rec,
            fertilizer_schedule=schedule,
            ai_raw_analysis=raw_ai
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_report_id(self, db: Session, report_id: int) -> Optional[SoilRecommendation]:
        """Retrieve AI recommendation for a specific soil report."""
        return db.query(SoilRecommendation).filter(SoilRecommendation.report_id == report_id).first()


soil_report_repo = SoilReportRepository()
soil_rec_repo = SoilRecommendationRepository()
