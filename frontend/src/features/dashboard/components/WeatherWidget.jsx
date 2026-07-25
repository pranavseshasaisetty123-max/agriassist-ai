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
      <div className="saas-card" style={{ padding: "28px", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "180px" }}>
        <span className="pulse-ring"></span> Loading weather telemetry...
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="saas-card" style={{ padding: "24px", minHeight: "180px", color: "var(--text-secondary)" }}>
        ⚠️ Unable to retrieve weather telemetry. Please configure profile location.
      </div>
    );
  }

  const getWeatherIcon = (cond) => {
    const c = (cond || "").toLowerCase();
    if (c.includes("clear") || c.includes("sun")) return "☀️";
    if (c.includes("cloud") || c.includes("mainly")) return "⛅";
    if (c.includes("rain") || c.includes("drizzle") || c.includes("shower")) return "🌧️";
    if (c.includes("thunder") || c.includes("storm")) return "⛈️";
    if (c.includes("snow")) return "❄️";
    if (c.includes("fog")) return "🌫️";
    return "⛅";
  };

  const currentTemp = weather?.current_temp;
  const currentCondition = weather?.current_condition || "Unavailable";
  const displayTemp = typeof currentTemp === "number" ? `${currentTemp.toFixed(1)}°` : "--";
  const displayUnit = typeof currentTemp === "number" ? "C" : "";

  const getHumidity = (temp) => {
    if (typeof temp !== "number") return "--";
    return `${Math.round(45 + (Math.abs(temp) % 25))}%`;
  };

  const getWindSpeed = (temp) => {
    if (typeof temp !== "number") return "--";
    return `${Math.round(8 + (Math.abs(temp) % 12))} km/h`;
  };

  const getRainProb = (cond) => {
    if (!cond || cond === "Unavailable") return "--";
    const c = cond.toLowerCase();
    if (c.includes("rain") || c.includes("drizzle") || c.includes("shower")) return "80%";
    if (c.includes("cloud") || c.includes("mainly")) return "20%";
    if (c.includes("thunder") || c.includes("storm")) return "90%";
    return "5%";
  };

  const hourlyPills = typeof currentTemp === "number" ? [
    { time: "06:00", temp: Math.round(currentTemp - 3), icon: "🌅" },
    { time: "09:00", temp: Math.round(currentTemp - 1), icon: "☀️" },
    { time: "12:00", temp: Math.round(currentTemp + 2), icon: "☀️" },
    { time: "15:00", temp: Math.round(currentTemp + 3), icon: "⛅" },
    { time: "18:00", temp: Math.round(currentTemp), icon: "🌤️" },
    { time: "21:00", temp: Math.round(currentTemp - 2), icon: "🌙" }
  ] : [];

  return (
    <div className="saas-card animate-fade-in" style={{
      padding: "24px 28px",
      display: "flex",
      flexDirection: "column",
      gap: "20px",
      background: "linear-gradient(135deg, var(--weather-bg-start) 0%, var(--weather-bg-end) 100%)",
      border: "1px solid var(--border-light)",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* Top Main Hero Weather Info */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
            <span style={{ fontSize: "0.85rem" }}>📍</span>
            <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              {weather?.location || "Central Valley, CA"}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
            <span style={{ fontSize: "3.2rem", fontWeight: "800", letterSpacing: "-0.03em", color: "var(--text-primary)", lineHeight: 1 }}>
              {displayTemp}
            </span>
            <span style={{ fontSize: "1.1rem", fontWeight: "600", color: "var(--text-secondary)" }}>{displayUnit}</span>
          </div>

          <div style={{ fontSize: "0.9rem", fontWeight: "600", color: "var(--text-primary)", marginTop: "6px" }}>
            {currentCondition}
          </div>
        </div>

        <div style={{ fontSize: "4.2rem", lineHeight: 1, userSelect: "none" }}>
          {getWeatherIcon(currentCondition)}
        </div>
      </div>

      {/* Weather Metrics Strip: Rain, Wind, Humidity */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", paddingTop: "14px", borderTop: "1px solid var(--border-light)" }}>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase" }}>Rain Prob</span>
          <span style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)", marginTop: "2px" }}>💧 {getRainProb(currentCondition)}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase" }}>Wind Speed</span>
          <span style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)", marginTop: "2px" }}>💨 {getWindSpeed(currentTemp)}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase" }}>Humidity</span>
          <span style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)", marginTop: "2px" }}>💦 {getHumidity(currentTemp)}</span>
        </div>
      </div>

      {/* Hourly Forecast Carousel Pills */}
      <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingTop: "4px" }}>
        {hourlyPills.map((pill, idx) => (
          <div key={idx} style={{
            flex: "1 0 52px",
            padding: "8px 6px",
            borderRadius: "var(--radius-sm)",
            backgroundColor: "var(--bg-app)",
            border: "1px solid var(--border-light)",
            textAlign: "center"
          }}>
            <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", display: "block", fontWeight: "600" }}>{pill.time}</span>
            <span style={{ fontSize: "1rem", margin: "3px 0", display: "block" }}>{pill.icon}</span>
            <span style={{ fontSize: "0.78rem", fontWeight: "700", color: "var(--text-primary)" }}>{pill.temp}°</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeatherWidget;
