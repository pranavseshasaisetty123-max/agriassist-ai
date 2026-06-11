from fastapi import status
from unittest.mock import patch


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Test",
            "last_name": "Farmer",
            "location": "Punjab"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_create_soil_report(client):
    token = _get_token(client, "soil-crud@example.com")
    
    response = client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.5,
            "nitrogen": 45.0,
            "phosphorus": 18.0,
            "potassium": 150.0,
            "organic_matter": 2.1,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-11"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["ph"] == 6.5
    assert data["crop_planned"] == "Wheat"
    assert "id" in data


def test_create_soil_report_validation(client):
    token = _get_token(client, "soil-valid@example.com")
    
    # Invalid pH (too high)
    response = client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 15.0,
            "nitrogen": 45.0,
            "phosphorus": 18.0,
            "potassium": 150.0,
            "organic_matter": 2.1,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-11"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid negative nitrogen
    response = client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.5,
            "nitrogen": -10.0,
            "phosphorus": 18.0,
            "potassium": 150.0,
            "organic_matter": 2.1,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-11"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_and_get_soil_reports(client):
    token = _get_token(client, "soil-list@example.com")
    
    # Create two reports
    client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.0,
            "nitrogen": 30.0,
            "phosphorus": 12.0,
            "potassium": 110.0,
            "crop_planned": "Rice",
            "tested_at": "2026-06-01"
        }
    )
    client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.5,
            "nitrogen": 40.0,
            "phosphorus": 15.0,
            "potassium": 120.0,
            "crop_planned": "Cotton",
            "tested_at": "2026-06-05"
        }
    )
    
    # List reports
    list_resp = client.get(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_resp.status_code == status.HTTP_200_OK
    list_data = list_resp.json()
    assert len(list_data) == 2
    assert list_data[0]["crop_planned"] == "Cotton"  # Sorted by tested_at desc
    
    # Get specific report
    report_id = list_data[0]["id"]
    get_resp = client.get(
        f"/api/v1/soil/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["crop_planned"] == "Cotton"


def test_delete_soil_report(client):
    token = _get_token(client, "soil-del@example.com")
    
    response = client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.5,
            "nitrogen": 45.0,
            "phosphorus": 18.0,
            "potassium": 150.0,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-11"
        }
    )
    report_id = response.json()["id"]
    
    # Delete report
    del_resp = client.delete(
        f"/api/v1/soil/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify get returns 404
    get_resp = client.get(
        f"/api/v1/soil/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_unauthorized_report_access(client):
    token1 = _get_token(client, "farmer-a@example.com")
    token2 = _get_token(client, "farmer-b@example.com")
    
    # Farmer A creates report
    response = client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "ph": 6.5,
            "nitrogen": 45.0,
            "phosphorus": 18.0,
            "potassium": 150.0,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-11"
        }
    )
    report_id = response.json()["id"]
    
    # Farmer B tries to fetch
    get_resp = client.get(
        f"/api/v1/soil/reports/{report_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert get_resp.status_code == status.HTTP_403_FORBIDDEN
    
    # Farmer B tries to delete
    del_resp = client.delete(
        f"/api/v1/soil/reports/{report_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert del_resp.status_code == status.HTTP_403_FORBIDDEN


@patch("app.services.soil.ai_service.generate_soil_recommendation")
def test_analyze_soil_report(mock_ai, client):
    mock_ai.return_value = {
        "nitrogen_recommendation": "Add 50kg Nitrogen",
        "phosphorus_recommendation": "Add 20kg Phosphorus",
        "potassium_recommendation": "Add 30kg Potassium",
        "fertilizer_schedule": "Week 1: MOP, Week 2: Urea",
        "ai_raw_analysis": "Soil is slightly acidic and low in nitrogen."
    }
    
    token = _get_token(client, "soil-analysis@example.com")
    
    # Log report
    response = client.post(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ph": 6.0,
            "nitrogen": 20.0,
            "phosphorus": 15.0,
            "potassium": 110.0,
            "crop_planned": "Tomatoes",
            "tested_at": "2026-06-11"
        }
    )
    report_id = response.json()["id"]
    
    # Run analysis
    analyze_resp = client.post(
        f"/api/v1/soil/reports/{report_id}/analyze",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert analyze_resp.status_code == status.HTTP_200_OK
    data = analyze_resp.json()
    assert data["nitrogen_recommendation"] == "Add 50kg Nitrogen"
    assert data["fertilizer_schedule"] == "Week 1: MOP, Week 2: Urea"
    assert data["report_id"] == report_id
    
    # Fetch report details again to check if recommendation is nested
    get_resp = client.get(
        f"/api/v1/soil/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == status.HTTP_200_OK
    report_data = get_resp.json()
    assert report_data["recommendation"] is not None
    assert report_data["recommendation"]["nitrogen_recommendation"] == "Add 50kg Nitrogen"
