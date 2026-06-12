from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.consult_agent import ConsultationAskRequest, ConsultationResponse, ConsultationHistoryResponse
from app.services.consult_agent import consult_agent_service

router = APIRouter()


@router.post("/ask", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
def ask_consultant(
    request: ConsultationAskRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return consult_agent_service.ask_consultant(db, current_farmer, request.question)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/history", response_model=List[ConsultationHistoryResponse])
def get_history(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return consult_agent_service.get_history(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{consultation_id}", response_model=ConsultationHistoryResponse)
def get_consultation_detail(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return consult_agent_service.get_detail(db, current_farmer, consultation_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
