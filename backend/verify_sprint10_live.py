import httpx
import sys
import uuid
from datetime import date

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint10():
    print("🚀 Starting Sprint 10 Unified AI Farm Consultant E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s10_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Ramesh",
            "last_name": "Kumar",
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

    # 3. Create a Soil Report
    print("\n3. Creating soil report...")
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

    # 4. Generate Crop Recommendations
    print("\n4. Running crop recommendations engine...")
    recs_resp = client.post(
        f"{BASE_URL}/crop-recommendations/generate",
        headers=headers
    )
    if recs_resp.status_code not in (200, 201):
        print(f"❌ Crop recommendations failed: {recs_resp.status_code} - {recs_resp.text}")
        sys.exit(1)
    print("✅ Crop recommendations compiled successfully!")

    # 5. Generate Yield Prediction
    print("\n5. Generating yield prediction for Tomato...")
    yield_resp = client.post(
        f"{BASE_URL}/yield-predictions/generate",
        headers=headers,
        json={"crop_name": "Tomato"}
    )
    if yield_resp.status_code not in (200, 201):
        print(f"❌ Yield prediction failed: {yield_resp.status_code} - {yield_resp.text}")
        sys.exit(1)
    print("✅ Crop yield predictions compiled successfully!")

    # 6. Generate Market Intelligence (Profitability Analysis)
    print("\n6. Running market price profitability analysis for Tomato...")
    market_resp = client.post(
        f"{BASE_URL}/market-intelligence/calculate",
        headers=headers,
        json={
            "crop_name": "Tomato",
            "expected_yield": 2000.0,
            "cultivation_cost": 15000.0
        }
    )
    if market_resp.status_code not in (200, 201):
        print(f"❌ Profitability analysis failed: {market_resp.status_code} - {market_resp.text}")
        sys.exit(1)
    print("✅ Market price profitability analysis compiled successfully!")

    # 7. Generate active Crop Operations Plan for Tomato
    print("\n7. Generating Crop Operations Plan for Tomato...")
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

    # 8. Generate Risk Warnings
    print("\n8. Running AI Risk Assessment Warning Scan...")
    risk_resp = client.post(
        f"{BASE_URL}/risk-intelligence/generate",
        headers=headers
    )
    if risk_resp.status_code != 201:
         print(f"❌ Risk warning scan generation failed: {risk_resp.status_code} - {risk_resp.text}")
         sys.exit(1)
    print("✅ Risk warning assessment generated successfully!")

    # 9. Ask Virtual Agronomist Consultant
    print("\n9. Invoking Unified AI Farm Consultant (Virtual Agronomist)...")
    consult_resp = client.post(
        f"{BASE_URL}/consult-agent/ask",
        headers=headers,
        json={"question": "Should I cultivate tomato this season?"}
    )
    if consult_resp.status_code not in (200, 201):
        print(f"❌ Consultant query failed: {consult_resp.status_code} - {consult_resp.text}")
        sys.exit(1)

    consult_data = consult_resp.json()
    print("✅ Consultation result returned successfully!")
    print(f"  Farm Health Score:     {consult_data['farm_health_score']}/100")
    print(f"  Health Summary:        {consult_data['health_summary']}")
    print(f"  Confidence Score:      {consult_data['confidence_score']}% certainty")
    print(f"  Risk Assessment:       {consult_data['risk_assessment']}")
    print(f"  Top Recommendations:   {consult_data['recommended_actions']}")
    print(f"  Key Findings:          {consult_data['key_findings']}")
    print(f"  Detailed Advice:       {consult_data['answer']}")
    print("========================================================================")

    # Validate output schema properties
    assert "farm_health_score" in consult_data
    assert "answer" in consult_data
    assert isinstance(consult_data["key_findings"], list)
    assert isinstance(consult_data["recommended_actions"], list)

    # 10. Verify history logs
    print("\n10. Fetching agronomist consulting history logs...")
    history_resp = client.get(
        f"{BASE_URL}/consult-agent/history",
        headers=headers
    )
    if history_resp.status_code != 200:
        print(f"❌ History logs retrieval failed: {history_resp.status_code}")
        sys.exit(1)
    
    history_list = history_resp.json()
    print(f"✅ History retrieved successfully! Total logs in DB: {len(history_list)}")
    
    # 11. Retrieve detail log
    consult_id = history_list[0]["id"]
    print(f"\n11. Retrieving details for consultation ID {consult_id}...")
    detail_resp = client.get(
        f"{BASE_URL}/consult-agent/{consult_id}",
        headers=headers
    )
    if detail_resp.status_code != 200:
        print(f"❌ Detail retrieval failed: {detail_resp.status_code}")
        sys.exit(1)
    
    detail_data = detail_resp.json()
    print(f"✅ Detail log retrieved successfully! Health score matched: {detail_data['farm_health_score'] == consult_data['farm_health_score']}")

    print("\n🎉 All Sprint 10 Unified AI Farm Consultant E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint10()
