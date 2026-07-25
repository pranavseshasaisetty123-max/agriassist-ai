import React, { useEffect, useState } from "react";
import api from "../../../services/api";
import { useLanguage } from "../../../context/LanguageContext";
import WeatherWidget from "../components/WeatherWidget";
import ForecastWidget from "../components/ForecastWidget";
import AdvisoryWidget from "../components/AdvisoryWidget";

const DashboardOverview = ({
  onNavigateToChat,
  onNavigateToSoil,
  onNavigateToMarket,
  onNavigateToYield,
  onNavigateToPlanner,
  onNavigateToRisk,
  onNavigateToConsultant,
  onNavigateToNotifications,
  onNavigateToAnalytics,
  onNavigateToPortfolio
}) => {
  const { t } = useLanguage();
  const [latestReport, setLatestReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upcomingTask, setUpcomingTask] = useState(null);
  const [overdueCount, setOverdueCount] = useState(0);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [analyticsKPIs, setAnalyticsKPIs] = useState(null);
  const [portfolioKPIs, setPortfolioKPIs] = useState(null);
  const [marketPrices, setMarketPrices] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [
          soilRes,
          upRes,
          overRes,
          riskRes,
          notifRes,
          kpiRes,
          portRes,
          marketRes
        ] = await Promise.allSettled([
          api.get("/soil/reports?limit=1"),
          api.get("/farm-planner/tasks/upcoming?days=30"),
          api.get("/farm-planner/tasks/overdue"),
          api.get("/risk-intelligence/warnings"),
          api.get("/notifications"),
          api.get("/analytics/kpis"),
          api.get("/farms/portfolio"),
          api.get("/market-intelligence/prices?limit=4")
        ]);

        if (soilRes.status === "fulfilled" && soilRes.value.data?.length > 0) {
          setLatestReport(soilRes.value.data[0]);
        }
        if (upRes.status === "fulfilled" && upRes.value.data?.length > 0) {
          setUpcomingTask(upRes.value.data[0]);
        }
        if (overRes.status === "fulfilled") {
          setOverdueCount(overRes.value.data.length);
        }
        if (riskRes.status === "fulfilled") {
          setRiskAssessment(riskRes.value.data);
        }
        if (notifRes.status === "fulfilled") {
          setNotifications(notifRes.value.data);
        }
        if (kpiRes.status === "fulfilled") {
          setAnalyticsKPIs(kpiRes.value.data);
        }
        if (portRes.status === "fulfilled") {
          setPortfolioKPIs(portRes.value.data);
        }
        if (marketRes.status === "fulfilled" && Array.isArray(marketRes.value.data)) {
          setMarketPrices(marketRes.value.data.slice(0, 4));
        }
      } catch (err) {
        console.error("Failed to load dashboard parameters:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="dashboard-scroll-container animate-fade-in" style={{ padding: "24px 28px", overflowY: "auto", height: "100%", display: "flex", flexDirection: "column", gap: "24px" }}>
      
      {/* 1. Hero Header & AI Recommendation Card Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
        
        {/* Weather Hero Widget */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <WeatherWidget />
        </div>

        {/* 🌱 AI Executive Recommendation Card */}
        <div className="saas-card hover-card" style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          borderLeft: "4px solid var(--primary)",
          background: "var(--bg-card)",
          boxShadow: "var(--shadow-sm)"
        }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span style={{ fontSize: "0.78rem", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--primary)", display: "flex", alignItems: "center", gap: "6px" }}>
                🌱 {t("db_today_recommendation")}
              </span>
              <span className="saas-badge saas-badge-success">94%</span>
            </div>

            <h3 style={{ fontSize: "1.1rem", color: "var(--text-primary)", fontWeight: "700", marginBottom: "6px" }}>
              {latestReport ? `${t("form_nitrogen")} (${latestReport.nitrogen} mg/kg)` : t("db_nitrogen_low")}
            </h3>

            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.5", marginBottom: "16px" }}>
              {t("db_recommended_crop")}: <strong style={{ color: "var(--text-primary)" }}>Soybean</strong>. {t("db_expected_yield")}: 95%.
            </p>
          </div>

          <div style={{ paddingTop: "12px", borderTop: "1px solid var(--border-light)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", display: "block", textTransform: "uppercase", fontWeight: "700" }}>
                {t("db_expected_profit")}
              </span>
              <span style={{ fontSize: "1.2rem", fontWeight: "800", color: "var(--advisory-info-text)" }}>₹42,000</span>
            </div>
            <button className="btn btn-primary" onClick={onNavigateToSoil} style={{ padding: "6px 14px", fontSize: "0.8rem" }}>
              {t("db_view_details")} →
            </button>
          </div>
        </div>
      </div>

      {/* 2. Quick Actions Bar */}
      <div className="saas-card" style={{ padding: "14px 20px", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px", background: "var(--bg-card)" }}>
        <span style={{ fontSize: "0.82rem", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)" }}>
          ⚡ {t("db_quick_actions")}
        </span>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          <button className="btn btn-secondary" onClick={onNavigateToSoil} style={{ padding: "6px 14px", fontSize: "0.82rem" }}>
            🧪 {t("action_analyze_soil")}
          </button>
          <button className="btn btn-secondary" onClick={onNavigateToChat} style={{ padding: "6px 14px", fontSize: "0.82rem" }}>
            🔍 {t("action_detect_disease")}
          </button>
          <button className="btn btn-secondary" onClick={onNavigateToChat} style={{ padding: "6px 14px", fontSize: "0.82rem" }}>
            🤖 {t("action_ask_ai")}
          </button>
          <button className="btn btn-secondary" onClick={onNavigateToMarket} style={{ padding: "6px 14px", fontSize: "0.82rem" }}>
            💰 {t("action_view_prices")}
          </button>
          <button className="btn btn-primary" onClick={onNavigateToYield} style={{ padding: "6px 14px", fontSize: "0.82rem" }}>
            📈 {t("action_predict_yield")}
          </button>
        </div>
      </div>

      {/* 3. Farm KPIs Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
        
        {/* KPI 1: Total Area */}
        <div className="saas-card hover-card" style={{ cursor: "pointer" }} onClick={onNavigateToPortfolio}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>{t("db_total_area")}</span>
            <span style={{ fontSize: "1.2rem" }}>🏡</span>
          </div>
          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: "var(--text-primary)" }}>
            {portfolioKPIs?.total_area ? `${portfolioKPIs.total_area.toFixed(1)} Ac` : "250.7 Ac"}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "4px" }}>
            {portfolioKPIs?.total_farms || 3} {t("nav_portfolio")}
          </div>
        </div>

        {/* KPI 2: Crop Health Index */}
        <div className="saas-card hover-card" style={{ cursor: "pointer" }} onClick={onNavigateToAnalytics}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>{t("db_health_score")}</span>
            <span style={{ fontSize: "1.2rem" }}>🌿</span>
          </div>
          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: "var(--advisory-info-text)" }}>
            {analyticsKPIs?.health_score ? `${analyticsKPIs.health_score.toFixed(0)}/100` : "88/100"}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "4px" }}>
            {t("db_soil_health")}
          </div>
        </div>

        {/* KPI 3: Expected Profit Return */}
        <div className="saas-card hover-card" style={{ cursor: "pointer" }} onClick={onNavigateToMarket}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>{t("db_expected_profit")}</span>
            <span style={{ fontSize: "1.2rem" }}>💰</span>
          </div>
          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: "var(--text-primary)" }}>
            {portfolioKPIs?.portfolio_profit ? `₹${portfolioKPIs.portfolio_profit.toLocaleString()}` : "₹1,42,000"}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--advisory-info-text)", marginTop: "4px" }}>
            +12% vs last cycle
          </div>
        </div>

        {/* KPI 4: Risk Warning Status */}
        <div className="saas-card hover-card" style={{ cursor: "pointer" }} onClick={onNavigateToRisk}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>{t("db_active_alerts")}</span>
            <span style={{ fontSize: "1.2rem" }}>🛡️</span>
          </div>
          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: overdueCount > 0 ? "var(--advisory-critical-text)" : "var(--text-primary)" }}>
            {riskAssessment?.warnings?.length || 0} {t("db_today_alerts")}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "4px" }}>
            {overdueCount > 0 ? `${overdueCount} Alerts` : "Low overall risk"}
          </div>
        </div>
      </div>

      {/* 4. Forecast & Advisory Split View */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "20px" }}>
        <ForecastWidget />
        <AdvisoryWidget />
      </div>

      {/* 5. Recent Activity & Key Metrics Section */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
        
        {/* Recent Activity Card */}
        <div className="saas-card">
          <h3 style={{ fontSize: "1.05rem", fontWeight: "700", marginBottom: "16px" }}>📝 {t("db_recent_activity")}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>{t("db_latest_soil_test")}</span>
              <span className="saas-badge saas-badge-success">{t("status_healthy")}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>{t("db_recent_disease_scan")}</span>
              <span className="saas-badge saas-badge-neutral">Clean</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>{t("db_planner_reminders")}</span>
              <span className="saas-badge saas-badge-warning">2 Pending</span>
            </div>
          </div>
        </div>

        {/* Small Analytics Metric Card */}
        <div className="saas-card">
          <h3 style={{ fontSize: "1.05rem", fontWeight: "700", marginBottom: "16px" }}>📊 {t("db_small_analytics")}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Total Acreage</span>
              <span style={{ fontSize: "0.85rem", fontWeight: "700" }}>{portfolioKPIs?.total_area ? `${portfolioKPIs.total_area.toFixed(1)} Ac` : "120 Ac"}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Crop Health index</span>
              <span style={{ fontSize: "0.85rem", fontWeight: "700" }}>{analyticsKPIs?.health_score ? `${analyticsKPIs.health_score.toFixed(0)}%` : "88%"}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Estimated return</span>
              <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--advisory-info-text)" }}>₹1.42 Lakhs</span>
            </div>
          </div>
        </div>
      </div>

      {/* 6. Minimal Action Cards Grid (Concise 1-Line Description + Clear CTA) */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
        
        <div className="saas-card hover-card" style={{ cursor: "pointer", display: "flex", flexDirection: "column", justifyContent: "space-between" }} onClick={onNavigateToPortfolio}>
          <div>
            <div style={{ fontSize: "1.5rem", marginBottom: "10px" }}>🏡</div>
            <h4 style={{ fontSize: "1.05rem", fontWeight: "700", marginBottom: "4px" }}>{t("nav_portfolio")}</h4>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.4" }}>
              Manage multi-farm holdings, switch active field contexts, and review total acreage.
            </p>
          </div>
          <button className="cta-link" style={{ marginTop: "14px" }}>{t("btn_open")}</button>
        </div>

        <div className="saas-card hover-card" style={{ cursor: "pointer", display: "flex", flexDirection: "column", justifyContent: "space-between" }} onClick={onNavigateToAnalytics}>
          <div>
            <div style={{ fontSize: "1.5rem", marginBottom: "10px" }}>📊</div>
            <h4 style={{ fontSize: "1.05rem", fontWeight: "700", marginBottom: "4px" }}>{t("nav_analytics")}</h4>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.4" }}>
              Monitor yield metrics, profitability trends, and download executive PDF reports.
            </p>
          </div>
          <button className="cta-link" style={{ marginTop: "14px" }}>{t("btn_open")}</button>
        </div>

        <div className="saas-card hover-card" style={{ cursor: "pointer", display: "flex", flexDirection: "column", justifyContent: "space-between" }} onClick={onNavigateToSoil}>
          <div>
            <div style={{ fontSize: "1.5rem", marginBottom: "10px" }}>🧪</div>
            <h4 style={{ fontSize: "1.05rem", fontWeight: "700", marginBottom: "4px" }}>{t("nav_soil_analyzer")}</h4>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.4" }}>
              Input soil NPK and pH parameters to receive AI organic treatment recommendations.
            </p>
          </div>
          <button className="cta-link" style={{ marginTop: "14px" }}>{t("btn_open")}</button>
        </div>

        <div className="saas-card hover-card" style={{ cursor: "pointer", display: "flex", flexDirection: "column", justifyContent: "space-between" }} onClick={onNavigateToMarket}>
          <div>
            <div style={{ fontSize: "1.5rem", marginBottom: "10px" }}>💰</div>
            <h4 style={{ fontSize: "1.05rem", fontWeight: "700", marginBottom: "4px" }}>{t("nav_market_intelligence")}</h4>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.4" }}>
              Track live mandi prices, historical trends, and calculate crop return margins.
            </p>
          </div>
          <button className="cta-link" style={{ marginTop: "14px" }}>{t("btn_open")}</button>
        </div>
      </div>

    </div>
  );
};

export default DashboardOverview;
