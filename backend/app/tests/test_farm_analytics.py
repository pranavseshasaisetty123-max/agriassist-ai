import pytest
from fastapi import status
from sqlalchemy.orm import Session
import json

from app.models.farmer import Farmer
from app.models.farm_analytics import FarmAnalyticsSnapshot
from app.services.farm_analytics import farm_analytics_service
from app.repositories.farm_analytics import farm_analytics_repo


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Raman",
            "last_name": "Singh",
            "location": "Punjab, India"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_endpoints_unauthorized(client):
    r1 = client.get("/api/v1/analytics/dashboard")
    assert r1.status_code == status.HTTP_401_UNAUTHORIZED

    r2 = client.get("/api/v1/analytics/trends")
    assert r2.status_code == status.HTTP_401_UNAUTHORIZED

    r3 = client.get("/api/v1/analytics/kpis")
    assert r3.status_code == status.HTTP_401_UNAUTHORIZED

    r4 = client.post("/api/v1/analytics/snapshot")
    assert r4.status_code == status.HTTP_401_UNAUTHORIZED

    r5 = client.get("/api/v1/analytics/report")
    assert r5.status_code == status.HTTP_401_UNAUTHORIZED


def test_calculate_kpis_and_snapshot(client, db):
    token = _get_token(client, "farmer_analytics@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch KPIs when database is fresh
    kpi_resp = client.get("/api/v1/analytics/kpis", headers=headers)
    assert kpi_resp.status_code == status.HTTP_200_OK
    kpis = kpi_resp.json()
    assert "health_score" in kpis
    assert "risk_score" in kpis
    assert "projected_yield" in kpis
    assert "projected_profit" in kpis
    assert "active_crop_count" in kpis
    assert "active_alert_count" in kpis

    # 2. POST /snapshot to generate historical data
    snap_resp = client.post("/api/v1/analytics/snapshot", headers=headers)
    assert snap_resp.status_code == status.HTTP_200_OK
    snap = snap_resp.json()
    assert "id" in snap
    assert snap["health_score"] == kpis["health_score"]
    assert snap["risk_score"] == kpis["risk_score"]

    # 3. GET /trends to fetch snapshots
    trends_resp = client.get("/api/v1/analytics/trends", headers=headers)
    assert trends_resp.status_code == status.HTTP_200_OK
    trends = trends_resp.json()
    assert len(trends) >= 1
    assert trends[0]["health_score"] == snap["health_score"]

    # 4. GET /dashboard
    dash_resp = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_resp.status_code == status.HTTP_200_OK
    dash = dash_resp.json()
    assert "kpis" in dash
    assert "trends" in dash
    assert "insights" in dash
    assert "crop_distribution" in dash
    assert "alert_distribution" in dash


def test_report_endpoints(client, db):
    token = _get_token(client, "farmer_analytics_reports@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a snapshot first so there is data point
    snap_resp = client.post("/api/v1/analytics/snapshot", headers=headers)
    assert snap_resp.status_code == status.HTTP_200_OK

    # 1. GET /report with format=json
    json_resp = client.get("/api/v1/analytics/report?format=json", headers=headers)
    assert json_resp.status_code == status.HTTP_200_OK
    rep = json_resp.json()
    assert "kpis" in rep
    assert "active_risks" in rep
    assert "recommendations" in rep
    assert "yield_forecasts" in rep
    assert "profit_forecasts" in rep

    # 2. GET /report with format=pdf
    pdf_resp = client.get("/api/v1/analytics/report?format=pdf", headers=headers)
    assert pdf_resp.status_code == status.HTTP_200_OK
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 0
