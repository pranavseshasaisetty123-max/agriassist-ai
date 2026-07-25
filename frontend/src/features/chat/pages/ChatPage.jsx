import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../../../context/AuthContext";
import { useLanguage } from "../../../context/LanguageContext";
import api from "../../../services/api";
import DashboardOverview from "../../dashboard/pages/DashboardOverview";
import SoilAnalyzerPage from "../../soil/pages/SoilAnalyzerPage";
import DiseaseDetectionPage from "../../disease/pages/DiseaseDetectionPage";
import CropRecommendationsPage from "../../crop-recommendations/pages/CropRecommendationsPage";
import MarketIntelligencePage from "../../market-intelligence/pages/MarketIntelligencePage";
import YieldPredictionPage from "../../yield-prediction/pages/YieldPredictionPage";
import FarmPlannerPage from "../../farm-planner/pages/FarmPlannerPage";
import RiskWarningPage from "../../risk-intelligence/pages/RiskWarningPage";
import ConsultAgentPage from "../../../pages/ConsultAgentPage";
import NotificationCenterPage from "../../../pages/NotificationCenterPage";
import FarmAnalyticsPage from "../../../pages/FarmAnalyticsPage";
import FarmPortfolioPage from "../../../pages/FarmPortfolioPage";
import SettingsPage from "../../../pages/SettingsPage";
import HelpCenterPage from "../../../pages/HelpCenterPage";
import "./Chat.css";

const ChatPage = () => {
  const { currentFarmer, logout, reloadProfile } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, soil, chat, etc.
  const [unreadCount, setUnreadCount] = useState(0);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [farmsList, setFarmsList] = useState([]);
  const [themeMode, setThemeMode] = useState("light");
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Group collapse states
  const [expandedGroups, setExpandedGroups] = useState({
    farm: true,
    aiTools: true,
    insights: true,
    system: true,
  });

  const toggleGroup = (groupKey) => {
    setExpandedGroups((prev) => ({ ...prev, [groupKey]: !prev[groupKey] }));
  };

  const fetchFarmsList = async () => {
    try {
      const response = await api.get("/farms");
      setFarmsList(response.data);
    } catch (error) {
      console.error("Failed to fetch farms list in header:", error);
    }
  };

  useEffect(() => {
    if (currentFarmer) {
      fetchFarmsList();
    }
  }, [currentFarmer?.active_farm_id]);

  useEffect(() => {
    const applySavedTheme = async () => {
      try {
        const response = await api.get("/farmers/settings");
        const theme = response.data.theme_preference || "light";
        setThemeMode(theme);
        document.body.classList.toggle("dark-theme", theme === "dark");
      } catch (err) {
        console.error("Failed to load theme preference:", err);
      }
    };
    if (currentFarmer) {
      applySavedTheme();
    }
  }, [currentFarmer]);

  const toggleTheme = async () => {
    const nextTheme = themeMode === "dark" ? "light" : "dark";
    setThemeMode(nextTheme);
    document.body.classList.toggle("dark-theme", nextTheme === "dark");
    try {
      await api.put("/farmers/settings", { theme_preference: nextTheme });
    } catch (err) {
      console.error("Failed to save theme toggle:", err);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await api.get("/notifications/unread");
      setUnreadCount(response.data.length);
    } catch (error) {
      console.error("Failed to load notifications unread count:", error);
    }
  };

  useEffect(() => {
    fetchUnreadCount();
  }, [activeTab]);
  
  const [isSessionsLoading, setIsSessionsLoading] = useState(true);
  const [isMessagesLoading, setIsMessagesLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (activeTab === "chat") {
      scrollToBottom();
    }
  }, [messages, isSending, activeTab]);

  const fetchSessions = async () => {
    try {
      const response = await api.get("/chat/sessions");
      setSessions(response.data);
      if (response.data.length > 0 && !activeSessionId) {
        setActiveSessionId(response.data[0].id);
      }
    } catch (error) {
      console.error("Failed to load chat sessions:", error);
    } finally {
      setIsSessionsLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (activeSessionId && activeTab === "chat") {
      const fetchMessages = async () => {
        setIsMessagesLoading(true);
        try {
          const response = await api.get(`/chat/sessions/${activeSessionId}/messages`);
          setMessages(response.data);
        } catch (error) {
          console.error("Failed to load messages:", error);
        } finally {
          setIsMessagesLoading(false);
        }
      };
      fetchMessages();
    } else if (!activeSessionId) {
      setMessages([]);
    }
  }, [activeSessionId, activeTab]);

  const handleCreateSession = async () => {
    try {
      const title = prompt("Enter topic name (optional):") || "New Agricultural Query";
      const response = await api.post("/chat/sessions", { title });
      setSessions([response.data, ...sessions]);
      setActiveSessionId(response.data.id);
      setShowProfileSettings(false);
      setActiveTab("chat");
    } catch (error) {
      console.error("Failed to create chat session:", error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !activeSessionId || isSending) return;

    const userPrompt = inputMessage.trim();
    setInputMessage("");
    setIsSending(true);

    try {
      const response = await api.post(`/chat/sessions/${activeSessionId}/messages`, {
        message_text: userPrompt,
      });
      setMessages((prev) => [
        ...prev,
        response.data.user_message,
        response.data.ai_response,
      ]);
      
      setSessions((prevSessions) => {
        const active = prevSessions.find((s) => s.id === activeSessionId);
        const rest = prevSessions.filter((s) => s.id !== activeSessionId);
        if (active) {
          return [active, ...rest];
        }
        return prevSessions;
      });
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsSending(false);
    }
  };

  const navigateTo = (tabName) => {
    setActiveTab(tabName);
    setShowProfileSettings(false);
    setIsMobileOpen(false);
  };

  const getHeaderTitle = () => {
    if (showProfileSettings) return t("nav_settings");
    switch (activeTab) {
      case "dashboard":
        return t("nav_dashboard");
      case "portfolio":
        return t("nav_portfolio");
      case "analytics":
        return t("nav_analytics");
      case "soil":
        return t("nav_soil_analyzer");
      case "disease":
        return t("nav_disease_detection");
      case "crop-recommendations":
        return t("nav_crop_recommendations");
      case "market-intelligence":
        return t("nav_market_intelligence");
      case "yield-prediction":
        return t("nav_yield_prediction");
      case "farm-planner":
        return t("nav_planner");
      case "risk-intelligence":
        return t("nav_crop_intelligence");
      case "consult-agent":
        return t("nav_virtual_agronomist");
      case "notifications":
        return t("nav_notifications");
      case "help-center":
        return t("nav_help");
      case "chat":
        return sessions.find((s) => s.id === activeSessionId)?.title || t("nav_virtual_agronomist");
      default:
        return "AgriAssist AI";
    }
  };

  const getHeaderStatus = () => {
    if (showProfileSettings) return t("nav_settings");
    switch (activeTab) {
      case "dashboard":
        return `${t("db_welcome")}, ${currentFarmer?.first_name || "Farmer"}`;
      case "portfolio":
        return t("nav_portfolio");
      case "analytics":
        return t("nav_analytics");
      case "soil":
        return t("nav_soil_analyzer");
      case "disease":
        return t("nav_disease_detection");
      case "crop-recommendations":
        return t("nav_crop_recommendations");
      case "market-intelligence":
        return t("nav_market_intelligence");
      case "yield-prediction":
        return t("nav_yield_prediction");
      case "farm-planner":
        return t("nav_planner");
      case "risk-intelligence":
        return t("nav_crop_intelligence");
      case "consult-agent":
        return t("nav_virtual_agronomist");
      case "notifications":
        return t("nav_notifications");
      case "help-center":
        return t("nav_help");
      case "chat":
        return t("nav_virtual_agronomist");
      default:
        return "";
    }
  };

  return (
    <div className="chat-layout-container">
      {/* Mobile Overlay */}
      <div
        className={`mobile-overlay ${isMobileOpen ? "mobile-open" : ""}`}
        onClick={() => setIsMobileOpen(false)}
      />

      {/* 1. Grouped Sidebar Panel */}
      <aside className={`chat-sidebar ${isMobileOpen ? "mobile-open" : ""}`}>
        <div className="sidebar-brand">
          <span className="brand-icon">🌱</span>
          <span className="brand-title brand-font">AgriAssist AI</span>
        </div>
        
        {/* Navigation Workspace Scroll */}
        <div className="sidebar-nav-scroll">
          {/* Main Dashboard Navigation Item */}
          <div
            className={`session-item-row ${activeTab === "dashboard" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => navigateTo("dashboard")}
          >
            <span className="session-icon">📊</span>
            <span className="session-title-text">{t("nav_dashboard")}</span>
          </div>

          {/* Group 1: My Farm */}
          <div className="sidebar-group">
            <div className="sidebar-group-header" onClick={() => toggleGroup("farm")}>
              <span>{t("nav_my_farm")}</span>
              <span>{expandedGroups.farm ? "▾" : "▸"}</span>
            </div>
            {expandedGroups.farm && (
              <div className="sidebar-group-items">
                <div
                  className={`session-item-row ${activeTab === "portfolio" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("portfolio")}
                >
                  <span className="session-icon">🏡</span>
                  <span className="session-title-text">{t("nav_portfolio")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "farm-planner" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("farm-planner")}
                >
                  <span className="session-icon">📅</span>
                  <span className="session-title-text">{t("nav_planner")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "analytics" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("analytics")}
                >
                  <span className="session-icon">📈</span>
                  <span className="session-title-text">{t("nav_analytics")}</span>
                </div>
              </div>
            )}
          </div>

          {/* Group 2: Crop Intelligence */}
          <div className="sidebar-group">
            <div className="sidebar-group-header" onClick={() => toggleGroup("aiTools")}>
              <span>{t("nav_crop_intelligence")}</span>
              <span>{expandedGroups.aiTools ? "▾" : "▸"}</span>
            </div>
            {expandedGroups.aiTools && (
              <div className="sidebar-group-items">
                <div
                  className={`session-item-row ${activeTab === "soil" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("soil")}
                >
                  <span className="session-icon">🧪</span>
                  <span className="session-title-text">{t("nav_soil_analyzer")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "disease" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("disease")}
                >
                  <span className="session-icon">🔍</span>
                  <span className="session-title-text">{t("nav_disease_detection")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "crop-recommendations" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("crop-recommendations")}
                >
                  <span className="session-icon">🌾</span>
                  <span className="session-title-text">{t("nav_crop_recommendations")}</span>
                </div>
              </div>
            )}
          </div>

          {/* Group 3: Insights */}
          <div className="sidebar-group">
            <div className="sidebar-group-header" onClick={() => toggleGroup("insights")}>
              <span>{t("nav_insights")}</span>
              <span>{expandedGroups.insights ? "▾" : "▸"}</span>
            </div>
            {expandedGroups.insights && (
              <div className="sidebar-group-items">
                <div
                  className={`session-item-row ${activeTab === "market-intelligence" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("market-intelligence")}
                >
                  <span className="session-icon">💰</span>
                  <span className="session-title-text">{t("nav_market_intelligence")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "yield-prediction" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("yield-prediction")}
                >
                  <span className="session-icon">📊</span>
                  <span className="session-title-text">{t("nav_yield_prediction")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "risk-intelligence" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("risk-intelligence")}
                >
                  <span className="session-icon">🛡️</span>
                  <span className="session-title-text">{t("nav_risk_warnings")}</span>
                </div>
              </div>
            )}
          </div>

          {/* Group 4: AI Assistant */}
          <div className="sidebar-group">
            <div className="sidebar-group-header" onClick={() => toggleGroup("system")}>
              <span>{t("nav_ai_assistant")}</span>
              <span>{expandedGroups.system ? "▾" : "▸"}</span>
            </div>
            {expandedGroups.system && (
              <div className="sidebar-group-items">
                <div
                  className={`session-item-row ${activeTab === "consult-agent" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("consult-agent")}
                >
                  <span className="session-icon">🤖</span>
                  <span className="session-title-text">{t("nav_virtual_agronomist")}</span>
                </div>
                <div
                  className={`session-item-row ${activeTab === "notifications" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("notifications")}
                >
                  <span className="session-icon">🔔</span>
                  <span className="session-title-text">{t("nav_notifications")}</span>
                  {unreadCount > 0 && (
                    <span className="saas-badge saas-badge-critical" style={{ marginLeft: "auto", padding: "1px 6px" }}>
                      {unreadCount}
                    </span>
                  )}
                </div>
                <div
                  className={`session-item-row ${activeTab === "help-center" && !showProfileSettings ? "active-item" : ""}`}
                  onClick={() => navigateTo("help-center")}
                >
                  <span className="session-icon">📖</span>
                  <span className="session-title-text">{t("nav_help")}</span>
                </div>
                <div
                  className={`session-item-row ${showProfileSettings ? "active-item" : ""}`}
                  onClick={() => {
                    setShowProfileSettings(true);
                    setIsMobileOpen(false);
                  }}
                >
                  <span className="session-icon">⚙️</span>
                  <span className="session-title-text">{t("nav_settings")}</span>
                </div>
              </div>
            )}
          </div>

          {/* Context Chat Sessions Sub-List */}
          {activeTab === "chat" && !showProfileSettings && (
            <div style={{ display: "flex", flexDirection: "column", marginTop: "12px" }}>
              <button className="btn btn-primary new-session-btn" onClick={handleCreateSession}>
                ➕ New Session
              </button>

              <div style={{ marginTop: "8px", display: "flex", flexDirection: "column", gap: "2px" }}>
                {isSessionsLoading ? (
                  <div className="sidebar-loader">Loading history...</div>
                ) : sessions.length === 0 ? (
                  <div className="no-sessions-msg">No consulting topics</div>
                ) : (
                  sessions.map((session) => (
                    <div
                      key={session.id}
                      className={`session-item-row ${activeSessionId === session.id ? "active-item" : ""}`}
                      onClick={() => setActiveSessionId(session.id)}
                    >
                      <span className="session-icon">💬</span>
                      <span className="session-title-text">{session.title}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar Footer User Widget */}
        <div className="sidebar-footer">
          <div className="user-profile-widget" onClick={() => setShowProfileSettings(true)}>
            <div className="avatar">👨‍🌾</div>
            <div className="user-info">
              <div className="user-name">{currentFarmer?.first_name} {currentFarmer?.last_name}</div>
              <div className="user-loc">{currentFarmer?.location || "Enterprise Farmer"}</div>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. Main Work Panel */}
      <main className="chat-main-panel">
        <header className="chat-panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <button className="mobile-nav-toggle" onClick={() => setIsMobileOpen(!isMobileOpen)}>
              ☰
            </button>
            <div className="header-title-container">
              <h2 className="header-title brand-font">{getHeaderTitle()}</h2>
              <p className="header-status">{getHeaderStatus()}</p>
            </div>
          </div>

          <div className="header-actions">
            {/* Multilingual Support - Language Selector Dropdown */}
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{
                  backgroundColor: "var(--bg-app)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-light)",
                  borderRadius: "var(--radius-sm)",
                  padding: "6px 12px",
                  fontSize: "0.82rem",
                  fontWeight: "600",
                  cursor: "pointer",
                  outline: "none",
                  boxShadow: "var(--shadow-sm)"
                }}
              >
                <option value="en">English</option>
                <option value="te">తెలుగు</option>
                <option value="hi">हिन्दी</option>
              </select>
            </div>

            {/* Active Farm Switcher Dropdown */}
            {farmsList.length > 0 && (
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <select
                  value={currentFarmer?.active_farm_id || ""}
                  onChange={async (e) => {
                    const selectedId = e.target.value;
                    if (selectedId) {
                      try {
                        await api.post(`/farms/${selectedId}/activate`);
                        await reloadProfile();
                      } catch (err) {
                        console.error("Failed to switch active farm:", err);
                      }
                    }
                  }}
                  style={{
                    backgroundColor: "var(--bg-app)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-light)",
                    borderRadius: "var(--radius-sm)",
                    padding: "6px 12px",
                    fontSize: "0.82rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    outline: "none",
                    boxShadow: "var(--shadow-sm)"
                  }}
                >
                  {farmsList.map((f) => (
                    <option key={f.id} value={f.id}>📍 {f.name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Quick Dark Mode Toggle */}
            <button
              className="btn btn-secondary"
              onClick={toggleTheme}
              style={{ width: "36px", height: "36px", padding: 0 }}
              title={`Switch to theme Mode`}
            >
              {themeMode === "dark" ? "☀️" : "🌙"}
            </button>

            {/* Logout Action */}
            <button className="btn btn-secondary logout-btn" onClick={logout} style={{ height: "36px" }}>
              {t("nav_logout")}
            </button>
          </div>
        </header>

        {/* Content Render View */}
        {showProfileSettings ? (
          <SettingsPage />
        ) : activeTab === "dashboard" ? (
          <DashboardOverview
            key={currentFarmer?.active_farm_id}
            onNavigateToChat={() => navigateTo("consult-agent")}
            onNavigateToSoil={() => navigateTo("soil")}
            onNavigateToMarket={() => navigateTo("market-intelligence")}
            onNavigateToYield={() => navigateTo("yield-prediction")}
            onNavigateToPlanner={() => navigateTo("farm-planner")}
            onNavigateToRisk={() => navigateTo("risk-intelligence")}
            onNavigateToConsultant={() => navigateTo("consult-agent")}
            onNavigateToNotifications={() => navigateTo("notifications")}
            onNavigateToAnalytics={() => navigateTo("analytics")}
            onNavigateToPortfolio={() => navigateTo("portfolio")}
          />
        ) : activeTab === "portfolio" ? (
          <FarmPortfolioPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "analytics" ? (
          <FarmAnalyticsPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "soil" ? (
          <SoilAnalyzerPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "disease" ? (
          <DiseaseDetectionPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "crop-recommendations" ? (
          <CropRecommendationsPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "market-intelligence" ? (
          <MarketIntelligencePage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "yield-prediction" ? (
          <YieldPredictionPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "farm-planner" ? (
          <FarmPlannerPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "risk-intelligence" ? (
          <RiskWarningPage key={currentFarmer?.active_farm_id} onNavigateToPlanner={() => navigateTo("farm-planner")} />
        ) : activeTab === "consult-agent" ? (
          <ConsultAgentPage key={currentFarmer?.active_farm_id} onNavigateToPlanner={() => navigateTo("farm-planner")} />
        ) : activeTab === "notifications" ? (
          <NotificationCenterPage key={currentFarmer?.active_farm_id} onUpdateUnread={setUnreadCount} />
        ) : activeTab === "help-center" ? (
          <HelpCenterPage />
        ) : (
          /* Chat Window Screen */
          <div className="chat-window-wrapper">
            <div className="chat-messages-container">
              {isMessagesLoading ? (
                <div className="chat-loader">
                  <span className="pulse-ring"></span> Loading conversation...
                </div>
              ) : messages.length === 0 ? (
                <div className="chat-welcome-hero animate-fade-in">
                  <div className="hero-badge">🌱 Virtual Agronomist</div>
                  <h1 className="hero-title">Namaste, {currentFarmer?.first_name}!</h1>
                  <p className="hero-subtitle">
                    Ask any agronomic questions regarding NPK ratios, crop disease remediation, weather protection, or market pricing.
                  </p>
                  <div className="quick-suggestions-grid">
                    <div className="suggestion-card saas-card hover-card" onClick={() => setInputMessage("What is the optimal NPK ratio for wheat?")}>
                      <span className="card-icon">🌾</span>
                      <h4>Wheat NPK Balance</h4>
                      <p>Analyze fertilizer application rates</p>
                    </div>
                    <div className="suggestion-card saas-card hover-card" onClick={() => setInputMessage("How do I control fungal leaf spot on cotton?")}>
                      <span className="card-icon">🍃</span>
                      <h4>Foliage Infection</h4>
                      <p>Organic treatment protocols</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="messages-list">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`message-bubble-row ${msg.sender === "FARMER" ? "row-farmer" : "row-ai"}`}
                    >
                      <div className="message-avatar">{msg.sender === "FARMER" ? "👨‍🌾" : "🤖"}</div>
                      <div className="message-bubble">
                        <div className="bubble-text">{msg.message_text}</div>
                        <div className="bubble-time">
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  ))}
                  {isSending && (
                    <div className="message-bubble-row row-ai animate-fade-in">
                      <div className="message-avatar">🤖</div>
                      <div className="message-bubble bubble-loading">
                        <div className="bouncing-dots">
                          <span className="dot"></span>
                          <span className="dot"></span>
                          <span className="dot"></span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {activeSessionId && (
              <form onSubmit={handleSendMessage} className="chat-input-bar">
                <input
                  type="text"
                  className="chat-text-input"
                  placeholder="Ask a question (e.g. 'How to optimize soil Nitrogen levels?')..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  disabled={isSending}
                />
                <button type="submit" className="btn btn-primary" disabled={isSending || !inputMessage.trim()}>
                  {isSending ? "..." : "Send →"}
                </button>
              </form>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default ChatPage;
