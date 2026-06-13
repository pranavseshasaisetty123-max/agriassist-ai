import httpx
import sys
import uuid
from datetime import date

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint13():
    print("🚀 Starting Sprint 13 Multi-Farm & Portfolio Management E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s13_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Sanjay",
            "last_name": "Patel",
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
    print("✅ Logged in successfully!")

    # 3. Check profile initial state (should have no active_farm_id)
    print("\n3. Retrieving farmer profile details...")
    profile_resp = client.get(f"{BASE_URL}/farmers/me", headers=headers)
    if profile_resp.status_code != 200:
        print(f"❌ Failed to fetch profile: {profile_resp.status_code}")
        sys.exit(1)
    
    profile = profile_resp.json()
    assert profile["active_farm_id"] is None, "Expected active_farm_id to be None initially"
    print("✅ Verified initial active_farm_id is None.")

    # 4. Trigger self-healing fallback by hitting a context-aware service endpoint (e.g. GET /soil/reports)
    print("\n4. Triggering graceful default farm self-healing fallback...")
    soil_list_resp = client.get(f"{BASE_URL}/soil/reports", headers=headers)
    if soil_list_resp.status_code != 200:
        print(f"❌ Failed to fetch soil reports: {soil_list_resp.status_code} - {soil_list_resp.text}")
        sys.exit(1)
    
    # Now check if a farm was auto-created and activated
    profile_resp2 = client.get(f"{BASE_URL}/farmers/me", headers=headers)
    profile2 = profile_resp2.json()
    active_farm_id_1 = profile2["active_farm_id"]
    if not active_farm_id_1:
        print("❌ Self-healing fallback failed to set an active farm.")
        sys.exit(1)
    print(f"✅ Self-healing triggered successfully! Created and set active farm ID: {active_farm_id_1}")

    # Check that this farm actually exists and details match the default profile
    farm1_resp = client.get(f"{BASE_URL}/farms/{active_farm_id_1}", headers=headers)
    if farm1_resp.status_code != 200:
        print(f"❌ Failed to fetch self-healed farm: {farm1_resp.status_code}")
        sys.exit(1)
    farm1 = farm1_resp.json()
    assert farm1["name"] == "Primary Farm"
    assert farm1["total_area_acres"] == 10.0
    assert farm1["soil_type"] == "Loam"
    print("✅ Verified Primary Farm details successfully!")

    # 5. Create a second farm
    print("\n5. Creating a secondary farm...")
    farm2_resp = client.post(
        f"{BASE_URL}/farms",
        headers=headers,
        json={
            "name": "Riverside Orchard",
            "location": "Amritsar, Punjab",
            "total_area_acres": 15.5,
            "soil_type": "Clay",
            "latitude": 31.6340,
            "longitude": 74.8723
        }
    )
    if farm2_resp.status_code != 201:
        print(f"❌ Failed to create second farm: {farm2_resp.status_code} - {farm2_resp.text}")
        sys.exit(1)
    farm2 = farm2_resp.json()
    active_farm_id_2 = farm2["id"]
    print(f"✅ Secondary farm created successfully! ID: {active_farm_id_2}")

    # 6. List farms and verify we have exactly two farms
    print("\n6. Listing farmer's farms...")
    farms_list_resp = client.get(f"{BASE_URL}/farms", headers=headers)
    if farms_list_resp.status_code != 200:
        sys.exit(1)
    farms_list = farms_list_resp.json()
    assert len(farms_list) == 2
    print("✅ Verified two farms are listed.")

    # 7. Switch active farm to secondary farm
    print("\n7. Activating the secondary farm...")
    act_resp = client.post(f"{BASE_URL}/farms/{active_farm_id_2}/activate", headers=headers)
    if act_resp.status_code != 200:
        print(f"❌ Activation failed: {act_resp.status_code}")
        sys.exit(1)
    
    # Confirm profile updated active farm ID
    profile_resp3 = client.get(f"{BASE_URL}/farmers/me", headers=headers)
    assert profile_resp3.json()["active_farm_id"] == active_farm_id_2
    print("✅ Switch active farm context verification passed!")

    # 8. Create metrics under active farm contexts and verify portfolio aggregations
    print("\n8. Adding metrics to verify Portfolio KPI aggregations...")
    # Add soil report for Active Farm (Farm 2 - Riverside Orchard)
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.2,
            "nitrogen": 50.0,
            "phosphorus": 40.0,
            "potassium": 180.0,
            "organic_matter": 2.5,
            "crop_planned": "Wheat",
            "tested_at": date.today().isoformat()
        }
    )
    assert soil_resp.status_code == 201

    # Generate yield prediction for Active Farm (Farm 2)
    yield_resp = client.post(
        f"{BASE_URL}/yield-predictions/generate",
        headers=headers,
        json={"crop_name": "Wheat"}
    )
    if yield_resp.status_code == 201:
        print("✅ Yield prediction registered successfully!")
    elif yield_resp.status_code in (429, 503, 500) and ("unavailable" in yield_resp.text.lower() or "quota" in yield_resp.text.lower() or "limit" in yield_resp.text.lower()):
        print("⚠️ Gemini yield prediction rate-limited. Skipping live yield assertions.")
    else:
        print(f"❌ Yield prediction failed: {yield_resp.status_code} - {yield_resp.text}")
        sys.exit(1)

    # Generate crop operations plan for Active Farm (Farm 2)
    plan_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        headers=headers,
        json={
            "crop_name": "Wheat",
            "area_acres": 5.0,
            "planned_start_date": date.today().isoformat()
        }
    )
    if plan_resp.status_code == 201:
        print("✅ Active crop operations plan registered successfully!")
    elif plan_resp.status_code in (429, 503, 500) and ("unavailable" in plan_resp.text.lower() or "quota" in plan_resp.text.lower() or "limit" in plan_resp.text.lower()):
        print("⚠️ Gemini planner rate-limited. Skipping live planner assertions.")
    else:
        print(f"❌ Farm plan generation failed: {plan_resp.status_code} - {plan_resp.text}")
        sys.exit(1)

    # Add profitability analysis for farmer
    market_resp = client.post(
        f"{BASE_URL}/market-intelligence/calculate",
        headers=headers,
        json={
            "crop_name": "Wheat",
            "expected_yield": 3000.0,
            "cultivation_cost": 15000.0,
            "market_price_per_kg": 20.0
        }
    )
    assert market_resp.status_code == 201

    # Fetch portfolio
    print("\n9. Querying aggregate portfolio response...")
    port_resp = client.get(f"{BASE_URL}/farms/portfolio", headers=headers)
    if port_resp.status_code != 200:
        print(f"❌ Failed to fetch portfolio: {port_resp.status_code}")
        sys.exit(1)
    
    portfolio = port_resp.json()
    print("Aggregate portfolio KPIs retrieved:")
    print(f"  Total Farms: {portfolio['total_farms']}")
    print(f"  Total Area: {portfolio['total_area']} Acres")
    print(f"  Portfolio Profit: Rs. {portfolio['portfolio_profit']}")
    print(f"  Portfolio Yield: {portfolio['portfolio_yield']} kg")
    print(f"  Portfolio Risk: {portfolio['portfolio_risk']}%")
    print(f"  Active Plans: {portfolio['active_crop_plans']}")

    assert portfolio["total_farms"] == 2
    assert portfolio["total_area"] == 25.5
    assert portfolio["active_crop_plans"] >= 0
    assert portfolio["portfolio_profit"] >= 0.0
    assert portfolio["portfolio_yield"] >= 0.0
    print("✅ Verified portfolio aggregations successfully!")

    # 10. Update farm details
    print("\n10. Testing PUT update farm metadata...")
    up_resp = client.put(
        f"{BASE_URL}/farms/{active_farm_id_2}",
        headers=headers,
        json={
            "name": "Riverside Orchard Updated",
            "location": "Amritsar Rural, Punjab",
            "total_area_acres": 18.0
        }
    )
    if up_resp.status_code != 200:
        print(f"❌ Failed to update farm: {up_resp.status_code}")
        sys.exit(1)
    updated_farm = up_resp.json()
    assert updated_farm["name"] == "Riverside Orchard Updated"
    assert updated_farm["total_area_acres"] == 18.0
    print("✅ Verified farm PUT request successfully!")

    # 11. Delete a farm
    print("\n11. Testing DELETE farm...")
    del_resp = client.delete(f"{BASE_URL}/farms/{active_farm_id_1}", headers=headers)
    if del_resp.status_code != 200:
        print(f"❌ Failed to delete farm: {del_resp.status_code} - {del_resp.text}")
        sys.exit(1)
    print("✅ Farm deleted successfully!")

    # Final checks: list should now contain 1 farm, portfolio area should adjust
    farms_list_resp_final = client.get(f"{BASE_URL}/farms", headers=headers)
    assert len(farms_list_resp_final.json()) == 1

    port_resp_final = client.get(f"{BASE_URL}/farms/portfolio", headers=headers)
    final_portfolio = port_resp_final.json()
    assert final_portfolio["total_farms"] == 1
    assert final_portfolio["total_area"] == 18.0
    print("✅ Final E2E checks verified clean deletion and updated totals.")

    print("\n🎉 All Sprint 13 Multi-Farm & Portfolio Management E2E Live Verification checks passed successfully!")


if __name__ == "__main__":
    verify_sprint13()
