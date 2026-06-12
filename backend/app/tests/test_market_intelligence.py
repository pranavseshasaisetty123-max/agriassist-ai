import pytest
from fastapi import status
from unittest.mock import patch
from datetime import date, timedelta


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Sanjay",
            "last_name": "Kumar",
            "location": "Punjab, India"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_get_prices_unauthorized(client):
    response = client.get("/api/v1/market-intelligence/prices?crop_name=Tomato")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_prices_success(client):
    token = _get_token(client, "test1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/market-intelligence/prices?crop_name=Tomato", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["crop_name"] == "Tomato"
    assert "average_price" in data
    assert len(data["top_markets"]) > 0
    assert len(data["state_averages"]) > 0
    assert len(data["markets"]) > 0


def test_get_trends_success(client):
    token = _get_token(client, "test2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/market-intelligence/trends?crop_name=Wheat&days=30", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "recorded_date" in data[0]
    assert "price_per_kg" in data[0]


def test_calculate_profitability_success(client):
    token = _get_token(client, "test3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "crop_name": "Paddy",
        "expected_yield": 1200.0,
        "cultivation_cost": 18000.0,
        "market_price_per_kg": 25.0
    }
    
    response = client.post("/api/v1/market-intelligence/calculate", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["crop_name"] == "Paddy"
    assert data["expected_yield"] == 1200.0
    assert data["cultivation_cost"] == 18000.0
    assert data["market_price_per_kg"] == 25.0
    
    # Expected: Revenue = 1200 * 25 = 30000
    # Expected: Profit = 30000 - 18000 = 12000
    # Expected: Margin = (12000 / 30000) * 100 = 40.0%
    assert data["estimated_revenue"] == 30000.0
    assert data["estimated_profit"] == 12000.0
    assert data["profit_margin"] == 40.0


def test_calculate_profitability_fallback_price(client):
    token = _get_token(client, "test4@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Pre-populate some price cache database entries by searching first
    client.get("/api/v1/market-intelligence/prices?crop_name=Wheat", headers=headers)
    
    payload = {
        "crop_name": "Wheat",
        "expected_yield": 1000.0,
        "cultivation_cost": 15000.0
        # No market_price_per_kg provided -> will pull average from DB cache
    }
    
    response = client.post("/api/v1/market-intelligence/calculate", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["crop_name"] == "Wheat"
    assert data["market_price_per_kg"] > 0
    assert data["estimated_revenue"] == 1000.0 * data["market_price_per_kg"]


def test_get_calculations_history_and_details(client):
    token_1 = _get_token(client, "user-a@example.com")
    token_2 = _get_token(client, "user-b@example.com")
    
    headers_1 = {"Authorization": f"Bearer {token_1}"}
    headers_2 = {"Authorization": f"Bearer {token_2}"}
    
    # 1. User A creates a calculation
    calc_payload = {
        "crop_name": "Mustard",
        "expected_yield": 800.0,
        "cultivation_cost": 12000.0,
        "market_price_per_kg": 60.0
    }
    create_resp = client.post("/api/v1/market-intelligence/calculate", json=calc_payload, headers=headers_1)
    analysis_id = create_resp.json()["id"]
    
    # 2. Get history list for User A (Should have 1 item)
    history_resp = client.get("/api/v1/market-intelligence/history", headers=headers_1)
    assert history_resp.status_code == status.HTTP_200_OK
    assert len(history_resp.json()) >= 1
    
    # 3. Get single detail for User A (Should succeed)
    detail_resp = client.get(f"/api/v1/market-intelligence/analysis/{analysis_id}", headers=headers_1)
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["crop_name"] == "Mustard"
    
    # 4. Fetch detail using User B token (Should return 403 Forbidden)
    forbidden_resp = client.get(f"/api/v1/market-intelligence/analysis/{analysis_id}", headers=headers_2)
    assert forbidden_resp.status_code == status.HTTP_403_FORBIDDEN


@patch("app.api.market_intelligence.ai_service.explain_price_trends")
def test_explain_trends_success(mock_explain, client):
    mock_explain.return_value = "The prices show a steady upward pattern matching the harvesting cycles."
    
    token = _get_token(client, "test5@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "crop_name": "Tomato",
        "trends": [
            {"recorded_date": "2026-06-01", "price_per_kg": 25.0},
            {"recorded_date": "2026-06-12", "price_per_kg": 30.0}
        ]
    }
    
    response = client.post("/api/v1/market-intelligence/explain-trends", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["explanation"] == "The prices show a steady upward pattern matching the harvesting cycles."
