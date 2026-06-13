from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import json

from app.api.deps import get_current_farmer, get_db
from app.models.farmer import Farmer
from app.models.consult_agent import ConsultationHistory
from app.models.yield_prediction import YieldPrediction
from app.models.market_intelligence import ProfitabilityAnalysis
from app.schemas.farm_analytics import (
    KPIMetricsResponse,
    AnalyticsSnapshotResponse,
    TrendSnapshotResponse,
    DashboardAnalyticsResponse,
    ReportPayloadResponse
)
from app.services.farm_analytics import farm_analytics_service
from app.repositories.risk_intelligence import risk_alert_repo

router = APIRouter()


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_analytics_service.get_dashboard_data(db, current_farmer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/trends", response_model=List[TrendSnapshotResponse])
def get_trends(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_analytics_service.list_trends(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/kpis", response_model=KPIMetricsResponse)
def get_kpis(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_analytics_service.calculate_realtime_kpis(db, current_farmer.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/snapshot", response_model=AnalyticsSnapshotResponse)
def create_snapshot(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        return farm_analytics_service.generate_snapshot(db, current_farmer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/report")
def get_report(
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
):
    try:
        if format == "pdf":
            pdf_buf = farm_analytics_service.generate_pdf_report(db, current_farmer)
            return StreamingResponse(
                pdf_buf,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=farm_report.pdf"}
            )
        elif format == "json":
            kpis = farm_analytics_service.calculate_realtime_kpis(db, current_farmer.id)
            
            alerts = risk_alert_repo.get_latest_run_alerts(db, current_farmer.id)
            active_risks = [
                {
                    "alert_title": alert.alert_title,
                    "category": alert.category,
                    "severity": alert.severity,
                    "probability": alert.probability
                }
                for alert in alerts
            ]
            
            latest_consult = db.query(ConsultationHistory).filter(
                ConsultationHistory.farmer_id == current_farmer.id
            ).order_by(ConsultationHistory.created_at.desc()).first()
            rec_list = []
            if latest_consult:
                try:
                    snap = json.loads(latest_consult.context_snapshot_json)
                    rec_list = snap.get("consultation_details", {}).get("recommended_actions", [])
                except Exception:
                    pass
            if not rec_list:
                rec_list = [
                    "Maintain scheduled watering intervals adapting to forecasts.",
                    "Apply customized NPK top-dressings matching plan cycles."
                ]
                
            from app.models.farm_planner import FarmPlan
            plans = db.query(FarmPlan).filter(
                FarmPlan.farmer_id == current_farmer.id, FarmPlan.status == "active"
            ).all()
            active_crops = [p.crop_name for p in plans]
            
            yield_forecasts = []
            if active_crops:
                for crop in active_crops:
                    pred = db.query(YieldPrediction).filter(
                        YieldPrediction.farmer_id == current_farmer.id,
                        YieldPrediction.crop_name == crop
                    ).order_by(YieldPrediction.created_at.desc()).first()
                    if pred:
                        yield_forecasts.append({
                            "crop_name": pred.crop_name,
                            "predicted_yield": pred.predicted_yield,
                            "confidence_score": pred.confidence_score,
                            "yield_category": pred.yield_category,
                            "created_at": pred.created_at
                        })
            if not yield_forecasts:
                distinct_predictions = db.query(
                    YieldPrediction.crop_name, func.max(YieldPrediction.id).label("max_id")
                ).filter(
                    YieldPrediction.farmer_id == current_farmer.id
                ).group_by(YieldPrediction.crop_name).subquery()
                yield_records = db.query(YieldPrediction).join(
                    distinct_predictions, YieldPrediction.id == distinct_predictions.c.max_id
                ).all()
                yield_forecasts = [
                    {
                        "crop_name": y.crop_name,
                        "predicted_yield": y.predicted_yield,
                        "confidence_score": y.confidence_score,
                        "yield_category": y.yield_category,
                        "created_at": y.created_at
                    }
                    for y in yield_records
                ]
                
            profit_forecasts = []
            if active_crops:
                for crop in active_crops:
                    analysis = db.query(ProfitabilityAnalysis).filter(
                        ProfitabilityAnalysis.farmer_id == current_farmer.id,
                        ProfitabilityAnalysis.crop_name == crop
                    ).order_by(ProfitabilityAnalysis.created_at.desc()).first()
                    if analysis:
                        profit_forecasts.append({
                            "crop_name": analysis.crop_name,
                            "estimated_revenue": analysis.estimated_revenue,
                            "estimated_profit": analysis.estimated_profit,
                            "profit_margin": analysis.profit_margin,
                            "created_at": analysis.created_at
                        })
            if not profit_forecasts:
                distinct_analyses = db.query(
                    ProfitabilityAnalysis.crop_name, func.max(ProfitabilityAnalysis.id).label("max_id")
                ).filter(
                    ProfitabilityAnalysis.farmer_id == current_farmer.id
                ).group_by(ProfitabilityAnalysis.crop_name).subquery()
                profit_records = db.query(ProfitabilityAnalysis).join(
                    distinct_analyses, ProfitabilityAnalysis.id == distinct_analyses.c.max_id
                ).all()
                profit_forecasts = [
                    {
                        "crop_name": p.crop_name,
                        "estimated_revenue": p.estimated_revenue,
                        "estimated_profit": p.estimated_profit,
                        "profit_margin": p.profit_margin,
                        "created_at": p.created_at
                    }
                    for p in profit_records
                ]
                
            return ReportPayloadResponse(
                kpis=KPIMetricsResponse(**kpis),
                active_risks=active_risks,
                recommendations=rec_list,
                yield_forecasts=yield_forecasts,
                profit_forecasts=profit_forecasts
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Supported options are 'pdf' and 'json'."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
