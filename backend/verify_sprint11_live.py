import httpx
import sys
import uuid
import io
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint11():
    print("🚀 Starting Sprint 11 Smart Notifications & Alert Center E2E Live Verification...")
    client = httpx.Client(timeout=60.0, follow_redirects=True)

    # 1. Register a test user
    email = f"live_farmer_s11_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Sanjay",
            "last_name": "Patel",
            "location": "Gujarat, India"
        }
    )
    if reg_resp.status_code in (200, 201):
        print("   ✅ Farmer registered successfully!")
    else:
        print(f"   ❌ Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        sys.exit(1)

    # 2. Login
    print("\n2. Logging in...")
    login_resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )
    if login_resp.status_code != 200:
        print(f"   ❌ Login failed: {login_resp.status_code} - {login_resp.text}")
        sys.exit(1)

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Logged in successfully! JWT token retrieved.")

    # 3. Create a Soil Report
    print("\n3. Creating soil report...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.8,
            "nitrogen": 55.0,
            "phosphorus": 35.0,
            "potassium": 210.0,
            "organic_matter": 2.5,
            "crop_planned": "Tomato",
            "tested_at": date.today().isoformat()
        }
    )
    if soil_resp.status_code != 201:
        print(f"   ❌ Failed to create soil report: {soil_resp.status_code} - {soil_resp.text}")
        sys.exit(1)
    print("   ✅ Soil report registered successfully!")

    # 4. Create active Crop Operations Plan (Farm Plan)
    print("\n4. Generating Crop Operations Plan for Tomato...")
    start_date = date.today().isoformat()
    plan_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 1.5,
            "planned_start_date": start_date
        },
        headers=headers
    )
    if plan_resp.status_code != 201:
        print(f"   ❌ Farm plan generation failed: {plan_resp.status_code} - {plan_resp.text}")
        sys.exit(1)
    plan_data = plan_resp.json()
    plan_id = plan_data["id"]
    print(f"   ✅ Farm plan registered successfully! Plan ID: {plan_id}")

    # Seed an overdue task (planned date = yesterday)
    print("\n5. Seeding an overdue manual task for planner notifications...")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    overdue_resp = client.post(
        f"{BASE_URL}/farm-planner/tasks",
        json={
            "farm_plan_id": plan_id,
            "title": "Clean Irrigation Channels",
            "description": "Clean weeds and debris from channels.",
            "planned_date": yesterday,
            "priority": "high",
            "category": "irrigation"
        },
        headers=headers
    )
    if overdue_resp.status_code != 201:
        print(f"   ❌ Failed to seed overdue task: {overdue_resp.status_code} - {overdue_resp.text}")
        sys.exit(1)
    print("   ✅ Overdue task seeded successfully!")

    # 5. Generate Risk Warning alert
    print("\n6. Running AI Risk Intelligence warning scan...")
    risk_resp = client.post(
        f"{BASE_URL}/risk-intelligence/generate",
        headers=headers
    )
    if risk_resp.status_code not in (200, 201):
         print(f"   ❌ Risk warnings generation failed: {risk_resp.status_code} - {risk_resp.text}")
         sys.exit(1)
    print("   ✅ Risk early warning assessment generated successfully!")

    # 6. Generate Disease alert (Upload realistic leaf image)
    print("\n7. Uploading leaf image for disease diagnostics early warning...")
    img_path = "/Users/pranav/.gemini/antigravity-ide/brain/61db1804-3357-4b81-918c-4dd50b0df21e/tomato_leaf_spot_1781229720140.png"
    try:
        with open(img_path, "rb") as f:
            img_bytes = f.read()
    except Exception as e:
        print(f"   ❌ Failed to read test image {img_path}: {e}")
        sys.exit(1)
    
    files = {"file": ("tomato_leaf_spot.png", io.BytesIO(img_bytes), "image/png")}
    disease_resp = client.post(
        f"{BASE_URL}/disease/scan",
        headers=headers,
        files=files,
        timeout=30.0
    )
    if disease_resp.status_code != 201:
        print(f"   ❌ Disease scan failed: {disease_resp.status_code} - {disease_resp.text}")
        sys.exit(1)
    print(f"   ✅ Disease scan completed! Diagnosis: {disease_resp.json().get('disease_name')}")

    # 7. Generate yield prediction
    print("\n8. Compiling yield prediction to scan yield categories...")
    yield_resp = client.post(
        f"{BASE_URL}/yield-predictions/generate",
        headers=headers,
        json={"crop_name": "Tomato"}
    )
    if yield_resp.status_code not in (200, 201):
        print(f"   ❌ Yield prediction failed: {yield_resp.status_code} - {yield_resp.text}")
        sys.exit(1)
    print("   ✅ Yield prediction registered successfully!")

    # 8. Trigger notifications generation
    print("\n9. Triggering central Alert Engine notification scan...")
    gen_resp = client.post(
        f"{BASE_URL}/notifications/generate",
        headers=headers
    )
    if gen_resp.status_code not in (200, 201):
        print(f"   ❌ Notification scan failed: {gen_resp.status_code} - {gen_resp.text}")
        sys.exit(1)
    
    generated_count = gen_resp.json()["generated_count"]
    print(f"   ✅ Alert engine executed. Generated {generated_count} notifications!")

    # Verify duplicates check on secondary trigger
    print("\n10. Testing Duplicate Prevention rule...")
    dup_resp = client.post(
        f"{BASE_URL}/notifications/generate",
        headers=headers
    )
    if dup_resp.status_code not in (200, 201):
        print(f"   ❌ Duplicate run failed: {dup_resp.status_code}")
        sys.exit(1)
    
    dup_count = dup_resp.json()["generated_count"]
    print(f"   ✅ Duplicate run count: {dup_count} (Expected: 0)")
    if dup_count != 0:
        print("   ❌ Warning: Duplicate checks did not return 0!")
        sys.exit(1)

    # 9. Verify notifications created
    print("\n11. Listing notifications...")
    list_resp = client.get(
        f"{BASE_URL}/notifications",
        headers=headers
    )
    if list_resp.status_code != 200:
        print(f"   ❌ Failed to list notifications: {list_resp.status_code}")
        sys.exit(1)
    
    notifications = list_resp.json()
    print(f"   ✅ Successfully retrieved {len(notifications)} notifications from DB:")
    for notif in notifications:
        print(f"      • [{notif['notification_type'].upper()} | {notif['priority'].upper()}] {notif['title']} (Read: {notif['is_read']})")

    if not notifications:
        print("   ❌ Notification engine generated no results.")
        sys.exit(1)

    # 10. Verify read/unread workflow
    # Get unread list
    print("\n12. Verifying unread notifications status...")
    unread_resp = client.get(
        f"{BASE_URL}/notifications/unread",
        headers=headers
    )
    if unread_resp.status_code != 200:
        print(f"   ❌ Failed to fetch unread: {unread_resp.status_code}")
        sys.exit(1)
    
    unread_notifications = unread_resp.json()
    print(f"   ✅ Unread count: {len(unread_notifications)}")
    if len(unread_notifications) != len(notifications):
        print("   ❌ Mismatch in initial unread count.")
        sys.exit(1)

    # Mark a single notification read
    target_notif = unread_notifications[0]
    print(f"\n13. Marking notification ID {target_notif['id']} read...")
    read_resp = client.patch(
        f"{BASE_URL}/notifications/{target_notif['id']}/read",
        headers=headers
    )
    if read_resp.status_code != 200:
        print(f"   ❌ Failed to mark read: {read_resp.status_code} - {read_resp.text}")
        sys.exit(1)
    print("   ✅ Notification marked read successfully!")

    # Verify unread list decreases
    unread_check_resp = client.get(
        f"{BASE_URL}/notifications/unread",
        headers=headers
    )
    new_unread_count = len(unread_check_resp.json())
    print(f"   ✅ New unread count: {new_unread_count} (Expected: {len(unread_notifications) - 1})")
    if new_unread_count != len(unread_notifications) - 1:
        print("   ❌ Unread count decrement mismatch.")
        sys.exit(1)

    # Bulk mark all read
    print("\n14. Triggering bulk action: Mark All Read...")
    bulk_resp = client.patch(
        f"{BASE_URL}/notifications/read-all",
        headers=headers
    )
    if bulk_resp.status_code != 200:
        print(f"   ❌ Bulk read-all failed: {bulk_resp.status_code}")
        sys.exit(1)
    print("   ✅ Bulk read-all request successful.")

    # Confirm unread notifications count is now 0 (dashboard update verification)
    print("\n15. Verifying dashboard widget count status...")
    final_unread_resp = client.get(
        f"{BASE_URL}/notifications/unread",
        headers=headers
    )
    final_unread_count = len(final_unread_resp.json())
    print(f"   ✅ Final unread count: {final_unread_count} (Expected: 0)")
    if final_unread_count != 0:
        print("   ❌ Unread notifications still exist after read-all!")
        sys.exit(1)

    # Delete single notification
    print(f"\n16. Testing delete for notification ID {target_notif['id']}...")
    del_resp = client.delete(
        f"{BASE_URL}/notifications/{target_notif['id']}",
        headers=headers
    )
    if del_resp.status_code != 204:
        print(f"   ❌ Deletion failed: {del_resp.status_code}")
        sys.exit(1)
    print("   ✅ Notification deleted successfully!")

    # Verify deletion
    verify_del_resp = client.get(
        f"{BASE_URL}/notifications",
        headers=headers
    )
    remaining_ids = [n["id"] for n in verify_del_resp.json()]
    print(f"   ✅ Remaining notifications: {len(remaining_ids)}")
    if target_notif["id"] in remaining_ids:
        print("   ❌ Notification still present after deletion!")
        sys.exit(1)
    print("   ✅ Deletion verified successfully!")

    print("\n🎉 All Sprint 11 Smart Notifications & Alert Center E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint11()
