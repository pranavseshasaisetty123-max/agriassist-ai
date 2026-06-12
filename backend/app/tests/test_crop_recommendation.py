import pytest
from fastapi import status
from unittest.mock import patch
from datetime import datetime


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Ramesh",
            "last_name": "Patel",
            "location": "Gujarat, India"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_generate_recommendations_unauthorized(client):
    response = client.post("/api/v1/crop-recommendations/generate")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_generate_recommendations_no_soil_report(client):
    token = _get_token(client, "no-soil@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/crop-recommendations/generate", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "log a soil test report first" in response.json()["detail"]


@patch("app.services.crop_recommendation.ai_service.generate_crop_recommendations")
def test_generate_recommendations_success(mock_ai, client):
    mock_ai.return_value = {
        "recommendations": [
            {
                "crop_name": "Wheat",
                "suitability_score": 95,
                "season": "Rabi",
                "recommendation_reason": "High nitrogen levels in soil support grain density.",
                "risk_factors": ["Frost"],
                "farming_tips": ["Sow early"]
            },
            {
                "crop_name": "Mustard",
                "suitability_score": 88,
                "season": "Rabi",
                "recommendation_reason": "Low water requirement.",
                "risk_factors": ["Aphids"],
                "farming_tips": ["Spacing"]
            },
            {
                "crop_name": "Barley",
                "suitability_score": 82,
                "season": "Rabi",
                "recommendation_reason": "Soil pH is optimal.",
                "risk_factors": ["Lodging"],
                "farming_tips": ["Certified seed"]
            },
            {
                "crop_name": "Chickpeas",
                "suitability_score": 80,
                "season": "Rabi",
                "recommendation_reason": "Fixes nitrogen.",
                "risk_factors": ["Wilt"],
                "farming_tips": ["Rhizobium treatment"]
            },
            {
                "crop_name": "Lentils",
                "suitability_score": 75,
                "season": "Rabi",
                "recommendation_reason": "High potassium.",
                "risk_factors": ["Pod borer"],
                "farming_tips": ["排水 (Drainage)"]
            }
        ]
    }

    token = _get_token(client, "has-soil@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a soil report first
    soil_resp = client.post(
        "/api/v1/soil/reports",
        headers=headers,
        json={
            "ph": 6.5,
            "nitrogen": 45.0,
            "phosphorus": 35.0,
            "potassium": 250.0,
            "organic_matter": 2.5,
            "crop_planned": "Tomatoes",
            "tested_at": "2026-06-10"
        }
    )
    assert soil_resp.status_code == status.HTTP_201_CREATED

    # 2. Generate recommendations
    rec_resp = client.post("/api/v1/crop-recommendations/generate", headers=headers)
    assert rec_resp.status_code == status.HTTP_201_CREATED
    recs = rec_resp.json()
    assert len(recs) == 5
    assert recs[0]["crop_name"] == "Wheat"
    assert recs[0]["suitability_score"] == 95
    assert recs[0]["season"] == "Rabi"
    assert len(recs[0]["risk_factors"]) == 1
    assert recs[0]["risk_factors"][0] == "Frost"

    # Verify they have a shared created_at
    created_at_list = [r["created_at"] for r in recs]
    assert len(set(created_at_list)) == 1


@patch("app.services.crop_recommendation.ai_service.generate_crop_recommendations")
def test_list_and_get_details(mock_ai, client):
    mock_ai.return_value = {
        "recommendations": [
            {
                "crop_name": "Mustard",
                "suitability_score": 85,
                "season": "Rabi",
                "recommendation_reason": "Low moisture requirement.",
                "risk_factors": [],
                "farming_tips": []
            }
        ]
    }

    token_1 = _get_token(client, "user1@example.com")
    token_2 = _get_token(client, "user2@example.com")

    # Add soil report for user 1
    client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token_1}"},
        json={
            "ph": 6.8,
            "nitrogen": 40.0,
            "phosphorus": 30.0,
            "potassium": 200.0,
            "organic_matter": 2.0,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-12"
        }
    )

    # Generate recommendations for user 1
    gen_resp = client.post(
        "/api/v1/crop-recommendations/generate",
        headers={"Authorization": f"Bearer {token_1}"}
    )
    rec_id = gen_resp.json()[0]["id"]

    # 1. Fetch list for user 1
    list_resp = client.get(
        "/api/v1/crop-recommendations",
        headers={"Authorization": f"Bearer {token_1}"}
    )
    assert list_resp.status_code == status.HTTP_200_OK
    assert len(list_resp.json()) >= 1

    # 2. Fetch specific recommendation details for user 1 (Should succeed)
    detail_resp = client.get(
        f"/api/v1/crop-recommendations/{rec_id}",
        headers={"Authorization": f"Bearer {token_1}"}
    )
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["crop_name"] == "Mustard"

    # 3. Fetch user 1's recommendation details using user 2's token (Should return 403 Forbidden)
    forbidden_resp = client.get(
        f"/api/v1/crop-recommendations/{rec_id}",
        headers={"Authorization": f"Bearer {token_2}"}
    )
    assert forbidden_resp.status_code == status.HTTP_403_FORBIDDEN
