import React, { useEffect, useState } from "react";
import api from "../../../services/api";

const AdvisoryWidget = () => {
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAdvisory = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await api.get("/weather/advisory");
      setAdvisory(response.data);
    } catch (error) {
      console.error("Failed to load advisory:", error);
      setError(error.response?.data?.detail || "Failed to load advisory.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdvisory();
  }, []);

  const getSeverityStyles = (sev) => {
    switch (sev.toLowerCase()) {
      case "critical":
        return {
          color: "var(--advisory-critical-text)",
          bg: "var(--advisory-critical-bg)",
          border: "var(--advisory-critical-border)",
          icon: "🚨"
        };
      case "warning":
        return {
          color: "var(--advisory-warning-text)",
          bg: "var(--advisory-warning-bg)",
          border: "var(--advisory-warning-border)",
          icon: "⚠️"
        };
      default:
        return {
          color: "var(--advisory-info-text)",
          bg: "var(--advisory-info-bg)",
          border: "var(--advisory-info-border)",
          icon: "💡"
        };
    }
  };

  if (loading) {
    return (
      <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "200px" }}>
        <span className="dot-spinner"></span> Compiling AI farming advisories...
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)", minHeight: "200px" }}>
        <h3 style={{ fontSize: "1.1rem", color: "var(--text-primary)", marginBottom: "12px", fontWeight: "700" }}>💡 Smart Farming Advisory</h3>
        <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>{error}</p>
      </div>
    );
  }

  if (!advisory) return null;

  const styles = getSeverityStyles(advisory.severity);

  return (
    <div className="glass animate-fade-in" style={{
      padding: "28px",
      borderRadius: "var(--radius-md)",
      display: "flex",
      flexDirection: "column",
      gap: "16px",
      borderLeft: `4px solid ${styles.color}`
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
        <div>
          <h3 style={{ fontSize: "1.1rem", color: "var(--text-primary)", fontWeight: "700" }}>
            {styles.icon} AI Weather-Soil Advisory
          </h3>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
            For Planned Crop: <strong>{advisory.crop}</strong>
          </span>
        </div>
        <button
          className="btn btn-secondary"
          onClick={fetchAdvisory}
          style={{
            padding: "6px 12px",
            fontSize: "0.75rem",
            border: `1px solid ${styles.color}`,
            color: styles.color,
            backgroundColor: "transparent",
            transition: "var(--transition-smooth)"
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = styles.bg;
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
          }}
        >
          🔄 Refresh
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {advisory.advisory_points.map((point, index) => (
          <div
            key={index}
            style={{
              padding: "12px 16px",
              backgroundColor: styles.bg,
              border: `1px solid ${styles.border}`,
              borderRadius: "var(--radius-sm)",
              fontSize: "0.875rem",
              lineHeight: "1.4",
              color: "var(--text-primary)",
              transition: "var(--transition-smooth)"
            }}
          >
            {point}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdvisoryWidget;
