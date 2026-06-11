import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def verify_sprint3():
    print("🚀 Starting Sprint 3 Weather & Advisory E2E Live Verification...")
    client = httpx.Client()
    
    # 1. Register a test user with a specific agricultural location
    email = "live_farmer_s3@example.com"
    password = "password123"
    location = "Ludhiana, Punjab, India"
    
    print("\n1. Registering test farmer in Ludhiana, Punjab...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Sukhwinder",
            "last_name": "Singh",
            "location": location,
            "contact_number": "9876543211"
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
    
    # 3. Log Soil Report (necessary prerequisite for smart advisories)
    print("\n3. Logging soil test report (crop planned: Rice)...")
    report_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.4,
            "nitrogen": 35.0,
            "phosphorus": 18.0,
            "potassium": 130.0,
            "organic_matter": 2.8,
            "crop_planned": "Rice",
            "tested_at": "2026-06-11"
        }
    )
    if report_resp.status_code != 201:
        print(f"❌ Logging report failed: {report_resp.status_code} - {report_resp.text}")
        sys.exit(1)
    print("✅ Soil report logged successfully!")

    # 4. Fetch Current Weather
    print("\n4. Querying current weather endpoint...")
    weather_resp = client.get(
        f"{BASE_URL}/weather/current",
        headers=headers
    )
    if weather_resp.status_code != 200:
        print(f"❌ Current weather retrieval failed: {weather_resp.status_code} - {weather_resp.text}")
        sys.exit(1)
    
    weather = weather_resp.json()
    print("✅ Current weather fetched successfully!")
    print(f"   Location: {weather['location']}")
    print(f"   Coordinates: {weather['latitude']}, {weather['longitude']}")
    print(f"   Temperature: {weather['current_temp']}°C, Condition: {weather['current_condition']}")
    
    # 5. Fetch Weather Forecast
    print("\n5. Querying 7-day forecast daily summaries...")
    forecast_resp = client.get(
        f"{BASE_URL}/weather/forecast",
        headers=headers
    )
    if forecast_resp.status_code != 200:
        print(f"❌ Forecast retrieval failed: {forecast_resp.status_code} - {forecast_resp.text}")
        sys.exit(1)
        
    forecast = forecast_resp.json()
    print("✅ 7-Day forecast fetched successfully!")
    for item in forecast["forecast"][:3]:
        print(f"   - {item['date']}: {item['condition']} (Min: {item['temp_min']}°C, Max: {item['temp_max']}°C)")
    print("   ...")
    
    # 6. Trigger AI-Powered Smart Farming Advisory (Gemini + Weather + Soil)
    print("\n6. Generating AI weather-soil smart crop advisory...")
    advisory_resp = client.get(
        f"{BASE_URL}/weather/advisory",
        headers=headers,
        timeout=30.0
    )
    if advisory_resp.status_code != 200:
        print(f"❌ AI Advisory failed: {advisory_resp.status_code} - {advisory_resp.text}")
        sys.exit(1)
        
    advisory = advisory_resp.json()
    print("✅ AI Smart Advisory retrieved successfully!")
    print("\n=== AI Agronomist Smart Weather-Crop Advisory ===")
    print(f"Planned Crop: {advisory['crop']}")
    print(f"Advisory Severity Level: {advisory['severity'].upper()}")
    print("Advisory Action Points:")
    for point in advisory["advisory_points"]:
        print(f"  • {point}")
    print("==================================================")
    print("\n🎉 All Sprint 3 weather and advisory live checks passed!")

if __name__ == "__main__":
    verify_sprint3()
