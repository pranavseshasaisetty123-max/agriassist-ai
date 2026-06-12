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
        "diagnosis_type": "disease",
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
    assert data["diagnosis_type"] == "disease"
    assert data["disease_name"] == "Tomato Leaf Mold"
    assert data["confidence"] == 0.94
    assert data["severity"] == "Medium"
    assert len(data["symptoms"]) == 2
    assert "image_path" in data
    assert data["image_path"].startswith("/disease/scans/")


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_list_and_get_scans_success(mock_ai, client):
    mock_ai.return_value = {
        "diagnosis_type": "healthy",
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
    assert scans[0]["diagnosis_type"] == "healthy"

    # 3. Get scan details
    detail_resp = client.get(f"/api/v1/disease/scans/{scan_id}", headers=headers)
    assert detail_resp.status_code == status.HTTP_200_OK
    detail = detail_resp.json()
    assert detail["id"] == scan_id
    assert detail["disease_name"] == "Healthy"
    assert detail["diagnosis_type"] == "healthy"
    assert detail["severity"] == "Low"


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_delete_scan_success(mock_ai, client):
    mock_ai.return_value = {
        "diagnosis_type": "disease",
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


def test_scan_image_size_exceeded(client):
    token = _get_token(client, "disease-size-user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # File size larger than 5 MB (e.g. 5.1 MB)
    large_content = b"0" * (5 * 1024 * 1024 + 1024)
    files = {"file": ("large.jpg", io.BytesIO(large_content), "image/jpeg")}

    response = client.post(
        "/api/v1/disease/scan",
        headers=headers,
        files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceeds the maximum" in response.json()["detail"]


def test_scan_image_invalid_format(client):
    token = _get_token(client, "disease-format-user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Send a GIF instead of allowed formats
    file_content = b"fake gif data"
    files = {"file": ("image.gif", io.BytesIO(file_content), "image/gif")}

    response = client.post(
        "/api/v1/disease/scan",
        headers=headers,
        files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only JPEG, PNG, and WEBP" in response.json()["detail"]


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_scan_non_plant_rejection(mock_ai, client):
    # Mock Gemini classifying image as invalid (non-plant)
    mock_ai.return_value = {
        "diagnosis_type": "invalid",
        "disease_name": "Invalid Image",
        "confidence": 0.0,
        "severity": "Low",
        "symptoms": [],
        "treatment": [],
        "preventive_measures": []
    }

    token = _get_token(client, "disease-rejection-user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"fake non-plant image bytes"
    files = {"file": ("keyboard.jpg", io.BytesIO(file_content), "image/jpeg")}

    response = client.post(
        "/api/v1/disease/scan",
        headers=headers,
        files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "does not appear to be a crop leaf" in response.json()["detail"]


@patch("app.services.disease.ai_service.analyze_crop_image")
def test_get_scan_image_security(mock_ai, client):
    mock_ai.return_value = {
        "diagnosis_type": "disease",
        "disease_name": "Tomato Late Blight",
        "confidence": 0.90,
        "severity": "High",
        "symptoms": ["Dark spots"],
        "treatment": ["Fungicide"],
        "preventive_measures": ["Clean seeds"]
    }

    # Generate tokens for two different users
    owner_token = _get_token(client, "disease-owner@example.com")
    other_token = _get_token(client, "disease-other@example.com")

    # 1. Create a scan for the owner
    files = {"file": ("leaf.jpg", io.BytesIO(b"fake leaf image content"), "image/jpeg")}
    create_resp = client.post(
        "/api/v1/disease/scan",
        headers={"Authorization": f"Bearer {owner_token}"},
        files=files
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    scan_id = create_resp.json()["id"]

    # 2. Try fetching the image as the owner (Should succeed: 200)
    image_url = f"/api/v1/disease/scans/{scan_id}/image"
    owner_get_resp = client.get(
        image_url,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert owner_get_resp.status_code == status.HTTP_200_OK

    # 3. Try fetching the image as a different user (Should fail: 403)
    other_get_resp = client.get(
        image_url,
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert other_get_resp.status_code == status.HTTP_403_FORBIDDEN

    # 4. Try fetching the image without authorization (Should fail: 401)
    anon_get_resp = client.get(image_url)
    assert anon_get_resp.status_code == status.HTTP_401_UNAUTHORIZED

