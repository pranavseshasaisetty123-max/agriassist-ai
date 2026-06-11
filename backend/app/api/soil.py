from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.schemas.soil import SoilReportCreate, SoilReportResponse, SoilRecommendationResponse
from app.services.soil import soil_report_service, soil_rec_service

router = APIRouter()


@router.post("/reports", response_model=SoilReportResponse, status_code=status.HTTP_201_CREATED)
def log_report(
    *,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    report_in: SoilReportCreate
):
    """Log a new soil test report."""
    return soil_report_service.create_report(
        db, farmer_id=current_farmer.id, report_in=report_in
    )


@router.get("/reports", response_model=List[SoilReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve all historical soil reports logged by the current farmer."""
    return soil_report_service.list_farmer_reports(
        db, farmer_id=current_farmer.id, limit=limit, offset=offset
    )


@router.get("/reports/{report_id}", response_model=SoilReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Fetch details for a specific soil test report."""
    return soil_report_service.get_report(
        db, farmer_id=current_farmer.id, report_id=report_id
    )


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Delete a soil test report record."""
    soil_report_service.delete_report(
        db, farmer_id=current_farmer.id, report_id=report_id
    )


@router.post("/reports/{report_id}/analyze", response_model=SoilRecommendationResponse)
def analyze_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Invoke Gemini AI to generate structured fertilizer and soil health recommendations."""
    return soil_rec_service.generate_recommendation(
        db, farmer_id=current_farmer.id, report_id=report_id
    )
