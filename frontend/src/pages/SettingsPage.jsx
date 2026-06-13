import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import { toast } from "../components/Toast";
import SystemHealthPanel from "../components/SystemHealthPanel";
import { TextSkeleton } from "../components/Skeleton";

const SettingsPage = () => {
  const { currentFarmer, updateProfile, reloadProfile } = useAuth();

  // Active settings tab: "profile", "security", "preferences", "diagnostics"
  const [activeTab, setActiveTab] = useState("profile");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [farmsList, setFarmsList] = useState([]);
  const [lastSync, setLastSync] = useState("");

  // Profile Form States
  const [profileForm, setProfileForm] = useState({
    first_name: "",
    last_name: "",
    location: "",
    contact_number: ""
  });

  // Password Form States
  const [passwordForm, setPasswordForm] = useState({
    old_password: "",
    new_password: "",
    confirm_password: ""
  });

  // Preferences Form States (theme, notifications, farm defaults)
  const [settingsForm, setSettingsForm] = useState({
    theme_preference: "dark",
    email_notifications: true,
    push_notifications: true,
    default_crop: "",
    default_soil_type: ""
  });

  // Load settings and profile data
  const loadData = async () => {
    setLoading(true);
    try {
      // Fetch user settings from API
      const settingsResp = await api.get("/farmers/settings");
      setSettingsForm(settingsResp.data);

      // Fetch farms list to identify active farm
      const farmsResp = await api.get("/farms");
      setFarmsList(farmsResp.data);

      // Set Profile details
      if (currentFarmer) {
        setProfileForm({
          first_name: currentFarmer.first_name || "",
          last_name: currentFarmer.last_name || "",
          location: currentFarmer.location || "",
          contact_number: currentFarmer.contact_number || ""
        });
      }

      setLastSync(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Failed to load settings data:", err);
      toast.error("Failed to load configuration parameters.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentFarmer]);

  // Save profile info
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateProfile(profileForm);
      toast.success("Profile details updated successfully.");
      await reloadProfile();
    } catch (err) {
      console.error("Profile update failed:", err);
      toast.error(err || "Failed to update profile details.");
    } finally {
      setSaving(false);
    }
  };

  // Change password
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error("New passwords do not match.");
      return;
    }
    if (passwordForm.new_password.length < 6) {
      toast.error("Password must be at least 6 characters.");
      return;
    }
    setSaving(true);
    try {
      await api.post("/farmers/change-password", {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      });
      toast.success("Password changed successfully.");
      setPasswordForm({ old_password: "", new_password: "", confirm_password: "" });
    } catch (err) {
      console.error("Password change failed:", err);
      toast.error(err.response?.data?.detail || "Failed to change password. Verify your old password.");
    } finally {
      setSaving(false);
    }
  };

  // Save notification, farm default, and theme preferences
  const handlePreferencesSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const resp = await api.put("/farmers/settings", settingsForm);
      setSettingsForm(resp.data);
      
      // Instantly apply theme to page layout
      document.body.classList.toggle("dark-theme", resp.data.theme_preference !== "light");
      
      toast.success("Preferences saved successfully.");
      setLastSync(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Preferences update failed:", err);
      toast.error("Failed to update preferences.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "32px", display: "flex", flexDirection: "column", gap: "20px" }}>
        <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.5rem" }}>⚙️ Application Settings</h2>
        <TextSkeleton />
        <TextSkeleton />
      </div>
    );
  }

  const activeFarm = farmsList.find((f) => f.id === currentFarmer?.active_farm_id);

  return (
    <div className="animate-fade-in" style={{ padding: "32px", overflowY: "auto", height: "100%", display: "flex", flexDirection: "column", gap: "24px" }}>
      
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "1.8rem", color: "var(--text-primary)", fontWeight: "800", margin: 0 }}>⚙️ Settings Center</h1>
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "4px" }}>
          Manage your personal details, operational parameters, farm defaults, and security configurations.
        </p>
      </div>

      <div className="settings-layout-grid" style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: "32px", alignItems: "start" }}>
        
        {/* Navigation Sidebar */}
        <div className="glass" style={{ borderRadius: "var(--radius-md)", padding: "12px", display: "flex", flexDirection: "column", gap: "6px" }}>
          <button
            className={`settings-nav-btn ${activeTab === "profile" ? "active" : ""}`}
            onClick={() => setActiveTab("profile")}
          >
            👤 Profile Details
          </button>
          <button
            className={`settings-nav-btn ${activeTab === "preferences" ? "active" : ""}`}
            onClick={() => setActiveTab("preferences")}
          >
            🌾 Farm & Alerts
          </button>
          <button
            className={`settings-nav-btn ${activeTab === "security" ? "active" : ""}`}
            onClick={() => setActiveTab("security")}
          >
            🛡️ Security
          </button>
          <button
            className={`settings-nav-btn ${activeTab === "diagnostics" ? "active" : ""}`}
            onClick={() => setActiveTab("diagnostics")}
          >
            🤖 AI & Diagnostics
          </button>
        </div>

        {/* Content Pane */}
        <div className="glass" style={{ padding: "32px", borderRadius: "var(--radius-md)", minHeight: "400px" }}>
          
          {/* 1. Profile Details */}
          {activeTab === "profile" && (
            <div className="animate-fade-in">
              <h2 style={{ fontSize: "1.25rem", color: "var(--text-primary)", marginBottom: "8px", fontWeight: "700" }}>Profile Details</h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "24px" }}>
                Keep your farmer profile data current to ensure custom location-specific weather alerts.
              </p>
              
              <form onSubmit={handleProfileSubmit} style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label" htmlFor="firstName">First Name</label>
                    <input
                      type="text"
                      id="firstName"
                      className="form-input"
                      value={profileForm.first_name}
                      onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label" htmlFor="lastName">Last Name</label>
                    <input
                      type="text"
                      id="lastName"
                      className="form-input"
                      value={profileForm.last_name}
                      onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Registered Email (Cannot modify)</label>
                  <input
                    type="text"
                    className="form-input"
                    value={currentFarmer?.email || ""}
                    disabled
                    style={{ backgroundColor: "var(--bg-app)", opacity: 0.7, cursor: "not-allowed" }}
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label" htmlFor="location">State/District Location</label>
                    <input
                      type="text"
                      id="location"
                      className="form-input"
                      value={profileForm.location}
                      onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })}
                      placeholder="e.g. Punjab, Ludhiana"
                    />
                  </div>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label" htmlFor="contact">Contact Number</label>
                    <input
                      type="text"
                      id="contact"
                      className="form-input"
                      value={profileForm.contact_number}
                      onChange={(e) => setProfileForm({ ...profileForm, contact_number: e.target.value })}
                      placeholder="e.g. +91 9876543210"
                    />
                  </div>
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: "fit-content", marginTop: "8px" }} disabled={saving}>
                  {saving ? "Saving Changes..." : "Save Profile Details"}
                </button>
              </form>
            </div>
          )}

          {/* 2. Farm Preferences */}
          {activeTab === "preferences" && (
            <div className="animate-fade-in">
              <h2 style={{ fontSize: "1.25rem", color: "var(--text-primary)", marginBottom: "8px", fontWeight: "700" }}>Farm & Alert Preferences</h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "24px" }}>
                Configure default search inputs for the virtual advisor and toggle automated notifications.
              </p>

              <form onSubmit={handlePreferencesSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                {/* Farm Defaults */}
                <div>
                  <h3 style={{ fontSize: "1rem", color: "var(--primary)", marginBottom: "12px", fontWeight: "600", fontFamily: "'Outfit', sans-serif" }}>🌾 Farm Sowing Defaults</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label className="form-label" htmlFor="defaultCrop">Default Main Crop</label>
                      <select
                        id="defaultCrop"
                        className="form-input"
                        value={settingsForm.default_crop || ""}
                        onChange={(e) => setSettingsForm({ ...settingsForm, default_crop: e.target.value })}
                        style={{ height: "46px" }}
                      >
                        <option value="">-- Select Crop --</option>
                        <option value="wheat">Wheat</option>
                        <option value="rice">Rice</option>
                        <option value="cotton">Cotton</option>
                        <option value="tomatoes">Tomatoes</option>
                        <option value="maize">Maize</option>
                        <option value="soybeans">Soybeans</option>
                      </select>
                    </div>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label className="form-label" htmlFor="defaultSoil">Default Soil Type</label>
                      <select
                        id="defaultSoil"
                        className="form-input"
                        value={settingsForm.default_soil_type || ""}
                        onChange={(e) => setSettingsForm({ ...settingsForm, default_soil_type: e.target.value })}
                        style={{ height: "46px" }}
                      >
                        <option value="">-- Select Soil Type --</option>
                        <option value="alluvial">Alluvial Soil</option>
                        <option value="black">Black Soil (Regur)</option>
                        <option value="red">Red Soil</option>
                        <option value="clayey">Clayey Soil</option>
                        <option value="loamy">Loamy Soil</option>
                        <option value="sandy">Sandy Soil</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div style={{ height: "1px", backgroundColor: "var(--border-light)", margin: "8px 0" }}></div>

                {/* Notifications */}
                <div>
                  <h3 style={{ fontSize: "1rem", color: "var(--primary)", marginBottom: "12px", fontWeight: "600", fontFamily: "'Outfit', sans-serif" }}>🔔 Smart Alert Preferences</h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "0.9rem", color: "var(--text-primary)" }}>
                      <input
                        type="checkbox"
                        checked={settingsForm.email_notifications}
                        onChange={(e) => setSettingsForm({ ...settingsForm, email_notifications: e.target.checked })}
                        style={{ width: "16px", height: "16px", accentColor: "var(--primary)", cursor: "pointer" }}
                      />
                      <span>Receive high-priority warnings via email (weather alerts, pest alerts)</span>
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "0.9rem", color: "var(--text-primary)" }}>
                      <input
                        type="checkbox"
                        checked={settingsForm.push_notifications}
                        onChange={(e) => setSettingsForm({ ...settingsForm, push_notifications: e.target.checked })}
                        style={{ width: "16px", height: "16px", accentColor: "var(--primary)", cursor: "pointer" }}
                      />
                      <span>Enable browser push notification warnings and reminders</span>
                    </label>
                  </div>
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: "fit-content", marginTop: "8px" }} disabled={saving}>
                  {saving ? "Saving preferences..." : "Save Preferences"}
                </button>
              </form>
            </div>
          )}

          {/* 3. Security */}
          {activeTab === "security" && (
            <div className="animate-fade-in">
              <h2 style={{ fontSize: "1.25rem", color: "var(--text-primary)", marginBottom: "8px", fontWeight: "700" }}>Security Center</h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "24px" }}>
                Modify your password to keep your agricultural portfolio and data reports protected.
              </p>

              <form onSubmit={handlePasswordSubmit} style={{ display: "flex", flexDirection: "column", gap: "18px", maxWidth: "450px" }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" htmlFor="oldPassword">Current Password</label>
                  <input
                    type="password"
                    id="oldPassword"
                    className="form-input"
                    value={passwordForm.old_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" htmlFor="newPassword">New Password</label>
                  <input
                    type="password"
                    id="newPassword"
                    className="form-input"
                    value={passwordForm.new_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" htmlFor="confirmPassword">Confirm New Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    className="form-input"
                    value={passwordForm.confirm_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                    required
                  />
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: "fit-content", marginTop: "8px" }} disabled={saving}>
                  {saving ? "Changing Password..." : "Update Password"}
                </button>
              </form>
            </div>
          )}

          {/* 4. AI & Diagnostics */}
          {activeTab === "diagnostics" && (
            <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
              <div>
                <h2 style={{ fontSize: "1.25rem", color: "var(--text-primary)", marginBottom: "8px", fontWeight: "700" }}>AI & Platform Diagnostics</h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "16px" }}>
                  Monitor AI status diagnostics, active farm listings, and toggle application layout styling options.
                </p>
              </div>

              {/* Theme Selector */}
              <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)" }}>
                <h3 style={{ fontSize: "1rem", color: "var(--primary)", marginBottom: "12px", fontWeight: "600", fontFamily: "'Outfit', sans-serif" }}>🎨 Layout Styling Preference</h3>
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <label style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>Theme Color Mode:</label>
                  <select
                    className="form-input"
                    value={settingsForm.theme_preference}
                    onChange={async (e) => {
                      const newTheme = e.target.value;
                      setSettingsForm((prev) => ({ ...prev, theme_preference: newTheme }));
                      try {
                        const resp = await api.put("/farmers/settings", { ...settingsForm, theme_preference: newTheme });
                        document.body.classList.toggle("dark-theme", resp.data.theme_preference !== "light");
                        toast.success(`Theme updated to ${resp.data.theme_preference}`);
                      } catch (err) {
                        console.error("Theme switch failed:", err);
                        toast.error("Failed to persist theme preference.");
                      }
                    }}
                    style={{ maxWidth: "200px" }}
                  >
                    <option value="dark">Dark Theme (Recommended)</option>
                    <option value="light">Light Theme</option>
                  </select>
                </div>
              </div>

              {/* AI Status Details */}
              <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "12px" }}>
                <h3 style={{ fontSize: "1rem", color: "var(--primary)", marginBottom: "4px", fontWeight: "600", fontFamily: "'Outfit', sans-serif" }}>🤖 Agricultural AI Context</h3>
                
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Active Farm Context:</span>
                    <span style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)" }}>
                      🏡 {activeFarm ? activeFarm.name : "None (Go to portfolio to create)"}
                    </span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Last Settings Sync:</span>
                    <span style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)" }}>
                      🕒 {lastSync || "Not synced"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Real-time Diagnostics Integration */}
              <SystemHealthPanel />
            </div>
          )}

        </div>
      </div>

      {/* Internal Custom Styles */}
      <style>{`
        .settings-nav-btn {
          width: 100%;
          text-align: left;
          padding: 12px 16px;
          background: transparent;
          border: none;
          color: var(--text-secondary);
          font-family: 'Outfit', sans-serif;
          font-size: 0.95rem;
          font-weight: 600;
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: var(--transition-smooth);
        }
        .settings-nav-btn:hover {
          background-color: var(--primary-soft);
          color: var(--primary);
        }
        .settings-nav-btn.active {
          background-color: var(--primary);
          color: var(--text-light);
        }
      `}</style>

    </div>
  );
};

export default SettingsPage;
