import pytest
from fastapi import status
from unittest.mock import patch


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Ramesh",
            "last_name": "Kumar",
            "location": "Haryana, India"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_endpoints_unauthorized(client):
    r1 = client.post("/api/v1/risk-intelligence/generate")
    assert r1.status_code == status.HTTP_401_UNAUTHORIZED

    r2 = client.get("/api/v1/risk-intelligence/warnings")
    assert r2.status_code == status.HTTP_401_UNAUTHORIZED

    r3 = client.get("/api/v1/risk-intelligence/history")
    assert r3.status_code == status.HTTP_401_UNAUTHORIZED


def test_generate_no_crop_plan(client):
    token = _get_token(client, "noriskplan@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/risk-intelligence/generate", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Please create a crop plan before generating risk intelligence." in response.json()["detail"]


@patch("app.services.risk_intelligence.weather_intelligence_service.get_weather_data")
@patch("app.services.risk_intelligence.ai_service.generate_risk_analysis")
@patch("app.services.farm_planner.ai_service.generate_farm_plan")
def test_generate_and_fetch_risk_intelligence_success(mock_farm_plan, mock_ai_risk, mock_weather, client):
    # Mock AI farm plan response
    mock_farm_plan.return_value = {
        "expected_harvest_days": 90,
        "tasks": [
            {
                "title": "Soil tilling",
                "description": "Till soil deeply",
                "planned_date_offset_days": 0,
                "priority": "medium",
                "category": "land_preparation"
            }
        ]
    }

    # Mock weather service response: (lat, lon, temp, condition, forecast)
    mock_weather.return_value = (
        28.61, 77.20, 28.0, "Sunny", [
            {"date": "2026-06-12", "condition": "Sunny", "temp_min": 25.0, "temp_max": 35.0}
        ]
    )

    # Mock AI risk warnings response
    mock_ai_risk.return_value = {
        "alerts": [
            {
                "crop_name": "Tomato",
                "title": "Tomato Early Blight",
                "category": "disease",
                "risk_level": "High",
                "probability": 75,
                "description": "High humidity conditions favor blight infection.",
                "prevention_steps": ["Ensure proper spacing", "Apply copper fungicide"],
                "monitoring_advice": ["Inspect lower leaves for dark concentric spots"]
            },
            {
                "crop_name": "Tomato",
                "title": "Whitefly Infestation",
                "category": "pest",
                "risk_level": "medium",
                "probability": 45,
                "description": "Rising temperatures increase whitefly population.",
                "prevention_steps": ["Use yellow sticky traps", "Introduce ladybugs"],
                "monitoring_advice": ["Check leaf undersides daily"]
            }
        ]
    }

    token = _get_token(client, "risksuccess@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a soil report first
    soil_resp = client.post(
        "/api/v1/soil/reports",
        headers=headers,
        json={
            "ph": 6.5,
            "nitrogen": 50.0,
            "phosphorus": 40.0,
            "potassium": 200.0,
            "organic_matter": 2.0,
            "crop_planned": "Tomato",
            "tested_at": "2026-06-12"
        }
    )
    assert soil_resp.status_code == status.HTTP_201_CREATED

    # 2. Create an active crop plan
    plan_resp = client.post(
        "/api/v1/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.5,
            "planned_start_date": "2026-06-12"
        },
        headers=headers
    )
    assert plan_resp.status_code == status.HTTP_201_CREATED

    # 3. Generate risk warnings
    risk_gen_resp = client.post("/api/v1/risk-intelligence/generate", headers=headers)
    assert risk_gen_resp.status_code == status.HTTP_201_CREATED
    
    data = risk_gen_resp.json()
    assert data["risk_level"] in ["Low", "Medium", "High", "Critical"]
    assert "overall_risk_score" in data
    assert len(data["alerts"]) == 2
    
    # Verify alerts format
    alert = data["alerts"][0]
    assert alert["crop_name"] == "Tomato"
    assert alert["alert_title"] in ["Tomato Early Blight", "Whitefly Infestation"]
    assert alert["category"] in ["disease", "pest"]
    assert isinstance(alert["prevention_steps"], list)
    assert len(alert["prevention_steps"]) > 0

    # 4. Get latest warnings
    warnings_resp = client.get("/api/v1/risk-intelligence/warnings", headers=headers)
    assert warnings_resp.status_code == status.HTTP_200_OK
    assert warnings_resp.json()["overall_risk_score"] == data["overall_risk_score"]
    assert len(warnings_resp.json()["alerts"]) == 2

    # 5. Get history
    history_resp = client.get("/api/v1/risk-intelligence/history", headers=headers)
    assert history_resp.status_code == status.HTTP_200_OK
    assert len(history_resp.json()) == 2
