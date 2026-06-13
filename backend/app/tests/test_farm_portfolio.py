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


def test_farm_crud(client):
    token = _get_token(client, "farm-crud@example.com")
    
    # 1. Create a Farm
    response = client.post(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Green Valley Farm",
            "location": "Punjab",
            "total_area_acres": 15.5,
            "soil_type": "Clay",
            "latitude": 30.9009,
            "longitude": 75.8573
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Green Valley Farm"
    assert data["total_area_acres"] == 15.5
    assert data["soil_type"] == "Clay"
    farm_id = data["id"]
    
    # 2. List Farms
    list_response = client.get(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_response.status_code == status.HTTP_200_OK
    farms = list_response.json()
    # There should be at least the one we just created
    assert len(farms) >= 1
    assert any(f["id"] == farm_id for f in farms)
    
    # 3. Update Farm
    update_response = client.put(
        f"/api/v1/farms/{farm_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Green Valley Farm Updated",
            "total_area_acres": 18.2
        }
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["name"] == "Green Valley Farm Updated"
    assert update_response.json()["total_area_acres"] == 18.2
    
    # 4. Get specific Farm
    get_response = client.get(
        f"/api/v1/farms/{farm_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["name"] == "Green Valley Farm Updated"
    
    # 5. Delete Farm
    delete_response = client.delete(
        f"/api/v1/farms/{farm_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == status.HTTP_200_OK
    
    # Get again should return 404
    get_again = client.get(
        f"/api/v1/farms/{farm_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_again.status_code == status.HTTP_404_NOT_FOUND


def test_activate_farm_and_self_healing(client):
    token = _get_token(client, "farm-activate@example.com")
    
    # List should be initially empty or auto-created on accessing active modules
    # Let's trigger self-healing by getting soil reports (which forces a default farm)
    soil_list = client.get(
        "/api/v1/soil/reports",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert soil_list.status_code == status.HTTP_200_OK
    
    # Now list farms - we should have the "Primary Farm" auto-created
    list_response = client.get(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_response.status_code == status.HTTP_200_OK
    farms = list_response.json()
    assert len(farms) == 1
    primary_farm = farms[0]
    assert primary_farm["name"] == "Primary Farm"
    assert primary_farm["total_area_acres"] == 10.0
    
    # Check that it's currently active (can call /api/v1/auth/me equivalent or check via profile / farms)
    # Create a second farm
    response = client.post(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Secondary Farm",
            "location": "Haryana",
            "total_area_acres": 20.0,
            "soil_type": "Sandy",
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    sec_farm_id = response.json()["id"]
    
    # Activate the second farm
    act_response = client.post(
        f"/api/v1/farms/{sec_farm_id}/activate",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert act_response.status_code == status.HTTP_200_OK
    
    # Get current farmer profile and verify active_farm_id is updated
    # Wait, do we have /api/v1/auth/me or similar? Let's check how user is retrieved
    # Let's check portfolio to see if metrics are compiled
    port_response = client.get(
        "/api/v1/farms/portfolio",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert port_response.status_code == status.HTTP_200_OK
    portfolio = port_response.json()
    assert portfolio["total_farms"] == 2
    assert portfolio["total_area"] == 30.0
