from fastapi import status


def _get_token(client, email, password="password123"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Settings",
            "last_name": "Test",
            "location": "Punjab"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    return login_response.json()["access_token"]


def test_get_settings(client):
    email = "settings-get@example.com"
    token = _get_token(client, email)
    
    response = client.get(
        "/api/v1/farmers/settings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["theme_preference"] == "dark"
    assert data["email_notifications"] is True
    assert data["push_notifications"] is True
    assert data["default_crop"] is None
    assert data["default_soil_type"] is None


def test_update_settings(client):
    email = "settings-put@example.com"
    token = _get_token(client, email)
    
    # 1. Update settings
    response = client.put(
        "/api/v1/farmers/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "theme_preference": "light",
            "email_notifications": False,
            "push_notifications": True,
            "default_crop": "Cotton",
            "default_soil_type": "Black Soil"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["theme_preference"] == "light"
    assert data["email_notifications"] is False
    assert data["push_notifications"] is True
    assert data["default_crop"] == "Cotton"
    assert data["default_soil_type"] == "Black Soil"

    # 2. Get and verify persistency
    get_resp = client.get(
        "/api/v1/farmers/settings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == status.HTTP_200_OK
    get_data = get_resp.json()
    assert get_data["theme_preference"] == "light"
    assert get_data["email_notifications"] is False
    assert get_data["default_crop"] == "Cotton"


def test_change_password_success(client):
    email = "pass-success@example.com"
    token = _get_token(client, email, "password123")
    
    # 1. Update password
    response = client.post(
        "/api/v1/farmers/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "password123",
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"

    # 2. Try logging in with old password (should fail)
    bad_login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    assert bad_login.status_code != status.HTTP_200_OK

    # 3. Try logging in with new password (should succeed)
    good_login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "newpassword456"}
    )
    assert good_login.status_code == status.HTTP_200_OK
    assert "access_token" in good_login.json()


def test_change_password_invalid(client):
    email = "pass-invalid@example.com"
    token = _get_token(client, email, "password123")
    
    response = client.post(
        "/api/v1/farmers/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "wrongoldpassword",
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()


def test_get_system_status(client):
    # Public health checks, no token needed
    response = client.get("/api/v1/system/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["backend_status"] == "healthy"
    assert "database_status" in data
    assert "gemini_status" in data
    assert data["last_api_response_time"] >= 0.0


def test_get_help_center(client):
    # Public help checks, no token needed
    response = client.get("/api/v1/system/help")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "guides" in data
    assert "faqs" in data
    assert "troubleshooting" in data
    assert len(data["faqs"]) > 0
