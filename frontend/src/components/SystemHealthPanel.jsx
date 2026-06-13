import React, { useState, useEffect } from "react";
import api from "../services/api";

const SystemHealthPanel = () => {
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchStatus = async () => {
    try {
      setError(false);
      const resp = await api.get("/system/status");
      setStatusData(resp.data);
    } catch (err) {
      console.error("Failed to load health status:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Poll every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "16px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
        Loading diagnostics...
      </div>
    );
  }

  if (error || !statusData) {
    return (
      <div style={{
        padding: "16px",
        borderRadius: "var(--radius-sm)",
        backgroundColor: "rgba(229, 62, 98, 0.1)",
        color: "#e53e3e",
        fontSize: "0.85rem",
        fontWeight: "600",
        border: "1px solid rgba(229, 62, 98, 0.2)"
      }}>
        ⚠️ Unable to establish contact with backend diagnostics.
      </div>
    );
  }

  const renderStatusIndicator = (status) => {
    const isOk = status === "healthy" || status === "connected" || status === "online";
    return (
      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
        <span style={{
          width: "8px",
          height: "8px",
          borderRadius: "50%",
          backgroundColor: isOk ? "#38a169" : "#e53e3e",
          display: "inline-block",
          boxShadow: isOk ? "0 0 8px #38a169" : "0 0 8px #e53e3e"
        }} />
        <span style={{
          fontSize: "0.85rem",
          fontWeight: "700",
          color: isOk ? "#38a169" : "#e53e3e",
          textTransform: "capitalize"
        }}>{status}</span>
      </div>
    );
  };

  return (
    <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "12px" }}>
      <h4 style={{
        fontSize: "0.95rem",
        fontWeight: "800",
        fontFamily: "'Outfit', sans-serif",
        color: "var(--text-primary)",
        margin: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between"
      }}>
        <span>🛠️ System Diagnostics</span>
        <span
          onClick={fetchStatus}
          style={{ cursor: "pointer", fontSize: "0.8rem", color: "var(--primary)", fontWeight: "600" }}
          title="Refresh stats"
        >
          ↻ Check
        </span>
      </h4>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "4px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>API Server:</span>
          {renderStatusIndicator(statusData.backend_status)}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Database:</span>
          {renderStatusIndicator(statusData.database_status)}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Gemini AI:</span>
          {renderStatusIndicator(statusData.gemini_status)}
        </div>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderTop: "1px solid var(--border-light)",
          paddingTop: "8px",
          marginTop: "4px"
        }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>API Response:</span>
          <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--text-primary)" }}>
            ⚡ {statusData.last_api_response_time} ms
          </span>
        </div>
      </div>
    </div>
  );
};

export default SystemHealthPanel;
