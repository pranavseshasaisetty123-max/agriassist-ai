import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def verify_e2e():
    print("🚀 Starting Sprint 2 E2E Live Verification...")
    client = httpx.Client()
    
    # 1. Register a test user
    email = "live_farmer@example.com"
    password = "password123"
    
    print("\n1. Registering test farmer...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "location": "Punjab, India",
            "contact_number": "9876543210"
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
    
    # 3. Log Soil Report
    print("\n3. Logging new soil test report...")
    report_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.8,
            "nitrogen": 45.0,
            "phosphorus": 22.0,
            "potassium": 140.0,
            "organic_matter": 3.0,
            "crop_planned": "Tomatoes",
            "tested_at": "2026-06-11"
        }
    )
    if report_resp.status_code != 201:
        print(f"❌ Logging report failed: {report_resp.status_code} - {report_resp.text}")
        sys.exit(1)
        
    report = report_resp.json()
    report_id = report["id"]
    print(f"✅ Soil report logged successfully! Report ID: {report_id}")
    print(f"   pH: {report['ph']}, N: {report['nitrogen']}, P: {report['phosphorus']}, K: {report['potassium']}")
    
    # 4. Trigger AI Analysis
    print("\n4. Triggering AI Agronomist recommendations (calling Gemini)...")
    analysis_resp = client.post(
        f"{BASE_URL}/soil/reports/{report_id}/analyze",
        headers=headers,
        timeout=30.0
    )
    if analysis_resp.status_code != 200:
        print(f"❌ AI Analysis failed: {analysis_resp.status_code} - {analysis_resp.text}")
        sys.exit(1)
        
    recommendation = analysis_resp.json()
    print("✅ AI Recommendations retrieved and saved successfully!")
    print("\n=== Gemini Structured Output Results ===")
    print(f"Nitrogen Recommendation:\n{recommendation['nitrogen_recommendation']}\n")
    print(f"Phosphorus Recommendation:\n{recommendation['phosphorus_recommendation']}\n")
    print(f"Potassium Recommendation:\n{recommendation['potassium_recommendation']}\n")
    print(f"Fertilizer Treatment Schedule:\n{recommendation['fertilizer_schedule']}\n")
    print(f"Diagnostics Summary:\n{recommendation['ai_raw_analysis']}\n")
    print("========================================")
    
    # 5. Fetch report details again to confirm relation loading
    print("\n5. Verifying report details fetch with nested recommendation...")
    get_resp = client.get(
        f"{BASE_URL}/soil/reports/{report_id}",
        headers=headers
    )
    if get_resp.status_code != 200:
        print(f"❌ Failed to fetch report details: {get_resp.status_code} - {get_resp.text}")
        sys.exit(1)
        
    nested_report = get_resp.json()
    assert nested_report["recommendation"] is not None
    assert nested_report["recommendation"]["nitrogen_recommendation"] == recommendation["nitrogen_recommendation"]
    print("✅ Nested relationship verified successfully!")
    print("\n🎉 All live checks passed successfully!")

if __name__ == "__main__":
    verify_e2e()
