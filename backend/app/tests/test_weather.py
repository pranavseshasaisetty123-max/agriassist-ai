import pytest
from fastapi import status
from unittest.mock import patch


def _get_token(client, email, location="Punjab, India"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "location": location
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_get_weather_unauthorized(client):
    response = client.get("/api/v1/weather/current")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.services.weather.httpx.get")
def test_get_current_weather_success(mock_get, client):
    # Mock Open-Meteo response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "current_weather": {
            "temperature": 32.5,
            "weathercode": 0
        },
        "daily": {
            "time": ["2026-06-11", "2026-06-12", "2026-06-13", "2026-06-14", "2026-06-15", "2026-06-16", "2026-06-17"],
            "temperature_2m_max": [35.0, 36.0, 35.0, 34.0, 33.0, 32.0, 32.0],
            "temperature_2m_min": [23.0, 24.0, 24.0, 23.0, 22.0, 21.0, 21.0],
            "weathercode": [0, 0, 1, 2, 3, 61, 63]
        }
    }
    
    token = _get_token(client, "weather-user@example.com", "Ludhiana, Punjab")
    
    response = client.get(
        "/api/v1/weather/current",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["location"] == "Ludhiana, Punjab"
    assert data["current_temp"] == 32.5
    assert data["current_condition"] == "Clear sky"


@patch("app.services.weather.httpx.get")
def test_get_weather_forecast_success(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "current_weather": {
            "temperature": 30.0,
            "weathercode": 2
        },
        "daily": {
            "time": ["2026-06-11", "2026-06-12"],
            "temperature_2m_max": [33.0, 34.0],
            "temperature_2m_min": [22.0, 23.0],
            "weathercode": [2, 61]
        }
    }
    
    token = _get_token(client, "forecast-user@example.com", "Chandigarh, India")
    
    response = client.get(
        "/api/v1/weather/forecast",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["forecast"]) == 2
    assert data["forecast"][0]["condition"] == "Partly cloudy"
    assert data["forecast"][1]["condition"] == "Slight rain"


def test_get_advisory_no_soil_report(client):
    token = _get_token(client, "advisory-err@example.com")
    
    response = client.get(
        "/api/v1/weather/advisory",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("app.services.weather.httpx.get")
@patch("app.services.weather.ai_service.generate_weather_advisory")
def test_get_advisory_success(mock_ai, mock_get, client):
    # Mock weather call
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "current_weather": {
            "temperature": 28.0,
            "weathercode": 3
        },
        "daily": {
            "time": ["2026-06-11"],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [20.0],
            "weathercode": [3]
        }
    }
    
    # Mock AI response
    mock_ai.return_value = {
        "advisory_points": [
            "Upcoming rain suggests postponing irrigation.",
            "Soil pH is perfect, no liming required."
        ],
        "severity": "info"
    }
    
    token = _get_token(client, "advisory-ok@example.com", "Amritsar, Punjab")
    
    # Create a soil report first
    client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.5,
            "nitrogen": 40.0,
            "phosphorus": 20.0,
            "potassium": 120.0,
            "crop_planned": "Rice",
            "tested_at": "2026-06-11"
        }
    )
    
    # Retrieve advisory
    response = client.get(
        "/api/v1/weather/advisory",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["crop"] == "Rice"
    assert len(data["advisory_points"]) == 2
    assert "advisory_points" in data
    assert data["severity"] == "info"


@patch("app.services.weather.httpx.get")
@patch("app.services.weather.ai_service.generate_weather_advisory")
def test_get_advisory_gemini_failure(mock_ai, mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "current_weather": {
            "temperature": 28.0,
            "weathercode": 3
        },
        "daily": {
            "time": ["2026-06-11"],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [20.0],
            "weathercode": [3]
        }
    }
    
    mock_ai.side_effect = Exception("Gemini down")
    token = _get_token(client, "advisory-fail@example.com", "Amritsar, Punjab")
    
    client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.5,
            "nitrogen": 40.0,
            "phosphorus": 20.0,
            "potassium": 120.0,
            "crop_planned": "Rice",
            "tested_at": "2026-06-11"
        }
    )
    
    response = client.get(
        "/api/v1/weather/advisory",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "AI advisory temporarily unavailable. Weather and soil data remain accessible."
