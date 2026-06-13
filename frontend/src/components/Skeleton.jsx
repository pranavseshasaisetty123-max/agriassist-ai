import React from "react";

const skeletonStyle = {
  background: "linear-gradient(90deg, var(--border-light) 25%, rgba(0,0,0,0.05) 50%, var(--border-light) 75%)",
  backgroundSize: "200% 100%",
  animation: "shimmer 1.5s infinite",
  borderRadius: "var(--radius-sm)"
};

export const CardSkeleton = () => {
  return (
    <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={{ ...skeletonStyle, height: "24px", width: "40%" }}></div>
      <div style={{ ...skeletonStyle, height: "16px", width: "80%" }}></div>
      <div style={{ ...skeletonStyle, height: "16px", width: "60%" }}></div>
      <div style={{ display: "flex", gap: "12px", marginTop: "12px" }}>
        <div style={{ ...skeletonStyle, height: "36px", flex: 1 }}></div>
        <div style={{ ...skeletonStyle, height: "36px", width: "40px" }}></div>
      </div>
    </div>
  );
};

export const ChartSkeleton = () => {
  return (
    <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "16px", minHeight: "220px" }}>
      <div style={{ ...skeletonStyle, height: "20px", width: "30%" }}></div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: "24px", flex: 1, minHeight: "140px", padding: "10px 0" }}>
        <div style={{ ...skeletonStyle, height: "60%", flex: 1 }}></div>
        <div style={{ ...skeletonStyle, height: "80%", flex: 1 }}></div>
        <div style={{ ...skeletonStyle, height: "40%", flex: 1 }}></div>
        <div style={{ ...skeletonStyle, height: "90%", flex: 1 }}></div>
        <div style={{ ...skeletonStyle, height: "70%", flex: 1 }}></div>
      </div>
    </div>
  );
};

export const TableSkeleton = ({ rows = 5 }) => {
  return (
    <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "12px" }}>
      <div style={{ display: "flex", gap: "20px", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
        <div style={{ ...skeletonStyle, height: "16px", flex: 2 }}></div>
        <div style={{ ...skeletonStyle, height: "16px", flex: 1 }}></div>
        <div style={{ ...skeletonStyle, height: "16px", flex: 1 }}></div>
      </div>
      {Array.from({ length: rows }).map((_, idx) => (
        <div key={idx} style={{ display: "flex", gap: "20px", padding: "8px 0" }}>
          <div style={{ ...skeletonStyle, height: "16px", flex: 2 }}></div>
          <div style={{ ...skeletonStyle, height: "16px", flex: 1 }}></div>
          <div style={{ ...skeletonStyle, height: "16px", flex: 1 }}></div>
        </div>
      ))}
    </div>
  );
};

export const TextSkeleton = () => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px", width: "100%" }}>
      <div style={{ ...skeletonStyle, height: "14px", width: "100%" }}></div>
      <div style={{ ...skeletonStyle, height: "14px", width: "95%" }}></div>
      <div style={{ ...skeletonStyle, height: "14px", width: "80%" }}></div>
    </div>
  );
};

// Insert keyframes into document header
const injectStyle = () => {
  if (typeof window !== "undefined") {
    const styleId = "skeleton-shimmer-style";
    if (!document.getElementById(styleId)) {
      const style = document.createElement("style");
      style.id = styleId;
      style.textContent = `
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `;
      document.head.appendChild(style);
    }
  }
};
injectStyle();
