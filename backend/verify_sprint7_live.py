import httpx
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint7():
    print("🚀 Starting Sprint 7 Crop Yield Prediction Engine E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s7_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Ramesh",
            "last_name": "Kumar",
            "location": "Haryana, India"
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

    # 3. Test check: generate before logging a soil report
    print("\n3. Testing prediction block when no soil report is present...")
    fail_resp = client.post(f"{BASE_URL}/yield-predictions/generate", json={"crop_name": "Wheat"}, headers=headers)
    if fail_resp.status_code == 400 and "log a soil test report first" in fail_resp.text:
        print("✅ Correctly rejected request: please log soil report first.")
    else:
        print(f"❌ Rejection check failed, status: {fail_resp.status_code} - {fail_resp.text}")
        sys.exit(1)

    # 4. Create a Soil Report
    print("\n4. Creating soil report for ramesh...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.8,
            "nitrogen": 45.0,
            "phosphorus": 32.0,
            "potassium": 200.0,
            "organic_matter": 2.0,
            "crop_planned": "Wheat",
            "tested_at": "2026-06-12"
        }
    )
    if soil_resp.status_code != 201:
        print(f"❌ Failed to create soil report: {soil_resp.status_code} - {soil_resp.text}")
        sys.exit(1)
    print("✅ Soil report registered successfully!")

    # 5. Generate Crop Yield Prediction (Calls Gemini or fallback Mock Demo)
    print("\n5. Generating Yield Prediction for Wheat...")
    gen_resp = client.post(
        f"{BASE_URL}/yield-predictions/generate",
        json={"crop_name": "Wheat"},
        headers=headers,
        timeout=60.0
    )
    if gen_resp.status_code != 201:
        print(f"❌ Yield prediction generation failed: {gen_resp.status_code} - {gen_resp.text}")
        sys.exit(1)

    prediction = gen_resp.json()
    print("✅ Crop yield predicted successfully!")
    print("\n=== AI Yield Prediction Statistics ===")
    print(f"  Crop:                {prediction['crop_name']}")
    print(f"  Predicted Yield:     {prediction['predicted_yield']} kg/acre")
    print(f"  Confidence Score:    {prediction['confidence_score']}%")
    print(f"  Yield Category:      {prediction['yield_category']}")
    print(f"  Key Factors:         {', '.join(prediction['prediction_factors'])}")
    print(f"  Advice:              {', '.join(prediction['recommendations'])}")
    print("=======================================")

    # 6. Retrieve History
    print("\n6. Fetching prediction history...")
    history_resp = client.get(f"{BASE_URL}/yield-predictions/", headers=headers)
    if history_resp.status_code != 200:
        print(f"❌ Failed to retrieve history: {history_resp.status_code}")
        sys.exit(1)
    
    history_list = history_resp.json()
    assert len(history_list) >= 1
    print(f"✅ History retrieved successfully (Found {len(history_list)} items).")

    # 7. Fetch specific prediction detail
    pred_id = prediction["id"]
    print(f"\n7. Retrieving details for prediction ID {pred_id}...")
    detail_resp = client.get(f"{BASE_URL}/yield-predictions/{pred_id}", headers=headers)
    if detail_resp.status_code != 200:
        print(f"❌ Failed to fetch details: {detail_resp.status_code}")
        sys.exit(1)
    
    detail = detail_resp.json()
    assert detail["crop_name"] == prediction["crop_name"]
    print(f"✅ Yield prediction details retrieved successfully: {detail['crop_name']} estimation confirmed.")

    print("\n🎉 All Sprint 7 Crop Yield Prediction Engine E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint7()
