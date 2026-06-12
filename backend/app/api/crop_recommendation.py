from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.schemas.crop_recommendation import CropRecommendationResponse
from app.services.crop_recommendation import crop_recommendation_service

router = APIRouter()


@router.post("/generate", response_model=List[CropRecommendationResponse], status_code=status.HTTP_201_CREATED)
def generate_recommendations(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Generate and save Top 5 crop recommendations based on soil metrics and weather forecast."""
    return crop_recommendation_service.generate_recommendations(db, current_farmer)


@router.get("", response_model=List[CropRecommendationResponse])
def list_recommendations(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve historical crop recommendations for the current farmer."""
    return crop_recommendation_service.list_recommendations(
        db, farmer_id=current_farmer.id, limit=limit, offset=offset
    )


@router.get("/{rec_id}", response_model=CropRecommendationResponse)
def get_recommendation(
    rec_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve details of a specific crop recommendation."""
    return crop_recommendation_service.get_recommendation(
        db, farmer_id=current_farmer.id, rec_id=rec_id
    )
