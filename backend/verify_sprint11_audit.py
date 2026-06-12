import httpx
import sys
import uuid
import io
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"


def run_audit():
    print("🔎 Starting Sprint 11 Smart Notifications Engine Final Audit...")
    client = httpx.Client(timeout=60.0, follow_redirects=True)

    # 1. Register test farmer
    email = f"audit_farmer_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering audit farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Audit",
            "last_name": "User",
            "location": "Punjab, India"
        }
    )
    if reg_resp.status_code not in (200, 201):
        print(f"❌ Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        sys.exit(1)
    print("   ✅ Registered successfully!")

    # 2. Login
    print("\n2. Logging in...")
    login_resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code}")
        sys.exit(1)
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Logged in successfully!")

    # 3. Seed initial farm plan context to trigger upcoming task notification
    print("\n3. Seeding soil report and farm plan...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.5,
            "nitrogen": 45.0,
            "phosphorus": 30.0,
            "potassium": 180.0,
            "organic_matter": 2.0,
            "crop_planned": "Wheat",
            "tested_at": date.today().isoformat()
        }
    )
    if soil_resp.status_code != 201:
        print("❌ Soil creation failed")
        sys.exit(1)

    plan_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        json={
            "crop_name": "Wheat",
            "area_acres": 2.0,
            "planned_start_date": date.today().isoformat()
        },
        headers=headers
    )
    if plan_resp.status_code != 201:
        print("❌ Plan creation failed")
        sys.exit(1)
    plan_id = plan_resp.json()["id"]
    print("   ✅ Soil report and farm plan seeded successfully!")

    # 4. First notification generation run
    print("\n4. Triggering initial notification generation...")
    gen1_resp = client.post(f"{BASE_URL}/notifications/generate", headers=headers)
    if gen1_resp.status_code not in (200, 201):
        print(f"❌ First generation failed: {gen1_resp.status_code}")
        sys.exit(1)
    
    g1_count = gen1_resp.json()["generated_count"]
    print(f"   ✅ Initial run generated {g1_count} notifications.")

    # List notifications to fetch IDs
    list1_resp = client.get(f"{BASE_URL}/notifications", headers=headers)
    notifications_run1 = list1_resp.json()
    total_run1 = len(notifications_run1)
    print(f"   ✅ Total notifications in database: {total_run1}")
    for n in notifications_run1:
        print(f"      - ID {n['id']} | [{n['source_module'].upper()}] {n['title']} (Read: {n['is_read']})")

    unread_resp1 = client.get(f"{BASE_URL}/notifications/unread", headers=headers)
    unread_run1 = len(unread_resp1.json())
    print(f"   ✅ Unread count: {unread_run1}")

    # 5. Second notification generation run (without changing any data)
    print("\n5. Running notification generation again without changing any data...")
    gen2_resp = client.post(f"{BASE_URL}/notifications/generate", headers=headers)
    g2_count = gen2_resp.json()["generated_count"]
    print(f"   ✅ Second run generated {g2_count} notifications (Expected: 0).")
    if g2_count != 0:
        print("❌ Idempotency failed: Duplicate notifications were generated!")
        sys.exit(1)
    print("   ✅ Idempotency test passed: 0 new notifications generated.")

    # Verify counts remain correct
    list2_resp = client.get(f"{BASE_URL}/notifications", headers=headers)
    total_run2 = len(list2_resp.json())
    unread_resp2 = client.get(f"{BASE_URL}/notifications/unread", headers=headers)
    unread_run2 = len(unread_resp2.json())
    print(f"   ✅ Total notifications count: {total_run2} (Expected: {total_run1})")
    print(f"   ✅ Unread notifications count: {unread_run2} (Expected: {unread_run1})")
    if total_run2 != total_run1 or unread_run2 != unread_run1:
        print("❌ Notification or unread counts changed unexpectedly!")
        sys.exit(1)
    print("   ✅ Counts idempotency check passed.")

    # 6. Deleting a notification
    target_notif = notifications_run1[0]
    target_id = target_notif["id"]
    print(f"\n6. Deleting notification ID {target_id} ('{target_notif['title']}')...")
    del_resp = client.delete(f"{BASE_URL}/notifications/{target_id}", headers=headers)
    if del_resp.status_code != 204:
        print(f"❌ Delete request failed: {del_resp.status_code}")
        sys.exit(1)
    print("   ✅ Notification deleted successfully.")

    # Verify counts after delete
    list_after_del = client.get(f"{BASE_URL}/notifications", headers=headers)
    total_after_del = len(list_after_del.json())
    print(f"   ✅ Notification count after deletion: {total_after_del} (Expected: {total_run1 - 1})")
    if total_after_del != total_run1 - 1:
        print("❌ Deletion failed to reduce the visible notifications count!")
        sys.exit(1)

    # 7. Run generation again (Deleted notification should NOT regenerate immediately)
    print("\n7. Triggering alert generation after deletion (condition unchanged)...")
    gen3_resp = client.post(f"{BASE_URL}/notifications/generate", headers=headers)
    g3_count = gen3_resp.json()["generated_count"]
    print(f"   ✅ Third run generated {g3_count} notifications (Expected: 0).")
    if g3_count != 0:
        print("❌ Bug: Deleted notification was regenerated immediately despite no change in conditions!")
        sys.exit(1)
    print("   ✅ Deletion persistence check passed: Deleted notification was NOT regenerated.")

    # Verify counts remain correct
    list_after_gen3 = client.get(f"{BASE_URL}/notifications", headers=headers)
    total_after_gen3 = len(list_after_gen3.json())
    print(f"   ✅ Total notifications count: {total_after_gen3} (Expected: {total_run1 - 1})")
    if total_after_gen3 != total_run1 - 1:
        print("❌ Notification count changed unexpectedly after running generation on deleted records!")
        sys.exit(1)

    # 8. Trigger condition change (Seed a new overdue task to trigger a new notification)
    print("\n8. Seeding a new overdue task (changing triggering conditions)...")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    new_task_resp = client.post(
        f"{BASE_URL}/farm-planner/tasks",
        json={
            "farm_plan_id": plan_id,
            "title": "Check Soil Moisture Levels",
            "description": "Ensure moisture matches winter crop requirements.",
            "planned_date": yesterday,
            "priority": "high",
            "category": "irrigation"
        },
        headers=headers
    )
    if new_task_resp.status_code != 201:
        print(f"❌ Failed to seed new task: {new_task_resp.status_code}")
        sys.exit(1)
    print("   ✅ New overdue task successfully registered.")

    # Run generation again (New condition should trigger a new notification)
    print("\n9. Triggering alert generation after condition change...")
    gen4_resp = client.post(f"{BASE_URL}/notifications/generate", headers=headers)
    g4_count = gen4_resp.json()["generated_count"]
    print(f"   ✅ Fourth run generated {g4_count} notifications (Expected: 1).")
    if g4_count != 1:
        print(f"❌ Expected exactly 1 new notification, but got {g4_count}!")
        sys.exit(1)

    # Verify counts update
    list_final = client.get(f"{BASE_URL}/notifications", headers=headers)
    notifications_final = list_final.json()
    total_final = len(notifications_final)
    print(f"   ✅ Final notifications count in database: {total_final} (Expected: {total_run1})")
    if total_final != total_run1:
        print("❌ Final notifications count mismatch.")
        sys.exit(1)

    print("\n✅ Verification details:")
    print(f"   - Newly generated notification: '{notifications_final[0]['title']}'")
    print(f"   - Priority level:                {notifications_final[0]['priority'].upper()}")
    print(f"   - Source module:                 {notifications_final[0]['source_module'].upper()}")

    print("\n🎉 Notification Engine Audit Completed successfully! All idempotency and soft-deletion rules verified.")


if __name__ == "__main__":
    run_audit()
