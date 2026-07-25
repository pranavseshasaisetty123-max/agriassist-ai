import React, { useEffect, useState } from "react";
import api from "../../../services/api";

const ForecastWidget = () => {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        const response = await api.get("/weather/forecast");
        setForecastData(response.data);
      } catch (error) {
        console.error("Failed to load forecast:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, []);

  if (loading) {
    return (
      <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "140px" }}>
        <span className="dot-spinner"></span> Loading 7-day forecast...
      </div>
    );
  }

  if (!forecastData || !forecastData.forecast) {
    return null;
  }

  const getWeatherIcon = (cond) => {
    const c = (cond || "").toLowerCase();
    if (c.includes("clear") || c.includes("sun")) return "☀️";
    if (c.includes("cloud") || c.includes("mainly")) return "☁️";
    if (c.includes("rain") || c.includes("drizzle") || c.includes("shower")) return "🌧️";
    if (c.includes("thunder") || c.includes("storm")) return "⛈️";
    if (c.includes("snow")) return "❄️";
    if (c.includes("fog")) return "🌫️";
    return "⛅";
  };

  const getDayName = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { weekday: "short" });
  };

  return (
    <div className="glass animate-fade-in" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
      <h3 style={{ fontSize: "1rem", color: "var(--text-primary)", marginBottom: "16px", fontWeight: "700" }}>📅 7-Day Weather Forecast</h3>
      <div style={{ display: "flex", gap: "12px", overflowX: "auto", paddingBottom: "8px" }}>
        {forecastData.forecast.map((item, index) => (
          <div
            key={index}
            style={{
              flex: "0 0 90px",
              textAlign: "center",
              padding: "16px 8px",
              backgroundColor: "var(--bg-app)",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--border-light)"
            }}
          >
            <span style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
              {getDayName(item.date)}
            </span>
            <div style={{ fontSize: "1.8rem", margin: "8px 0" }}>{getWeatherIcon(item.condition)}</div>
            <div style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--text-primary)" }}>{item.temp_max.toFixed(0)}°</div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{item.temp_min.toFixed(0)}°</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ForecastWidget;
