import React, { useState, useEffect } from "react";
import api from "../../../services/api";

const CropRecommendationsPage = () => {
  const [latestReport, setLatestReport] = useState(null);
  const [loadingContext, setLoadingContext] = useState(true);
  const [weatherData, setWeatherData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  
  const [currentRecommendations, setCurrentRecommendations] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [selectedCrop, setSelectedCrop] = useState(null);
  
  const [selectedBatchTime, setSelectedBatchTime] = useState(null);

  // Fetch context (soil report + weather) and history
  const fetchContextAndHistory = async () => {
    setLoadingContext(true);
    setLoadingHistory(true);
    setError("");
    try {
      // 1. Get soil reports
      const soilResp = await api.get("/soil/reports?limit=1");
      const report = soilResp.data && soilResp.data.length > 0 ? soilResp.data[0] : null;
      setLatestReport(report);

      // 2. Get current weather
      try {
        const weatherResp = await api.get("/weather/current");
        setWeatherData(weatherResp.data);
      } catch (wErr) {
        console.error("Failed to load current weather:", wErr);
      }

      // 3. Get recommendations history
      await fetchHistory();

    } catch (err) {
      console.error("Failed to fetch initial recommendation context:", err);
      setError("Failed to load initial soil or weather data. Please refresh.");
    } finally {
      setLoadingContext(false);
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const resp = await api.get("/crop-recommendations");
      setHistory(resp.data);
      
      // If we have history, show the latest batch automatically by default
      if (resp.data.length > 0 && currentRecommendations.length === 0) {
        const latestTime = resp.data[0].created_at;
        const latestBatch = resp.data.filter(r => r.created_at === latestTime);
        setCurrentRecommendations(latestBatch);
        setSelectedBatchTime(latestTime);
      }
    } catch (err) {
      console.error("Failed to fetch crop recommendation history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchContextAndHistory();
  }, []);

  const handleGenerate = async () => {
    if (generating) return;
    setGenerating(true);
    setError("");
    setSelectedCrop(null);
    try {
      const resp = await api.post("/crop-recommendations/generate");
      setCurrentRecommendations(resp.data);
      if (resp.data.length > 0) {
        setSelectedBatchTime(resp.data[0].created_at);
      }
      // Reload history to include the new batch
      await fetchHistory();
    } catch (err) {
      console.error("Failed to generate recommendations:", err);
      setError(
        err.response?.data?.detail ||
        "Failed to generate crop recommendations. Please check your network or try again."
      );
    } finally {
      setGenerating(false);
    }
  };

  // Group history items by created_at timestamp
  const groupHistoryByBatch = () => {
    const batches = {};
    history.forEach(item => {
      const time = item.created_at;
      if (!batches[time]) {
        batches[time] = [];
      }
      batches[time].push(item);
    });
    return Object.entries(batches).map(([timestamp, items]) => ({
      timestamp,
      crops: items
    }));
  };

  const selectHistoryBatch = (timestamp, crops) => {
    setCurrentRecommendations(crops);
    setSelectedBatchTime(timestamp);
    setSelectedCrop(null);
    setError("");
  };

  const getScoreColor = (score) => {
    if (score >= 85) return { color: "#38a169", bg: "#f0fff4", border: "#c6f6d5" }; // Green
    if (score >= 70) return { color: "#dd6b20", bg: "#fffaf0", border: "#fbd38d" }; // Orange/Yellow
    return { color: "#e53e3e", bg: "#fff5f5", border: "#f8b4b4" }; // Red
  };

  const batches = groupHistoryByBatch();

  if (loadingContext) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "calc(100vh - 100px)", color: "var(--text-secondary)" }}>
        <span className="dot-spinner"></span> Loading crop recommendation context...
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
      {/* Left Panel: Inputs summary and results */}
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", overflowY: "auto", paddingRight: "8px" }}>
        
        {/* Environmental Context Widget */}
        <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "1.2rem", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
              🌱 Live Environmental Context
            </h3>
            <button 
              className="btn btn-primary" 
              onClick={handleGenerate}
              disabled={generating || !latestReport}
              style={{ minWidth: "160px" }}
            >
              {generating ? (
                <>
                  <span className="dot-spinner"></span> Analyzing Context...
                </>
              ) : "🔍 Recommend Crops"}
            </button>
          </div>

          {!latestReport ? (
            <div style={{
              padding: "20px",
              backgroundColor: "#fff5f5",
              color: "#e53e3e",
              borderRadius: "var(--radius-sm)",
              borderLeft: "4px solid #e53e3e",
              fontSize: "0.9rem"
            }}>
              ⚠️ <strong>No soil test report found.</strong> Please log at least one soil test report in the Soil Diagnostics Center before requesting AI recommendations.
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: "600" }}>LATEST SOIL METRICS (Planned: {latestReport.crop_planned})</span>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px" }}>
                  <div style={{ padding: "8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Soil pH</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "var(--primary)" }}>{latestReport.ph}</div>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Nitrogen</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "var(--primary)" }}>{latestReport.nitrogen} <span style={{ fontSize: "0.65rem" }}>mg/kg</span></div>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Phosphorus</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "var(--primary)" }}>{latestReport.phosphorus} <span style={{ fontSize: "0.65rem" }}>mg/kg</span></div>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Potassium</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "var(--primary)" }}>{latestReport.potassium} <span style={{ fontSize: "0.65rem" }}>mg/kg</span></div>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Organic Matter</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "var(--primary)" }}>{latestReport.organic_matter != null ? `${latestReport.organic_matter}%` : "N/A"}</div>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "rgba(255,255,255,0.4)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                    <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Logged On</div>
                    <div style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--text-primary)", marginTop: "4px" }}>{new Date(latestReport.tested_at).toLocaleDateString()}</div>
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px", borderLeft: "1px solid var(--border-light)", paddingLeft: "20px" }}>
                <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: "600" }}>LOCATION & LOCAL CLIMATE</span>
                {weatherData ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <div style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)" }}>📍 {weatherData.location}</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--primary)" }}>{weatherData.temp}°C</div>
                    <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", textTransform: "capitalize" }}>☁️ {weatherData.condition}</div>
                  </div>
                ) : (
                  <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    Loading location weather...
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {error && (
          <div style={{ padding: "12px 16px", backgroundColor: "#fff5f5", color: "#e53e3e", borderRadius: "var(--radius-sm)", fontSize: "0.875rem", borderLeft: "4px solid #e53e3e" }}>
            ⚠️ {error}
          </div>
        )}

        {/* Top 5 Recommendation List */}
        {currentRecommendations.length > 0 && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", justifycontent: "space-between", alignItems: "center" }}>
              <h4 style={{ fontSize: "1rem", color: "var(--text-secondary)", fontWeight: "700" }}>
                🎯 Top 5 Crop Matches (Batch: {new Date(selectedBatchTime).toLocaleString()})
              </h4>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "12px" }}>
              {currentRecommendations.map((rec) => {
                const scoreStyles = getScoreColor(rec.suitability_score);
                const isSelected = selectedCrop && selectedCrop.id === rec.id;

                return (
                  <div 
                    key={rec.id}
                    onClick={() => setSelectedCrop(rec)}
                    className="glass hover-card"
                    style={{
                      padding: "16px",
                      borderRadius: "var(--radius-md)",
                      cursor: "pointer",
                      border: isSelected ? "2px solid var(--primary)" : "1px solid var(--border-light)",
                      backgroundColor: isSelected ? "var(--primary-soft)" : "rgba(255, 255, 255, 0.4)",
                      textAlign: "center",
                      display: "flex",
                      flexDirection: "column",
                      gap: "10px",
                      position: "relative",
                      transition: "var(--transition-smooth)"
                    }}
                  >
                    <div style={{
                      width: "48px",
                      height: "48px",
                      borderRadius: "50%",
                      backgroundColor: scoreStyles.bg,
                      color: scoreStyles.color,
                      border: `2px solid ${scoreStyles.border}`,
                      fontSize: "1.1rem",
                      fontWeight: "800",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      margin: "0 auto"
                    }}>
                      {rec.suitability_score}%
                    </div>
                    <div>
                      <h4 style={{ fontSize: "0.95rem", fontWeight: "800", color: "var(--text-primary)" }}>{rec.crop_name}</h4>
                      <span style={{ 
                        fontSize: "0.7rem", 
                        fontWeight: "700", 
                        color: "var(--text-muted)", 
                        textTransform: "uppercase",
                        backgroundColor: "rgba(0,0,0,0.05)",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        display: "inline-block",
                        marginTop: "4px"
                      }}>
                        {rec.season}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Selected Crop Detail Panel */}
        {selectedCrop && (
          <div className="glass animate-fade-in" style={{
            padding: "28px",
            borderRadius: "var(--radius-md)",
            borderLeft: `5px solid ${getScoreColor(selectedCrop.suitability_score).color}`,
            display: "flex",
            flexDirection: "column",
            gap: "20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <span style={{
                  fontSize: "0.75rem",
                  fontWeight: "700",
                  textTransform: "uppercase",
                  padding: "4px 8px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: getScoreColor(selectedCrop.suitability_score).bg,
                  color: getScoreColor(selectedCrop.suitability_score).color,
                  border: `1px solid ${getScoreColor(selectedCrop.suitability_score).border}`
                }}>
                  {selectedCrop.suitability_score}% Match Suitability
                </span>
                <h2 style={{ fontSize: "1.8rem", color: "var(--text-primary)", fontWeight: "800", marginTop: "8px" }}>
                  🌾 {selectedCrop.crop_name}
                </h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  Optimal Cultivation Season: <strong>{selectedCrop.season}</strong>
                </p>
              </div>
              <button 
                style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "1.2rem" }}
                onClick={() => setSelectedCrop(null)}
              >
                ✕
              </button>
            </div>

            <hr style={{ border: "none", borderTop: "1px solid var(--border-light)" }} />

            <div>
              <h4 style={{ color: "var(--text-primary)", fontSize: "0.95rem", fontWeight: "700", marginBottom: "6px" }}>
                💡 Why Recommended
              </h4>
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                {selectedCrop.recommendation_reason}
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              {/* Farming Tips */}
              <div>
                <h4 style={{ color: "var(--text-primary)", fontSize: "0.95rem", fontWeight: "700", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                  🚜 Actionable Farming Tips
                </h4>
                <ul style={{ paddingLeft: "16px", fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                  {selectedCrop.farming_tips.map((tip, i) => (
                    <li key={i} style={{ marginBottom: "4px" }}>{tip}</li>
                  ))}
                </ul>
              </div>

              {/* Risks */}
              <div>
                <h4 style={{ color: "#dd6b20", fontSize: "0.95rem", fontWeight: "700", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                  ⚠️ Potential Risks & Challenges
                </h4>
                <ul style={{ paddingLeft: "16px", fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                  {selectedCrop.risk_factors.map((risk, i) => (
                    <li key={i} style={{ marginBottom: "4px" }}>{risk}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Right Side: Recommendation History Panel */}
      <div className="glass" style={{
        borderRadius: "var(--radius-md)",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        overflowY: "hidden"
      }}>
        <h3 style={{ fontSize: "1.1rem", padding: "0 8px", color: "var(--text-primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
          📜 Recommendation History
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px", overflowY: "auto", flex: 1, padding: "2px" }}>
          {loadingHistory ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              <span className="dot-spinner"></span> Loading history...
            </div>
          ) : batches.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              No crop recommendations generated yet.
            </div>
          ) : (
            batches.map((batch) => {
              const isSelected = selectedBatchTime === batch.timestamp;
              return (
                <div 
                  key={batch.timestamp}
                  onClick={() => selectHistoryBatch(batch.timestamp, batch.crops)}
                  className="glass hover-card"
                  style={{
                    padding: "12px",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    backgroundColor: isSelected ? "var(--primary-soft)" : "var(--bg-card)",
                    borderLeft: isSelected ? "4px solid var(--primary)" : "4px solid var(--border-light)",
                    transition: "var(--transition-smooth)"
                  }}
                >
                  <div style={{ fontSize: "0.8rem", fontWeight: "700", color: "var(--text-primary)" }}>
                    📅 {new Date(batch.timestamp).toLocaleDateString()}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", marginTop: "2px" }}>
                    Time: {new Date(batch.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "6px" }}>
                    {batch.crops.map((c, i) => (
                      <span key={i} style={{ 
                        fontSize: "0.65rem", 
                        backgroundColor: "rgba(0,0,0,0.05)", 
                        padding: "2px 4px", 
                        borderRadius: "2px",
                        color: "var(--text-primary)"
                      }}>
                        {c.crop_name} ({c.suitability_score}%)
                      </span>
                    ))}
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

export default CropRecommendationsPage;
