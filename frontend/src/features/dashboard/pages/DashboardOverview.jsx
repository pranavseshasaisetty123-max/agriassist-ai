import React, { useEffect, useState } from "react";
import api from "../../../services/api";

const DashboardOverview = ({ onNavigateToChat, onNavigateToSoil }) => {
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
    // Basic agricultural thresholds for demo status badges
    if (name === "ph") {
      if (val < 6.0) return { label: "Acidic", class: "status-low", color: "#e53e3e" };
      if (val > 7.5) return { label: "Alkaline", class: "status-high", color: "#dd6b20" };
      return { label: "Optimal", class: "status-optimal", color: "#38a169" };
    }
    // NPK ranges in mg/kg
    if (val < 30) return { label: "Low (Deficient)", class: "status-low", color: "#e53e3e" };
    if (val < 80) return { label: "Moderate", class: "status-moderate", color: "#d69e2e" };
    return { label: "Optimal", class: "status-optimal", color: "#38a169" };
  };

  return (
    <div className="dashboard-scroll-container animate-fade-in" style={{ padding: "32px", overflowY: "auto", height: "100%" }}>
      <div className="dashboard-hero" style={{
        background: "linear-gradient(135deg, var(--primary) 0%, hsl(var(--primary-hue), var(--primary-sat), 15%) 100%)",
        color: "var(--text-light)",
        borderRadius: "var(--radius-md)",
        padding: "32px",
        marginBottom: "32px",
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
            Log soil reports, get AI-powered fertilizer recommendations tailored for your planned crops, and consult with our agronomist chatbot.
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

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px", marginBottom: "32px" }}>
        {/* Quick Action Card 1 */}
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

        {/* Quick Action Card 2 */}
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
      </div>

      <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)" }}>
        <h2 style={{ fontSize: "1.35rem", marginBottom: "20px", color: "var(--text-primary)" }}>📊 Recent Soil Health Status</h2>
        
        {loading ? (
          <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)" }}>
            <span className="dot-spinner"></span> Loading diagnostics...
          </div>
        ) : !latestReport ? (
          <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)" }}>
            <p style={{ marginBottom: "16px" }}>No soil test reports logged yet.</p>
            <button className="btn btn-primary" onClick={onNavigateToSoil}>
              🧪 Log First Soil Test
            </button>
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "16px", marginBottom: "24px", paddingBottom: "16px", borderBottom: "1px solid var(--border-light)" }}>
              <div>
                <h4 style={{ fontSize: "1.1rem", color: "var(--text-primary)" }}>Target Crop: <strong>{latestReport.crop_planned}</strong></h4>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Tested on {new Date(latestReport.tested_at).toLocaleDateString()}</p>
              </div>
              <div>
                <button className="btn btn-secondary" onClick={onNavigateToSoil}>
                  View Analyzer Timeline
                </button>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "20px" }}>
              {/* pH dial */}
              <div style={{ textAlign: "center", padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)", display: "block", marginBottom: "8px" }}>Soil pH</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", marginBottom: "4px" }}>{latestReport.ph}</div>
                <span style={{
                  fontSize: "0.75rem",
                  fontWeight: "600",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: getNutrientStatus(latestReport.ph, "ph").color + "20",
                  color: getNutrientStatus(latestReport.ph, "ph").color
                }}>{getNutrientStatus(latestReport.ph, "ph").label}</span>
              </div>

              {/* N dial */}
              <div style={{ textAlign: "center", padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)", display: "block", marginBottom: "8px" }}>Nitrogen (N)</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", marginBottom: "4px" }}>{latestReport.nitrogen} <span style={{ fontSize: "0.75rem", fontWeight: "500" }}>mg/kg</span></div>
                <span style={{
                  fontSize: "0.75rem",
                  fontWeight: "600",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: getNutrientStatus(latestReport.nitrogen, "n").color + "20",
                  color: getNutrientStatus(latestReport.nitrogen, "n").color
                }}>{getNutrientStatus(latestReport.nitrogen, "n").label}</span>
              </div>

              {/* P dial */}
              <div style={{ textAlign: "center", padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)", display: "block", marginBottom: "8px" }}>Phosphorus (P)</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", marginBottom: "4px" }}>{latestReport.phosphorus} <span style={{ fontSize: "0.75rem", fontWeight: "500" }}>mg/kg</span></div>
                <span style={{
                  fontSize: "0.75rem",
                  fontWeight: "600",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: getNutrientStatus(latestReport.phosphorus, "p").color + "20",
                  color: getNutrientStatus(latestReport.phosphorus, "p").color
                }}>{getNutrientStatus(latestReport.phosphorus, "p").label}</span>
              </div>

              {/* K dial */}
              <div style={{ textAlign: "center", padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)", display: "block", marginBottom: "8px" }}>Potassium (K)</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--text-primary)", marginBottom: "4px" }}>{latestReport.potassium} <span style={{ fontSize: "0.75rem", fontWeight: "500" }}>mg/kg</span></div>
                <span style={{
                  fontSize: "0.75rem",
                  fontWeight: "600",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: getNutrientStatus(latestReport.potassium, "k").color + "20",
                  color: getNutrientStatus(latestReport.potassium, "k").color
                }}>{getNutrientStatus(latestReport.potassium, "k").label}</span>
              </div>
            </div>

            {latestReport.recommendation ? (
              <div style={{
                marginTop: "24px",
                padding: "20px",
                backgroundColor: "var(--primary-soft)",
                borderRadius: "var(--radius-sm)",
                borderLeft: "4px solid var(--primary)"
              }}>
                <h5 style={{ fontSize: "1rem", color: "var(--primary)", marginBottom: "8px", fontWeight: "700" }}>🌿 Current AI Fertilizer Recommendation Status</h5>
                <p style={{ fontSize: "0.875rem", color: "var(--text-primary)", lineHeight: "1.5" }}>
                  {latestReport.recommendation.ai_raw_analysis.substring(0, 180)}...
                </p>
                <span style={{ fontSize: "0.8rem", fontWeight: "600", color: "var(--primary)", marginTop: "8px", display: "inline-block", cursor: "pointer" }} onClick={onNavigateToSoil}>
                  Read Full Recommendations & Fertilizer Schedule ➔
                </span>
              </div>
            ) : (
              <div style={{
                marginTop: "24px",
                padding: "20px",
                backgroundColor: "#fffdf5",
                borderRadius: "var(--radius-sm)",
                borderLeft: "4px solid var(--accent)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px"
              }}>
                <div>
                  <h5 style={{ fontSize: "1rem", color: "var(--accent)", marginBottom: "4px", fontWeight: "700" }}>⚠️ Recommendations Pending</h5>
                  <p style={{ fontSize: "0.875rem", color: "var(--text-primary)" }}>
                    You have not generated the AI agronomist analysis for this report yet.
                  </p>
                </div>
                <button className="btn btn-primary" onClick={onNavigateToSoil} style={{ backgroundColor: "var(--accent)", boxShadow: "none" }}>
                  Analyze Soil
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardOverview;
