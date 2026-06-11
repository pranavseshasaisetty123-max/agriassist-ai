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
        return { color: "#e53e3e", bg: "#fff5f5", border: "#f8b4b4", icon: "🚨" };
      case "warning":
        return { color: "#dd6b20", bg: "#fffaf0", border: "#fbd38d", icon: "⚠️" };
      default:
        return { color: "var(--primary)", bg: "var(--primary-soft)", border: "var(--border-light)", icon: "💡" };
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
          style={{ padding: "6px 12px", fontSize: "0.75rem", border: `1px solid ${styles.color}`, color: styles.color }}
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
              borderRadius: "var(--radius-sm)",
              fontSize: "0.875rem",
              lineHeight: "1.4",
              color: "var(--text-primary)"
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
