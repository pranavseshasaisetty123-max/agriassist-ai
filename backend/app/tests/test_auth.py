from fastapi import status


def test_register_farmer(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "farmer@example.com",
            "password": "secretpassword",
            "first_name": "Ramesh",
            "last_name": "Kumar",
            "location": "Karnataka",
            "contact_number": "+919876543210"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "farmer@example.com"
    assert data["first_name"] == "Ramesh"
    assert data["last_name"] == "Kumar"
    assert "id" in data


def test_register_duplicate_email(client):
    farmer_data = {
        "email": "duplicate@example.com",
        "password": "secretpassword",
        "first_name": "John",
        "last_name": "Doe"
    }
    # First registration
    client.post("/api/v1/auth/register", json=farmer_data)
    
    # Second registration
    response = client.post("/api/v1/auth/register", json=farmer_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()


def test_login_success(client):
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "correctpassword",
            "first_name": "Sita",
            "last_name": "Devi"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "correctpassword"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpwd@example.com",
            "password": "correctpassword",
            "first_name": "Sita",
            "last_name": "Devi"
        }
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrongpwd@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_profile_me(client):
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile@example.com",
            "password": "password123",
            "first_name": "Ali",
            "last_name": "Khan",
            "location": "Punjab"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "profile@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    response = client.get(
        "/api/v1/farmers/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["location"] == "Punjab"


def test_update_profile_me(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "update@example.com",
            "password": "password123",
            "first_name": "Dev",
            "last_name": "Singh"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "update@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Update profile
    response = client.put(
        "/api/v1/farmers/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Devender",
            "location": "Haryana"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Devender"
    assert data["last_name"] == "Singh"
    assert data["location"] == "Haryana"
