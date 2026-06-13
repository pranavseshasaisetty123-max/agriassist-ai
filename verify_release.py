import httpx
import sys
import subprocess
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"


def run_unit_tests():
    print("🧪 Running backend unit tests suite using pytest...")
    # Change cwd to backend for imports alignment
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
    
    result = subprocess.run(
        ["venv/bin/pytest", "app/tests/test_sprint14_ui.py"],
        cwd=backend_dir,
        env={**os.environ, "PYTHONPATH": "."},
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Backend unit tests passed successfully!")
        print(result.stdout.split("\n")[-2]) # Print summary line
    else:
        print(f"❌ Backend unit tests failed! Code: {result.returncode}")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)


def verify_live_endpoints():
    print("\n🚀 Verifying live system API endpoints...")
    client = httpx.Client(timeout=30.0)

    # 1. System status healthcheck
    print("\n1. Pinging GET /system/status...")
    try:
        resp = client.get(f"{BASE_URL}/system/status")
        if resp.status_code == 200:
            status = resp.json()
            print("✅ Status retrieved:")
            print(f"   Backend Status:   {status.get('backend_status')}")
            print(f"   Database Status:  {status.get('database_status')}")
            print(f"   Gemini Status:    {status.get('gemini_status')}")
            print(f"   Response Time:    {status.get('last_api_response_time')} ms")
        else:
            print(f"❌ System status returned error: {resp.status_code} - {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to reach system status api: {e}")
        sys.exit(1)

    # 2. System documentation guides
    print("\n2. Pinging GET /system/help...")
    try:
        resp = client.get(f"{BASE_URL}/system/help")
        if resp.status_code == 200:
            help_data = resp.json()
            print(f"✅ Loaded guides list: {list(help_data.get('guides', {}).keys())}")
            print(f"   Number of Collapsible FAQs: {len(help_data.get('faqs', []))}")
        else:
            print(f"❌ Help center returned error: {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to reach system help api: {e}")
        sys.exit(1)

    # 3. Recruiter login
    print("\n3. Verifying recruiter credential login...")
    try:
        login_resp = client.post(
            f"{BASE_URL}/auth/login",
            data={"username": "recruiter@agriassist.ai", "password": "password123"}
        )
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Logged in successfully! JWT token retrieved.")
        else:
            print(f"❌ Recruiter login failed: {login_resp.status_code} - {login_resp.text}")
            print("💡 Did you run 'python scripts/seed_demo_data.py' first?")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to post credentials: {e}")
        sys.exit(1)

    # 4. Profile retrieval
    print("\n4. Retrieving profile details...")
    try:
        me_resp = client.get(f"{BASE_URL}/farmers/me", headers=headers)
        if me_resp.status_code == 200:
            profile = me_resp.json()
            print(f"✅ Profile verified: {profile.get('first_name')} {profile.get('last_name')}")
            print(f"   Active Farm Context ID: {profile.get('active_farm_id')}")
        else:
            print(f"❌ Failed to load profile: {me_resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Profile query connection failed: {e}")
        sys.exit(1)

    # 5. Farms checklist
    print("\n5. Auditing multi-farm portfolio list...")
    try:
        farms_resp = client.get(f"{BASE_URL}/farms", headers=headers)
        if farms_resp.status_code == 200:
            farms = farms_resp.json()
            print(f"✅ Loaded {len(farms)} holdings successfully:")
            for farm in farms:
                print(f"   - {farm.get('name')} ({farm.get('location')}): {farm.get('total_area_acres')} Acres")
        else:
            print(f"❌ Farms retrieval failed: {farms_resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Farms list query connection failed: {e}")
        sys.exit(1)

    # 6. Unread notifications count
    print("\n6. Checking alert center inbox...")
    try:
        notif_resp = client.get(f"{BASE_URL}/notifications/unread", headers=headers)
        if notif_resp.status_code == 200:
            unreads = notif_resp.json()
            print(f"✅ Checked unread inbox. Found {len(unreads)} active notification(s).")
        else:
            print(f"❌ Notification count failed: {notif_resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Notification query connection failed: {e}")
        sys.exit(1)

    print("\n🎉 All release E2E live and unit test checks passed successfully!")


if __name__ == "__main__":
    run_unit_tests()
    verify_live_endpoints()
