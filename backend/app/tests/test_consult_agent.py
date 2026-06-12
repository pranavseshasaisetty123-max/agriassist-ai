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
    r1 = client.post("/api/v1/consult-agent/ask", json={"question": "Should I grow tomato?"})
    assert r1.status_code == status.HTTP_401_UNAUTHORIZED

    r2 = client.get("/api/v1/consult-agent/history")
    assert r2.status_code == status.HTTP_401_UNAUTHORIZED

    r3 = client.get("/api/v1/consult-agent/1")
    assert r3.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.services.consult_agent.ai_service.generate_farm_consultation")
def test_ask_no_context_available(mock_ai, client):
    mock_ai.return_value = {
        "farm_health_score": 82,
        "health_summary": "[DEMO] Your farm shows stable health indicators.",
        "key_findings": ["[DEMO] Soil nutrients are moderate."],
        "recommended_actions": ["[DEMO] Mulch crops."],
        "risk_assessment": "[DEMO] Low risk.",
        "answer": "[DEMO] Cultivating tomato is recommended.",
        "confidence_score": 90
    }
    
    # Testing that asking agronomist works even if no soil report, weather, or crop plan exists
    token = _get_token(client, "nocontext@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/consult-agent/ask",
        json={"question": "Should I cultivate tomato?"},
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "farm_health_score" in data
    assert "answer" in data
    assert data["farm_health_score"] == 82
    assert "[DEMO]" in data["answer"]


@patch("app.services.consult_agent.weather_intelligence_service.get_weather_data")
@patch("app.services.consult_agent.ai_service.generate_farm_consultation")
def test_consultation_success_and_history(mock_ai, mock_weather, client):
    # 1. Setup mock responses
    mock_weather.return_value = (
        28.61, 77.20, 28.0, "Sunny", [
            {"date": "2026-06-12", "condition": "Sunny", "temp_min": 25.0, "temp_max": 35.0}
        ]
    )
    mock_ai.return_value = {
        "farm_health_score": 90,
        "health_summary": "Excellent soil parameters and upcoming weather forecast suggest positive yields.",
        "key_findings": ["Soil nitrogen level is optimal", "No severe pest risks currently active"],
        "recommended_actions": ["Maintain daily irrigation", "Apply organic mulch"],
        "risk_assessment": "Low environmental risk forecast",
        "answer": "Yes, cultivation of tomato is highly recommended this season. Profitability index is high.",
        "confidence_score": 95
    }

    token_1 = _get_token(client, "consultsuccess@example.com")
    token_2 = _get_token(client, "otherfarmer@example.com")
    headers_1 = {"Authorization": f"Bearer {token_1}"}
    headers_2 = {"Authorization": f"Bearer {token_2}"}

    # 2. Add soil report for user 1
    client.post(
        "/api/v1/soil/reports",
        headers=headers_1,
        json={
            "ph": 6.5, "nitrogen": 48.0, "phosphorus": 32.0, "potassium": 190.0,
            "organic_matter": 2.1, "crop_planned": "Tomato", "tested_at": "2026-06-12"
        }
    )

    # 3. Post a query
    resp = client.post(
        "/api/v1/consult-agent/ask",
        json={"question": "Should I grow tomato this season?"},
        headers=headers_1
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["farm_health_score"] == 90
    assert data["answer"] == "Yes, cultivation of tomato is highly recommended this season. Profitability index is high."
    assert len(data["recommended_actions"]) == 2

    # 4. Get history for user 1
    history_resp = client.get("/api/v1/consult-agent/history", headers=headers_1)
    assert history_resp.status_code == status.HTTP_200_OK
    history_list = history_resp.json()
    assert len(history_list) == 1
    consult_id = history_list[0]["id"]
    assert history_list[0]["farm_health_score"] == 90
    assert history_list[0]["question"] == "Should I grow tomato this season?"

    # 5. Retrieve details for user 1 (Should succeed)
    detail_resp = client.get(f"/api/v1/consult-agent/{consult_id}", headers=headers_1)
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["answer"] == data["answer"]

    # 6. Retrieve details from user 2's token (Should return 403 Forbidden)
    forbidden_resp = client.get(f"/api/v1/consult-agent/{consult_id}", headers=headers_2)
    assert forbidden_resp.status_code == status.HTTP_403_FORBIDDEN
