import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an exception:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: "32px",
          textAlign: "center",
          backgroundColor: "var(--bg-card)",
          borderRadius: "var(--radius-md)",
          border: "1px solid rgba(229, 62, 98, 0.2)",
          boxShadow: "var(--shadow-md)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "16px",
          margin: "24px"
        }}>
          <span style={{ fontSize: "3rem" }}>⚠️</span>
          <h3 style={{ fontSize: "1.25rem", color: "var(--text-primary)", fontWeight: "800", fontFamily: "'Outfit', sans-serif" }}>
            Workspace Exception Encountered
          </h3>
          <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", maxWidth: "400px", margin: "0 auto", lineHeight: "1.5" }}>
            An unexpected error occurred while loading this module. You can reload the page or click below to recover.
          </p>
          <button
            className="btn btn-primary"
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            style={{ padding: "10px 20px", fontSize: "0.85rem" }}
          >
            ↻ Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
