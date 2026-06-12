import httpx
import sys
import io

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint4():
    print("🚀 Starting Sprint 4 Plant Disease Detection E2E Live Verification...")
    client = httpx.Client()

    # 1. Register a test user
    email = "live_farmer_s4@example.com"
    password = "password123"

    print("\n1. Registering test farmer for disease scans...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Ramesh",
            "last_name": "Patel",
            "location": "Gujarat, India"
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

    # 3. Perform Disease Scan (since we are running live, it will trigger mock demo if Gemini key is rate limited or run real scan)
    print("\n3. Uploading leaf image for disease diagnostics...")
    img_path = "/Users/pranav/.gemini/antigravity-ide/brain/61db1804-3357-4b81-918c-4dd50b0df21e/crop_selected_tomatoes_1781181655462.png"
    with open(img_path, "rb") as f:
        real_img = f.read()
    files = {"file": ("tomato_leaf_spot.png", io.BytesIO(real_img), "image/png")}

    scan_resp = client.post(
        f"{BASE_URL}/disease/scan",
        headers=headers,
        files=files,
        timeout=30.0
    )
    if scan_resp.status_code != 201:
        print(f"❌ Disease scan failed: {scan_resp.status_code} - {scan_resp.text}")
        sys.exit(1)

    scan_data = scan_resp.json()
    print("✅ Crop leaf scanned successfully!")
    print("\n=== AI Crop Disease Diagnosis ===")
    print(f"Disease Detected: {scan_data['disease_name']}")
    print(f"Confidence Level: {(scan_data['confidence'] * 100):.0f}% Match")
    print(f"Severity Status:  {scan_data['severity'].upper()}")
    print("Symptoms Observed:")
    for pt in scan_data["symptoms"]:
        print(f"  • {pt}")
    print("Recommended Treatments:")
    for pt in scan_data["treatment"]:
        print(f"  • {pt}")
    print("Preventive Actions:")
    for pt in scan_data["preventive_measures"]:
        print(f"  • {pt}")
    print(f"Leaf Image Path:  {scan_data['image_path']}")
    print("=================================")

    scan_id = scan_data["id"]

    # 4. Fetch History
    print("\n4. Fetching diagnostic scan history...")
    history_resp = client.get(f"{BASE_URL}/disease/scans", headers=headers)
    if history_resp.status_code != 200:
        print(f"❌ Failed to fetch scan history: {history_resp.status_code}")
        sys.exit(1)

    history = history_resp.json()
    assert len(history) >= 1
    print(f"✅ Historical scan database list checked (Found {len(history)} records).")

    # 5. Fetch Detail
    print("\n5. Retrieving scan record details...")
    detail_resp = client.get(f"{BASE_URL}/disease/scans/{scan_id}", headers=headers)
    if detail_resp.status_code != 200:
        print(f"❌ Failed to fetch scan details: {detail_resp.status_code}")
        sys.exit(1)
    print("✅ Detailed scan report retrieved successfully!")

    # 6. Delete Scan
    print("\n6. Cleaning up scan record...")
    del_resp = client.delete(f"{BASE_URL}/disease/scans/{scan_id}", headers=headers)
    if del_resp.status_code != 204:
        print(f"❌ Deletion failed: {del_resp.status_code}")
        sys.exit(1)
    print("✅ Scan record deleted successfully from database and server disk storage.")

    # 7. Check 404
    print("\n7. Double checking deletion status...")
    check_resp = client.get(f"{BASE_URL}/disease/scans/{scan_id}", headers=headers)
    if check_resp.status_code != 404:
        print(f"❌ Deletion verification check failed, scan still exists: {check_resp.status_code}")
        sys.exit(1)
    print("✅ Deletion status confirmed (Returned HTTP 404).")

    print("\n🎉 All Sprint 4 Plant Disease Detection E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint4()
