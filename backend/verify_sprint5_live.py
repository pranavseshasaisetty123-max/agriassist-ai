import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint5():
    print("🚀 Starting Sprint 5 Smart Crop Recommendation Engine E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    import uuid
    email = f"live_farmer_s5_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "location": "Punjab, India"
        }
    )
    if reg_resp.status_code in (200, 201):
        print("✅ Farmer registered successfully!")
    elif reg_resp.status_code == 400 and ("already" in reg_resp.text or "exists" in reg_resp.text):
        print("ℹ️ Farmer already registered, proceeding to login.")
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

    # 3. Test validation check: request generate before logging a soil report
    print("\n3. Testing recommendation block when no soil report is present...")
    fail_resp = client.post(f"{BASE_URL}/crop-recommendations/generate", headers=headers)
    if fail_resp.status_code == 400 and "log a soil test report first" in fail_resp.text:
        print("✅ Correctly rejected recommendation request with warning: please log soil report first.")
    else:
        print(f"❌ Rejection check failed, status: {fail_resp.status_code} - {fail_resp.text}")
        sys.exit(1)

    # 4. Create a Soil Report
    print("\n4. Creating soil report for rajesh...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.8,
            "nitrogen": 35.0,
            "phosphorus": 28.0,
            "potassium": 180.0,
            "organic_matter": 1.8,
            "crop_planned": "Cotton",
            "tested_at": "2026-06-12"
        }
    )
    if soil_resp.status_code != 201:
        print(f"❌ Failed to create soil report: {soil_resp.status_code} - {soil_resp.text}")
        sys.exit(1)
    print("✅ Soil report registered successfully!")

    # 5. Generate Crop Recommendations (Will call Gemini or return Mock Demo if rate limited)
    print("\n5. Generating Smart Crop Recommendations...")
    gen_resp = client.post(
        f"{BASE_URL}/crop-recommendations/generate",
        headers=headers,
        timeout=60.0
    )
    if gen_resp.status_code != 201:
        print(f"❌ Crop recommendations generation failed: {gen_resp.status_code} - {gen_resp.text}")
        sys.exit(1)

    recommendations = gen_resp.json()
    print("✅ Crop recommendations generated successfully!")
    print("\n=== AI Smart Crop Recommendations ===")
    for idx, item in enumerate(recommendations):
        print(f"\n#{idx+1}: {item['crop_name']} ({item['suitability_score']}% Match)")
        print(f"  Season:      {item['season']}")
        print(f"  Why:         {item['recommendation_reason']}")
        print(f"  Risks:       {', '.join(item['risk_factors'])}")
        print(f"  Tips:        {', '.join(item['farming_tips'])}")
    print("\n=====================================")

    # 6. Retrieve History
    print("\n6. Fetching recommendation history...")
    history_resp = client.get(f"{BASE_URL}/crop-recommendations", headers=headers)
    if history_resp.status_code != 200:
        print(f"❌ Failed to retrieve history: {history_resp.status_code}")
        sys.exit(1)
    
    history_list = history_resp.json()
    assert len(history_list) >= 5
    print(f"✅ History retrieved successfully (Found {len(history_list)} items).")

    # 7. Fetch specific recommendation detail
    rec_id = recommendations[0]["id"]
    print(f"\n7. Retrieving details for recommendation ID {rec_id}...")
    detail_resp = client.get(f"{BASE_URL}/crop-recommendations/{rec_id}", headers=headers)
    if detail_resp.status_code != 200:
        print(f"❌ Failed to fetch details: {detail_resp.status_code}")
        sys.exit(1)
    
    detail = detail_resp.json()
    assert detail["crop_name"] == recommendations[0]["crop_name"]
    print(f"✅ Recommendation detail retrieved successfully: {detail['crop_name']} match confirmed.")

    print("\n🎉 All Sprint 5 Smart Crop Recommendation Engine E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint5()
