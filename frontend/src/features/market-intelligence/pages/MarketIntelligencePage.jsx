import React, { useState, useEffect } from "react";
import api from "../../../services/api";

const MarketIntelligencePage = () => {
  // Crop Search State
  const [searchCrop, setSearchCrop] = useState("Tomato");
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [marketData, setMarketData] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [searchError, setSearchError] = useState("");

  // AI Trend Explainer State
  const [aiExplanation, setAiExplanation] = useState("");
  const [loadingAI, setLoadingAI] = useState(false);

  // Profit Calculator State
  const [calcCrop, setCalcCrop] = useState("Tomato");
  const [expectedYield, setExpectedYield] = useState("");
  const [cultivationCost, setCultivationCost] = useState("");
  const [customPrice, setCustomPrice] = useState("");
  const [calculationResult, setCalculationResult] = useState(null);
  const [calcError, setCalcError] = useState("");
  const [calculating, setCalculating] = useState(false);

  // History State
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Active Tooltip State for Custom SVG Chart
  const [hoveredPoint, setHoveredPoint] = useState(null);

  // Auto-fill calculator with searched crop name and price
  useEffect(() => {
    if (marketData) {
      setCalcCrop(marketData.crop_name);
      setCustomPrice(marketData.average_price.toString());
    }
  }, [marketData]);

  // Load initial data
  useEffect(() => {
    handleSearch();
    fetchHistory();
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!searchCrop.trim()) return;

    setLoadingSearch(true);
    setSearchError("");
    setAiExplanation("");
    setHoveredPoint(null);

    try {
      // 1. Fetch current market intelligence
      const priceResp = await api.get("/market-intelligence/prices", {
        params: { crop_name: searchCrop.trim() },
      });
      setMarketData(priceResp.data);

      // 2. Fetch trends
      const trendResp = await api.get("/market-intelligence/trends", {
        params: { crop_name: searchCrop.trim(), days: 30 },
      });
      setTrendData(trendResp.data);
    } catch (err) {
      console.error("Failed to load crop pricing:", err);
      setSearchError(
        err.response?.data?.detail || "No price records found for this crop. Try Tomato, Wheat, or Paddy."
      );
      setMarketData(null);
      setTrendData([]);
    } finally {
      setLoadingSearch(false);
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const resp = await api.get("/market-intelligence/history");
      setHistory(resp.data);
    } catch (err) {
      console.error("Failed to load calculations history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleCalculate = async (e) => {
    if (e) e.preventDefault();
    if (!calcCrop.trim() || !expectedYield || !cultivationCost) {
      setCalcError("Please enter all required fields.");
      return;
    }

    setCalculating(true);
    setCalcError("");
    setCalculationResult(null);

    try {
      const payload = {
        crop_name: calcCrop.trim(),
        expected_yield: parseFloat(expectedYield),
        cultivation_cost: parseFloat(cultivationCost),
      };

      if (customPrice && customPrice.trim()) {
        payload.market_price_per_kg = parseFloat(customPrice);
      }

      const resp = await api.post("/market-intelligence/calculate", payload);
      setCalculationResult(resp.data);
      // Reload history list
      fetchHistory();
    } catch (err) {
      console.error("Failed to calculate profitability:", err);
      setCalcError(err.response?.data?.detail || "Calculation failed. Please check your parameters.");
    } finally {
      setCalculating(false);
    }
  };

  const handleAIExplain = async () => {
    if (trendData.length === 0 || loadingAI) return;
    setLoadingAI(true);
    setAiExplanation("");
    try {
      const resp = await api.post("/market-intelligence/explain-trends", {
        crop_name: marketData?.crop_name || searchCrop,
        trends: trendData.map((pt) => ({
          recorded_date: pt.recorded_date,
          price_per_kg: pt.price_per_kg,
        })),
      });
      setAiExplanation(resp.data.explanation);
    } catch (err) {
      console.error("Failed to get AI insights:", err);
      setAiExplanation("AI service is currently busy. Please try again in a few moments.");
    } finally {
      setLoadingAI(false);
    }
  };

  const selectHistoryItem = (item) => {
    setCalcCrop(item.crop_name);
    setExpectedYield(item.expected_yield.toString());
    setCultivationCost(item.cultivation_cost.toString());
    setCustomPrice(item.market_price_per_kg.toString());
    setCalculationResult(item);
    setCalcError("");
  };

  // Custom SVG Chart parameters
  const renderSVGChart = () => {
    if (trendData.length < 2) {
      return (
        <div style={{ height: "200px", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
          Insufficient trend history to plot.
        </div>
      );
    }

    const width = 600;
    const height = 220;
    const paddingX = 40;
    const paddingY = 25;

    // Find min and max values for scaling
    const prices = trendData.map((t) => t.price_per_kg);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceDiff = maxPrice - minPrice || 10;
    
    // Add vertical buffer
    const yMin = Math.max(0, minPrice - priceDiff * 0.1);
    const yMax = maxPrice + priceDiff * 0.1;
    const yRange = yMax - yMin;

    const points = trendData.map((t, idx) => {
      const x = paddingX + (idx / (trendData.length - 1)) * (width - 2 * paddingX);
      const y = height - paddingY - ((t.price_per_kg - yMin) / yRange) * (height - 2 * paddingY);
      return { x, y, price: t.price_per_kg, date: t.recorded_date, index: idx };
    });

    // Create Path Commands
    let pathD = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      pathD += ` L ${points[i].x} ${points[i].y}`;
    }

    // Gradient path command (closes the shape at the bottom)
    const areaD = `${pathD} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${height - paddingY} Z`;

    // Calculate Y grid positions
    const midPrice = (yMax + yMin) / 2;
    const getGridY = (val) => height - paddingY - ((val - yMin) / yRange) * (height - 2 * paddingY);

    return (
      <div style={{ position: "relative", width: "100%" }}>
        <svg 
          viewBox={`0 0 ${width} ${height}`} 
          width="100%" 
          height={height} 
          style={{ overflow: "visible", fontFamily: "inherit" }}
        >
          <defs>
            <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.4" />
              <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="var(--primary)" />
              <stop offset="100%" stopColor="var(--primary)" />
            </linearGradient>
          </defs>

          {/* Horizontal Grid lines */}
          <line x1={paddingX} y1={getGridY(yMin)} x2={width - paddingX} y2={getGridY(yMin)} stroke="var(--border-light)" strokeDasharray="4" />
          <line x1={paddingX} y1={getGridY(midPrice)} x2={width - paddingX} y2={getGridY(midPrice)} stroke="var(--border-light)" strokeDasharray="4" />
          <line x1={paddingX} y1={getGridY(yMax)} x2={width - paddingX} y2={getGridY(yMax)} stroke="var(--border-light)" strokeDasharray="4" />

          {/* Grid Value Labels (Left Y-Axis) */}
          <text x={paddingX - 8} y={getGridY(yMin) + 4} textAnchor="end" fontSize="10" fill="var(--text-muted)">₹{Math.round(yMin)}</text>
          <text x={paddingX - 8} y={getGridY(midPrice) + 4} textAnchor="end" fontSize="10" fill="var(--text-muted)">₹{Math.round(midPrice)}</text>
          <text x={paddingX - 8} y={getGridY(yMax) + 4} textAnchor="end" fontSize="10" fill="var(--text-muted)">₹{Math.round(yMax)}</text>

          {/* Date Labels (X-Axis) */}
          <text x={paddingX} y={height - 8} textAnchor="start" fontSize="9" fill="var(--text-muted)">
            {new Date(trendData[0].recorded_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}
          </text>
          <text x={width / 2} y={height - 8} textAnchor="middle" fontSize="9" fill="var(--text-muted)">
            {new Date(trendData[Math.floor(trendData.length / 2)].recorded_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}
          </text>
          <text x={width - paddingX} y={height - 8} textAnchor="end" fontSize="9" fill="var(--text-muted)">
            {new Date(trendData[trendData.length - 1].recorded_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}
          </text>

          {/* Filled Area */}
          <path d={areaD} fill="url(#chartGrad)" />

          {/* Trend Line */}
          <path d={pathD} fill="none" stroke="url(#lineGrad)" strokeWidth="2.5" strokeLinecap="round" />

          {/* Interactive Hover Dots */}
          {points.map((pt) => (
            <circle
              key={pt.index}
              cx={pt.x}
              cy={pt.y}
              r={hoveredPoint?.index === pt.index ? "6" : "3.5"}
              fill={hoveredPoint?.index === pt.index ? "var(--primary)" : "rgba(255,255,255,0.9)"}
              stroke="var(--primary)"
              strokeWidth="2"
              style={{ cursor: "pointer", transition: "all 0.15s ease" }}
              onMouseEnter={() => setHoveredPoint(pt)}
            />
          ))}
        </svg>

        {/* Hover Tooltip display */}
        {hoveredPoint && (
          <div style={{
            position: "absolute",
            left: `${(hoveredPoint.x / width) * 100}%`,
            top: `${(hoveredPoint.y / height) * 100 - 25}%`,
            transform: "translate(-50%, -100%)",
            backgroundColor: "rgba(10, 25, 20, 0.95)",
            border: "1px solid var(--primary)",
            color: "#fff",
            padding: "6px 10px",
            borderRadius: "4px",
            fontSize: "0.75rem",
            pointerEvents: "none",
            zIndex: 10,
            boxShadow: "var(--shadow-md)",
            whiteSpace: "nowrap"
          }}>
            <strong style={{ color: "var(--primary)" }}>₹{hoveredPoint.price.toFixed(2)} / kg</strong>
            <div style={{ fontSize: "0.65rem", color: "#a0aec0", marginTop: "2px" }}>
              {new Date(hoveredPoint.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 340px",
      gap: "24px",
      padding: "32px",
      height: "calc(100vh - 100px)",
      overflow: "hidden"
    }}>
      {/* Left Panel: Primary Content Area */}
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", overflowY: "auto", paddingRight: "8px" }}>
        
        {/* Search header bar widget */}
        <div className="glass" style={{ padding: "20px 24px", borderRadius: "var(--radius-md)" }}>
          <form onSubmit={handleSearch} style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <span style={{ fontSize: "1.3rem" }}>🔍</span>
            <input
              type="text"
              className="form-input"
              placeholder="Search crop prices (e.g. Tomato, Wheat, Paddy, Mustard)..."
              value={searchCrop}
              onChange={(e) => setSearchCrop(e.target.value)}
              style={{ flex: 1, margin: 0 }}
              required
            />
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loadingSearch || !searchCrop.trim()}
              style={{ minWidth: "120px", margin: 0 }}
            >
              {loadingSearch ? "Searching..." : "Check Prices"}
            </button>
          </form>

          {searchError && (
            <div style={{
              marginTop: "12px",
              padding: "10px 14px",
              backgroundColor: "#fff5f5",
              color: "#e53e3e",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.85rem",
              borderLeft: "4px solid #e53e3e"
            }}>
              ⚠️ {searchError}
            </div>
          )}
        </div>

        {marketData && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Stat Cards Row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: "20px" }}>
              
              {/* Core Price Card */}
              <div className="glass" style={{
                padding: "24px",
                borderRadius: "var(--radius-md)",
                background: "linear-gradient(135deg, rgba(56, 161, 105, 0.12) 0%, rgba(255,255,255,0.4) 100%)",
                border: "1px solid var(--border-light)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                position: "relative",
                overflow: "hidden"
              }}>
                <div>
                  <span style={{ fontSize: "0.7rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)", letterSpacing: "0.05em" }}>
                    NATIONAL AVERAGE RATE
                  </span>
                  <h2 style={{ fontSize: "2.2rem", fontWeight: "800", color: "var(--primary)", marginTop: "6px" }}>
                    ₹{marketData.average_price.toFixed(2)} <span style={{ fontSize: "1rem", fontWeight: "500", color: "var(--text-secondary)" }}>/ kg</span>
                  </h2>
                </div>
                <div style={{ marginTop: "16px" }}>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    Crop Analyzed: <strong style={{ color: "var(--text-primary)" }}>{marketData.crop_name}</strong>
                  </span>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>
                    Last recorded: {new Date(marketData.recorded_date).toLocaleDateString([], { month: 'long', day: 'numeric', year: 'numeric' })}
                  </div>
                </div>
                <div style={{ position: "absolute", right: "-15px", bottom: "-15px", fontSize: "5rem", opacity: 0.08 }}>📈</div>
              </div>

              {/* State Averages Card */}
              <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
                <h3 style={{ fontSize: "0.9rem", color: "var(--text-primary)", fontWeight: "700", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  📍 State Level Averages
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px" }}>
                  {marketData.state_averages.map((sa, i) => (
                    <div 
                      key={i} 
                      style={{
                        padding: "10px 12px",
                        backgroundColor: "rgba(255, 255, 255, 0.4)",
                        border: "1px solid var(--border-light)",
                        borderRadius: "var(--radius-sm)",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                      }}
                    >
                      <span style={{ fontSize: "0.85rem", fontWeight: "600", color: "var(--text-secondary)" }}>{sa.state}</span>
                      <strong style={{ fontSize: "0.95rem", color: "var(--text-primary)" }}>₹{sa.price_per_kg.toFixed(2)}</strong>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Price Chart and Top Mandis split row */}
            <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: "24px" }}>
              
              {/* Trends widget */}
              <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h3 style={{ fontSize: "1rem", color: "var(--text-primary)", fontWeight: "700" }}>
                    📊 30-Day Historical Trend
                  </h3>
                  <button 
                    className="btn btn-secondary"
                    onClick={handleAIExplain}
                    disabled={loadingAI || trendData.length === 0}
                    style={{ padding: "6px 12px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "6px", margin: 0 }}
                  >
                    ✨ {loadingAI ? "Analyzing..." : "Explain with AI"}
                  </button>
                </div>

                {renderSVGChart()}

                {aiExplanation && (
                  <div className="animate-fade-in" style={{
                    marginTop: "8px",
                    padding: "16px",
                    backgroundColor: "var(--primary-soft)",
                    borderLeft: "4px solid var(--primary)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.85rem",
                    color: "var(--text-primary)",
                    lineHeight: "1.5"
                  }}>
                    <strong>💡 AI Trend Insights:</strong>
                    <p style={{ marginTop: "4px" }}>{aiExplanation}</p>
                  </div>
                )}
              </div>

              {/* Top Mandis widget */}
              <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column" }}>
                <h3 style={{ fontSize: "1rem", color: "var(--text-primary)", fontWeight: "700", marginBottom: "16px" }}>
                  🏆 Top Markets Offering Best Prices
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px", flex: 1 }}>
                  {marketData.top_markets.slice(0, 4).map((tm, idx) => (
                    <div 
                      key={idx}
                      style={{
                        padding: "12px",
                        backgroundColor: idx === 0 ? "rgba(56, 161, 105, 0.06)" : "rgba(255,255,255,0.3)",
                        border: idx === 0 ? "1.5px solid var(--primary)" : "1px solid var(--border-light)",
                        borderRadius: "var(--radius-sm)",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                      }}
                    >
                      <div>
                        <div style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--text-primary)" }}>
                          {idx + 1}. {tm.market_name}
                        </div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>📍 {tm.state}</div>
                      </div>
                      <strong style={{ fontSize: "1.1rem", color: "var(--primary)" }}>₹{tm.price_per_kg.toFixed(2)}</strong>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Profitability Calculator */}
            <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)" }}>
              <h3 style={{ fontSize: "1.2rem", color: "var(--text-primary)", fontWeight: "800", marginBottom: "6px" }}>
                🧮 Profitability & Revenue Calculator
              </h3>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "20px" }}>
                Estimate cultivation metrics based on average market price rates or enter a custom rate.
              </p>

              {calcError && (
                <div style={{
                  padding: "10px 14px",
                  backgroundColor: "#fff5f5",
                  color: "#e53e3e",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "0.85rem",
                  marginBottom: "16px",
                  borderLeft: "4px solid #e53e3e"
                }}>
                  ⚠️ {calcError}
                </div>
              )}

              <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1.8fr", gap: "32px" }}>
                
                {/* Calculator Form */}
                <form onSubmit={handleCalculate} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label" style={{ fontSize: "0.8rem" }}>Crop Name</label>
                    <input
                      type="text"
                      className="form-input"
                      value={calcCrop}
                      onChange={(e) => setCalcCrop(e.target.value)}
                      required
                    />
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label" style={{ fontSize: "0.8rem" }}>Expected Yield (kg/acre)</label>
                      <input
                        type="number"
                        className="form-input"
                        placeholder="e.g. 1200"
                        value={expectedYield}
                        onChange={(e) => setExpectedYield(e.target.value)}
                        required
                      />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label" style={{ fontSize: "0.8rem" }}>Cultivation Cost (₹)</label>
                      <input
                        type="number"
                        className="form-input"
                        placeholder="e.g. 15000"
                        value={cultivationCost}
                        onChange={(e) => setCultivationCost(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label" style={{ fontSize: "0.8rem" }}>Market Price (₹ / kg)</label>
                    <input
                      type="number"
                      step="0.01"
                      className="form-input"
                      placeholder="e.g. 25.50"
                      value={customPrice}
                      onChange={(e) => setCustomPrice(e.target.value)}
                    />
                  </div>

                  <button 
                    type="submit" 
                    className="btn btn-primary" 
                    disabled={calculating}
                    style={{ marginTop: "8px" }}
                  >
                    {calculating ? "Calculating..." : "Compute Returns"}
                  </button>
                </form>

                {/* Calculation Outputs */}
                <div style={{
                  backgroundColor: "rgba(255,255,255,0.25)",
                  border: "1px solid var(--border-light)",
                  borderRadius: "var(--radius-md)",
                  padding: "24px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center"
                }}>
                  {calculationResult ? (
                    <div className="animate-fade-in" style={{ width: "100%", display: "flex", flexDirection: "column", gap: "16px" }}>
                      
                      {/* Profit Margin Gauge */}
                      <div style={{ textAlign: "center", paddingBottom: "12px", borderBottom: "1px solid var(--border-light)" }}>
                        <div style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)" }}>
                          Estimated Profit Margin
                        </div>
                        <div style={{
                          fontSize: "2.4rem",
                          fontWeight: "900",
                          color: calculationResult.profit_margin >= 0 ? "var(--primary)" : "#e53e3e",
                          marginTop: "4px"
                        }}>
                          {calculationResult.profit_margin.toFixed(1)}%
                        </div>
                      </div>

                      {/* Revenue and Cost split */}
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "4px" }}>
                        <div style={{ textAlign: "center" }}>
                          <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Estimated Revenue</span>
                          <div style={{ fontSize: "1.2rem", fontWeight: "800", color: "var(--text-primary)", marginTop: "2px" }}>
                            ₹{calculationResult.estimated_revenue.toLocaleString()}
                          </div>
                        </div>
                        <div style={{ textAlign: "center" }}>
                          <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Net Profit</span>
                          <div style={{
                            fontSize: "1.2rem",
                            fontWeight: "800",
                            color: calculationResult.estimated_profit >= 0 ? "var(--primary)" : "#e53e3e",
                            marginTop: "2px"
                          }}>
                            ₹{calculationResult.estimated_profit.toLocaleString()}
                          </div>
                        </div>
                      </div>

                      {/* Summary Text */}
                      <div style={{
                        marginTop: "8px",
                        padding: "10px 14px",
                        backgroundColor: calculationResult.estimated_profit >= 0 ? "rgba(56, 161, 105, 0.05)" : "rgba(229, 62, 62, 0.05)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "0.8rem",
                        color: "var(--text-secondary)",
                        textAlign: "center",
                        lineHeight: "1.4"
                      }}>
                        {calculationResult.estimated_profit >= 0 ? (
                          <span>🌱 High return margin. Your cultivation variables yield an estimated profit of <strong>₹{calculationResult.estimated_profit.toLocaleString()}</strong> per acre.</span>
                        ) : (
                          <span>⚠️ Warning: High cultivation costs relative to pricing yield a net loss. Adjust inputs or check other crop parameters.</span>
                        )}
                      </div>

                    </div>
                  ) : (
                    <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center" }}>
                      📊 Enter expected yield and cost parameters, then click Compute to render detailed return forecasts here.
                    </div>
                  )}
                </div>

              </div>
            </div>

          </div>
        )}

      </div>

      {/* Right Sidebar: Historical Calculations History list */}
      <div className="glass" style={{
        borderRadius: "var(--radius-md)",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        overflowY: "hidden"
      }}>
        <h3 style={{ fontSize: "1.1rem", padding: "0 8px", color: "var(--text-primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
          📜 Calculation History
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px", overflowY: "auto", flex: 1, padding: "2px" }}>
          {loadingHistory ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              <span className="dot-spinner"></span> Loading history...
            </div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              No history calculations saved yet.
            </div>
          ) : (
            history.map((item) => {
              const isPositive = item.estimated_profit >= 0;
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
                    borderLeft: isPositive ? "4px solid var(--primary)" : "4px solid #e53e3e",
                    transition: "var(--transition-smooth)"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>
                      🌾 {item.crop_name}
                    </strong>
                    <span style={{
                      fontSize: "0.7rem",
                      fontWeight: "700",
                      color: isPositive ? "var(--primary)" : "#e53e3e"
                    }}>
                      {item.profit_margin.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                    Yield: {item.expected_yield} kg/ac | Cost: ₹{item.cultivation_cost.toLocaleString()}
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "6px", borderTop: "1px solid rgba(0,0,0,0.03)", paddingTop: "4px" }}>
                    <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>
                      Profit: <strong>₹{item.estimated_profit.toLocaleString()}</strong>
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

export default MarketIntelligencePage;
