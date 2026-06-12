import React, { useState, useEffect } from "react";
import api from "../services/api";

const NotificationCenterPage = ({ onUpdateUnread }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [filter, setFilter] = useState("all"); // all, unread, critical, weather, disease, risk, planner
  const [error, setError] = useState("");

  const fetchNotifications = async () => {
    setLoading(true);
    setError("");
    try {
      const resp = await api.get("/notifications");
      setNotifications(resp.data);
    } catch (err) {
      console.error("Failed to load notifications:", err);
      setError("Failed to load notifications. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleScan = async () => {
    setScanning(true);
    setError("");
    try {
      const resp = await api.post("/notifications/generate");
      const generatedCount = resp.data.generated_count;
      await fetchNotifications();
      alert(`Scan complete! Generated ${generatedCount} new notification(s).`);
    } catch (err) {
      console.error("Failed to generate alerts:", err);
      setError("Alert engine scan failed. Please check backend services.");
    } finally {
      setScanning(false);
    }
  };

  const handleMarkRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.patch("/notifications/read-all");
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error("Failed to mark all as read:", err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/notifications/${id}`);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      console.error("Failed to delete notification:", err);
    }
  };

  const getPriorityColors = (priority) => {
    switch (priority.toLowerCase()) {
      case "critical":
        return { color: "#e53e3e", bg: "#fff5f5", border: "#feb2b2" };
      case "high":
        return { color: "#dd6b20", bg: "#fffaf0", border: "#fbd38d" };
      case "medium":
        return { color: "#3182ce", bg: "#ebf8ff", border: "#90cdf4" };
      default:
        return { color: "#38a169", bg: "#f0fff4", border: "#9ae6b4" };
    }
  };

  const getModuleIcon = (module) => {
    switch (module.toLowerCase()) {
      case "weather":
        return "🌧️";
      case "risk":
        return "⚠️";
      case "disease":
        return "🔬";
      case "planner":
        return "📅";
      case "yield":
        return "📈";
      case "agronomist":
        return "🤖";
      default:
        return "🔔";
    }
  };

  const filteredNotifications = notifications.filter((n) => {
    if (filter === "all") return true;
    if (filter === "unread") return !n.is_read;
    if (filter === "critical") return n.priority.toLowerCase() === "critical";
    if (filter === "weather") return n.notification_type === "weather";
    if (filter === "disease") return n.notification_type === "disease";
    if (filter === "risk") return n.notification_type === "risk";
    if (filter === "planner") return n.notification_type === "planner";
    return true;
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;
  const criticalCount = notifications.filter((n) => n.priority.toLowerCase() === "critical").length;

  useEffect(() => {
    if (onUpdateUnread) {
      onUpdateUnread(unreadCount);
    }
  }, [unreadCount, onUpdateUnread]);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "260px 1fr",
        gap: "24px",
        padding: "32px",
        height: "calc(100vh - 100px)",
        overflow: "hidden",
      }}
    >
      {/* Left Filters Sidebar */}
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
        <button
          className="btn btn-primary"
          onClick={handleScan}
          disabled={scanning}
          style={{ width: "100%", height: "42px" }}
        >
          {scanning ? "Scanning..." : "🔍 Scan For Alerts"}
        </button>

        <div style={{ borderBottom: "1px solid var(--border-light)", paddingBottom: "8px" }}>
          <strong style={{ fontSize: "0.85rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            📁 Categories
          </strong>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            overflowY: "auto",
            flex: 1,
          }}
        >
          {[
            { id: "all", label: "All Alerts", icon: "🔔", count: notifications.length },
            { id: "unread", label: "Unread", icon: "✉️", count: unreadCount, badgeColor: "var(--primary)" },
            { id: "critical", label: "Critical", icon: "⚠️", count: criticalCount, badgeColor: "#e53e3e" },
            { id: "weather", label: "Weather", icon: "🌧️" },
            { id: "disease", label: "Disease Detection", icon: "🔬" },
            { id: "risk", label: "Risk Warnings", icon: "🛡️" },
            { id: "planner", label: "Planner Activities", icon: "📅" },
          ].map((item) => (
            <div
              key={item.id}
              onClick={() => setFilter(item.id)}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px",
                borderRadius: "var(--radius-sm)",
                cursor: "pointer",
                backgroundColor: filter === item.id ? "rgba(56, 161, 105, 0.1)" : "var(--bg-card)",
                borderLeft: filter === item.id ? "4px solid var(--primary)" : "4px solid transparent",
                transition: "var(--transition-smooth)",
              }}
            >
              <span style={{ fontSize: "0.85rem", fontWeight: filter === item.id ? "700" : "600", color: "var(--text-primary)" }}>
                {item.icon} {item.label}
              </span>
              {item.count !== undefined && item.count > 0 && (
                <span
                  style={{
                    fontSize: "0.7rem",
                    fontWeight: "800",
                    color: "#fff",
                    backgroundColor: item.badgeColor || "var(--text-muted)",
                    padding: "2px 8px",
                    borderRadius: "10px",
                  }}
                >
                  {item.count}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Alert List View */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          height: "100%",
          overflow: "hidden",
        }}
      >
        {/* Bulk action buttons header */}
        <div
          className="glass"
          style={{
            padding: "16px 24px",
            borderRadius: "var(--radius-md)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <span style={{ fontSize: "0.7rem", fontWeight: "800", color: "var(--primary)", textTransform: "uppercase" }}>
              Alert Center
            </span>
            <h3 style={{ fontSize: "1.2rem", fontWeight: "900", color: "var(--text-primary)", margin: "2px 0 0" }}>
              {filter.charAt(0).toUpperCase() + filter.slice(1)} Notifications ({filteredNotifications.length})
            </h3>
          </div>
          {unreadCount > 0 && (
            <button className="btn btn-secondary" onClick={handleMarkAllRead}>
              ✓ Mark All Read
            </button>
          )}
        </div>

        {error && (
          <div className="glass" style={{ padding: "16px", borderRadius: "var(--radius-sm)", borderLeft: "4px solid #e53e3e", backgroundColor: "#fff5f5", color: "#e53e3e", fontSize: "0.85rem" }}>
            ⚠️ {error}
          </div>
        )}

        {/* Notifications Timeline List */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "16px",
            paddingRight: "8px",
          }}
        >
          {loading ? (
            <div style={{ textAlign: "center", padding: "64px", color: "var(--text-secondary)" }}>
              <span className="dot-spinner"></span> Loading alerts...
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div
              className="glass"
              style={{
                padding: "64px 48px",
                textAlign: "center",
                borderRadius: "var(--radius-md)",
                color: "var(--text-secondary)",
              }}
            >
              <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🔔</div>
              <h4 style={{ margin: "0 0 8px", color: "var(--text-primary)", fontWeight: "800" }}>No Notifications Found</h4>
              <p style={{ margin: 0, fontSize: "0.875rem" }}>
                All clear! No alerts matching the '{filter}' filter exist. Click 'Scan For Alerts' to pull fresh updates.
              </p>
            </div>
          ) : (
            filteredNotifications.map((notif) => {
              const priorityStyle = getPriorityColors(notif.priority);
              return (
                <div
                  key={notif.id}
                  className="glass hover-card"
                  style={{
                    padding: "20px",
                    borderRadius: "var(--radius-md)",
                    display: "grid",
                    gridTemplateColumns: "40px 1fr auto",
                    gap: "16px",
                    alignItems: "start",
                    backgroundColor: notif.is_read ? "var(--bg-card)" : "rgba(56, 161, 105, 0.04)",
                    borderLeft: `5px solid ${priorityStyle.color}`,
                    transition: "var(--transition-smooth)",
                  }}
                >
                  <div style={{ fontSize: "2rem", alignSelf: "center", textAlign: "center" }}>
                    {getModuleIcon(notif.source_module)}
                  </div>
                  <div>
                    <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "4px" }}>
                      <h4
                        style={{
                          fontSize: "0.95rem",
                          fontWeight: notif.is_read ? "700" : "900",
                          color: "var(--text-primary)",
                          margin: 0,
                        }}
                      >
                        {notif.title}
                      </h4>
                      <span
                        style={{
                          fontSize: "0.65rem",
                          fontWeight: "800",
                          color: priorityStyle.color,
                          backgroundColor: priorityStyle.bg,
                          border: `1px solid ${priorityStyle.border}`,
                          padding: "1px 6px",
                          borderRadius: "4px",
                          textTransform: "uppercase",
                        }}
                      >
                        {notif.priority}
                      </span>
                      {!notif.is_read && (
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "var(--primary)" }}></span>
                      )}
                    </div>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", margin: "0 0 8px", lineHeight: "1.5" }}>
                      {notif.message}
                    </p>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                      ⏰ {new Date(notif.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "8px", alignSelf: "center" }}>
                    {!notif.is_read && (
                      <button
                        title="Mark as Read"
                        onClick={() => handleMarkRead(notif.id)}
                        style={{
                          border: "none",
                          background: "none",
                          fontSize: "1.1rem",
                          cursor: "pointer",
                          padding: "6px",
                        }}
                      >
                        ✓
                      </button>
                    )}
                    <button
                      title="Delete Notification"
                      onClick={() => handleDelete(notif.id)}
                      style={{
                        border: "none",
                        background: "none",
                        fontSize: "1.1rem",
                        cursor: "pointer",
                        padding: "6px",
                        opacity: 0.6,
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationCenterPage;
