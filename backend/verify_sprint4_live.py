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

    # 3. Perform Valid Disease Scan (using generated tomato leaf image)
    print("\n3. Uploading realistic leaf image for disease diagnostics...")
    img_path = "/Users/pranav/.gemini/antigravity-ide/brain/61db1804-3357-4b81-918c-4dd50b0df21e/tomato_leaf_spot_1781229720140.png"
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
    print(f"Diagnosis Type:   {scan_data['diagnosis_type']}")
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

    # 4. Verification: Fetch Private Image Authenticated vs Unauthenticated
    print("\n4. Testing private authenticated image endpoint...")
    image_url = f"{BASE_URL}{scan_data['image_path']}"
    
    # 4a. Fetch as owner (Should return 200 OK)
    owner_img_resp = client.get(image_url, headers=headers)
    if owner_img_resp.status_code != 200:
        print(f"❌ Failed to fetch image as owner: {owner_img_resp.status_code}")
        sys.exit(1)
    print("✅ Successfully fetched private image as the owner (HTTP 200 OK).")

    # 4b. Fetch without token (Should return 401 Unauthorized)
    anon_img_resp = client.get(image_url)
    if anon_img_resp.status_code != 401:
        print(f"❌ Failed security check: anonymous fetch returned {anon_img_resp.status_code}")
        sys.exit(1)
    print("✅ Secure: Anonymous request blocked (HTTP 401 Unauthorized).")

    # 5. Verification: Non-plant/screenshot image safety rejection
    print("\n5. Testing non-plant image rejection safety check...")
    unrelated_img_path = "/Users/pranav/.gemini/antigravity-ide/brain/61db1804-3357-4b81-918c-4dd50b0df21e/crop_selected_tomatoes_1781181655462.png"
    with open(unrelated_img_path, "rb") as f:
        unrelated_img = f.read()
    
    bad_files = {"file": ("ui_screenshot.png", io.BytesIO(unrelated_img), "image/png")}
    bad_scan_resp = client.post(
        f"{BASE_URL}/disease/scan",
        headers=headers,
        files=bad_files,
        timeout=30.0
    )
    if bad_scan_resp.status_code == 400:
        print("✅ Success: Unrelated/non-plant image correctly rejected by backend!")
        print(f"   Received Warning Message: {bad_scan_resp.json()['detail']}")
    else:
        print(f"❌ Safety check failed: Non-plant image was not rejected. Code: {bad_scan_resp.status_code} - {bad_scan_resp.text}")
        sys.exit(1)

    # 6. Verification: Validation checks (File format / Size checks)
    print("\n6. Testing file extension and size validation limits...")
    
    # 6a. Format validation check (gif should fail with 400)
    gif_files = {"file": ("test.gif", io.BytesIO(b"fake gif bytes"), "image/gif")}
    gif_resp = client.post(f"{BASE_URL}/disease/scan", headers=headers, files=gif_files)
    if gif_resp.status_code == 400:
        print("✅ Success: Invalid file extension rejected (HTTP 400).")
    else:
        print(f"❌ Format validation check failed, status: {gif_resp.status_code}")
        sys.exit(1)

    # 6b. Size validation check (>5MB should fail with 400)
    huge_data = b"0" * (5 * 1024 * 1024 + 1024)
    huge_files = {"file": ("large.png", io.BytesIO(huge_data), "image/png")}
    huge_resp = client.post(f"{BASE_URL}/disease/scan", headers=headers, files=huge_files)
    if huge_resp.status_code == 400:
        print("✅ Success: Over-sized image file (>5MB) rejected (HTTP 400).")
    else:
        print(f"❌ Size validation check failed, status: {huge_resp.status_code}")
        sys.exit(1)

    # 7. Fetch History
    print("\n7. Fetching diagnostic scan history...")
    history_resp = client.get(f"{BASE_URL}/disease/scans", headers=headers)
    if history_resp.status_code != 200:
        print(f"❌ Failed to fetch scan history: {history_resp.status_code}")
        sys.exit(1)

    history = history_resp.json()
    assert len(history) >= 1
    print(f"✅ Historical scan database list checked (Found {len(history)} records).")

    # 8. Fetch Detail
    print("\n8. Retrieving scan record details...")
    detail_resp = client.get(f"{BASE_URL}/disease/scans/{scan_id}", headers=headers)
    if detail_resp.status_code != 200:
        print(f"❌ Failed to fetch scan details: {detail_resp.status_code}")
        sys.exit(1)
    print("✅ Detailed scan report retrieved successfully!")

    # 9. Delete Scan
    print("\n9. Cleaning up scan record...")
    del_resp = client.delete(f"{BASE_URL}/disease/scans/{scan_id}", headers=headers)
    if del_resp.status_code != 204:
        print(f"❌ Deletion failed: {del_resp.status_code}")
        sys.exit(1)
    print("✅ Scan record deleted successfully from database and server disk storage.")

    # 10. Check 404
    print("\n10. Double checking deletion status...")
    check_resp = client.get(f"{BASE_URL}/disease/scans/{scan_id}", headers=headers)
    if check_resp.status_code != 404:
        print(f"❌ Deletion verification check failed, scan still exists: {check_resp.status_code}")
        sys.exit(1)
    print("✅ Deletion status confirmed (Returned HTTP 404).")

    print("\n🎉 All Sprint 4 Plant Disease Detection E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint4()
