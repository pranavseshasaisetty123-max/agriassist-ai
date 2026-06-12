import React, { useState, useEffect } from "react";
import api from "../../../services/api";

const YieldPredictionPage = () => {
  const [selectedCrop, setSelectedCrop] = useState("Wheat");
  const [latestReport, setLatestReport] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [loadingContext, setLoadingContext] = useState(true);
  const [error, setError] = useState("");

  // Prediction output state
  const [prediction, setPrediction] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState("");

  // History state
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    fetchContextAndHistory();
  }, []);

  const fetchContextAndHistory = async () => {
    setLoadingContext(true);
    setLoadingHistory(true);
    setError("");
    try {
      // 1. Get latest soil report
      const soilResp = await api.get("/soil/reports?limit=1");
      const report = soilResp.data && soilResp.data.length > 0 ? soilResp.data[0] : null;
      setLatestReport(report);

      // 2. Get weather info
      try {
        const weatherResp = await api.get("/weather/current");
        setWeatherData(weatherResp.data);
      } catch (wErr) {
        console.error("Failed to load current weather:", wErr);
      }

      // 3. Get predictions history
      await fetchHistory();
    } catch (err) {
      console.error("Failed to load context:", err);
      setError("Failed to load soil report or weather details. Please refresh.");
    } finally {
      setLoadingContext(false);
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const resp = await api.get("/yield-predictions");
      setHistory(resp.data);
      // Load latest prediction automatically by default
      if (resp.data.length > 0 && !prediction) {
        setPrediction(resp.data[0]);
        setSelectedCrop(resp.data[0].crop_name);
      }
    } catch (err) {
      console.error("Failed to load prediction history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleGenerate = async (e) => {
    if (e) e.preventDefault();
    if (generating || !latestReport) return;

    setGenerating(true);
    setGenError("");
    setPrediction(null);

    try {
      const resp = await api.post("/yield-predictions/generate", {
        crop_name: selectedCrop,
      });
      setPrediction(resp.data);
      fetchHistory();
    } catch (err) {
      console.error("Failed to estimate yield:", err);
      setGenError(
        err.response?.data?.detail || "Yield prediction failed. Please try again."
      );
    } finally {
      setGenerating(false);
    }
  };

  const selectHistoryItem = (item) => {
    setPrediction(item);
    setSelectedCrop(item.crop_name);
    setGenError("");
  };

  const getCategoryStyles = (category) => {
    const cat = category?.toLowerCase();
    if (cat === "high") {
      return { color: "#38a169", bg: "#f0fff4", border: "#c6f6d5" };
    }
    if (cat === "medium") {
      return { color: "#dd6b20", bg: "#fffaf0", border: "#fbd38d" };
    }
    return { color: "#e53e3e", bg: "#fff5f5", border: "#f8b4b4" };
  };

  // Render Yield Speedometer / Gauge
  const renderYieldGauge = (yieldVal) => {
    // Let's cap max gauge value around 2000 kg/acre
    const maxVal = 2000;
    const value = Math.min(yieldVal, maxVal);
    const percentage = value / maxVal;
    
    // SVG dial path coordinates (semi-circle arc)
    const radius = 60;
    const cx = 80;
    const cy = 80;
    
    // Circle math
    const circumference = Math.PI * radius; // half circle
    const strokeDashoffset = circumference - percentage * circumference;

    return (
      <div style={{ position: "relative", width: "160px", height: "100px", margin: "0 auto" }}>
        <svg width="160" height="100" viewBox="0 0 160 100">
          {/* Background Arc */}
          <path
            d="M 20 80 A 60 60 0 0 1 140 80"
            fill="none"
            stroke="var(--border-light)"
            strokeWidth="10"
            strokeLinecap="round"
          />
          {/* Value Arc */}
          <path
            d="M 20 80 A 60 60 0 0 1 140 80"
            fill="none"
            stroke="var(--primary)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
          />
        </svg>
        <div style={{
          position: "absolute",
          top: "50px",
          left: "0",
          right: "0",
          textAlign: "center"
        }}>
          <strong style={{ fontSize: "1.4rem", color: "var(--text-primary)" }}>{yieldVal.toLocaleString()}</strong>
          <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: "700" }}>kg / acre</div>
        </div>
      </div>
    );
  };

  if (loadingContext) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "calc(100vh - 100px)", color: "var(--text-secondary)" }}>
        <span className="dot-spinner"></span> Loading yield prediction context...
      </div>
    );
  }

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 340px",
      gap: "24px",
      padding: "32px",
      height: "calc(100vh - 100px)",
      overflow: "hidden"
    }}>
      {/* Left panel */}
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", overflowY: "auto", paddingRight: "8px" }}>
        
        {/* Environment Summary Banner */}
        <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
          <h3 style={{ fontSize: "1.1rem", color: "var(--text-primary)", fontWeight: "700", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            🌱 Environmental Prediction Context
          </h3>
          
          {error && (
            <div style={{ padding: "12px", backgroundColor: "#fff5f5", color: "#e53e3e", borderRadius: "var(--radius-sm)", fontSize: "0.85rem", marginBottom: "16px" }}>
              ⚠️ {error}
            </div>
          )}

          {!latestReport ? (
            <div style={{
              padding: "20px",
              backgroundColor: "#fff5f5",
              color: "#e53e3e",
              borderRadius: "var(--radius-sm)",
              borderLeft: "4px solid #e53e3e",
              fontSize: "0.9rem"
            }}>
              ⚠️ <strong>No soil report logged.</strong> Please complete a soil analysis in the Soil Diagnostics Center before predicting crop yield.
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: "24px" }}>
              
              {/* Soil summary */}
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", fontWeight: "600", textTransform: "uppercase" }}>
                  LATEST SOIL METRICS (pH: {latestReport.ph})
                </span>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px", marginTop: "8px" }}>
                  <div style={{ padding: "6px 8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>Nitrogen</div>
                    <strong style={{ fontSize: "0.95rem", color: "var(--primary)" }}>{latestReport.nitrogen} <span style={{ fontSize: "0.6rem" }}>mg/kg</span></strong>
                  </div>
                  <div style={{ padding: "6px 8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>Phosphorus</div>
                    <strong style={{ fontSize: "0.95rem", color: "var(--primary)" }}>{latestReport.phosphorus} <span style={{ fontSize: "0.6rem" }}>mg/kg</span></strong>
                  </div>
                  <div style={{ padding: "6px 8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>Potassium</div>
                    <strong style={{ fontSize: "0.95rem", color: "var(--primary)" }}>{latestReport.potassium} <span style={{ fontSize: "0.6rem" }}>mg/kg</span></strong>
                  </div>
                </div>
              </div>

              {/* Weather summary */}
              <div style={{ borderLeft: "1px solid var(--border-light)", paddingLeft: "24px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", fontWeight: "600", textTransform: "uppercase" }}>
                  LOCATION WEATHER
                </span>
                {weatherData ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "2px", marginTop: "6px" }}>
                    <strong style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>📍 {weatherData.location}</strong>
                    <div style={{ fontSize: "1.1rem", fontWeight: "800", color: "var(--primary)", marginTop: "2px" }}>{weatherData.temp}°C</div>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "capitalize" }}>☁️ {weatherData.condition}</span>
                  </div>
                ) : (
                  <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "6px" }}>Loading climate data...</div>
                )}
              </div>

            </div>
          )}
        </div>

        {/* Prediction Trigger Card */}
        {latestReport && (
          <div className="glass" style={{ padding: "20px 24px", borderRadius: "var(--radius-md)" }}>
            <form onSubmit={handleGenerate} style={{ display: "flex", gap: "16px", alignItems: "center" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <label style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--text-secondary)" }}>SELECT TARGET CROP</label>
                <select
                  className="form-input"
                  value={selectedCrop}
                  onChange={(e) => setSelectedCrop(e.target.value)}
                  style={{ minWidth: "200px", margin: 0 }}
                >
                  {["Wheat", "Paddy", "Mustard", "Cotton", "Maize", "Tomato", "Potato", "Onion", "Sugarcane"].map((crop) => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={generating}
                style={{ flex: 1, height: "42px", marginTop: "18px", margin: "18px 0 0" }}
              >
                {generating ? (
                  <>
                    <span className="dot-spinner"></span> Forecasting expected yields...
                  </>
                ) : `📊 Forecast Expected Yield for ${selectedCrop}`}
              </button>
            </form>

            {genError && (
              <div style={{ marginTop: "12px", padding: "10px 14px", backgroundColor: "#fff5f5", color: "#e53e3e", borderRadius: "var(--radius-sm)", fontSize: "0.85rem", borderLeft: "4px solid #e53e3e" }}>
                ⚠️ {genError}
              </div>
            )}
          </div>
        )}

        {/* Prediction Outputs */}
        {prediction && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Split Dials Row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr 1fr", gap: "20px" }}>
              
              {/* Predicted Yield Gauge */}
              <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", textAlign: "center" }}>
                <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase", display: "block", marginBottom: "12px" }}>
                  ESTIMATED YIELD
                </span>
                {renderYieldGauge(prediction.predicted_yield)}
              </div>

              {/* Confidence Circle */}
              <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", textAlign: "center", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase" }}>
                  AI CONFIDENCE SCORE
                </span>
                
                {/* Custom circular progress SVG */}
                <div style={{ position: "relative", width: "80px", height: "80px", margin: "10px auto" }}>
                  <svg width="80" height="80" viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="34" fill="none" stroke="var(--border-light)" strokeWidth="6" />
                    <circle
                      cx="40"
                      cy="40"
                      r="34"
                      fill="none"
                      stroke="var(--primary)"
                      strokeWidth="6"
                      strokeDasharray="213.6"
                      strokeDashoffset={213.6 - (prediction.confidence_score / 100) * 213.6}
                      strokeLinecap="round"
                      transform="rotate(-90 40 40)"
                      style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
                    />
                  </svg>
                  <div style={{
                    position: "absolute",
                    top: "0", left: "0", right: "0", bottom: "0",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "1.2rem", fontWeight: "900", color: "var(--text-primary)"
                  }}>
                    {prediction.confidence_score}%
                  </div>
                </div>

                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                  Based on soil parameters & forecast consistency.
                </div>
              </div>

              {/* Yield category card */}
              <div className="glass" style={{
                padding: "20px",
                borderRadius: "var(--radius-md)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: "12px"
              }}>
                <span style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase" }}>
                  YIELD CLASSIFICATION
                </span>
                
                {(() => {
                  const styles = getCategoryStyles(prediction.yield_category);
                  return (
                    <div style={{
                      padding: "12px 24px",
                      backgroundColor: styles.bg,
                      color: styles.color,
                      border: `1.5px solid ${styles.border}`,
                      borderRadius: "var(--radius-full)",
                      fontSize: "1.2rem",
                      fontWeight: "900",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      boxShadow: "var(--shadow-sm)"
                    }}>
                      {prediction.yield_category}
                    </div>
                  );
                })()}
                
                <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", textAlign: "center" }}>
                  Relative to regional {prediction.crop_name} averages.
                </span>
              </div>

            </div>

            {/* Split Factors & Recommendations */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
              
              {/* Factors card */}
              <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
                <h4 style={{ fontSize: "0.95rem", color: "var(--text-primary)", fontWeight: "700", marginBottom: "14px", display: "flex", alignItems: "center", gap: "6px" }}>
                  📊 Factors Influencing Yield
                </h4>
                <ul style={{ paddingLeft: "16px", display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                  {prediction.prediction_factors.map((factor, idx) => (
                    <li key={idx} style={{ position: "relative" }}>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommendations card */}
              <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
                <h4 style={{ fontSize: "0.95rem", color: "var(--text-primary)", fontWeight: "700", marginBottom: "14px", display: "flex", alignItems: "center", gap: "6px" }}>
                  💡 Agronomist Suggestions
                </h4>
                <ul style={{ paddingLeft: "16px", display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                  {prediction.recommendations.map((rec, idx) => (
                    <li key={idx}>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>

            </div>

          </div>
        )}

      </div>

      {/* Right Sidebar: Historical calculations */}
      <div className="glass" style={{
        borderRadius: "var(--radius-md)",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        overflowY: "hidden"
      }}>
        <h3 style={{ fontSize: "1.1rem", padding: "0 8px", color: "var(--text-primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
          📜 Estimation History
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px", overflowY: "auto", flex: 1, padding: "2px" }}>
          {loadingHistory ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              <span className="dot-spinner"></span> Loading history...
            </div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              No yield predictions recorded yet.
            </div>
          ) : (
            history.map((item) => {
              const styles = getCategoryStyles(item.yield_category);
              return (
                <div
                  key={item.id}
                  onClick={() => selectHistoryItem(item)}
                  className="glass hover-card"
                  style={{
                    padding: "12px",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    backgroundColor: "var(--bg-card)",
                    borderLeft: `4px solid ${styles.color}`,
                    transition: "var(--transition-smooth)"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>
                      🌾 {item.crop_name}
                    </strong>
                    <span style={{
                      fontSize: "0.65rem",
                      fontWeight: "800",
                      color: styles.color,
                      backgroundColor: styles.bg,
                      padding: "2px 6px",
                      borderRadius: "4px"
                    }}>
                      {item.yield_category}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "8px", borderTop: "1px solid rgba(0,0,0,0.03)", paddingTop: "6px" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--text-secondary)" }}>
                      {item.predicted_yield.toLocaleString()} <span style={{ fontSize: "0.6rem", fontWeight: "500" }}>kg/ac</span>
                    </span>
                    <span style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
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

export default YieldPredictionPage;
