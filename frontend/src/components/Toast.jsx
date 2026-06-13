import React, { useState, useEffect } from "react";

const listeners = new Set();

export const toast = {
  show(message, type = "success") {
    const id = Math.random().toString(36).substring(2, 9);
    listeners.forEach((listener) => listener({ id, message, type }));
  },
  success(message) {
    this.show(message, "success");
  },
  error(message) {
    this.show(message, "error");
  },
  warning(message) {
    this.show(message, "warning");
  },
  info(message) {
    this.show(message, "info");
  }
};

export const ToastContainer = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleToast = (newToast) => {
      setToasts((prev) => [...prev, newToast]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== newToast.id));
      }, 4000);
    };

    listeners.add(handleToast);
    return () => {
      listeners.delete(handleToast);
    };
  }, []);

  const getToastColors = (type) => {
    switch (type) {
      case "success":
        return { bg: "#38a169", text: "#ffffff", icon: "✅" };
      case "error":
        return { bg: "#e53e3e", text: "#ffffff", icon: "❌" };
      case "warning":
        return { bg: "#dd6b20", text: "#ffffff", icon: "⚠️" };
      case "info":
      default:
        return { bg: "#3182ce", text: "#ffffff", icon: "ℹ️" };
    }
  };

  return (
    <div style={{
      position: "fixed",
      bottom: "24px",
      right: "24px",
      display: "flex",
      flexDirection: "column",
      gap: "10px",
      zIndex: 9999,
      maxWidth: "350px"
    }}>
      {toasts.map((t) => {
        const colors = getToastColors(t.type);
        return (
          <div
            key={t.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              backgroundColor: colors.bg,
              color: colors.text,
              padding: "12px 20px",
              borderRadius: "8px",
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
              fontFamily: "'Outfit', sans-serif",
              fontSize: "0.9rem",
              fontWeight: "600",
              animation: "slideIn 0.3s ease-out forwards",
              opacity: 0.95
            }}
          >
            <span>{colors.icon}</span>
            <span>{t.message}</span>
          </div>
        );
      })}

      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%) translateY(10px);
            opacity: 0;
          }
          to {
            transform: translateX(0) translateY(0);
            opacity: 0.95;
          }
        }
      `}</style>
    </div>
  );
};
