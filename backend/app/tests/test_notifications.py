import pytest
from fastapi import status
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.farmer import Farmer
from app.repositories.notification import notification_repo
from app.services.notification import notification_service


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Ramesh",
            "last_name": "Kumar",
            "location": "Punjab, India"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_endpoints_unauthorized(client):
    r1 = client.get("/api/v1/notifications")
    assert r1.status_code == status.HTTP_401_UNAUTHORIZED

    r2 = client.get("/api/v1/notifications/unread")
    assert r2.status_code == status.HTTP_401_UNAUTHORIZED

    r3 = client.patch("/api/v1/notifications/1/read")
    assert r3.status_code == status.HTTP_401_UNAUTHORIZED

    r4 = client.patch("/api/v1/notifications/read-all")
    assert r4.status_code == status.HTTP_401_UNAUTHORIZED

    r5 = client.delete("/api/v1/notifications/1")
    assert r5.status_code == status.HTTP_401_UNAUTHORIZED

    r6 = client.post("/api/v1/notifications/generate")
    assert r6.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_list_and_read_notifications(client, db):
    token = _get_token(client, "farmer_notif@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Run generate manually
    gen_resp = client.post("/api/v1/notifications/generate", headers=headers)
    assert gen_resp.status_code == status.HTTP_200_OK
    assert gen_resp.json()["status"] == "success"
    assert gen_resp.json()["generated_count"] >= 0

    # 2. Add manual alerts directly to the database via repository for verification
    farmer = db.query(Farmer).filter(Farmer.email == "farmer_notif@example.com").first()
    assert farmer is not None

    notification_repo.create(
        db=db,
        farmer_id=farmer.id,
        title="Rain warning",
        message="Heavy rain forecast",
        notification_type="weather",
        priority="critical",
        source_module="weather"
    )
    notification_repo.create(
        db=db,
        farmer_id=farmer.id,
        title="Overdue Sowing",
        message="Your tomato sowing task is overdue",
        notification_type="planner",
        priority="high",
        source_module="planner"
    )

    # 3. Retrieve list of all notifications
    resp = client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) >= 2
    titles = [d["title"] for d in data]
    assert "Rain warning" in titles
    assert "Overdue Sowing" in titles

    # 4. Retrieve list of unread only
    unread_resp = client.get("/api/v1/notifications/unread", headers=headers)
    assert unread_resp.status_code == status.HTTP_200_OK
    assert len(unread_resp.json()) >= 2

    # 5. Mark single notification as read
    target_notif = [d for d in data if d["title"] == "Rain warning"][0]
    notif_id = target_notif["id"]
    read_resp = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=headers)
    assert read_resp.status_code == status.HTTP_200_OK
    assert read_resp.json()["is_read"] is True


def test_mark_all_read_and_delete(client, db):
    token = _get_token(client, "farmer_notif_2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    farmer = db.query(Farmer).filter(Farmer.email == "farmer_notif_2@example.com").first()
    assert farmer is not None

    # Create two notifications
    notification_repo.create(
        db=db,
        farmer_id=farmer.id,
        title="Warning 1",
        message="Description 1",
        notification_type="risk",
        priority="medium",
        source_module="risk"
    )
    notification_repo.create(
        db=db,
        farmer_id=farmer.id,
        title="Warning 2",
        message="Description 2",
        notification_type="yield",
        priority="low",
        source_module="yield"
    )

    # Mark all read
    read_all_resp = client.patch("/api/v1/notifications/read-all", headers=headers)
    assert read_all_resp.status_code == status.HTTP_200_OK
    assert read_all_resp.json()["status"] == "success"

    # Get list
    list_resp = client.get("/api/v1/notifications", headers=headers)
    data = list_resp.json()
    target_warnings = [d for d in data if d["title"] in ["Warning 1", "Warning 2"]]
    assert len(target_warnings) == 2
    assert target_warnings[0]["is_read"] is True
    assert target_warnings[1]["is_read"] is True

    # Delete one
    delete_id = target_warnings[0]["id"]
    del_resp = client.delete(f"/api/v1/notifications/{delete_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT


def test_duplicate_prevention_logic(db):
    # Retrieve or create a temp farmer
    farmer = db.query(Farmer).first()
    if not farmer:
        from app.repositories.farmer import farmer_repo
        from app.schemas.farmer import FarmerCreate
        farmer = farmer_repo.create(
            db=db,
            obj_in=FarmerCreate(
                email="seed_notif@example.com",
                password="password123",
                first_name="Seed",
                last_name="Notif"
            )
        )

    # Clear existing identical alerts if any
    existing_alerts = db.query(Notification).filter(
        Notification.farmer_id == farmer.id,
        Notification.notification_type == "weather",
        Notification.source_module == "weather",
        Notification.title == "Test Duplicate"
    ).all()
    for a in existing_alerts:
        db.delete(a)
    db.commit()

    # Generate alert
    res1 = notification_service._create_if_not_exists(db, farmer.id, "Test Duplicate", "Rain warning text", "weather", "high", "weather")
    assert res1 is True

    # Try generating identical alert
    res2 = notification_service._create_if_not_exists(db, farmer.id, "Test Duplicate", "Rain warning text", "weather", "high", "weather")
    assert res2 is False

    # Retrieve count
    count = db.query(Notification).filter(
        Notification.farmer_id == farmer.id,
        Notification.notification_type == "weather",
        Notification.source_module == "weather",
        Notification.title == "Test Duplicate"
    ).count()
    assert count == 1
