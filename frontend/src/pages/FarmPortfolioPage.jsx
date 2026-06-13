import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

const FarmPortfolioPage = () => {
  const { currentFarmer, reloadProfile } = useAuth();
  
  const [farms, setFarms] = useState([]);
  const [portfolio, setPortfolio] = useState({
    total_farms: 0,
    total_area: 0,
    portfolio_profit: 0,
    portfolio_yield: 0,
    portfolio_risk: 0,
    active_crop_plans: 0,
  });

  const [loadingFarms, setLoadingFarms] = useState(true);
  const [loadingPortfolio, setLoadingPortfolio] = useState(true);
  
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedFarm, setSelectedFarm] = useState(null);
  
  const [addForm, setAddForm] = useState({
    name: "",
    location: "",
    total_area_acres: "",
    soil_type: "Loam", // default
    latitude: "",
    longitude: "",
  });

  const [editForm, setEditForm] = useState({
    name: "",
    location: "",
    total_area_acres: "",
    soil_type: "",
    latitude: "",
    longitude: "",
  });

  const [alertMsg, setAlertMsg] = useState({ type: "", text: "" });

  const soilTypes = [
    "Loam",
    "Clay",
    "Silt",
    "Sandy",
    "Peaty",
    "Chalky",
    "Saline",
    "Black Soil",
    "Red Soil",
    "Alluvial",
  ];

  const fetchFarms = async () => {
    setLoadingFarms(true);
    try {
      const resp = await api.get("/farms");
      setFarms(resp.data);
    } catch (err) {
      console.error("Failed to load farms:", err);
      showAlert("error", "Failed to retrieve farms. Please refresh.");
    } finally {
      setLoadingFarms(false);
    }
  };

  const fetchPortfolio = async () => {
    setLoadingPortfolio(true);
    try {
      const resp = await api.get("/farms/portfolio");
      setPortfolio(resp.data);
    } catch (err) {
      console.error("Failed to load portfolio metrics:", err);
    } finally {
      setLoadingPortfolio(false);
    }
  };

  useEffect(() => {
    fetchFarms();
    fetchPortfolio();
  }, []);

  const showAlert = (type, text) => {
    setAlertMsg({ type, text });
    setTimeout(() => setAlertMsg({ type: "", text: "" }), 5000);
  };

  const handleActivate = async (farmId) => {
    try {
      await api.post(`/farms/${farmId}/activate`);
      await reloadProfile();
      showAlert("success", "Active farm switched successfully!");
      fetchPortfolio(); // active planner tasks or analytics will change portfolio values
    } catch (err) {
      console.error("Failed to switch farm:", err);
      showAlert("error", err.response?.data?.detail || "Could not switch active farm.");
    }
  };

  const handleAddFarm = async (e) => {
    e.preventDefault();
    if (!addForm.name.trim() || !addForm.location.trim() || !addForm.total_area_acres) {
      showAlert("error", "Please fill in all required fields.");
      return;
    }
    
    const payload = {
      name: addForm.name,
      location: addForm.location,
      total_area_acres: parseFloat(addForm.total_area_acres),
      soil_type: addForm.soil_type,
      latitude: addForm.latitude ? parseFloat(addForm.latitude) : null,
      longitude: addForm.longitude ? parseFloat(addForm.longitude) : null,
    };

    try {
      await api.post("/farms", payload);
      showAlert("success", "Farm added successfully!");
      setShowAddModal(false);
      setAddForm({
        name: "",
        location: "",
        total_area_acres: "",
        soil_type: "Loam",
        latitude: "",
        longitude: "",
      });
      await reloadProfile();
      fetchFarms();
      fetchPortfolio();
    } catch (err) {
      console.error("Failed to add farm:", err);
      showAlert("error", err.response?.data?.detail || "Error adding farm.");
    }
  };

  const handleEditClick = (farm) => {
    setSelectedFarm(farm);
    setEditForm({
      name: farm.name,
      location: farm.location,
      total_area_acres: farm.total_area_acres,
      soil_type: farm.soil_type,
      latitude: farm.latitude !== null ? farm.latitude : "",
      longitude: farm.longitude !== null ? farm.longitude : "",
    });
    setShowEditModal(true);
  };

  const handleUpdateFarm = async (e) => {
    e.preventDefault();
    if (!selectedFarm) return;

    const payload = {
      name: editForm.name,
      location: editForm.location,
      total_area_acres: parseFloat(editForm.total_area_acres),
      soil_type: editForm.soil_type,
      latitude: editForm.latitude !== "" ? parseFloat(editForm.latitude) : null,
      longitude: editForm.longitude !== "" ? parseFloat(editForm.longitude) : null,
    };

    try {
      await api.put(`/farms/${selectedFarm.id}`, payload);
      showAlert("success", "Farm updated successfully!");
      setShowEditModal(false);
      setSelectedFarm(null);
      await reloadProfile();
      fetchFarms();
      fetchPortfolio();
    } catch (err) {
      console.error("Failed to update farm:", err);
      showAlert("error", err.response?.data?.detail || "Error updating farm.");
    }
  };

  const handleDeleteFarm = async (farmId, farmName) => {
    if (!window.confirm(`Are you sure you want to delete "${farmName}"? This will permanently delete all soil records, yield predictions, and schedules associated with this farm.`)) {
      return;
    }

    try {
      await api.delete(`/farms/${farmId}`);
      showAlert("success", "Farm deleted successfully!");
      await reloadProfile();
      fetchFarms();
      fetchPortfolio();
    } catch (err) {
      console.error("Failed to delete farm:", err);
      showAlert("error", err.response?.data?.detail || "Error deleting farm.");
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: "32px", overflowY: "auto", height: "100%", display: "flex", flexDirection: "column", gap: "28px" }}>
      
      {/* 1. Header Row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.8rem", color: "var(--text-primary)", fontWeight: "800", margin: 0 }}>🏡 Farm Portfolio</h1>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "4px" }}>
            Manage multiple farm contexts, coordinates, and view aggregated holdings
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          ➕ Add New Farm
        </button>
      </div>

      {/* 2. Alert Notification banner */}
      {alertMsg.text && (
        <div style={{
          padding: "12px 20px",
          borderRadius: "var(--radius-sm)",
          fontSize: "0.9rem",
          fontWeight: "600",
          backgroundColor: alertMsg.type === "success" ? "rgba(56, 161, 105, 0.1)" : "rgba(229, 62, 98, 0.1)",
          color: alertMsg.type === "success" ? "#38a169" : "#e53e3e",
          borderLeft: `4px solid ${alertMsg.type === "success" ? "#38a169" : "#e53e3e"}`,
          transition: "var(--transition-smooth)",
        }}>
          {alertMsg.text}
        </div>
      )}

      {/* 3. Portfolio KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "20px" }}>
        <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "1.6rem" }}>🏡</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700", letterSpacing: "0.05em" }}>Total Farms</span>
          <h2 style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", margin: 0 }}>
            {loadingPortfolio ? "..." : portfolio.total_farms}
          </h2>
        </div>
        <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "1.6rem" }}>📐</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700", letterSpacing: "0.05em" }}>Total Holdings</span>
          <h2 style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", margin: 0 }}>
            {loadingPortfolio ? "..." : `${portfolio.total_area?.toFixed(1) || 0} Ac`}
          </h2>
        </div>
        <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "1.6rem" }}>💰</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700", letterSpacing: "0.05em" }}>Portfolio Profit</span>
          <h2 style={{ fontSize: "1.4rem", fontWeight: "800", color: "#38a169", margin: "4px 0 0" }}>
            {loadingPortfolio ? "..." : `Rs. ${portfolio.portfolio_profit?.toLocaleString()}`}
          </h2>
        </div>
        <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "1.6rem" }}>🌾</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700", letterSpacing: "0.05em" }}>Portfolio Yield</span>
          <h2 style={{ fontSize: "1.6rem", fontWeight: "800", color: "var(--primary)", margin: 0 }}>
            {loadingPortfolio ? "..." : `${portfolio.portfolio_yield?.toFixed(1) || 0} tons`}
          </h2>
        </div>
        <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "1.6rem" }}>🛡️</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700", letterSpacing: "0.05em" }}>Risk Index</span>
          <h2 style={{ fontSize: "1.8rem", fontWeight: "800", color: portfolio.portfolio_risk >= 60 ? "#e53e3e" : (portfolio.portfolio_risk >= 30 ? "#dd6b20" : "#38a169"), margin: 0 }}>
            {loadingPortfolio ? "..." : `${portfolio.portfolio_risk?.toFixed(0)}%`}
          </h2>
        </div>
        <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "8px" }}>
          <span style={{ fontSize: "1.6rem" }}>📅</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700", letterSpacing: "0.05em" }}>Active Plans</span>
          <h2 style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", margin: 0 }}>
            {loadingPortfolio ? "..." : portfolio.active_crop_plans}
          </h2>
        </div>
      </div>

      {/* 4. Farms List */}
      <div>
        <h2 style={{ fontSize: "1.3rem", color: "var(--text-primary)", marginBottom: "16px", fontWeight: "700" }}>🚜 Your Registered Farms</h2>
        
        {loadingFarms ? (
          <div style={{ textAlign: "center", padding: "60px", color: "var(--text-secondary)" }}>
            <span className="dot-spinner"></span> Loading holdings...
          </div>
        ) : farms.length === 0 ? (
          <div style={{
            textAlign: "center",
            padding: "60px",
            background: "var(--bg-surface)",
            borderRadius: "var(--radius-md)",
            border: "1px dashed var(--border-light)",
            color: "var(--text-secondary)"
          }}>
            <span style={{ fontSize: "3rem", display: "block", marginBottom: "16px" }}>🚜</span>
            <h3 style={{ fontSize: "1.2rem", marginBottom: "8px", color: "var(--text-primary)" }}>No Farms Registered</h3>
            <p style={{ marginBottom: "20px", fontSize: "0.9rem" }}>Get started by adding a farm location to activate local alerts and operations planner.</p>
            <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
              Add Your First Farm
            </button>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px" }}>
            {farms.map((farm) => {
              const isActive = currentFarmer?.active_farm_id === farm.id;
              return (
                <div key={farm.id} className="glass hover-card" style={{
                  padding: "24px",
                  borderRadius: "var(--radius-md)",
                  border: isActive ? "2px solid var(--primary)" : "1px solid var(--border-light)",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  transition: "var(--transition-bounce)",
                  position: "relative"
                }}>
                  {isActive && (
                    <span style={{
                      position: "absolute",
                      top: "16px",
                      right: "16px",
                      backgroundColor: "rgba(56, 161, 105, 0.12)",
                      color: "#38a169",
                      padding: "4px 10px",
                      borderRadius: "var(--radius-full)",
                      fontSize: "0.75rem",
                      fontWeight: "700",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px"
                    }}>
                      <span style={{
                        width: "8px",
                        height: "8px",
                        backgroundColor: "#38a169",
                        borderRadius: "50%",
                        display: "inline-block",
                        animation: "pulse-ring 2s infinite"
                      }}></span>
                      Active Context
                    </span>
                  )}
                  
                  <div>
                    <h3 style={{ fontSize: "1.25rem", color: "var(--text-primary)", fontWeight: "800", marginBottom: "12px", paddingRight: isActive ? "120px" : "0" }}>
                      {farm.name}
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "20px" }}>
                      <div>📍 <strong>Location:</strong> {farm.location}</div>
                      <div>📐 <strong>Total Area:</strong> {farm.total_area_acres} Acres</div>
                      <div>🧪 <strong>Soil Type:</strong> {farm.soil_type}</div>
                      <div>🧭 <strong>Coordinates:</strong> {farm.latitude !== null && farm.longitude !== null ? `${farm.latitude.toFixed(4)}, ${farm.longitude.toFixed(4)}` : "Not provided"}</div>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "12px", borderTop: "1px solid var(--border-light)", paddingTop: "16px", marginTop: "10px" }}>
                    {!isActive ? (
                      <button className="btn btn-secondary" onClick={() => handleActivate(farm.id)} style={{ flex: 1, padding: "8px 12px", fontSize: "0.85rem" }}>
                        Activate Farm
                      </button>
                    ) : (
                      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#38a169", fontWeight: "700", fontSize: "0.85rem" }}>
                        ✓ Context Active
                      </div>
                    )}
                    <button className="btn btn-secondary" onClick={() => handleEditClick(farm)} style={{ padding: "8px 14px", fontSize: "0.85rem" }} title="Edit Farm">
                      ✏️
                    </button>
                    <button className="btn btn-secondary" onClick={() => handleDeleteFarm(farm.id, farm.name)} style={{ padding: "8px 14px", fontSize: "0.85rem", border: "1px solid #e53e3e", color: "#e53e3e" }} title="Delete Farm">
                      🗑️
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 5. Add Farm Modal */}
      {showAddModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.5)", display: "flex",
          alignItems: "center", justifyContent: "center", zIndex: 1000
        }}>
          <div className="glass animate-fade-in" style={{
            backgroundColor: "var(--bg-card)", padding: "32px",
            borderRadius: "var(--radius-md)", width: "100%", maxWidth: "500px",
            boxShadow: "var(--shadow-lg)"
          }}>
            <h3 style={{ fontSize: "1.4rem", color: "var(--text-primary)", marginBottom: "8px", fontWeight: "800" }}>➕ Add New Farm</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "20px" }}>
              Define coordinates and soil parameters to setup farm profile context.
            </p>
            
            <form onSubmit={handleAddFarm}>
              <div className="form-group">
                <label className="form-label">Farm Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Green Valley Fields"
                  value={addForm.name}
                  onChange={(e) => setAddForm({ ...addForm, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Location (District, State) *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Ludhiana, Punjab"
                  value={addForm.location}
                  onChange={(e) => setAddForm({ ...addForm, location: e.target.value })}
                  required
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="form-group">
                  <label className="form-label">Area (Acres) *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-input"
                    placeholder="e.g. 12.5"
                    value={addForm.total_area_acres}
                    onChange={(e) => setAddForm({ ...addForm, total_area_acres: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Soil Type *</label>
                  <select
                    className="form-input"
                    value={addForm.soil_type}
                    onChange={(e) => setAddForm({ ...addForm, soil_type: e.target.value })}
                    style={{ height: "46px" }}
                  >
                    {soilTypes.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="form-group">
                  <label className="form-label">Latitude (Optional)</label>
                  <input
                    type="number"
                    step="0.000001"
                    className="form-input"
                    placeholder="e.g. 30.9010"
                    value={addForm.latitude}
                    onChange={(e) => setAddForm({ ...addForm, latitude: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Longitude (Optional)</label>
                  <input
                    type="number"
                    step="0.000001"
                    className="form-input"
                    placeholder="e.g. 75.8573"
                    value={addForm.longitude}
                    onChange={(e) => setAddForm({ ...addForm, longitude: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)} style={{ flex: 1 }}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  Add Farm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 6. Edit Farm Modal */}
      {showEditModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.5)", display: "flex",
          alignItems: "center", justifyContent: "center", zIndex: 1000
        }}>
          <div className="glass animate-fade-in" style={{
            backgroundColor: "var(--bg-card)", padding: "32px",
            borderRadius: "var(--radius-md)", width: "100%", maxWidth: "500px",
            boxShadow: "var(--shadow-lg)"
          }}>
            <h3 style={{ fontSize: "1.4rem", color: "var(--text-primary)", marginBottom: "8px", fontWeight: "800" }}>✏️ Edit Farm Details</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "20px" }}>
              Update farm metadata and parameters below.
            </p>
            
            <form onSubmit={handleUpdateFarm}>
              <div className="form-group">
                <label className="form-label">Farm Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Green Valley Fields"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Location (District, State) *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Ludhiana, Punjab"
                  value={editForm.location}
                  onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                  required
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="form-group">
                  <label className="form-label">Area (Acres) *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-input"
                    placeholder="e.g. 12.5"
                    value={editForm.total_area_acres}
                    onChange={(e) => setEditForm({ ...editForm, total_area_acres: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Soil Type *</label>
                  <select
                    className="form-input"
                    value={editForm.soil_type}
                    onChange={(e) => setEditForm({ ...editForm, soil_type: e.target.value })}
                    style={{ height: "46px" }}
                  >
                    {soilTypes.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="form-group">
                  <label className="form-label">Latitude (Optional)</label>
                  <input
                    type="number"
                    step="0.000001"
                    className="form-input"
                    placeholder="e.g. 30.9010"
                    value={editForm.latitude}
                    onChange={(e) => setEditForm({ ...editForm, latitude: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Longitude (Optional)</label>
                  <input
                    type="number"
                    step="0.000001"
                    className="form-input"
                    placeholder="e.g. 75.8573"
                    value={editForm.longitude}
                    onChange={(e) => setEditForm({ ...editForm, longitude: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
                <button type="button" className="btn btn-secondary" onClick={() => { setShowEditModal(false); setSelectedFarm(null); }} style={{ flex: 1 }}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default FarmPortfolioPage;
