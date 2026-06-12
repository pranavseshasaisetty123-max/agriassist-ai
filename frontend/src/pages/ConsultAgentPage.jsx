import React, { useState, useEffect } from "react";
import api from "../services/api";

const ConsultAgentPage = ({ onNavigateToPlanner }) => {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [activeConsult, setActiveConsult] = useState(null);
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);

  const loadingMessages = [
    "Reading latest soil report parameters...",
    "Retrieving local weather forecast trends...",
    "Fetching smart crop recommendations...",
    "Evaluating yield and price profitability...",
    "Assessing pest, disease, and weather risk alerts...",
    "Virtual agronomist is synthesizing recommendations..."
  ];

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    let interval;
    if (asking) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev + 1) % loadingMessages.length);
      }, 2500);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [asking]);

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const resp = await api.get("/consult-agent/history");
      setHistory(resp.data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleAsk = async (queryText) => {
    const query = queryText || question;
    if (!query.trim() || asking) return;

    setAsking(true);
    setAskError("");
    setActiveConsult(null);
    try {
      const resp = await api.post("/consult-agent/ask", { question: query });
      setActiveConsult(resp.data);
      setQuestion("");
      fetchHistory();
    } catch (err) {
      console.error("Failed to consult agronomist:", err);
      setAskError(err.response?.data?.detail || "Agronomist consultation failed. Please try again.");
    } finally {
      setAsking(false);
    }
  };

  const handleSelectHistory = async (id) => {
    setAsking(true);
    setAskError("");
    try {
      const resp = await api.get(`/consult-agent/${id}`);
      setActiveConsult(resp.data);
    } catch (err) {
      console.error("Failed to fetch details:", err);
      setAskError("Failed to retrieve consultation details.");
    } finally {
      setAsking(false);
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 80) return "#38a169"; // Green
    if (score >= 50) return "#dd6b20"; // Orange
    return "#e53e3e"; // Red
  };

  const getConfidenceBadgeColor = (score) => {
    if (score >= 85) return { color: "#2f855a", bg: "#f0fff4" };
    if (score >= 60) return { color: "#c05621", bg: "#fffaf0" };
    return { color: "#9b2c2c", bg: "#fff5f5" };
  };

  const suggestedQuestions = [
    "Which crop should I grow next?",
    "How can I maximize profit?",
    "What is my biggest farm risk?",
    "Compare Tomato vs Paddy",
    "Should I delay planting?"
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "280px 1fr",
        gap: "24px",
        padding: "32px",
        height: "calc(100vh - 100px)",
        overflow: "hidden",
      }}
    >
      {/* Left Sidebar: Conversation History Logs */}
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
          onClick={() => {
            setActiveConsult(null);
            setAskError("");
            setQuestion("");
          }}
          style={{ width: "100%", height: "42px" }}
        >
          ➕ New Consultation
        </button>

        <div style={{ borderBottom: "1px solid var(--border-light)", paddingBottom: "8px" }}>
          <strong style={{ fontSize: "0.85rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            📜 Recent Sessions
          </strong>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            overflowY: "auto",
            flex: 1,
            paddingRight: "2px"
          }}
        >
          {loadingHistory ? (
            <div style={{ textAlign: "center", padding: "24px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
              <span className="dot-spinner"></span> Loading history...
            </div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: "center", padding: "24px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
              No previous consultations logged.
            </div>
          ) : (
            history.map((h) => (
              <div
                key={h.id}
                className={`glass hover-card ${activeConsult?.id === h.id ? "active-item" : ""}`}
                onClick={() => handleSelectHistory(h.id)}
                style={{
                  padding: "12px",
                  borderRadius: "var(--radius-sm)",
                  cursor: "pointer",
                  backgroundColor: activeConsult?.id === h.id ? "rgba(56, 161, 105, 0.1)" : "var(--bg-card)",
                  borderLeft: activeConsult?.id === h.id ? "4px solid var(--primary)" : "4px solid transparent",
                  transition: "var(--transition-smooth)"
                }}
              >
                <p style={{
                  fontSize: "0.825rem",
                  fontWeight: "600",
                  color: "var(--text-primary)",
                  margin: "0 0 6px",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis"
                }}>
                  {h.question}
                </p>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.68rem", color: "var(--text-muted)" }}>
                  <span>Health Score: <strong>{h.farm_health_score}</strong></span>
                  <span>{new Date(h.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Main Workspace panel */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          height: "100%",
          overflow: "hidden"
        }}
      >
        <div style={{ flex: 1, overflowY: "auto", paddingRight: "8px" }}>
          
          {/* 1. Loading AI Thinking State */}
          {asking && (
            <div style={{
              height: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "24px",
              padding: "48px"
            }}>
              <div className="pulse-ring" style={{ width: "80px", height: "80px", fontSize: "2.5rem", display: "flex", alignItems: "center", justifyContent: "center" }}>
                🤖
              </div>
              <div style={{ textAlign: "center" }}>
                <h4 style={{ color: "var(--text-primary)", fontWeight: "800", fontSize: "1.1rem", margin: "0 0 8px" }}>
                  Virtual Agronomist Analyzing...
                </h4>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", margin: 0 }}>
                  {loadingMessages[loadingStep]}
                </p>
              </div>
            </div>
          )}

          {/* 2. Initial Welcome Hero & Suggested Questions */}
          {!asking && !activeConsult && (
            <div className="animate-fade-in" style={{ padding: "16px 0" }}>
              <div className="chat-welcome-hero glass" style={{ padding: "40px", borderRadius: "var(--radius-md)", textAlign: "center" }}>
                <div className="hero-badge" style={{ marginBottom: "16px" }}>🌱 Unified Farm Advisor</div>
                <h1 className="hero-title" style={{ fontSize: "1.8rem", fontWeight: "900", color: "var(--text-primary)", margin: "0 0 12px" }}>
                  Virtual Agronomist Reasoning Engine
                </h1>
                <p className="hero-subtitle" style={{ maxWidth: "650px", margin: "0 auto 32px", fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                  Ask questions regarding your farm planner schedules, soil parameters, weather hazards, price profit forecasting, and disease warnings. The agronomist analyzes all modules to return cohesive recommendations.
                </p>
                
                <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "16px", fontWeight: "700" }}>
                  Suggested Questions
                </h4>
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: "16px",
                  maxWidth: "800px",
                  margin: "0 auto"
                }}>
                  {suggestedQuestions.map((q, idx) => (
                    <div
                      key={idx}
                      className="glass hover-card"
                      onClick={() => handleAsk(q)}
                      style={{
                        padding: "16px",
                        borderRadius: "var(--radius-sm)",
                        cursor: "pointer",
                        backgroundColor: "var(--bg-card)",
                        transition: "var(--transition-bounce)"
                      }}
                    >
                      <p style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--primary)", margin: 0 }}>
                        {q} ➔
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 3. Render AI Response Cards */}
          {!asking && activeConsult && (
            <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px", padding: "8px 0" }}>
              
              {/* Top Overview: Health Gauge & Summary */}
              <div className="glass" style={{
                padding: "24px",
                borderRadius: "var(--radius-md)",
                display: "grid",
                gridTemplateColumns: "130px 1fr 180px",
                gap: "24px",
                alignItems: "center"
              }}>
                {/* Health Score Gauge */}
                <div style={{ position: "relative", width: "110px", height: "110px", margin: "0 auto" }}>
                  <svg width="110" height="110" viewBox="0 0 110 110">
                    <circle cx="55" cy="55" r="46" fill="none" stroke="var(--border-light)" strokeWidth="8" />
                    <circle
                      cx="55"
                      cy="55"
                      r="46"
                      fill="none"
                      stroke={getHealthScoreColor(activeConsult.farm_health_score)}
                      strokeWidth="8"
                      strokeDasharray="289"
                      strokeDashoffset={289 - (activeConsult.farm_health_score / 100) * 289}
                      strokeLinecap="round"
                      transform="rotate(-90 55 55)"
                      style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
                    />
                  </svg>
                  <div style={{
                    position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
                    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center"
                  }}>
                    <span style={{ fontSize: "1.7rem", fontWeight: "900", color: "var(--text-primary)", lineHeight: 1 }}>
                      {activeConsult.farm_health_score}
                    </span>
                    <span style={{ fontSize: "0.55rem", color: "var(--text-secondary)", fontWeight: "800", textTransform: "uppercase", marginTop: "2px" }}>
                      Health Index
                    </span>
                  </div>
                </div>

                {/* Health Summary details */}
                <div>
                  <span style={{ fontSize: "0.7rem", fontWeight: "800", color: "var(--primary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Expert Consultation Analysis
                  </span>
                  <h3 style={{ fontSize: "1.25rem", fontWeight: "900", color: "var(--text-primary)", margin: "4px 0 6px" }}>
                    Virtual Agronomist Health Evaluation
                  </h3>
                  <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", margin: 0, lineHeight: "1.5" }}>
                    {activeConsult.health_summary}
                  </p>
                </div>

                {/* Confidence & Created details */}
                <div style={{ textAlign: "right", display: "flex", flexDirection: "column", gap: "8px", alignItems: "flex-end" }}>
                  <div>
                    <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", display: "block" }}>Confidence Score</span>
                    <span
                      style={{
                        fontSize: "0.75rem",
                        fontWeight: "800",
                        padding: "3px 10px",
                        borderRadius: "4px",
                        display: "inline-block",
                        marginTop: "2px",
                        color: getConfidenceBadgeColor(activeConsult.confidence_score).color,
                        backgroundColor: getConfidenceBadgeColor(activeConsult.confidence_score).bg
                      }}
                    >
                      {activeConsult.confidence_score}% certainty
                    </span>
                  </div>
                  {activeConsult.created_at && (
                    <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>
                      Logged: {new Date(activeConsult.created_at).toLocaleString()}
                    </span>
                  )}
                </div>
              </div>

              {/* Specific Answer and Recommended Actions */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "24px", alignItems: "start" }}>
                
                {/* Left Side: Specific Answer & Key Findings */}
                <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                  {/* The Detailed Answer */}
                  <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
                    <h4 style={{ fontSize: "1.05rem", fontWeight: "800", color: "var(--text-primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "10px", marginBottom: "14px" }}>
                      💬 Detailed Response
                    </h4>
                    <p style={{ fontSize: "0.925rem", color: "var(--text-secondary)", lineHeight: "1.6", margin: 0, whiteSpace: "pre-line" }}>
                      {activeConsult.answer}
                    </p>
                  </div>

                  {/* Key Findings list */}
                  <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
                    <h4 style={{ fontSize: "1.05rem", fontWeight: "800", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px", borderBottom: "1px solid var(--border-light)", paddingBottom: "10px", marginBottom: "14px" }}>
                      🔍 Key Diagnostic Findings
                    </h4>
                    <ul style={{ margin: 0, paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "10px" }}>
                      {activeConsult.key_findings.map((finding, idx) => (
                        <li key={idx} style={{ fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                          {finding}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Right Side: Risk Assessment & Action Checklist */}
                <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                  {/* Risk Assessment Card */}
                  <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", borderLeft: "5px solid #e53e3e" }}>
                    <h4 style={{ fontSize: "0.95rem", fontWeight: "800", color: "#e53e3e", margin: "0 0 10px", display: "flex", alignItems: "center", gap: "6px" }}>
                      ⚠️ Hazards & Risks
                    </h4>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.5", margin: 0 }}>
                      {activeConsult.risk_assessment}
                    </p>
                  </div>

                  {/* Recommended Action Items */}
                  <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)" }}>
                    <h4 style={{ fontSize: "0.95rem", fontWeight: "800", color: "var(--text-primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "8px", marginBottom: "12px" }}>
                      ✅ Recommended Actions
                    </h4>
                    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                      {activeConsult.recommended_actions.map((action, idx) => (
                        <div key={idx} style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
                          <span style={{ color: "var(--primary)", fontWeight: "bold", fontSize: "0.95rem", lineHeight: 1 }}>✓</span>
                          <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                            {action}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {askError && (
            <div className="glass animate-fade-in" style={{ padding: "16px", borderRadius: "var(--radius-sm)", borderLeft: "4px solid #e53e3e", backgroundColor: "#fff5f5", color: "#e53e3e", marginTop: "16px", fontSize: "0.85rem" }}>
              ⚠️ {askError}
            </div>
          )}
        </div>

        {/* Bottom Message Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="chat-input-bar glass"
          style={{ padding: "12px" }}
        >
          <input
            type="text"
            className="chat-text-input"
            placeholder="Ask the Virtual Agronomist (e.g. 'Compare Tomato vs Paddy profit margins')..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={asking}
            style={{ fontSize: "0.9rem" }}
          />
          <button
            type="submit"
            className="btn btn-primary send-button"
            disabled={asking || !question.trim()}
            style={{ height: "42px", padding: "0 20px" }}
          >
            {asking ? "Consulting..." : "Send Advice ➔"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ConsultAgentPage;
