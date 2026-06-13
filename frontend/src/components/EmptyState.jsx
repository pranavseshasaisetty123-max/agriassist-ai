import React from "react";

const EmptyState = ({ icon = "🌾", title = "No data available", description = "Get started by logging parameters or triggering a diagnostic.", actionLabel, onAction }) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      textAlign: "center",
      padding: "48px 24px",
      background: "var(--bg-surface)",
      backdropFilter: "blur(8px)",
      borderRadius: "var(--radius-md)",
      border: "1px dashed var(--border-light)",
      boxShadow: "var(--shadow-sm)",
      gap: "12px",
      margin: "16px 0"
    }}>
      <span style={{ fontSize: "2.5rem", marginBottom: "8px" }}>{icon}</span>
      <h3 style={{
        fontSize: "1.15rem",
        color: "var(--text-primary)",
        fontWeight: "700",
        fontFamily: "'Outfit', sans-serif",
        margin: 0
      }}>{title}</h3>
      <p style={{
        fontSize: "0.875rem",
        color: "var(--text-secondary)",
        maxWidth: "360px",
        lineHeight: "1.4",
        margin: "0 0 8px"
      }}>{description}</p>
      {actionLabel && onAction && (
        <button className="btn btn-primary" onClick={onAction} style={{ padding: "8px 16px", fontSize: "0.8rem" }}>
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
