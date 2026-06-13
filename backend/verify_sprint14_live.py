import httpx
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"


def verify_sprint14():
    print("🚀 Starting Sprint 14 Quality of Service, Settings & Landing Page E2E Live Verification...")
    client = httpx.Client(timeout=60.0)

    # 1. Register a test user
    email = f"live_farmer_s14_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    print(f"\n1. Registering test farmer ({email})...")
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
    else:
        print(f"❌ Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        sys.exit(1)

    # 2. Login
    print("\n2. Logging in with original credentials...")
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

    # 3. Retrieve default settings
    print("\n3. Testing GET /farmers/settings (Retrieving Defaults)...")
    get_settings_resp = client.get(f"{BASE_URL}/farmers/settings", headers=headers)
    if get_settings_resp.status_code != 200:
        print(f"❌ GET settings failed: {get_settings_resp.status_code} - {get_settings_resp.text}")
        sys.exit(1)
    
    settings = get_settings_resp.json()
    print("✅ Defaults retrieved:")
    print(f"  Theme Preference:    {settings.get('theme_preference')}")
    print(f"  Email Notifications: {settings.get('email_notifications')}")
    print(f"  Push Notifications:  {settings.get('push_notifications')}")
    print(f"  Default Crop:        {settings.get('default_crop')}")
    print(f"  Default Soil Type:   {settings.get('default_soil_type')}")

    # Verify initial defaults
    assert settings["theme_preference"] == "dark", "Default theme should be dark"
    assert settings["email_notifications"] is True, "Default email notifications should be enabled"
    assert settings["push_notifications"] is True, "Default push notifications should be enabled"
    print("✅ Initial defaults verified!")

    # 4. Update settings
    print("\n4. Testing PUT /farmers/settings (Updating Preferences)...")
    update_payload = {
        "theme_preference": "light",
        "email_notifications": False,
        "push_notifications": True,
        "default_crop": "rice",
        "default_soil_type": "clayey"
    }
    put_settings_resp = client.put(f"{BASE_URL}/farmers/settings", json=update_payload, headers=headers)
    if put_settings_resp.status_code != 200:
        print(f"❌ PUT settings failed: {put_settings_resp.status_code} - {put_settings_resp.text}")
        sys.exit(1)
    
    updated_settings = put_settings_resp.json()
    print("✅ Settings updated successfully:")
    print(f"  Theme Preference:    {updated_settings.get('theme_preference')}")
    print(f"  Email Notifications: {updated_settings.get('email_notifications')}")
    print(f"  Push Notifications:  {updated_settings.get('push_notifications')}")
    print(f"  Default Crop:        {updated_settings.get('default_crop')}")
    print(f"  Default Soil Type:   {updated_settings.get('default_soil_type')}")

    assert updated_settings["theme_preference"] == "light"
    assert updated_settings["email_notifications"] is False
    assert updated_settings["push_notifications"] is True
    assert updated_settings["default_crop"] == "rice"
    assert updated_settings["default_soil_type"] == "clayey"
    print("✅ Updated preferences match update payload!")

    # 5. Retrieve settings again to ensure persistence
    print("\n5. Testing settings persistence via GET...")
    verify_settings_resp = client.get(f"{BASE_URL}/farmers/settings", headers=headers)
    if verify_settings_resp.status_code != 200:
        print(f"❌ Persistent GET failed: {verify_settings_resp.status_code}")
        sys.exit(1)
    
    persisted = verify_settings_resp.json()
    assert persisted["theme_preference"] == "light"
    assert persisted["default_crop"] == "rice"
    print("✅ Verified: Settings are successfully stored in MySQL database!")

    # 6. Update Profile details
    print("\n6. Testing PUT /farmers/me (Updating Profile details)...")
    profile_update = {
        "first_name": "Rameshbhai",
        "last_name": "Patel",
        "location": "Surat, Gujarat",
        "contact_number": "+91 9999888877"
    }
    profile_resp = client.put(f"{BASE_URL}/farmers/me", json=profile_update, headers=headers)
    if profile_resp.status_code != 200:
        print(f"❌ PUT profile failed: {profile_resp.status_code} - {profile_resp.text}")
        sys.exit(1)
    
    updated_profile = profile_resp.json()
    print("✅ Profile updated successfully:")
    print(f"  First Name:     {updated_profile.get('first_name')}")
    print(f"  Last Name:      {updated_profile.get('last_name')}")
    print(f"  Location:       {updated_profile.get('location')}")
    print(f"  Contact Number: {updated_profile.get('contact_number')}")

    assert updated_profile["first_name"] == "Rameshbhai"
    assert updated_profile["location"] == "Surat, Gujarat"
    print("✅ Profile updates verified!")

    # 7. Change Password
    print("\n7. Testing POST /farmers/change-password...")
    new_password = "newpassword456"
    pwd_resp = client.post(
        f"{BASE_URL}/farmers/change-password",
        json={
            "old_password": password,
            "new_password": new_password
        },
        headers=headers
    )
    if pwd_resp.status_code != 200:
        print(f"❌ Change password failed: {pwd_resp.status_code} - {pwd_resp.text}")
        sys.exit(1)
    
    print("✅ Password updated successfully status returned!")

    # 8. Attempt login with old password (should fail)
    print("\n8. Verifying old password is invalidated...")
    old_login_resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )
    if old_login_resp.status_code != 200:
        print("✅ Correctly rejected old credentials login attempt!")
    else:
        print("❌ Security failure: Old password could still log in!")
        sys.exit(1)

    # 9. Attempt login with new password (should succeed)
    print("\n9. Logging in with new credentials...")
    new_login_resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": new_password}
    )
    if new_login_resp.status_code == 200:
        print("✅ Logged in successfully with new credentials!")
    else:
        print(f"❌ Login failed with new credentials: {new_login_resp.status_code} - {new_login_resp.text}")
        sys.exit(1)

    # 10. Check health diagnostics endpoint
    print("\n10. Testing GET /system/status (System Diagnostics)...")
    status_resp = client.get(f"{BASE_URL}/system/status")
    if status_resp.status_code != 200:
        print(f"❌ System status failed: {status_resp.status_code}")
        sys.exit(1)
    
    sys_status = status_resp.json()
    print("✅ Live system status:")
    print(f"  Backend API Server:   {sys_status.get('backend_status')}")
    print(f"  Database Status:      {sys_status.get('database_status')}")
    print(f"  Gemini AI Status:     {sys_status.get('gemini_status')}")
    print(f"  Response Latency:     {sys_status.get('last_api_response_time')} ms")

    assert sys_status["backend_status"] == "healthy"
    assert "database_status" in sys_status
    assert "gemini_status" in sys_status
    print("✅ Health diagnostics schema matches requirements!")

    # 11. Check dynamic documentation guide endpoint
    print("\n11. Testing GET /system/help (Help Center Dynamic Content)...")
    help_resp = client.get(f"{BASE_URL}/system/help")
    if help_resp.status_code != 200:
        print(f"❌ Help center failed: {help_resp.status_code}")
        sys.exit(1)
    
    help_data = help_resp.json()
    print("✅ Help center content loaded:")
    print(f"  Number of FAQs:          {len(help_data.get('faqs', []))}")
    print(f"  Troubleshooting Steps:   {len(help_data.get('troubleshooting', []))}")
    print("  Available Guides:")
    for guide_name in help_data.get("guides", {}).keys():
        print(f"    - {guide_name}")

    assert "guides" in help_data
    assert "faqs" in help_data
    assert "troubleshooting" in help_data
    assert len(help_data["faqs"]) > 0
    print("✅ Help Center dynamic content verified!")

    print("\n🎉 All Sprint 14 Settings, Diagnostics, Help, and security E2E live checks passed successfully!")


if __name__ == "__main__":
    verify_sprint14()
