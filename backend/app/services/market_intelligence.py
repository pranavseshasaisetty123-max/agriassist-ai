import logging
import math
import random
import httpx
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.market_intelligence import market_price_repo, profitability_analysis_repo
from app.models.market_intelligence import MarketPrice, ProfitabilityAnalysis

logger = logging.getLogger("agriassist.market_intelligence_service")

# Base crop price references in INR/kg
CROP_BASE_PRICES = {
    "wheat": 24.50,
    "paddy": 22.00,
    "rice": 48.00,
    "mustard": 58.00,
    "cotton": 72.00,
    "maize": 21.00,
    "tomato": 28.00,
    "potato": 18.00,
    "onion": 22.00,
    "barley": 20.00,
    "sugarcane": 4.50, # sugarcane price is lower per kg
}

MOCK_MARKETS = {
    "Punjab": ["Khanna Mandi", "Ludhiana Mandi", "Amritsar Mandi"],
    "Haryana": ["Karnal Mandi", "Kurukshetra Mandi", "Ambala Mandi"],
    "Maharashtra": ["Vashi Mandi", "Pune Mandi", "Nagpur Mandi"],
    "Karnataka": ["Bengaluru Mandi", "Kolar Mandi", "Mysuru Mandi"],
    "Gujarat": ["Gondal Mandi", "Rajkot Mandi", "Ahmedabad Mandi"],
    "Uttar Pradesh": ["Sahibabad Mandi", "Lucknow Mandi", "Kanpur Mandi"]
}


class MarketDataProvider(ABC):
    @abstractmethod
    def fetch_market_prices(self, crop_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch market prices for a given crop over a number of days.
        Returns a list of dicts:
        {
            "crop_name": str,
            "market_name": str,
            "state": str,
            "price_per_kg": float,
            "recorded_date": date
        }
        """
        pass


class FallbackMockDataProvider(MarketDataProvider):
    def fetch_market_prices(self, crop_name: str, days: int = 30) -> List[Dict[str, Any]]:
        logger.info(f"[MockProvider] Generating mock prices for crop '{crop_name}' over last {days} days.")
        
        crop_clean = crop_name.lower().strip()
        base_price = CROP_BASE_PRICES.get(crop_clean, 35.00)
        
        results = []
        today = date.today()
        
        # Select 3 states and 1-2 markets per state to generate
        selected_states = ["Punjab", "Haryana", "Maharashtra"] if crop_clean in ["wheat", "paddy", "mustard"] else ["Maharashtra", "Karnataka", "Uttar Pradesh"]
        
        # Use a seed based on crop name to keep trends somewhat consistent per run
        random.seed(hash(crop_clean))
        
        for d_idx in range(days):
            recorded_date = today - timedelta(days=(days - 1 - d_idx))
            
            # Sine wave to simulate market cycles, with small random fluctuations
            cycle_factor = 1.0 + 0.12 * math.sin(d_idx / 4.0) + random.uniform(-0.03, 0.03)
            daily_base = base_price * cycle_factor
            
            for state in selected_states:
                markets = MOCK_MARKETS.get(state, [])
                # Pick 2 markets
                for market in markets[:2]:
                    market_factor = random.uniform(0.95, 1.05)
                    price_per_kg = round(daily_base * market_factor, 2)
                    
                    results.append({
                        "crop_name": crop_name,
                        "market_name": market,
                        "state": state,
                        "price_per_kg": max(1.0, price_per_kg),
                        "recorded_date": recorded_date
                    })
        # Reset seed
        random.seed(None)
        return results


class GovMarketDataProvider(MarketDataProvider):
    def fetch_market_prices(self, crop_name: str, days: int = 30) -> List[Dict[str, Any]]:
        # Check settings
        gov_key = getattr(settings, "GOV_DATA_API_KEY", None)
        if not gov_key:
            logger.warning("No GOV_DATA_API_KEY set. GovMarketDataProvider unavailable.")
            return []
            
        logger.info(f"[GovProvider] Fetching data for crop '{crop_name}' from data.gov.in.")
        try:
            # The government resource ID for Agmarknet bulletin prices
            resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
            url = f"https://api.data.gov.in/resource/{resource_id}"
            
            # Capitalize to match government database conventions
            query_crop = crop_name.strip().capitalize()
            
            params = {
                "api-key": gov_key,
                "format": "json",
                "limit": 100,
                "filters[commodity]": query_crop
            }
            
            response = httpx.get(url, params=params, timeout=12.0)
            if response.status_code != 200:
                logger.error(f"data.gov.in API returned code {response.status_code}")
                return []
                
            data = response.json()
            records = data.get("records", [])
            
            results = []
            for r in records:
                try:
                    modal_price = float(r.get("modal_price", 0))
                    if modal_price <= 0:
                        continue
                    # modal_price is per quintal (100 kg), convert to per kg
                    price_per_kg = round(modal_price / 100.0, 2)
                    
                    # Parse arrival_date (e.g. DD/MM/YYYY)
                    date_str = r.get("arrival_date", "")
                    recorded_date = date.today()
                    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                        try:
                            recorded_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                            
                    results.append({
                        "crop_name": crop_name,
                        "market_name": f"{r.get('market', 'Mandi')} ({r.get('district', 'District')})",
                        "state": r.get("state", "Unknown"),
                        "price_per_kg": price_per_kg,
                        "recorded_date": recorded_date
                    })
                except Exception as ex:
                    logger.warning(f"Error parsing Gov API record row: {ex}")
                    continue
                    
            return results
        except Exception as e:
            logger.error(f"GovMarketDataProvider failed to fetch: {e}")
            return []


class MarketDataService:
    def __init__(self):
        self.mock_provider = FallbackMockDataProvider()
        self.gov_provider = GovMarketDataProvider()

    def _get_active_provider(self) -> MarketDataProvider:
        gov_key = getattr(settings, "GOV_DATA_API_KEY", None)
        if gov_key:
            return self.gov_provider
        return self.mock_provider

    def fetch_and_cache_prices(self, db: Session, crop_name: str) -> None:
        """Fetch records from provider and store in local database caching repository."""
        provider = self._get_active_provider()
        
        # 1. Fetch from live provider
        prices = provider.fetch_market_prices(crop_name, days=30)
        
        # 2. Fall back to mock if live API returns nothing
        if not prices and provider == self.gov_provider:
            logger.info("Live provider returned empty. Falling back to FallbackMockDataProvider.")
            prices = self.mock_provider.fetch_market_prices(crop_name, days=30)
            
        if not prices:
            logger.warning(f"No price data generated or retrieved for crop: {crop_name}")
            return

        # 3. Clean up DB records for this crop for dates we retrieved, to avoid duplicates
        retrieved_dates = {item["recorded_date"] for item in prices}
        for r_date in retrieved_dates:
            market_price_repo.delete_by_crop_and_date(db, crop_name=crop_name, recorded_date=r_date)
            
        # 4. Save to DB
        market_price_repo.bulk_create(db, price_items=prices)
        logger.info(f"Cached {len(prices)} price records for crop '{crop_name}' to local database.")

    def get_market_intelligence(self, db: Session, crop_name: str) -> dict:
        """Retrieve state-averages, top markets, and average price for a crop."""
        crop_clean = crop_name.lower().strip()
        
        # 1. Check cache state
        latest_date = market_price_repo.get_latest_date_for_crop(db, crop_name=crop_clean)
        
        # If cache is missing or older than today, refresh cache
        if not latest_date or latest_date < date.today():
            self.fetch_and_cache_prices(db, crop_name=crop_clean)
            latest_date = market_price_repo.get_latest_date_for_crop(db, crop_name=crop_clean)
            
        if not latest_date:
            raise ValueError(f"No market data could be loaded for crop '{crop_name}'.")

        # 2. Get latest market records
        latest_records = market_price_repo.get_prices_by_crop_and_date(db, crop_name=crop_clean, recorded_date=latest_date)
        
        if not latest_records:
            raise ValueError(f"No pricing records found in DB for crop '{crop_name}' on date {latest_date}")
            
        # 3. Compute stats
        # Convert model instances to list of dicts for parsing
        market_items = []
        for r in latest_records:
            market_items.append({
                "market_name": r.market_name,
                "state": r.state,
                "price_per_kg": r.price_per_kg,
                "recorded_date": r.recorded_date
            })
            
        avg_price = round(sum(m["price_per_kg"] for m in market_items) / len(market_items), 2)
        
        # Top markets (highest price)
        top_markets = sorted(market_items, key=lambda x: x["price_per_kg"], reverse=True)[:5]
        
        # State averages
        state_totals = {}
        state_counts = {}
        for m in market_items:
            s = m["state"]
            state_totals[s] = state_totals.get(s, 0.0) + m["price_per_kg"]
            state_counts[s] = state_counts.get(s, 0) + 1
            
        state_averages = [
            {"state": s, "price_per_kg": round(state_totals[s] / state_counts[s], 2)}
            for s in state_totals
        ]
        
        return {
            "crop_name": crop_name,
            "average_price": avg_price,
            "recorded_date": latest_date,
            "top_markets": top_markets,
            "state_averages": state_averages,
            "markets": market_items
        }

    def get_trends(self, db: Session, crop_name: str, days: int = 30) -> List[dict]:
        """Fetch daily average prices over N days for plotting."""
        crop_clean = crop_name.lower().strip()
        
        # Seed cache if empty
        latest_date = market_price_repo.get_latest_date_for_crop(db, crop_name=crop_clean)
        if not latest_date or latest_date < date.today():
            self.fetch_and_cache_prices(db, crop_name=crop_clean)
            
        trends = market_price_repo.get_trends_by_crop(db, crop_name=crop_clean, days=days)
        return trends


class ProfitabilityAnalysisService:
    def calculate_profitability(
        self,
        db: Session,
        farmer_id: int,
        crop_name: str,
        expected_yield: float,
        cultivation_cost: float,
        custom_price: Optional[float] = None
    ) -> ProfitabilityAnalysis:
        # Determine market price per kg
        price = custom_price
        if price is None:
            try:
                # Fetch recent market price average from our database
                intel = market_data_service.get_market_intelligence(db, crop_name=crop_name)
                price = intel["average_price"]
            except Exception as e:
                logger.warning(f"Could not load market average price for calculator: {e}. Defaulting to 30.0.")
                # Default fallback price rate if database calculation completely fails
                price = 30.0
                
        # Estimate financials
        estimated_revenue = expected_yield * price
        estimated_profit = estimated_revenue - cultivation_cost
        
        # Calculate margin percentage
        profit_margin = 0.0
        if estimated_revenue > 0:
            profit_margin = round((estimated_profit / estimated_revenue) * 100, 2)
            
        # Save analysis history
        record = profitability_analysis_repo.create(
            db=db,
            farmer_id=farmer_id,
            crop_name=crop_name,
            expected_yield=expected_yield,
            cultivation_cost=cultivation_cost,
            market_price_per_kg=price,
            estimated_revenue=round(estimated_revenue, 2),
            estimated_profit=round(estimated_profit, 2),
            profit_margin=profit_margin
        )
        
        return record


market_data_service = MarketDataService()
profitability_analysis_service = ProfitabilityAnalysisService()
