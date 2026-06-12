import React, { useState, useEffect } from "react";
import api from "../../../services/api";

const RiskWarningPage = ({ onNavigateToPlanner }) => {
  const [plans, setPlans] = useState([]);
  const [loadingContext, setLoadingContext] = useState(true);
  const [assessment, setAssessment] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState("");
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    fetchContextAndWarnings();
  }, []);

  const fetchContextAndWarnings = async () => {
    setLoadingContext(true);
    setScanError("");
    try {
      // 1. Check if crop plans exist
      const plansResp = await api.get("/farm-planner/plans");
      const activePlans = plansResp.data.filter(p => p.status === "active");
      setPlans(activePlans);

      if (activePlans.length > 0) {
        // 2. Fetch latest generated warnings
        const warningsResp = await api.get("/risk-intelligence/warnings");
        setAssessment(warningsResp.data);
      }
      
      // 3. Fetch history
      await fetchHistory();
    } catch (err) {
      console.error("Failed to load risk context:", err);
    } finally {
      setLoadingContext(false);
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const resp = await api.get("/risk-intelligence/history");
      setHistory(resp.data);
    } catch (err) {
      console.error("Failed to fetch risk history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleScan = async () => {
    if (plans.length === 0 || scanning) return;
    setScanning(true);
    setScanError("");
    try {
      const resp = await api.post("/risk-intelligence/generate");
      setAssessment(resp.data);
      fetchHistory();
    } catch (err) {
      console.error("Failed to scan for risks:", err);
      setScanError(
        err.response?.data?.detail || "Pest & Disease risk scan failed. Please try again."
      );
    } finally {
      setScanning(false);
    }
  };

  const getSeverityStyles = (severity) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return { color: "#742a2a", bg: "#fff5f5", border: "#fed7d7", label: "Critical" };
      case "high":
        return { color: "#9b2c2c", bg: "#fff5f5", border: "#feb2b2", label: "High" };
      case "medium":
        return { color: "#c05621", bg: "#fffaf0", border: "#fbd38d", label: "Medium" };
      default:
        return { color: "#2c5282", bg: "#ebf8ff", border: "#bee3f8", label: "Low" };
    }
  };

  const getRiskScoreColor = (score) => {
    if (score <= 30) return "#38a169"; // Green
    if (score <= 60) return "#dd6b20"; // Orange
    if (score <= 80) return "#e53e3e"; // Red
    return "#822727"; // Dark Red
  };

  if (loadingContext) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "calc(100vh - 100px)", color: "var(--text-secondary)" }}>
        <span className="dot-spinner"></span> Analyzing crop hazard indicators...
      </div>
    );
  }

  // Prerequisite check: Farmer must have active plans
  if (plans.length === 0) {
    return (
      <div style={{ padding: "32px", height: "calc(100vh - 100px)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="glass text-center animate-fade-in" style={{ padding: "40px", borderRadius: "var(--radius-md)", maxWidth: "550px" }}>
          <span style={{ fontSize: "3.5rem", display: "block", marginBottom: "16px" }}>🛡️</span>
          <h3 style={{ fontSize: "1.35rem", fontWeight: "800", color: "var(--text-primary)", marginBottom: "12px" }}>
            Prerequisites Missing
          </h3>
          <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "24px" }}>
            Please create an active crop plan in the Farm Operations Planner before generating proactive pest, disease, and weather risk warnings.
          </p>
          <button className="btn btn-primary" onClick={onNavigateToPlanner} style={{ padding: "10px 24px", height: "44px" }}>
            📅 Navigate to Farm Planner
          </button>
        </div>
      </div>
    );
  }

  const alertsList = assessment?.alerts || [];
  const pestAlerts = alertsList.filter(a => a.category === "pest");
  const diseaseAlerts = alertsList.filter(a => a.category === "disease");
  const weatherAlerts = alertsList.filter(a => a.category === "weather");

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 340px",
        gap: "24px",
        padding: "32px",
        height: "calc(100vh - 100px)",
        overflow: "hidden",
      }}
    >
      {/* Main Panel */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "24px",
          overflowY: "auto",
          paddingRight: "8px",
        }}
      >
        {/* Top Assessment Overview Header */}
        <div
          className="glass"
          style={{
            padding: "24px",
            borderRadius: "var(--radius-md)",
            display: "grid",
            gridTemplateColumns: "140px 1fr 200px",
            gap: "24px",
            alignItems: "center",
          }}
        >
          {/* Overall Risk Score Dynamic Gauge */}
          <div style={{ position: "relative", width: "120px", height: "120px", margin: "0 auto" }}>
            <svg width="120" height="120" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border-light)" strokeWidth="8" />
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke={getRiskScoreColor(assessment?.overall_risk_score || 0)}
                strokeWidth="8"
                strokeDasharray="314.16"
                strokeDashoffset={314.16 - ((assessment?.overall_risk_score || 0) / 100) * 314.16}
                strokeLinecap="round"
                transform="rotate(-90 60 60)"
                style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
              />
            </svg>
            <div
              style={{
                position: "absolute",
                top: 0, left: 0, right: 0, bottom: 0,
                display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              }}
            >
              <span style={{ fontSize: "1.8rem", fontWeight: "900", color: "var(--text-primary)", lineHeight: 1 }}>
                {assessment?.overall_risk_score || 0}
              </span>
              <span style={{ fontSize: "0.6rem", color: "var(--text-secondary)", fontWeight: "800", textTransform: "uppercase", letterSpacing: "0.05em", marginTop: "2px" }}>
                Risk Index
              </span>
            </div>
          </div>

          {/* Warning Summary Status */}
          <div>
            <span style={{ fontSize: "0.7rem", fontWeight: "800", color: "var(--primary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Active Farm Risk Assessment
            </span>
            <h3 style={{ fontSize: "1.4rem", fontWeight: "900", color: "var(--text-primary)", margin: "4px 0 6px" }}>
              Overall Farm Risk: <span style={{ color: getRiskScoreColor(assessment?.overall_risk_score || 0) }}>{assessment?.risk_level || "Low"}</span>
            </h3>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", margin: 0, lineHeight: "1.4" }}>
              Evaluating conditions across **{plans.length} active crop plan(s)**. Outbreaks are estimated using local soil report metrics and forecast moisture charts.
            </p>
          </div>

          {/* Scanning Action */}
          <div style={{ textAlign: "right" }}>
            <button
              className="btn btn-primary"
              disabled={scanning}
              onClick={handleScan}
              style={{
                width: "100%",
                height: "44px",
                boxShadow: "var(--shadow-md)",
              }}
            >
              {scanning ? (
                <>
                  <span className="dot-spinner"></span> Scanning...
                </>
              ) : "🛡️ Scan For Risks"}
            </button>
            {scanError && (
              <span style={{ fontSize: "0.7rem", color: "#e53e3e", display: "block", marginTop: "6px", textAlign: "center" }}>
                ⚠️ {scanError}
              </span>
            )}
          </div>
        </div>

        {/* Dynamic Risk Categories Grid Columns */}
        {alertsList.length === 0 ? (
          <div className="glass" style={{ padding: "48px", textAlign: "center", borderRadius: "var(--radius-md)", color: "var(--text-secondary)" }}>
            <span style={{ fontSize: "2.5rem", display: "block", marginBottom: "12px" }}>✅</span>
            <h4>No Proactive Hazards Detected</h4>
            <p style={{ fontSize: "0.85rem", margin: "4px 0 0" }}>Click "Scan For Risks" to run the dynamic warning intelligence engine.</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Disease Section */}
            {diseaseAlerts.length > 0 && (
              <div>
                <h4 style={{ fontSize: "1.1rem", fontWeight: "800", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
                  🦠 Disease Infection Risks
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                  {diseaseAlerts.map(alert => renderAlertCard(alert))}
                </div>
              </div>
            )}

            {/* Pest Section */}
            {pestAlerts.length > 0 && (
              <div>
                <h4 style={{ fontSize: "1.1rem", fontWeight: "800", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
                  🐛 Pest Outbreak Risks
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                  {pestAlerts.map(alert => renderAlertCard(alert))}
                </div>
              </div>
            )}

            {/* Weather Section */}
            {weatherAlerts.length > 0 && (
              <div>
                <h4 style={{ fontSize: "1.1rem", fontWeight: "800", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
                  ⚠️ Weather Hazard Risks
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                  {weatherAlerts.map(alert => renderAlertCard(alert))}
                </div>
              </div>
            )}

          </div>
        )}
      </div>

      {/* Right Sidebar history */}
      <div
        className="glass"
        style={{
          borderRadius: "var(--radius-md)",
          padding: "24px 16px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          overflowY: "hidden",
        }}
      >
        <h3
          style={{
            fontSize: "1.1rem",
            padding: "0 8px",
            color: "var(--text-primary)",
            borderBottom: "1px solid var(--border-light)",
            paddingBottom: "12px",
            margin: 0,
          }}
        >
          📜 Risk Warning Logs
        </h3>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            overflowY: "auto",
            flex: 1,
            padding: "2px",
          }}
        >
          {loadingHistory ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              <span className="dot-spinner"></span> Loading history...
            </div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              No warnings logged yet. Run a risk assessment scan!
            </div>
          ) : (
            history.map((h) => {
              const styles = getSeverityStyles(h.severity);
              return (
                <div
                  key={h.id}
                  className="glass hover-card"
                  style={{
                    padding: "12px",
                    borderRadius: "var(--radius-sm)",
                    backgroundColor: "var(--bg-card)",
                    borderLeft: `4px solid ${styles.color}`,
                    transition: "var(--transition-smooth)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ fontSize: "0.8rem", color: "var(--text-primary)" }}>
                      {h.alert_title}
                    </strong>
                    <span
                      style={{
                        fontSize: "0.6rem",
                        fontWeight: "800",
                        color: styles.color,
                        backgroundColor: styles.bg,
                        padding: "2px 6px",
                        borderRadius: "4px",
                      }}
                    >
                      {styles.label}
                    </span>
                  </div>
                  <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", margin: "4px 0 8px" }}>
                    Crop: <strong>{h.crop_name}</strong> | Probability: <strong>{h.probability}%</strong>
                  </p>
                  <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textAlign: "right" }}>
                    {new Date(h.created_at).toLocaleString()}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );

  function renderAlertCard(alert) {
    const sevStyles = getSeverityStyles(alert.severity);
    const categoryIcons = {
      pest: "🐛",
      disease: "🦠",
      weather: "⚠️"
    };

    return (
      <div
        className="glass hover-card"
        key={alert.id}
        style={{
          padding: "20px",
          borderRadius: "var(--radius-md)",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          backgroundColor: "var(--bg-card)",
          borderLeft: `5px solid ${sevStyles.color}`,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", fontWeight: "700", textTransform: "uppercase" }}>
              {categoryIcons[alert.category] || "🛡️"} {alert.crop_name} Warning
            </span>
            <h4 style={{ fontSize: "1.05rem", fontWeight: "800", color: "var(--text-primary)", margin: "2px 0 0" }}>
              {alert.alert_title}
            </h4>
          </div>
          <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
            <span
              style={{
                fontSize: "0.6rem",
                fontWeight: "800",
                textTransform: "uppercase",
                padding: "2px 8px",
                borderRadius: "4px",
                color: sevStyles.color,
                backgroundColor: sevStyles.bg,
                border: `1px solid ${sevStyles.border}`,
              }}
            >
              {sevStyles.label}
            </span>
            <span style={{ fontSize: "0.75rem", fontWeight: "800", color: sevStyles.color }}>
              {alert.probability}%
            </span>
          </div>
        </div>

        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.4", margin: 0 }}>
          {alert.description}
        </p>

        {/* Prevention Steps Checklist */}
        <div>
          <span style={{ fontSize: "0.7rem", fontWeight: "800", color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "6px" }}>
            🛡️ Prevention Measures
          </span>
          <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
            {alert.prevention_steps.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ul>
        </div>

        {/* Monitoring Advice Checklist */}
        <div>
          <span style={{ fontSize: "0.7rem", fontWeight: "800", color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "6px" }}>
            🔍 Scouting & Monitoring Advice
          </span>
          <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
            {alert.monitoring_advice.map((advice, idx) => (
              <li key={idx}>{advice}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
};

export default RiskWarningPage;
