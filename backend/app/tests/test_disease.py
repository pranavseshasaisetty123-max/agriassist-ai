import pytest
import io
from fastapi import status
from unittest.mock import patch


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


def test_scan_unauthorized(client):
    response = client.post("/api/v1/disease/scan")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_scans_unauthorized(client):
    response = client.get("/api/v1/disease/scans")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_scan_crop_leaf_success(mock_ai, client):
    # Mock Gemini response
    mock_ai.return_value = {
        "disease_name": "Tomato Leaf Mold",
        "confidence": 0.94,
        "severity": "Medium",
        "symptoms": ["Yellow spots on upper leaf surfaces", "Olive green mold on lower surfaces"],
        "treatment": ["Apply appropriate fungicides", "Improve greenhouse ventilation"],
        "preventive_measures": ["Use resistant varieties", "Sanitize tools regularly"]
    }

    token = _get_token(client, "disease-scan-user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Simulate multipart file upload
    file_content = b"fake image bytes"
    file_name = "leaf.jpg"
    files = {"file": (file_name, io.BytesIO(file_content), "image/jpeg")}

    response = client.post(
        "/api/v1/disease/scan",
        headers=headers,
        files=files
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["disease_name"] == "Tomato Leaf Mold"
    assert data["confidence"] == 0.94
    assert data["severity"] == "Medium"
    assert len(data["symptoms"]) == 2
    assert "image_path" in data
    assert data["image_path"].startswith("/static/uploads/")


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_list_and_get_scans_success(mock_ai, client):
    mock_ai.return_value = {
        "disease_name": "Healthy",
        "confidence": 0.99,
        "severity": "Low",
        "symptoms": ["No visible disease symptoms observed"],
        "treatment": ["Continue regular crop monitoring"],
        "preventive_measures": ["Keep sanitizing tools"]
    }

    token = _get_token(client, "disease-list-user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a scan
    file_content = b"fake healthy leaf bytes"
    files = {"file": ("healthy.png", io.BytesIO(file_content), "image/png")}
    create_resp = client.post(
        "/api/v1/disease/scan",
        headers=headers,
        files=files
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    scan_id = create_resp.json()["id"]

    # 2. List scans
    list_resp = client.get("/api/v1/disease/scans", headers=headers)
    assert list_resp.status_code == status.HTTP_200_OK
    scans = list_resp.json()
    assert len(scans) >= 1
    assert scans[0]["id"] == scan_id
    assert scans[0]["disease_name"] == "Healthy"

    # 3. Get scan details
    detail_resp = client.get(f"/api/v1/disease/scans/{scan_id}", headers=headers)
    assert detail_resp.status_code == status.HTTP_200_OK
    detail = detail_resp.json()
    assert detail["id"] == scan_id
    assert detail["disease_name"] == "Healthy"
    assert detail["severity"] == "Low"


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_delete_scan_success(mock_ai, client):
    mock_ai.return_value = {
        "disease_name": "Potato Blight",
        "confidence": 0.85,
        "severity": "High",
        "symptoms": ["Dark spot on potato leaves"],
        "treatment": ["Fungicidal spray"],
        "preventive_measures": ["Crop rotation"]
    }

    token = _get_token(client, "disease-delete-user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create scan
    file_content = b"fake potato leaf bytes"
    files = {"file": ("potato.jpg", io.BytesIO(file_content), "image/jpeg")}
    create_resp = client.post(
        "/api/v1/disease/scan",
        headers=headers,
        files=files
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    scan_id = create_resp.json()["id"]

    # 2. Delete scan
    delete_resp = client.delete(f"/api/v1/disease/scans/{scan_id}", headers=headers)
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

    # 3. Verify it is deleted (GET returns 404)
    get_resp = client.get(f"/api/v1/disease/scans/{scan_id}", headers=headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
