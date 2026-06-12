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


def test_generate_prediction_unauthorized(client):
    response = client.post("/api/v1/yield-predictions/generate", json={"crop_name": "Wheat"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_generate_prediction_no_soil_report(client):
    token = _get_token(client, "nosoil@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/yield-predictions/generate", json={"crop_name": "Wheat"}, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "log a soil test report first" in response.json()["detail"]


@patch("app.services.yield_prediction.ai_service.generate_yield_prediction")
def test_generate_prediction_success(mock_ai, client):
    mock_ai.return_value = {
        "predicted_yield": 950.0,
        "confidence_score": 88,
        "yield_category": "High",
        "prediction_factors": ["Optimal nitrogen level", "Favorable weather"],
        "recommendations": ["Add potash in Week 4", "Maintain irrigation spacing"]
    }

    token = _get_token(client, "hasreport@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Log a soil report first
    soil_resp = client.post(
        "/api/v1/soil/reports",
        headers=headers,
        json={
            "ph": 6.7,
            "nitrogen": 48.0,
            "phosphorus": 36.0,
            "potassium": 220.0,
            "organic_matter": 2.2,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-12"
        }
    )
    assert soil_resp.status_code == status.HTTP_201_CREATED

    # 2. Run yield prediction
    pred_resp = client.post("/api/v1/yield-predictions/generate", json={"crop_name": "Wheat"}, headers=headers)
    assert pred_resp.status_code == status.HTTP_201_CREATED
    data = pred_resp.json()
    assert data["crop_name"] == "Wheat"
    assert data["predicted_yield"] == 950.0
    assert data["confidence_score"] == 88
    assert data["yield_category"] == "High"
    assert len(data["prediction_factors"]) == 2
    assert data["prediction_factors"][0] == "Optimal nitrogen level"


@patch("app.services.yield_prediction.ai_service.generate_yield_prediction")
def test_list_and_get_details(mock_ai, client):
    mock_ai.return_value = {
        "predicted_yield": 720.5,
        "confidence_score": 82,
        "yield_category": "Medium",
        "prediction_factors": ["Moderate pH value"],
        "recommendations": ["No extra fertilizers needed"]
    }

    token_1 = _get_token(client, "user1@example.com")
    token_2 = _get_token(client, "user2@example.com")
    headers_1 = {"Authorization": f"Bearer {token_1}"}
    headers_2 = {"Authorization": f"Bearer {token_2}"}

    # Add soil report for user 1
    client.post(
        "/api/v1/soil/reports",
        headers=headers_1,
        json={
            "ph": 6.2,
            "nitrogen": 32.0,
            "phosphorus": 24.0,
            "potassium": 160.0,
            "organic_matter": 1.5,
            "crop_planned": "Cotton",
            "tested_at": "2026-06-12"
        }
    )

    # Generate prediction for user 1
    gen_resp = client.post("/api/v1/yield-predictions/generate", json={"crop_name": "Cotton"}, headers=headers_1)
    pred_id = gen_resp.json()["id"]

    # 1. Fetch history for user 1
    history_resp = client.get("/api/v1/yield-predictions/", headers=headers_1)
    assert history_resp.status_code == status.HTTP_200_OK
    assert len(history_resp.json()) >= 1

    # 2. Retrieve details for user 1 (Should succeed)
    detail_resp = client.get(f"/api/v1/yield-predictions/{pred_id}", headers=headers_1)
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["crop_name"] == "Cotton"
    assert detail_resp.json()["predicted_yield"] == 720.5

    # 3. Retrieve user 1's prediction details using user 2's token (Should return 403 Forbidden)
    forbidden_resp = client.get(f"/api/v1/yield-predictions/{pred_id}", headers=headers_2)
    assert forbidden_resp.status_code == status.HTTP_403_FORBIDDEN
