import React from "react";

const PageLoader = ({ message = "Loading AgriAssist AI..." }) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      width: "100vw",
      backgroundColor: "var(--bg-app)",
      fontFamily: "'Outfit', sans-serif",
      color: "var(--primary)"
    }}>
      <div style={{
        width: "50px",
        height: "50px",
        border: "5px solid var(--border-light)",
        borderTop: "5px solid var(--primary)",
        borderRadius: "50%",
        animation: "spin 1s linear infinite",
        marginBottom: "16px"
      }}></div>
      <div style={{
        fontSize: "1.1rem",
        fontWeight: "600",
        color: "var(--text-secondary)"
      }}>
        🌱 {message}
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default PageLoader;
