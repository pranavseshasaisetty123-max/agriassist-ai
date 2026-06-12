import React, { useEffect, useState } from "react";
import api from "../../../services/api";
import WeatherWidget from "../components/WeatherWidget";
import ForecastWidget from "../components/ForecastWidget";
import AdvisoryWidget from "../components/AdvisoryWidget";

const DashboardOverview = ({ onNavigateToChat, onNavigateToSoil, onNavigateToMarket }) => {
  const [latestReport, setLatestReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLatestReport = async () => {
      try {
        const response = await api.get("/soil/reports?limit=1");
        if (response.data && response.data.length > 0) {
          setLatestReport(response.data[0]);
        }
      } catch (error) {
        console.error("Failed to load latest soil report:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLatestReport();
  }, []);

  const getNutrientStatus = (val, name) => {
    if (name === "ph") {
      if (val < 6.0) return { label: "Acidic", class: "status-low", color: "#e53e3e" };
      if (val > 7.5) return { label: "Alkaline", class: "status-high", color: "#dd6b20" };
      return { label: "Optimal", class: "status-optimal", color: "#38a169" };
    }
    if (val < 30) return { label: "Low (Deficient)", class: "status-low", color: "#e53e3e" };
    if (val < 80) return { label: "Moderate", class: "status-moderate", color: "#d69e2e" };
    return { label: "Optimal", class: "status-optimal", color: "#38a169" };
  };

  return (
    <div className="dashboard-scroll-container animate-fade-in" style={{ padding: "32px", overflowY: "auto", height: "100%", display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* 1. Hero banner */}
      <div className="dashboard-hero" style={{
        background: "linear-gradient(135deg, var(--primary) 0%, hsl(var(--primary-hue), var(--primary-sat), 15%) 100%)",
        color: "var(--text-light)",
        borderRadius: "var(--radius-md)",
        padding: "32px",
        boxShadow: "var(--shadow-lg)",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{ position: "relative", zIndex: 2 }}>
          <span style={{
            fontSize: "0.85rem",
            fontWeight: "700",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            backgroundColor: "rgba(255, 255, 255, 0.15)",
            padding: "4px 12px",
            borderRadius: "var(--radius-full)",
            marginBottom: "12px",
            display: "inline-block"
          }}>🌾 Smart Agriculture Dashboard</span>
          <h1 style={{ fontSize: "2rem", marginBottom: "8px", fontWeight: "800" }}>Manage Your Soil Health</h1>
          <p style={{ fontSize: "1rem", opacity: 0.9, maxWidth: "600px", lineHeight: "1.5" }}>
            Log soil reports, get AI-powered fertilizer recommendations tailored for planned crops, and monitor weather variables.
          </p>
        </div>
        <div style={{
          position: "absolute",
          right: "-50px",
          bottom: "-50px",
          fontSize: "12rem",
          opacity: 0.08,
          transform: "rotate(-15deg)",
          userSelect: "none",
          pointerEvents: "none"
        }}>🌱</div>
      </div>

      {/* 2. Weather Section Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px" }}>
        <WeatherWidget />
        <ForecastWidget />
      </div>

      {/* 3. Action Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px" }}>
        <div className="glass" style={{
          padding: "24px",
          borderRadius: "var(--radius-md)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          transition: "var(--transition-bounce)",
          cursor: "pointer"
        }} onClick={onNavigateToSoil}>
          <div>
            <span style={{ fontSize: "2rem", marginBottom: "16px", display: "block" }}>🧪</span>
            <h3 style={{ fontSize: "1.2rem", marginBottom: "8px", color: "var(--text-primary)" }}>Soil Health Analyzer</h3>
            <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: "1.5", marginBottom: "16px" }}>
              Input your soil pH, Nitrogen, Phosphorus, and Potassium values to generate step-by-step treatment recommendations.
            </p>
          </div>
          <span style={{ fontSize: "0.9rem", fontWeight: "600", color: "var(--primary)" }}>Configure reports ➔</span>
        </div>

        <div className="glass" style={{
          padding: "24px",
          borderRadius: "var(--radius-md)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          transition: "var(--transition-bounce)",
          cursor: "pointer"
        }} onClick={onNavigateToChat}>
          <div>
            <span style={{ fontSize: "2rem", marginBottom: "16px", display: "block" }}>💬</span>
            <h3 style={{ fontSize: "1.2rem", marginBottom: "8px", color: "var(--text-primary)" }}>AI Agronomist Consultation</h3>
            <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: "1.5", marginBottom: "16px" }}>
              Ask immediate questions regarding crop health, pest treatments, regional schedules, or weather actions.
            </p>
          </div>
          <span style={{ fontSize: "0.9rem", fontWeight: "600", color: "var(--primary)" }}>Consult agent ➔</span>
        </div>

        <div className="glass" style={{
          padding: "24px",
          borderRadius: "var(--radius-md)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          transition: "var(--transition-bounce)",
          cursor: "pointer"
        }} onClick={onNavigateToMarket}>
          <div>
            <span style={{ fontSize: "2rem", marginBottom: "16px", display: "block" }}>📈</span>
            <h3 style={{ fontSize: "1.2rem", marginBottom: "8px", color: "var(--text-primary)" }}>Market Price Intelligence</h3>
            <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: "1.5", marginBottom: "16px" }}>
              Analyze historical crop price trends across states and compute yield-to-profit return margins instantly.
            </p>
          </div>
          <span style={{ fontSize: "0.9rem", fontWeight: "600", color: "var(--primary)" }}>Analyze markets ➔</span>
        </div>
      </div>

      {/* 4. Split Status & Advisory Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "24px" }}>
        {/* Soil health status */}
        <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column" }}>
          <h2 style={{ fontSize: "1.25rem", marginBottom: "20px", color: "var(--text-primary)", fontWeight: "700" }}>📊 Recent Soil Health</h2>
          
          {loading ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span className="dot-spinner"></span> Loading diagnostics...
            </div>
          ) : !latestReport ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
              <p style={{ marginBottom: "16px" }}>No soil test reports logged yet.</p>
              <button className="btn btn-primary" onClick={onNavigateToSoil}>
                Log First Soil Test
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px", flex: 1 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
                <div>
                  <h4 style={{ fontSize: "1rem", color: "var(--text-primary)" }}>Planned Crop: <strong>{latestReport.crop_planned}</strong></h4>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Tested on {new Date(latestReport.tested_at).toLocaleDateString()}</p>
                </div>
                <button className="btn btn-secondary" onClick={onNavigateToSoil} style={{ padding: "6px 12px", fontSize: "0.75rem" }}>
                  View Analyzer
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div style={{ padding: "12px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Soil pH</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", margin: "4px 0" }}>{latestReport.ph}</div>
                  <span style={{
                    fontSize: "0.7rem",
                    fontWeight: "600",
                    padding: "1px 6px",
                    borderRadius: "var(--radius-full)",
                    backgroundColor: getNutrientStatus(latestReport.ph, "ph").color + "20",
                    color: getNutrientStatus(latestReport.ph, "ph").color
                  }}>{getNutrientStatus(latestReport.ph, "ph").label}</span>
                </div>

                <div style={{ padding: "12px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Nitrogen</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", margin: "4px 0" }}>{latestReport.nitrogen}</div>
                  <span style={{
                    fontSize: "0.7rem",
                    fontWeight: "600",
                    padding: "1px 6px",
                    borderRadius: "var(--radius-full)",
                    backgroundColor: getNutrientStatus(latestReport.nitrogen, "n").color + "20",
                    color: getNutrientStatus(latestReport.nitrogen, "n").color
                  }}>{getNutrientStatus(latestReport.nitrogen, "n").label}</span>
                </div>

                <div style={{ padding: "12px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Phosphorus</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", margin: "4px 0" }}>{latestReport.phosphorus}</div>
                  <span style={{
                    fontSize: "0.7rem",
                    fontWeight: "600",
                    padding: "1px 6px",
                    borderRadius: "var(--radius-full)",
                    backgroundColor: getNutrientStatus(latestReport.phosphorus, "p").color + "20",
                    color: getNutrientStatus(latestReport.phosphorus, "p").color
                  }}>{getNutrientStatus(latestReport.phosphorus, "p").label}</span>
                </div>

                <div style={{ padding: "12px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Potassium</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", margin: "4px 0" }}>{latestReport.potassium}</div>
                  <span style={{
                    fontSize: "0.7rem",
                    fontWeight: "600",
                    padding: "1px 6px",
                    borderRadius: "var(--radius-full)",
                    backgroundColor: getNutrientStatus(latestReport.potassium, "k").color + "20",
                    color: getNutrientStatus(latestReport.potassium, "k").color
                  }}>{getNutrientStatus(latestReport.potassium, "k").label}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* AI Weather-Soil Smart Advisory */}
        <AdvisoryWidget />
      </div>
    </div>
  );
};

export default DashboardOverview;
