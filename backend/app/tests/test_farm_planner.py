import pytest
from fastapi import status
from unittest.mock import patch
from datetime import date, timedelta


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


def test_generate_plan_unauthorized(client):
    response = client.post(
        "/api/v1/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.5,
            "planned_start_date": "2026-06-12"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_generate_plan_no_soil_report(client):
    token = _get_token(client, "nosoilplan@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.5,
            "planned_start_date": "2026-06-12"
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "log a soil test report first" in response.json()["detail"]


@patch("app.services.farm_planner.ai_service.generate_farm_plan")
def test_generate_plan_success(mock_ai, client):
    mock_ai.return_value = {
        "expected_harvest_days": 90,
        "tasks": [
            {
                "title": "Soil tilling",
                "description": "Till soil deeply",
                "planned_date_offset_days": 0,
                "priority": "medium",
                "category": "land_preparation"
            },
            {
                "title": "Irrigation check",
                "description": "Perform watering check",
                "planned_date_offset_days": 5,
                "priority": "high",
                "category": "irrigation"
            }
        ]
    }

    token = _get_token(client, "hasreportplan@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create soil report first
    soil_resp = client.post(
        "/api/v1/soil/reports",
        headers=headers,
        json={
            "ph": 6.5,
            "nitrogen": 50.0,
            "phosphorus": 40.0,
            "potassium": 200.0,
            "organic_matter": 2.0,
            "crop_planned": "Tomato",
            "tested_at": "2026-06-12"
        }
    )
    assert soil_resp.status_code == status.HTTP_201_CREATED

    # 2. Generate plan
    start_date_str = "2026-06-12"
    plan_resp = client.post(
        "/api/v1/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.5,
            "planned_start_date": start_date_str
        },
        headers=headers
    )
    assert plan_resp.status_code == status.HTTP_201_CREATED
    data = plan_resp.json()
    assert data["crop_name"] == "Tomato"
    assert data["area_acres"] == 2.5
    assert data["planned_start_date"] == start_date_str
    assert data["expected_harvest_date"] == "2026-09-10" # 90 days offset
    assert len(data["tasks"]) == 2
    
    # Task 0 (offset 0)
    assert data["tasks"][0]["title"] == "Soil tilling"
    assert data["tasks"][0]["planned_date"] == "2026-06-12"
    assert data["tasks"][0]["status"] == "pending"

    # Task 1 (offset 5)
    assert data["tasks"][1]["title"] == "Irrigation check"
    assert data["tasks"][1]["planned_date"] == "2026-06-17"


@patch("app.services.farm_planner.ai_service.generate_farm_plan")
def test_task_actions_and_filtering(mock_ai, client):
    mock_ai.return_value = {
        "expected_harvest_days": 100,
        "tasks": [
            {
                "title": "Prepare field",
                "description": "Level the fields",
                "planned_date_offset_days": 0,
                "priority": "low",
                "category": "land_preparation"
            }
        ]
    }

    token = _get_token(client, "taskactions@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Soil report
    client.post(
        "/api/v1/soil/reports",
        headers=headers,
        json={
            "ph": 6.8, "nitrogen": 45.0, "phosphorus": 35.0, "potassium": 180.0,
            "organic_matter": 1.8, "crop_planned": "Wheat", "tested_at": "2026-06-12"
        }
    )

    # Generate plan
    plan_resp = client.post(
        "/api/v1/farm-planner/plans/generate",
        json={"crop_name": "Wheat", "area_acres": 5.0, "planned_start_date": "2026-06-12"},
        headers=headers
    )
    plan_id = plan_resp.json()["id"]
    task_id = plan_resp.json()["tasks"][0]["id"]

    # 1. Complete task
    complete_resp = client.patch(f"/api/v1/farm-planner/tasks/{task_id}/complete", headers=headers)
    assert complete_resp.status_code == status.HTTP_200_OK
    assert complete_resp.json()["status"] == "completed"
    assert complete_resp.json()["completed_at"] is not None

    # 2. Update task status (back to pending)
    pending_resp = client.patch(
        f"/api/v1/farm-planner/tasks/{task_id}/status",
        json={"status": "pending"},
        headers=headers
    )
    assert pending_resp.status_code == status.HTTP_200_OK
    assert pending_resp.json()["status"] == "pending"

    # 3. Postpone task (snooze +3 days)
    orig_date = date.fromisoformat(pending_resp.json()["planned_date"])
    snooze_resp = client.patch(f"/api/v1/farm-planner/tasks/{task_id}/snooze?days=3", headers=headers)
    assert snooze_resp.status_code == status.HTTP_200_OK
    new_date = date.fromisoformat(snooze_resp.json()["planned_date"])
    assert new_date == orig_date + timedelta(days=3)

    # 4. Create manual task
    manual_date_str = (date.today() + timedelta(days=2)).isoformat()
    manual_resp = client.post(
        "/api/v1/farm-planner/tasks",
        json={
            "farm_plan_id": plan_id,
            "title": "Check crop growth",
            "description": "Examine foliage",
            "planned_date": manual_date_str,
            "priority": "medium",
            "category": "monitoring"
        },
        headers=headers
    )
    assert manual_resp.status_code == status.HTTP_201_CREATED
    assert manual_resp.json()["title"] == "Check crop growth"
    assert manual_resp.json()["planned_date"] == manual_date_str

    # 5. Get upcoming tasks (should return the manual task we scheduled in +2 days)
    upcoming_resp = client.get("/api/v1/farm-planner/tasks/upcoming?days=7", headers=headers)
    assert upcoming_resp.status_code == status.HTTP_200_OK
    assert len(upcoming_resp.json()) >= 1

    # 6. Delete task
    delete_task_resp = client.delete(f"/api/v1/farm-planner/tasks/{task_id}", headers=headers)
    assert delete_task_resp.status_code == status.HTTP_200_OK
    
    # Verify deletion from plan details
    details_resp = client.get(f"/api/v1/farm-planner/plans/{plan_id}", headers=headers)
    task_ids = [t["id"] for t in details_resp.json()["tasks"]]
    assert task_id not in task_ids


@patch("app.services.farm_planner.ai_service.generate_farm_plan")
def test_delete_plan_cascades(mock_ai, client):
    mock_ai.return_value = {
        "expected_harvest_days": 100,
        "tasks": [{"title": "Prep", "description": "Prep", "planned_date_offset_days": 0, "priority": "low", "category": "land_preparation"}]
    }

    token = _get_token(client, "cascadedelete@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/soil/reports",
        headers=headers,
        json={
            "ph": 6.8, "nitrogen": 45.0, "phosphorus": 35.0, "potassium": 180.0,
            "organic_matter": 1.8, "crop_planned": "Wheat", "tested_at": "2026-06-12"
        }
    )

    plan_resp = client.post(
        "/api/v1/farm-planner/plans/generate",
        json={"crop_name": "Wheat", "area_acres": 5.0, "planned_start_date": "2026-06-12"},
        headers=headers
    )
    plan_id = plan_resp.json()["id"]

    # Delete plan
    del_resp = client.delete(f"/api/v1/farm-planner/plans/{plan_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_200_OK

    # Fetching plan should return 404
    get_resp = client.get(f"/api/v1/farm-planner/plans/{plan_id}", headers=headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
