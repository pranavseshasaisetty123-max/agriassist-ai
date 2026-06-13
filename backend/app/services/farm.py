import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.farmer import Farmer
from app.models.farm import Farm
from app.repositories.farm import farm_repo

logger = logging.getLogger("agriassist.farm_service")


class FarmService:
    def get_or_create_active_farm(self, db: Session, farmer: Farmer) -> Farm:
        """
        Retrieves the currently active farm for the farmer, fallback to the first farm,
        or self-heals by auto-creating a Default Farm if no farms exist yet.
        """
        if farmer.active_farm_id:
            active = farm_repo.get(db, farmer.active_farm_id)
            if active and active.farmer_id == farmer.id:
                return active

        # Try to fallback to the first farm registered
        farms = farm_repo.list_by_farmer(db, farmer.id)
        if farms:
            farmer.active_farm_id = farms[0].id
            db.commit()
            db.refresh(farmer)
            return farms[0]

        # No farms exist - self-heal by creating a Primary Farm
        default_farm = Farm(
            farmer_id=farmer.id,
            name="Primary Farm",
            location=farmer.location or "Delhi, India",
            total_area_acres=10.0,
            soil_type="Loam",
            latitude=28.6139,
            longitude=77.2090
        )
        db.add(default_farm)
        db.commit()
        db.refresh(default_farm)

        farmer.active_farm_id = default_farm.id
        db.commit()
        db.refresh(farmer)
        return default_farm

    def set_active_farm(self, db: Session, farmer: Farmer, farm_id: int) -> Farm:
        """Activate a specific farm owned by the farmer."""
        farm = farm_repo.get(db, farm_id)
        if not farm or farm.farmer_id != farmer.id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farm not found or access denied"
            )
        
        farmer.active_farm_id = farm.id
        db.commit()
        db.refresh(farmer)
        return farm

    def get_farmer_portfolio(self, db: Session, farmer_id: int) -> Dict[str, Any]:
        """Aggregate portfolio statistics across all farms owned by the farmer."""
        farms = farm_repo.list_by_farmer(db, farmer_id)
        total_farms = len(farms)
        total_area = sum(f.total_area_acres for f in farms)

        portfolio_profit = 0.0
        portfolio_yield = 0.0
        total_risk_score = 0.0
        active_crop_plans = 0

        from app.models.farm_planner import FarmPlan
        from app.models.yield_prediction import YieldPrediction
        from app.models.market_intelligence import ProfitabilityAnalysis
        from app.services.farm_analytics import farm_analytics_service

        for farm in farms:
            # 1. Count active planner sowing plans
            plans = db.query(FarmPlan).filter(
                FarmPlan.farm_id == farm.id, FarmPlan.status == "active"
            ).all()
            active_crop_plans += len(plans)
            active_crops = [p.crop_name for p in plans]

            # 2. Aggregating projected profit
            farm_profit = 0.0
            if active_crops:
                for crop in active_crops:
                    analysis = db.query(ProfitabilityAnalysis).filter(
                        ProfitabilityAnalysis.farmer_id == farm.farmer_id,
                        ProfitabilityAnalysis.crop_name == crop
                    ).order_by(ProfitabilityAnalysis.created_at.desc()).first()
                    if analysis:
                        farm_profit += analysis.estimated_profit
            
            # Fallback if no crop plans match
            if farm_profit == 0.0:
                distinct_analyses = db.query(
                    ProfitabilityAnalysis.crop_name, func.max(ProfitabilityAnalysis.id).label("max_id")
                ).filter(
                    ProfitabilityAnalysis.farmer_id == farm.farmer_id
                ).group_by(ProfitabilityAnalysis.crop_name).subquery()
                
                profit_records = db.query(ProfitabilityAnalysis).join(
                    distinct_analyses, ProfitabilityAnalysis.id == distinct_analyses.c.max_id
                ).all()
                farm_profit = sum(p.estimated_profit for p in profit_records)
            portfolio_profit += farm_profit

            # 3. Aggregating projected yield
            farm_yield = 0.0
            if active_crops:
                for crop in active_crops:
                    pred = db.query(YieldPrediction).filter(
                        YieldPrediction.farm_id == farm.id,
                        YieldPrediction.crop_name == crop
                    ).order_by(YieldPrediction.created_at.desc()).first()
                    if pred:
                        farm_yield += pred.predicted_yield
            
            # Fallback if no crop plans match
            if farm_yield == 0.0:
                distinct_predictions = db.query(
                    YieldPrediction.crop_name, func.max(YieldPrediction.id).label("max_id")
                ).filter(
                    YieldPrediction.farm_id == farm.id
                ).group_by(YieldPrediction.crop_name).subquery()
                
                yield_records = db.query(YieldPrediction).join(
                    distinct_predictions, YieldPrediction.id == distinct_predictions.c.max_id
                ).all()
                farm_yield = sum(y.predicted_yield for y in yield_records)
            portfolio_yield += farm_yield

            # 4. Aggregating farm risk warning scores
            try:
                kpis = farm_analytics_service.calculate_realtime_kpis(db, farmer_id, farm_id=farm.id)
                total_risk_score += kpis["risk_score"]
            except Exception:
                total_risk_score += 25.0  # fallback base risk

        portfolio_risk = total_risk_score / max(total_farms, 1)

        return {
            "total_farms": total_farms,
            "total_area": total_area,
            "portfolio_profit": portfolio_profit,
            "portfolio_yield": portfolio_yield,
            "portfolio_risk": portfolio_risk,
            "active_crop_plans": active_crop_plans
        }


farm_service = FarmService()
