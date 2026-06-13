import httpx
import sys
import uuid
from datetime import date

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint12():
    print("🚀 Starting Sprint 12 Farm Analytics & Reports E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s12_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Ramesh",
            "last_name": "Gopal",
            "location": "Delhi, India"
        }
    )
    if reg_resp.status_code in (200, 201):
        print("✅ Farmer registered successfully!")
    else:
        print(f"❌ Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        sys.exit(1)

    # 2. Login
    print("\n2. Logging in...")
    login_resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code} - {login_resp.text}")
        sys.exit(1)

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully! JWT token retrieved.")

    # 3. Create soil report
    print("\n3. Creating soil health report...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.8,
            "nitrogen": 45.0,
            "phosphorus": 35.0,
            "potassium": 160.0,
            "organic_matter": 2.2,
            "crop_planned": "Tomato",
            "tested_at": date.today().isoformat()
        }
    )
    if soil_resp.status_code != 201:
        print(f"❌ Soil report creation failed: {soil_resp.status_code} - {soil_resp.text}")
        sys.exit(1)
    print("✅ Soil health report logged successfully!")

    # 4. Generate crop recommendations
    print("\n4. Generating crop recommendations match...")
    crop_resp = client.post(f"{BASE_URL}/crop-recommendations/generate", headers=headers)
    if crop_resp.status_code != 201:
        print(f"❌ Crop match generation failed: {crop_resp.status_code} - {crop_resp.text}")
        sys.exit(1)
    print(f"✅ Generated match recommendations successfully!")

    # 5. Generate yield prediction
    print("\n5. Generating yield predictions forecast...")
    yield_resp = client.post(
        f"{BASE_URL}/yield-predictions/generate",
        headers=headers,
        json={"crop_name": "Tomato"}
    )
    if yield_resp.status_code != 201:
        print(f"❌ Yield forecast failed: {yield_resp.status_code} - {yield_resp.text}")
        sys.exit(1)
    print("✅ Yield prediction registered successfully!")

    # 6. Generate market analysis / profitability calculation
    print("\n6. Calculating market price profitability returns...")
    market_resp = client.post(
        f"{BASE_URL}/market-intelligence/calculate",
        headers=headers,
        json={
            "crop_name": "Tomato",
            "expected_yield": 4200.0,
            "cultivation_cost": 22000.0,
            "market_price_per_kg": 18.0
        }
    )
    if market_resp.status_code != 201:
        print(f"❌ Profit calculation failed: {market_resp.status_code} - {market_resp.text}")
        sys.exit(1)
    print("✅ Profitability analysis calculated and stored successfully!")

    # 7. Create active sowing plan
    print("\n7. Launching active crop operations plan...")
    plan_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        headers=headers,
        json={
            "crop_name": "Tomato",
            "area_acres": 2.0,
            "planned_start_date": date.today().isoformat()
        }
    )
    if plan_resp.status_code != 201:
        print(f"❌ Farm plan creation failed: {plan_resp.status_code} - {plan_resp.text}")
        sys.exit(1)
    print("✅ Active crop operations plan registered successfully!")

    # 8. Generate risk early warnings
    print("\n8. Generating risk early warning scans...")
    risk_resp = client.post(f"{BASE_URL}/risk-intelligence/generate", headers=headers)
    if risk_resp.status_code != 201:
        print(f"❌ Risk warning scan failed: {risk_resp.status_code} - {risk_resp.text}")
        sys.exit(1)
    print("✅ Active hazard risk scan generated successfully!")

    # 9. Create analytics snapshot
    print("\n9. Capturing farm analytics snapshots...")
    snap_resp = client.post(f"{BASE_URL}/analytics/snapshot", headers=headers)
    if snap_resp.status_code != 200:
        print(f"❌ Snapshot capture failed: {snap_resp.status_code} - {snap_resp.text}")
        sys.exit(1)
    snapshot = snap_resp.json()
    print(f"✅ Snapshot recorded successfully! ID: {snapshot['id']}")
    print(f"  Health: {snapshot['health_score']} / Risk: {snapshot['risk_score']}")
    print(f"  Projected Profit: Rs. {snapshot['projected_profit']}")
    print(f"  Projected Yield: {snapshot['projected_yield']} kg")

    # 10. Verify KPIs
    print("\n10. Fetching real-time core KPIs...")
    kpis_resp = client.get(f"{BASE_URL}/analytics/kpis", headers=headers)
    if kpis_resp.status_code != 200:
        print(f"❌ KPIs fetch failed: {kpis_resp.status_code}")
        sys.exit(1)
    kpis = kpis_resp.json()
    assert kpis["health_score"] >= 0.0
    assert kpis["projected_profit"] > 0.0
    assert kpis["projected_yield"] > 0.0
    print("✅ Verified core dashboard KPIs successfully!")

    # 11. Verify Trends
    print("\n11. Fetching historical snapshots timeline...")
    trends_resp = client.get(f"{BASE_URL}/analytics/trends", headers=headers)
    if trends_resp.status_code != 200:
        print(f"❌ Trends fetch failed: {trends_resp.status_code}")
        sys.exit(1)
    trends = trends_resp.json()
    assert len(trends) >= 1
    print(f"✅ Verified trend timeline counts ({len(trends)} point(s)) successfully!")

    # 12. Verify report formats (PDF download & JSON payload)
    print("\n12. Exporting complete performance reports...")
    report_json_resp = client.get(f"{BASE_URL}/analytics/report?format=json", headers=headers)
    if report_json_resp.status_code != 200:
        print(f"❌ JSON report generation failed: {report_json_resp.status_code} - {report_json_resp.text}")
        sys.exit(1)
    report_json = report_json_resp.json()
    assert "kpis" in report_json
    assert len(report_json["yield_forecasts"]) >= 1
    assert len(report_json["profit_forecasts"]) >= 1
    print("✅ Verified JSON report payload schema successfully!")

    report_pdf_resp = client.get(f"{BASE_URL}/analytics/report?format=pdf", headers=headers)
    if report_pdf_resp.status_code != 200:
        print(f"❌ PDF report generation failed: {report_pdf_resp.status_code} - {report_pdf_resp.text}")
        sys.exit(1)
    assert report_pdf_resp.headers["content-type"] == "application/pdf"
    assert len(report_pdf_resp.content) > 0
    print(f"✅ Verified PDF report format size ({len(report_pdf_resp.content)} bytes) successfully!")

    # 13. Verify Dashboard Widget Endpoint
    print("\n13. Verifying main executive dashboard analytics data feed...")
    dash_resp = client.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    if dash_resp.status_code != 200:
        print(f"❌ Dashboard feed failed: {dash_resp.status_code}")
        sys.exit(1)
    dash = dash_resp.json()
    assert "kpis" in dash
    assert "insights" in dash
    assert len(dash["insights"]) > 0
    print("✅ Verified dashboard widget structure and automatic insights feed successfully!")

    print("\n🎉 All Sprint 12 Farm Analytics & Reports E2E Live Verification checks passed successfully!")


if __name__ == "__main__":
    verify_sprint12()
