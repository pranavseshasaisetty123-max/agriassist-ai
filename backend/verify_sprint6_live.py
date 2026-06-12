import httpx
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint6():
    print("🚀 Starting Sprint 6 Market Price Intelligence & Profitability Engine E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s6_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Sanjay",
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

    # 3. Fetch current market intelligence
    print("\n3. Fetching market prices for Tomato...")
    prices_resp = client.get(f"{BASE_URL}/market-intelligence/prices?crop_name=Tomato", headers=headers)
    if prices_resp.status_code != 200:
        print(f"❌ Failed to fetch crop prices: {prices_resp.status_code} - {prices_resp.text}")
        sys.exit(1)
        
    prices_data = prices_resp.json()
    print("✅ Market prices fetched successfully!")
    print(f"  Crop:           {prices_data['crop_name']}")
    print(f"  Average Price:  ₹{prices_data['average_price']}/kg")
    print(f"  State Averages: {', '.join([f'{sa['state']}: ₹{sa['price_per_kg']}' for sa in prices_data['state_averages']])}")
    print(f"  Top Markets:    {', '.join([f'{tm['market_name']}: ₹{tm['price_per_kg']}' for tm in prices_data['top_markets'][:3]])}")

    # 4. Fetch price trends
    print("\n4. Fetching 30-day price trends for Tomato...")
    trends_resp = client.get(f"{BASE_URL}/market-intelligence/trends?crop_name=Tomato&days=30", headers=headers)
    if trends_resp.status_code != 200:
        print(f"❌ Failed to fetch price trends: {trends_resp.status_code} - {trends_resp.text}")
        sys.exit(1)
        
    trends_data = trends_resp.json()
    print(f"✅ Price trends retrieved successfully! Found {len(trends_data)} data points.")

    # 5. Calculate profitability with custom price
    print("\n5. Testing calculator with custom market price...")
    calc_payload_1 = {
        "crop_name": "Tomato",
        "expected_yield": 1500.0,
        "cultivation_cost": 22000.0,
        "market_price_per_kg": 30.0
    }
    calc_resp_1 = client.post(f"{BASE_URL}/market-intelligence/calculate", json=calc_payload_1, headers=headers)
    if calc_resp_1.status_code != 201:
        print(f"❌ Calculator failed with custom price: {calc_resp_1.status_code} - {calc_resp_1.text}")
        sys.exit(1)
        
    res_1 = calc_resp_1.json()
    # Revenue = 1500 * 30 = 45000
    # Profit = 45000 - 22000 = 23000
    # Margin = 23000 / 45000 * 100 = 51.11%
    assert res_1["estimated_revenue"] == 45000.0
    assert res_1["estimated_profit"] == 23000.0
    assert abs(res_1["profit_margin"] - 51.11) < 0.1
    print("✅ Calculator verified successfully with custom price parameters:")
    print(f"  Revenue: ₹{res_1['estimated_revenue']} | Profit: ₹{res_1['estimated_profit']} | Margin: {res_1['profit_margin']}%")

    # 6. Calculate profitability using default DB average price
    print("\n6. Testing calculator with default database fallback price...")
    calc_payload_2 = {
        "crop_name": "Tomato",
        "expected_yield": 1000.0,
        "cultivation_cost": 15000.0
    }
    calc_resp_2 = client.post(f"{BASE_URL}/market-intelligence/calculate", json=calc_payload_2, headers=headers)
    if calc_resp_2.status_code != 201:
        print(f"❌ Calculator failed with fallback price: {calc_resp_2.status_code} - {calc_resp_2.text}")
        sys.exit(1)
        
    res_2 = calc_resp_2.json()
    print("✅ Calculator verified successfully with fallback DB average price:")
    print(f"  Resolved Price: ₹{res_2['market_price_per_kg']}/kg")
    print(f"  Revenue: ₹{res_2['estimated_revenue']} | Profit: ₹{res_2['estimated_profit']} | Margin: {res_2['profit_margin']}%")

    # 7. Fetch history list
    print("\n7. Fetching profitability calculations history...")
    history_resp = client.get(f"{BASE_URL}/market-intelligence/history", headers=headers)
    if history_resp.status_code != 200:
        print(f"❌ Failed to fetch calculation history: {history_resp.status_code}")
        sys.exit(1)
        
    history_data = history_resp.json()
    assert len(history_data) >= 2
    print(f"✅ History retrieved successfully! Found {len(history_data)} logged calculations.")

    # 8. Fetch single calculation detail
    analysis_id = res_1["id"]
    print(f"\n8. Retrieving detail for analysis ID {analysis_id}...")
    detail_resp = client.get(f"{BASE_URL}/market-intelligence/analysis/{analysis_id}", headers=headers)
    if detail_resp.status_code != 200:
        print(f"❌ Failed to retrieve analysis detail: {detail_resp.status_code}")
        sys.exit(1)
        
    detail = detail_resp.json()
    assert detail["crop_name"] == "Tomato"
    assert detail["estimated_profit"] == 23000.0
    print("✅ Analysis detail fetched successfully!")

    # 9. Explain trends using Gemini
    print("\n9. Requesting AI explanation for price trends...")
    explain_payload = {
        "crop_name": "Tomato",
        "trends": trends_data[:5]  # Send first 5 points for simplicity
    }
    explain_resp = client.post(f"{BASE_URL}/market-intelligence/explain-trends", json=explain_payload, headers=headers)
    if explain_resp.status_code != 200:
        print(f"❌ AI explain endpoint failed: {explain_resp.status_code} - {explain_resp.text}")
        sys.exit(1)
        
    explanation = explain_resp.json()["explanation"]
    print("✅ AI Trend advisory returned successfully!")
    print("\n=== AI Agronomist Trend Summary ===")
    print(explanation)
    print("====================================")

    print("\n🎉 All Sprint 6 Market Price Intelligence & Profitability Engine E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint6()
