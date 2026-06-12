from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
from app.models.market_intelligence import MarketPrice, ProfitabilityAnalysis


class MarketPriceRepository:
    def create(self, db: Session, crop_name: str, market_name: str, state: str, price_per_kg: float, recorded_date: date) -> MarketPrice:
        db_obj = MarketPrice(
            crop_name=crop_name,
            market_name=market_name,
            state=state,
            price_per_kg=price_per_kg,
            recorded_date=recorded_date
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def bulk_create(self, db: Session, price_items: List[dict]) -> List[MarketPrice]:
        db_objs = [
            MarketPrice(
                crop_name=item["crop_name"],
                market_name=item["market_name"],
                state=item["state"],
                price_per_kg=item["price_per_kg"],
                recorded_date=item["recorded_date"]
            )
            for item in price_items
        ]
        db.add_all(db_objs)
        db.commit()
        return db_objs

    def delete_by_crop_and_date(self, db: Session, crop_name: str, recorded_date: date) -> None:
        db.query(MarketPrice).filter(
            func.lower(MarketPrice.crop_name) == crop_name.lower(),
            MarketPrice.recorded_date == recorded_date
        ).delete()
        db.commit()

    def get_latest_date_for_crop(self, db: Session, crop_name: str) -> Optional[date]:
        result = db.query(func.max(MarketPrice.recorded_date)).filter(
            func.lower(MarketPrice.crop_name) == crop_name.lower()
        ).scalar()
        return result

    def get_prices_by_crop_and_date(self, db: Session, crop_name: str, recorded_date: date) -> List[MarketPrice]:
        return db.query(MarketPrice).filter(
            func.lower(MarketPrice.crop_name) == crop_name.lower(),
            MarketPrice.recorded_date == recorded_date
        ).all()

    def get_trends_by_crop(self, db: Session, crop_name: str, days: int = 30) -> List[dict]:
        start_date = date.today() - timedelta(days=days)
        results = (
            db.query(
                MarketPrice.recorded_date,
                func.avg(MarketPrice.price_per_kg).label("price_per_kg")
            )
            .filter(
                func.lower(MarketPrice.crop_name) == crop_name.lower(),
                MarketPrice.recorded_date >= start_date
            )
            .group_by(MarketPrice.recorded_date)
            .order_by(MarketPrice.recorded_date.asc())
            .all()
        )
        return [{"recorded_date": r[0], "price_per_kg": round(float(r[1]), 2)} for r in results]


class ProfitabilityAnalysisRepository:
    def create(
        self,
        db: Session,
        farmer_id: int,
        crop_name: str,
        expected_yield: float,
        cultivation_cost: float,
        market_price_per_kg: float,
        estimated_revenue: float,
        estimated_profit: float,
        profit_margin: float
    ) -> ProfitabilityAnalysis:
        db_obj = ProfitabilityAnalysis(
            farmer_id=farmer_id,
            crop_name=crop_name,
            expected_yield=expected_yield,
            cultivation_cost=cultivation_cost,
            market_price_per_kg=market_price_per_kg,
            estimated_revenue=estimated_revenue,
            estimated_profit=estimated_profit,
            profit_margin=profit_margin
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, analysis_id: int) -> Optional[ProfitabilityAnalysis]:
        return db.query(ProfitabilityAnalysis).filter(ProfitabilityAnalysis.id == analysis_id).first()

    def list_by_farmer(self, db: Session, farmer_id: int, limit: int = 100, offset: int = 0) -> List[ProfitabilityAnalysis]:
        return (
            db.query(ProfitabilityAnalysis)
            .filter(ProfitabilityAnalysis.farmer_id == farmer_id)
            .order_by(ProfitabilityAnalysis.created_at.desc(), ProfitabilityAnalysis.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


market_price_repo = MarketPriceRepository()
profitability_analysis_repo = ProfitabilityAnalysisRepository()
