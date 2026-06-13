import React from "react";
import { useNavigate } from "react-router-dom";

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      backgroundColor: "#080d0a",
      color: "#f0fff4",
      fontFamily: "'Inter', sans-serif",
      minHeight: "100vh",
      overflowX: "hidden"
    }}>
      {/* Navigation Header */}
      <header style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "20px 48px",
        borderBottom: "1px solid rgba(56, 161, 105, 0.15)",
        backgroundColor: "rgba(8, 13, 10, 0.8)",
        backdropFilter: "blur(12px)",
        position: "sticky",
        top: 0,
        zIndex: 1000
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "1.8rem" }}>🌱</span>
          <span style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: "1.35rem",
            fontWeight: "800",
            color: "#38a169",
            letterSpacing: "-0.02em"
          }}>AgriAssist AI</span>
        </div>
        <div style={{ display: "flex", gap: "24px", alignItems: "center" }}>
          <span
            onClick={() => navigate("/login")}
            style={{ cursor: "pointer", fontWeight: "600", fontSize: "0.95rem", color: "#a3b8ad", transition: "all 0.2s" }}
            onMouseOver={(e) => e.target.style.color = "#f0fff4"}
            onMouseOut={(e) => e.target.style.color = "#a3b8ad"}
          >
            Login
          </span>
          <button
            onClick={() => navigate("/register")}
            className="btn"
            style={{
              backgroundColor: "#38a169",
              color: "#ffffff",
              padding: "10px 20px",
              borderRadius: "8px",
              fontSize: "0.9rem",
              fontWeight: "700",
              border: "none",
              cursor: "pointer",
              boxShadow: "0 4px 14px rgba(56, 161, 105, 0.3)"
            }}
          >
            Register
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        padding: "80px 48px 60px",
        textAlign: "center",
        maxWidth: "900px",
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "24px"
      }}>
        <span style={{
          fontSize: "0.85rem",
          fontWeight: "700",
          color: "#38a169",
          textTransform: "uppercase",
          letterSpacing: "0.15em",
          backgroundColor: "rgba(56, 161, 105, 0.1)",
          padding: "6px 16px",
          borderRadius: "50px",
          display: "inline-block"
        }}>
          🌾 Investor-Grade Precision Agriculture
        </span>
        <h1 style={{
          fontSize: "3.25rem",
          fontWeight: "900",
          fontFamily: "'Outfit', sans-serif",
          lineHeight: "1.15",
          letterSpacing: "-0.03em",
          color: "#ffffff",
          margin: 0
        }}>
          Transform Farm Operations with <span style={{ color: "#38a169" }}>AI-Powered</span> Intelligence
        </h1>
        <p style={{
          fontSize: "1.15rem",
          color: "#a3b8ad",
          lineHeight: "1.6",
          maxWidth: "700px",
          margin: 0
        }}>
          AgriAssist AI aggregates soil parameters, weather analytics, market data, and crop planning into a unified multi-farm management platform for professional farmers.
        </p>
        <div style={{ display: "flex", gap: "16px", marginTop: "12px" }}>
          <button
            onClick={() => navigate("/chat")}
            className="btn btn-primary"
            style={{ padding: "14px 28px", fontSize: "1rem", borderRadius: "8px", background: "#38a169" }}
          >
            Launch Dashboard ➔
          </button>
          <button
            onClick={() => {
              const element = document.getElementById("features");
              element?.scrollIntoView({ behavior: "smooth" });
            }}
            className="btn btn-secondary"
            style={{
              padding: "14px 28px",
              fontSize: "1rem",
              borderRadius: "8px",
              border: "1px solid rgba(56, 161, 105, 0.4)",
              color: "#38a169"
            }}
          >
            Explore Features
          </button>
        </div>
      </section>

      {/* Dashboard Preview / Mockup */}
      <section style={{ padding: "0 48px 80px", textAlign: "center" }}>
        <div style={{
          maxWidth: "1000px",
          margin: "0 auto",
          background: "linear-gradient(135deg, #132219 0%, #0d1711 100%)",
          borderRadius: "16px",
          border: "1px solid rgba(56, 161, 105, 0.25)",
          boxShadow: "0 20px 40px rgba(0, 0, 0, 0.6), 0 0 40px rgba(56, 161, 105, 0.08)",
          padding: "20px",
          overflow: "hidden"
        }}>
          {/* Simulated Browser Header */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            borderBottom: "1px solid rgba(56, 161, 105, 0.1)",
            paddingBottom: "12px",
            marginBottom: "16px"
          }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#e53e3e" }}></span>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#dd6b20" }}></span>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#38a169" }}></span>
            <div style={{
              backgroundColor: "rgba(0,0,0,0.3)",
              fontSize: "0.75rem",
              padding: "4px 24px",
              borderRadius: "4px",
              color: "#a3b8ad",
              marginLeft: "16px"
            }}>agriassist.ai/dashboard</div>
          </div>
          
          {/* Simulated App Dashboard Layout Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: "16px", textAlign: "left" }}>
            {/* Sidebar */}
            <div style={{ borderRight: "1px solid rgba(56, 161, 105, 0.1)", paddingRight: "12px", display: "flex", flexDirection: "column", gap: "10px" }}>
              <div style={{ height: "24px", backgroundColor: "rgba(56,161,105,0.15)", borderRadius: "4px", width: "80%" }}></div>
              <div style={{ height: "18px", backgroundColor: "rgba(255,255,255,0.04)", borderRadius: "4px" }}></div>
              <div style={{ height: "18px", backgroundColor: "rgba(255,255,255,0.04)", borderRadius: "4px" }}></div>
              <div style={{ height: "18px", backgroundColor: "rgba(255,255,255,0.04)", borderRadius: "4px" }}></div>
            </div>
            {/* Main Area */}
            <div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginBottom: "16px" }}>
                <div style={{ padding: "16px", backgroundColor: "rgba(255,255,255,0.02)", border: "1px solid rgba(56,161,105,0.1)", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.65rem", color: "#a3b8ad", textTransform: "uppercase" }}>Holdings</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "#ffffff", marginTop: "4px" }}>25.5 Ac</div>
                </div>
                <div style={{ padding: "16px", backgroundColor: "rgba(255,255,255,0.02)", border: "1px solid rgba(56,161,105,0.1)", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.65rem", color: "#a3b8ad", textTransform: "uppercase" }}>Health Index</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "#38a169", marginTop: "4px" }}>92/100</div>
                </div>
                <div style={{ padding: "16px", backgroundColor: "rgba(255,255,255,0.02)", border: "1px solid rgba(56,161,105,0.1)", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.65rem", color: "#a3b8ad", textTransform: "uppercase" }}>Est. Profit</span>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "#38a169", marginTop: "4px" }}>Rs. 90,000</div>
                </div>
              </div>
              <div style={{ height: "120px", backgroundColor: "rgba(255,255,255,0.02)", border: "1px solid rgba(56,161,105,0.1)", borderRadius: "8px", padding: "16px" }}>
                <span style={{ fontSize: "0.75rem", color: "#a3b8ad", textTransform: "uppercase", fontWeight: "700" }}>Live Operations Timeline</span>
                <div style={{ display: "flex", gap: "10px", marginTop: "16px" }}>
                  <div style={{ ...skeletonStyle, height: "40px", flex: 1 }}></div>
                  <div style={{ ...skeletonStyle, height: "40px", flex: 1 }}></div>
                  <div style={{ ...skeletonStyle, height: "40px", flex: 1 }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" style={{
        padding: "80px 48px",
        backgroundColor: "#0b110e",
        borderTop: "1px solid rgba(56, 161, 105, 0.1)"
      }}>
        <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
          <h2 style={{
            fontSize: "2.2rem",
            fontWeight: "800",
            fontFamily: "'Outfit', sans-serif",
            textAlign: "center",
            marginBottom: "48px"
          }}>Core Capabilities</h2>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px" }}>
            <div style={featureCardStyle}>
              <span style={{ fontSize: "2rem" }}>🧪</span>
              <h3 style={{ fontSize: "1.15rem", color: "#ffffff" }}>Soil Health Diagnostics</h3>
              <p style={{ fontSize: "0.85rem", color: "#a3b8ad", lineHeight: "1.5" }}>
                Input NPK parameters to check diagnostic metrics and print tailored fertilizer treatment schedules.
              </p>
            </div>
            <div style={featureCardStyle}>
              <span style={{ fontSize: "2rem" }}>🔍</span>
              <h3 style={{ fontSize: "1.15rem", color: "#ffffff" }}>AI Leaf Spot Scanning</h3>
              <p style={{ fontSize: "0.85rem", color: "#a3b8ad", lineHeight: "1.5" }}>
                Upload crop foliage images to detect pests, fungus, or deficiencies, detailing organic mitigation steps.
              </p>
            </div>
            <div style={featureCardStyle}>
              <span style={{ fontSize: "2rem" }}>📅</span>
              <h3 style={{ fontSize: "1.15rem", color: "#ffffff" }}>Weather-Adaptive Planning</h3>
              <p style={{ fontSize: "0.85rem", color: "#a3b8ad", lineHeight: "1.5" }}>
                Generate weather-aware sowing calendars that adjust schedules to rainfall anomalies automatically.
              </p>
            </div>
            <div style={featureCardStyle}>
              <span style={{ fontSize: "2rem" }}>🤖</span>
              <h3 style={{ fontSize: "1.15rem", color: "#ffffff" }}>Virtual AI Agronomist</h3>
              <p style={{ fontSize: "0.85rem", color: "#a3b8ad", lineHeight: "1.5" }}>
                Ask questions to the unified recommendations coach linked directly to weather, prices, and risks.
              </p>
            </div>
            <div style={featureCardStyle}>
              <span style={{ fontSize: "2rem" }}>📊</span>
              <h3 style={{ fontSize: "1.15rem", color: "#ffffff" }}>Multi-Farm Portfolio</h3>
              <p style={{ fontSize: "0.85rem", color: "#a3b8ad", lineHeight: "1.5" }}>
                Register and check multiple land parcels, tracking expected yield and aggregate profit metrics.
              </p>
            </div>
            <div style={featureCardStyle}>
              <span style={{ fontSize: "2rem" }}>📈</span>
              <h3 style={{ fontSize: "1.15rem", color: "#ffffff" }}>Analytics & PDF Reports</h3>
              <p style={{ fontSize: "0.85rem", color: "#a3b8ad", lineHeight: "1.5" }}>
                Monitor performance using charts and export comprehensive executive farm status reports as PDF.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section style={{ padding: "80px 48px", maxWidth: "900px", margin: "0 auto" }}>
        <h2 style={{
          fontSize: "2.2rem",
          fontWeight: "800",
          fontFamily: "'Outfit', sans-serif",
          textAlign: "center",
          marginBottom: "40px"
        }}>Why AgriAssist AI?</h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px" }}>
          <div>
            <h4 style={{ color: "#38a169", fontSize: "1.1rem", marginBottom: "8px", fontWeight: "700" }}>✓ Data-Driven Projections</h4>
            <p style={{ fontSize: "0.9rem", color: "#a3b8ad", lineHeight: "1.5" }}>
              Eliminate guesswork by validating soil values and matching optimal crop matches based on real local historical yield databases.
            </p>
          </div>
          <div>
            <h4 style={{ color: "#38a169", fontSize: "1.1rem", marginBottom: "8px", fontWeight: "700" }}>✓ Proactive Risk Reduction</h4>
            <p style={{ fontSize: "0.9rem", color: "#a3b8ad", lineHeight: "1.5" }}>
              Receive early warning signals of pest hazards, severe weather anomalies, or crop disease trends.
            </p>
          </div>
          <div>
            <h4 style={{ color: "#38a169", fontSize: "1.1rem", marginBottom: "8px", fontWeight: "700" }}>✓ Executive Level Reporting</h4>
            <p style={{ fontSize: "0.9rem", color: "#a3b8ad", lineHeight: "1.5" }}>
              Export data as PDF summaries to keep investors, banks, or insurance providers updated on your portfolio’s health metrics.
            </p>
          </div>
          <div>
            <h4 style={{ color: "#38a169", fontSize: "1.1rem", marginBottom: "8px", fontWeight: "700" }}>✓ Responsive Mobile Audits</h4>
            <p style={{ fontSize: "0.9rem", color: "#a3b8ad", lineHeight: "1.5" }}>
              Access diagnostic reports, schedules, and virtual consulting chat logs natively on mobile devices in the field.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: "40px 48px",
        textAlign: "center",
        borderTop: "1px solid rgba(56, 161, 105, 0.15)",
        backgroundColor: "#060907",
        fontSize: "0.85rem",
        color: "#6b7d74"
      }}>
        <p style={{ marginBottom: "12px" }}>🌱 AgriAssist AI — Production placement agricultural intelligence platform.</p>
        <p>© 2026 AgriAssist AI. Built with FastAPI, React, MySQL, and Gemini AI. All rights reserved.</p>
      </footer>
    </div>
  );
};

const featureCardStyle = {
  padding: "28px",
  backgroundColor: "rgba(255, 255, 255, 0.02)",
  borderRadius: "12px",
  border: "1px solid rgba(56, 161, 105, 0.12)",
  display: "flex",
  flexDirection: "column",
  gap: "12px"
};

const skeletonStyle = {
  background: "linear-gradient(90deg, rgba(56, 161, 105, 0.1) 25%, rgba(56, 161, 105, 0.05) 50%, rgba(56, 161, 105, 0.1) 75%)",
  backgroundSize: "200% 100%",
  borderRadius: "4px"
};

export default LandingPage;
