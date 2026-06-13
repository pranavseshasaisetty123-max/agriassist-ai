from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.soil import SoilReport, SoilRecommendation
from app.models.farmer import Farmer
from app.repositories.soil import soil_report_repo, soil_rec_repo
from app.schemas.soil import SoilReportCreate
from app.services.ai import ai_service
from app.services.farm import farm_service


class SoilReportService:
    def create_report(self, db: Session, farmer_id: int, report_in: SoilReportCreate, farmer: Optional[Farmer] = None) -> SoilReport:
        """Log a new soil report card."""
        if not farmer:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        return soil_report_repo.create(db, farmer_id=farmer_id, obj_in=report_in, farm_id=active_farm.id)

    def _verify_report_ownership(self, db: Session, report_id: int, farmer_id: int) -> SoilReport:
        """Assert report exists and belongs to the active farmer."""
        report = soil_report_repo.get_by_id(db, report_id=report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Soil report entry not found."
            )
        if report.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this soil report entry."
            )
        return report

    def get_report(self, db: Session, farmer_id: int, report_id: int) -> SoilReport:
        """Retrieve a specific report after verifying owner permissions."""
        return self._verify_report_ownership(db, report_id=report_id, farmer_id=farmer_id)

    def list_farmer_reports(
        self, db: Session, farmer_id: int, limit: int = 50, offset: int = 0, farmer: Optional[Farmer] = None
    ) -> List[SoilReport]:
        """Fetch all historical reports logged by the farmer."""
        if not farmer:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        active_farm = farm_service.get_or_create_active_farm(db, farmer)
        return soil_report_repo.list_by_farmer(db, farmer_id=farmer_id, limit=limit, offset=offset, farm_id=active_farm.id)

    def delete_report(self, db: Session, farmer_id: int, report_id: int) -> None:
        """Delete a report entry after verifying owner permissions."""
        report = self._verify_report_ownership(db, report_id=report_id, farmer_id=farmer_id)
        soil_report_repo.delete(db, db_obj=report)


soil_report_service = SoilReportService()



class SoilRecommendationService:
    def generate_recommendation(self, db: Session, farmer_id: int, report_id: int) -> SoilRecommendation:
        """
        Verify report ownership, request structured recommendations from Gemini AI,
        and persist them to the database.
        """
        # 1. Verify report ownership
        report = soil_report_service._verify_report_ownership(db, report_id=report_id, farmer_id=farmer_id)
        
        # 2. Check if recommendation already exists to avoid redundant calls
        existing = soil_rec_repo.get_by_report_id(db, report_id=report_id)
        if existing:
            return existing
            
        # 3. Retrieve location from farmer profile
        location = report.farmer.location if report.farmer else None
        
        # 4. Generate structured advice via AI service
        try:
            ai_data = ai_service.generate_soil_recommendation(
                ph=report.ph,
                nitrogen=report.nitrogen,
                phosphorus=report.phosphorus,
                potassium=report.potassium,
                organic_matter=report.organic_matter,
                crop_planned=report.crop_planned,
                location=location
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate AI recommendations: {str(e)}"
            )
            
        # 5. Persist to database
        try:
            recommendation = soil_rec_repo.create(
                db=db,
                report_id=report_id,
                nitrogen_rec=ai_data["nitrogen_recommendation"],
                phosphorus_rec=ai_data["phosphorus_recommendation"],
                potassium_rec=ai_data["potassium_recommendation"],
                schedule=ai_data["fertilizer_schedule"],
                raw_ai=ai_data["ai_raw_analysis"]
            )
            return recommendation
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save recommendations: {str(e)}"
            )


soil_rec_service = SoilRecommendationService()
