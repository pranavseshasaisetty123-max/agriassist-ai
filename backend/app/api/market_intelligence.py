from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.schemas.market_intelligence import (
    CropMarketPricesResponse,
    PriceTrendResponse,
    ProfitCalculationRequest,
    ProfitabilityAnalysisResponse,
    ExplainTrendsRequest,
    ExplainTrendsResponse
)
from app.services.market_intelligence import market_data_service, profitability_analysis_service
from app.repositories.market_intelligence import profitability_analysis_repo
from app.services.ai import ai_service

router = APIRouter()


@router.get("/prices", response_model=CropMarketPricesResponse)
def get_crop_prices(
    crop_name: str,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    try:
        data = market_data_service.get_market_intelligence(db, crop_name=crop_name)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/trends", response_model=List[PriceTrendResponse])
def get_crop_trends(
    crop_name: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    try:
        trends = market_data_service.get_trends(db, crop_name=crop_name, days=days)
        return trends
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/calculate", response_model=ProfitabilityAnalysisResponse, status_code=status.HTTP_201_CREATED)
def calculate_profitability(
    payload: ProfitCalculationRequest,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    try:
        record = profitability_analysis_service.calculate_profitability(
            db=db,
            farmer_id=current_farmer.id,
            crop_name=payload.crop_name,
            expected_yield=payload.expected_yield,
            cultivation_cost=payload.cultivation_cost,
            custom_price=payload.market_price_per_kg
        )
        return record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/history", response_model=List[ProfitabilityAnalysisResponse])
def get_calculations_history(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    history = profitability_analysis_repo.list_by_farmer(
        db=db,
        farmer_id=current_farmer.id,
        limit=limit,
        offset=offset
    )
    return history


@router.get("/analysis/{analysis_id}", response_model=ProfitabilityAnalysisResponse)
def get_single_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    analysis = profitability_analysis_repo.get_by_id(db, analysis_id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found."
        )
    if analysis.farmer_id != current_farmer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not own this analysis record."
        )
    return analysis


@router.post("/explain-trends", response_model=ExplainTrendsResponse)
def explain_trends(
    payload: ExplainTrendsRequest,
    current_farmer: Farmer = Depends(get_current_farmer)
):
    trends_dict = [{"recorded_date": p.recorded_date, "price_per_kg": p.price_per_kg} for p in payload.trends]
    explanation = ai_service.explain_price_trends(crop_name=payload.crop_name, trends=trends_dict)
    return {"explanation": explanation}
