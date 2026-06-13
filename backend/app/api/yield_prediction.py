from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.yield_prediction import YieldPredictionRequest, YieldPredictionResponse
from app.services.yield_prediction import yield_prediction_service

router = APIRouter()


@router.post("/generate", response_model=YieldPredictionResponse, status_code=status.HTTP_201_CREATED)
def generate_yield_prediction(
    payload: YieldPredictionRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    try:
        result = yield_prediction_service.generate_yield_prediction(
            db=db,
            farmer=current_farmer,
            crop_name=payload.crop_name
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[YieldPredictionResponse])
def get_predictions_history(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    history = yield_prediction_service.list_predictions(
        db=db,
        farmer_id=current_farmer.id,
        limit=limit,
        offset=offset,
        farmer=current_farmer
    )
    return history



@router.get("/{prediction_id}", response_model=YieldPredictionResponse)
def get_single_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    result = yield_prediction_service.get_prediction(
        db=db,
        farmer_id=current_farmer.id,
        pred_id=prediction_id
    )
    return result
