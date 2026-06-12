from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.risk_intelligence import RiskAlertResponse, RiskAssessmentResponse
from app.services.risk_intelligence import risk_intelligence_service

router = APIRouter()


@router.post("/generate", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
def generate_risk_alerts(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        assessment = risk_intelligence_service.generate_risk_intelligence(db, current_farmer)
        return assessment
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/warnings", response_model=RiskAssessmentResponse)
def get_warnings(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return risk_intelligence_service.get_latest_warnings(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/history", response_model=List[RiskAlertResponse])
def get_history(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return risk_intelligence_service.get_history(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
