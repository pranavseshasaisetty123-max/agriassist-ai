import httpx
import sys
import uuid
from datetime import date

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint9():
    print("🚀 Starting Sprint 9 Pest & Disease Risk Warning System E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s9_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Ramesh",
            "last_name": "Sharma",
            "location": "Punjab, India"
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

    # 3. Test check: generate risk alerts before creating a crop plan (should fail with HTTP 400)
    print("\n3. Testing risk warnings generation rejection when no active crop plan exists...")
    fail_resp = client.post(
        f"{BASE_URL}/risk-intelligence/generate",
        headers=headers
    )
    if fail_resp.status_code == 400 and "Please create a crop plan before generating risk intelligence." in fail_resp.text:
        print("✅ Correctly rejected: Please create a crop plan before generating risk intelligence.")
    else:
        print(f"❌ Rejection check failed, status: {fail_resp.status_code} - {fail_resp.text}")
        sys.exit(1)

    # 4. Create a Soil Report
    print("\n4. Creating soil report...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.5,
            "nitrogen": 48.0,
            "phosphorus": 32.0,
            "potassium": 190.0,
            "organic_matter": 2.1,
            "crop_planned": "Tomato",
            "tested_at": "2026-06-12"
        }
    )
    if soil_resp.status_code != 201:
        print(f"❌ Failed to create soil report: {soil_resp.status_code} - {soil_resp.text}")
        sys.exit(1)
    print("✅ Soil report registered successfully!")

    # 5. Create an active Crop Operations Plan for Tomato
    print("\n5. Generating Crop Operations Plan for Tomato...")
    start_date = date.today().isoformat()
    plan_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.5,
            "planned_start_date": start_date
        },
        headers=headers
    )
    if plan_resp.status_code != 201:
        print(f"❌ Farm plan generation failed: {plan_resp.status_code} - {plan_resp.text}")
        sys.exit(1)
    print("✅ Farm plan registered successfully!")

    # 6. Generate Risk Warnings
    print("\n6. Running AI Risk Assessment Warning Scan...")
    risk_resp = client.post(
        f"{BASE_URL}/risk-intelligence/generate",
        headers=headers
    )
    if risk_resp.status_code != 201:
         print(f"❌ Risk warning scan generation failed: {risk_resp.status_code} - {risk_resp.text}")
         sys.exit(1)

    risk_assessment = risk_resp.json()
    print("✅ Risk early warning assessment generated successfully!")
    print(f"  Overall Risk Score:  {risk_assessment['overall_risk_score']}/100")
    print(f"  Overall Risk Level:  {risk_assessment['risk_level']}")
    print(f"  Total Alerts Found:  {len(risk_assessment['alerts'])}")
    print("=======================================")

    alerts = risk_assessment["alerts"]
    if not alerts:
        print("❌ Generated risk warning alerts list is empty!")
        sys.exit(1)

    for i, alert in enumerate(alerts, 1):
        print(f"  Alert {i}:")
        print(f"    Title:       {alert['alert_title']}")
        print(f"    Category:    {alert['category']}")
        print(f"    Severity:    {alert['severity']}")
        print(f"    Probability: {alert['probability']}%")
        print(f"    Description: {alert['description']}")

    # 7. Get Latest Warnings
    print("\n7. Retrieving latest active warnings status...")
    latest_resp = client.get(
        f"{BASE_URL}/risk-intelligence/warnings",
        headers=headers
    )
    if latest_resp.status_code != 200:
        print(f"❌ Failed to retrieve latest warnings: {latest_resp.status_code} - {latest_resp.text}")
        sys.exit(1)
    latest_assessment = latest_resp.json()
    print(f"✅ Latest warnings retrieved successfully! Score matches: {latest_assessment['overall_risk_score'] == risk_assessment['overall_risk_score']}")

    # 8. Retrieve History
    print("\n8. Retrieving risk alerts scan history logs...")
    history_resp = client.get(
        f"{BASE_URL}/risk-intelligence/history",
        headers=headers
    )
    if history_resp.status_code != 200:
        print(f"❌ Failed to retrieve risk history: {history_resp.status_code} - {history_resp.text}")
        sys.exit(1)
    
    history_list = history_resp.json()
    print(f"✅ Risk history retrieved successfully! Total logged alerts in DB: {len(history_list)}")
    
    print("\n🎉 All Sprint 9 Pest & Disease Risk Warning System E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint9()
