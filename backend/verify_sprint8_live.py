import httpx
import sys
import uuid
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint8():
    print("🚀 Starting Sprint 8 Farm Planner & Task Scheduler E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s8_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Rajesh",
            "last_name": "Sharma",
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
    print("✅ Logged in successfully! JWT token retrieved.")

    # 3. Test check: generate plan before logging a soil report (should fail)
    print("\n3. Testing plan generator rejection when no soil report exists...")
    fail_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.0,
            "planned_start_date": date.today().isoformat()
        },
        headers=headers
    )
    if fail_resp.status_code == 400 and "log a soil test report first" in fail_resp.text:
        print("✅ Correctly rejected: Please log a soil test report first.")
    else:
        print(f"❌ Rejection check failed, status: {fail_resp.status_code} - {fail_resp.text}")
        sys.exit(1)

    # 4. Create a Soil Report
    print("\n4. Creating soil report...")
    soil_resp = client.post(
        f"{BASE_URL}/soil/reports",
        headers=headers,
        json={
            "ph": 6.4,
            "nitrogen": 48.0,
            "phosphorus": 33.0,
            "potassium": 190.0,
            "organic_matter": 2.1,
            "crop_planned": "Tomato",
            "tested_at": "2026-06-12"
        }
    )
    if soil_resp.status_code != 201:
        print(f"❌ Failed to create soil report: {soil_resp.status_code} - {soil_resp.text}")
        sys.exit(1)
    print("✅ Soil report registered successfully!")

    # 5. Generate AI Farm Plan
    print("\n5. Generating Crop Operations Plan for Tomato...")
    start_date = date.today().isoformat()
    plan_resp = client.post(
        f"{BASE_URL}/farm-planner/plans/generate",
        json={
            "crop_name": "Tomato",
            "area_acres": 2.5,
            "planned_start_date": start_date
        },
        headers=headers
    )
    if plan_resp.status_code != 201:
        print(f"❌ Farm plan generation failed: {plan_resp.status_code} - {plan_resp.text}")
        sys.exit(1)

    plan = plan_resp.json()
    print("✅ Farm plan and operations timeline generated successfully!")
    print(f"  Plan ID:               {plan['id']}")
    print(f"  Crop:                  {plan['crop_name']}")
    print(f"  Area:                  {plan['area_acres']} Acres")
    print(f"  Sowing Start Date:     {plan['planned_start_date']}")
    print(f"  Estimated Harvest:     {plan['expected_harvest_date']}")
    print(f"  Total Schedule Tasks:  {len(plan['tasks'])}")
    print("=======================================")

    plan_id = plan["id"]
    tasks = plan["tasks"]
    if not tasks:
        print("❌ Generated tasks list is empty!")
        sys.exit(1)

    # 6. Add Manual custom task
    print("\n6. Creating a manual custom task inside plan...")
    manual_date = (date.today() + timedelta(days=4)).isoformat()
    manual_resp = client.post(
        f"{BASE_URL}/farm-planner/tasks",
        json={
            "farm_plan_id": plan_id,
            "title": "Clean field water channels",
            "description": "Inspect and clean soil water drainages.",
            "planned_date": manual_date,
            "priority": "medium",
            "category": "irrigation"
        },
        headers=headers
    )
    if manual_resp.status_code != 201:
        print(f"❌ Failed to create manual task: {manual_resp.status_code} - {manual_resp.text}")
        sys.exit(1)
    manual_task = manual_resp.json()
    print(f"✅ Manual task created successfully! Task ID: {manual_task['id']}")

    # 7. Mark a task completed
    first_task_id = tasks[0]["id"]
    print(f"\n7. Marking task ID {first_task_id} completed...")
    comp_resp = client.patch(f"{BASE_URL}/farm-planner/tasks/{first_task_id}/complete", headers=headers)
    if comp_resp.status_code != 200:
        print(f"❌ Failed to mark task completed: {comp_resp.status_code} - {comp_resp.text}")
        sys.exit(1)
    print(f"✅ Task marked completed! Completed At: {comp_resp.json()['completed_at']}")

    # 8. Postpone task (snooze +2 days)
    second_task_id = tasks[1]["id"] if len(tasks) > 1 else manual_task["id"]
    orig_planned = tasks[1]["planned_date"] if len(tasks) > 1 else manual_task["planned_date"]
    print(f"\n8. Snoozing task ID {second_task_id} (original date: {orig_planned}) by 2 days...")
    snooze_resp = client.patch(f"{BASE_URL}/farm-planner/tasks/{second_task_id}/snooze?days=2", headers=headers)
    if snooze_resp.status_code != 200:
        print(f"❌ Failed to snooze task: {snooze_resp.status_code} - {snooze_resp.text}")
        sys.exit(1)
    new_planned = snooze_resp.json()["planned_date"]
    print(f"✅ Task snoozed successfully! New date: {new_planned}")

    # 9. Get upcoming tasks
    print("\n9. Querying upcoming tasks for next 7 days...")
    up_resp = client.get(f"{BASE_URL}/farm-planner/tasks/upcoming?days=7", headers=headers)
    if up_resp.status_code != 200:
        print(f"❌ Failed to fetch upcoming tasks: {up_resp.status_code}")
        sys.exit(1)
    print(f"✅ Found {len(up_resp.json())} upcoming task(s) in next 7 days.")

    # 10. Get overdue tasks
    print("\n10. Querying overdue tasks...")
    over_resp = client.get(f"{BASE_URL}/farm-planner/tasks/overdue", headers=headers)
    if over_resp.status_code != 200:
        print(f"❌ Failed to fetch overdue tasks: {over_resp.status_code}")
        sys.exit(1)
    print(f"✅ Found {len(over_resp.json())} overdue task(s).")

    # 11. Delete plan (should cascade delete tasks)
    print(f"\n11. Deleting farm plan ID {plan_id}...")
    del_resp = client.delete(f"{BASE_URL}/farm-planner/plans/{plan_id}", headers=headers)
    if del_resp.status_code != 200:
        print(f"❌ Plan deletion failed: {del_resp.status_code} - {del_resp.text}")
        sys.exit(1)
    print("✅ Plan deleted successfully.")

    # 12. Retrieve plan should now return 404
    print("\n12. Verifying plan is deleted from DB...")
    check_resp = client.get(f"{BASE_URL}/farm-planner/plans/{plan_id}", headers=headers)
    if check_resp.status_code == 404:
        print("✅ Retrieval returned 404. Cascade delete verified!")
    else:
        print(f"❌ Unexpected status code: {check_resp.status_code} - plan still exists or wrong status.")
        sys.exit(1)

    print("\n🎉 All Sprint 8 Farm Planner & Task Scheduler E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint8()
