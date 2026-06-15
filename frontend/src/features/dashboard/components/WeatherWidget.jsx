import React, { useEffect, useState } from "react";
import api from "../../../services/api";

const WeatherWidget = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await api.get("/weather/current");
        setWeather(response.data);
      } catch (error) {
        console.error("Failed to load weather:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchWeather();
  }, []);

  if (loading) {
    return (
      <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "140px" }}>
        <span className="dot-spinner"></span> Loading local weather...
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", minHeight: "140px", color: "var(--text-secondary)" }}>
        ⚠️ Unable to retrieve weather. Please configure profile location.
      </div>
    );
  }

  const getWeatherIcon = (cond) => {
    const c = cond.toLowerCase();
    if (c.includes("clear") || c.includes("sun")) return "☀️";
    if (c.includes("cloud") || c.includes("mainly")) return "☁️";
    if (c.includes("rain") || c.includes("drizzle") || c.includes("shower")) return "🌧️";
    if (c.includes("thunder") || c.includes("storm")) return "⛈️";
    if (c.includes("snow")) return "❄️";
    if (c.includes("fog")) return "🌫️";
    return "⛅";
  };

  return (
    <div className="glass animate-fade-in" style={{
      padding: "24px",
      borderRadius: "var(--radius-md)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      minHeight: "140px",
      position: "relative",
      overflow: "hidden",
      background: "linear-gradient(135deg, var(--weather-bg-start) 0%, var(--weather-bg-end) 100%)"
    }}>
      <div style={{ zIndex: 2 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
          <span style={{ fontSize: "1.1rem" }}>📍</span>
          <span style={{ fontSize: "1rem", fontWeight: "700", color: "var(--text-primary)" }}>{weather.location}</span>
        </div>
        <h2 style={{ fontSize: "3rem", fontWeight: "800", color: "var(--text-primary)", display: "flex", alignItems: "baseline", margin: "4px 0" }}>
          {weather.current_temp.toFixed(1)}<span style={{ fontSize: "1.8rem", fontWeight: "500", marginLeft: "2px" }}>°C</span>
        </h2>
        <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", fontWeight: "600", marginTop: "4px" }}>
          {weather.current_condition}
        </p>
      </div>
      <div style={{ fontSize: "4.5rem", zIndex: 1, userSelect: "none" }}>
        {getWeatherIcon(weather.current_condition)}
      </div>
    </div>
  );
};

export default WeatherWidget;
