import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../../../context/AuthContext";
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
import "./Chat.css";

const ChatPage = () => {
  const { currentFarmer, logout, reloadProfile } = useAuth();
  
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, soil, chat
  const [unreadCount, setUnreadCount] = useState(0);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [farmsList, setFarmsList] = useState([]);

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
  
  // Profile update form values
  const [profileForm, setProfileForm] = useState({
    first_name: currentFarmer?.first_name || "",
    last_name: currentFarmer?.last_name || "",
    location: currentFarmer?.location || "",
    contact_number: currentFarmer?.contact_number || "",
  });
  const [profileAlert, setProfileAlert] = useState({ type: "", text: "" });
  const { updateProfile } = useAuth();

  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (activeTab === "chat") {
      scrollToBottom();
    }
  }, [messages, isSending, activeTab]);

  // Load chat sessions on component mount
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

  // Fetch messages when active session changes
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

  // Handle creating a new chat session
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

  // Handle sending a message
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
      // Append user prompt and AI response to messages list
      setMessages((prev) => [
        ...prev,
        response.data.user_message,
        response.data.ai_response,
      ]);
      
      // Update session's placement in list to be first
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

  // Handle updating profile parameters
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setProfileAlert({ type: "", text: "" });
    try {
      await updateProfile(profileForm);
      setProfileAlert({ type: "success", text: "Profile settings saved successfully!" });
    } catch (err) {
      setProfileAlert({ type: "error", text: err });
    }
  };

  const getHeaderTitle = () => {
    if (showProfileSettings) return "Farmer Settings";
    switch (activeTab) {
      case "dashboard":
        return "AgriAssist Dashboard";
      case "portfolio":
        return "Farm Portfolio & Holdings";
      case "analytics":
        return "Farm Analytics Dashboard";
      case "soil":
        return "Soil Diagnostics Center";
      case "disease":
        return "Plant Disease Diagnostics";
      case "crop-recommendations":
        return "Smart Crop Recommendations";
      case "market-intelligence":
        return "Market Price Intelligence";
      case "yield-prediction":
        return "Crop Yield Prediction";
      case "farm-planner":
        return "Farm Planner & Scheduler";
      case "risk-intelligence":
        return "Risk Early Warning System";
      case "consult-agent":
        return "Virtual Agronomist Consultant";
      case "notifications":
        return "Smart Alert Center";
      case "chat":
        return sessions.find((s) => s.id === activeSessionId)?.title || "AI Consult Agent";
      default:
        return "AgriAssist Agent";
    }
  };

  const getHeaderStatus = () => {
    if (showProfileSettings) return "Manage personal parameters";
    switch (activeTab) {
      case "dashboard":
        return `Welcome back, ${currentFarmer?.first_name || "Farmer"}`;
      case "portfolio":
        return "View and switch between your farms, view aggregated holdings";
      case "analytics":
        return "Real-time metrics, profit projections, and PDF report downloads";
      case "soil":
        return "Log and analyze soil parameters";
      case "disease":
        return "Upload leaves to analyze issues";
      case "crop-recommendations":
        return "AI-powered crop matches";
      case "market-intelligence":
        return "Live price tracking & profitability analyzer";
      case "yield-prediction":
        return "Estimate expected crop returns per acre";
      case "farm-planner":
        return "AI crop activities timeline & operational calendar";
      case "risk-intelligence":
        return "Proactive AI pest, disease, and weather risk warnings";
      case "consult-agent":
        return "AI-powered unified farm advisor and recommendations coach";
      case "notifications":
        return "Aggregate warnings, weather, yield, and planning task alerts";
      case "chat":
        return "AI Agronomist Active";
      default:
        return "";
    }
  };

  return (
    <div className="chat-layout-container">
      {/* 1. Sidebar Panel */}
      <aside className="chat-sidebar glass">
        <div className="sidebar-brand">
          <span className="brand-icon">🌱</span>
          <span className="brand-title brand-font">AgriAssist AI</span>
        </div>
        
        {/* Navigation Workspace Tabs */}
        <div className="sidebar-tabs-nav" style={{ padding: "16px 12px 8px", display: "flex", flexDirection: "column", gap: "4px" }}>
          <div
            className={`session-item-row ${activeTab === "dashboard" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("dashboard");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🌾</span>
            <span className="session-title-text">Dashboard</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "analytics" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("analytics");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">📊</span>
            <span className="session-title-text">Analytics</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "portfolio" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("portfolio");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🏡</span>
            <span className="session-title-text">Farm Portfolio</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "soil" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("soil");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🧪</span>
            <span className="session-title-text">Soil Analyzer</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "disease" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("disease");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🔍</span>
            <span className="session-title-text">Disease Detection</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "crop-recommendations" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("crop-recommendations");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🌾</span>
            <span className="session-title-text">Crop Recommendations</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "market-intelligence" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("market-intelligence");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">📈</span>
            <span className="session-title-text">Market Intelligence</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "yield-prediction" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("yield-prediction");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">📊</span>
            <span className="session-title-text">Yield Prediction</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "farm-planner" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("farm-planner");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">📅</span>
            <span className="session-title-text">Farm Planner</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "risk-intelligence" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("risk-intelligence");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🛡️</span>
            <span className="session-title-text">Risk Warnings</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "consult-agent" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("consult-agent");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🤖</span>
            <span className="session-title-text">Virtual Agronomist</span>
          </div>
          <div
            className={`session-item-row ${activeTab === "notifications" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("notifications");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">🔔</span>
            <span className="session-title-text">Alert Center</span>
            {unreadCount > 0 && (
              <span
                style={{
                  backgroundColor: "#e53e3e",
                  color: "white",
                  borderRadius: "10px",
                  padding: "2px 8px",
                  fontSize: "0.7rem",
                  fontWeight: "bold",
                  marginLeft: "auto"
                }}
              >
                {unreadCount}
              </span>
            )}
          </div>
          <div
            className={`session-item-row ${activeTab === "chat" && !showProfileSettings ? "active-item" : ""}`}
            onClick={() => {
              setActiveTab("chat");
              setShowProfileSettings(false);
            }}
          >
            <span className="session-icon">💬</span>
            <span className="session-title-text">Consult Agent</span>
          </div>
        </div>

        {/* Context-aware Chat Section */}
        {activeTab === "chat" && !showProfileSettings && (
          <div style={{ display: "flex", flexDirection: "column", flex: 1, overflow: "hidden" }}>
            <div style={{ height: "1px", backgroundColor: "var(--border-light)", margin: "8px 20px" }}></div>
            <button className="btn btn-primary new-session-btn" onClick={handleCreateSession} style={{ marginTop: "8px" }}>
              ➕ New Consult
            </button>

            <div className="sidebar-sessions-list" style={{ marginTop: "4px" }}>
              {isSessionsLoading ? (
                <div className="sidebar-loader">
                  <span className="dot-spinner"></span> Loading history...
                </div>
              ) : sessions.length === 0 ? (
                <div className="no-sessions-msg">No consulting topics started yet.</div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`session-item-row ${activeSessionId === session.id ? "active-item" : ""}`}
                    onClick={() => {
                      setActiveSessionId(session.id);
                    }}
                  >
                    <span className="session-icon">💬</span>
                    <span className="session-title-text">{session.title}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        <div className="sidebar-footer" style={{ marginTop: "auto" }}>
          <div className="user-profile-widget" onClick={() => setShowProfileSettings(true)}>
            <div className="avatar">🚜</div>
            <div className="user-info">
              <div className="user-name">{currentFarmer?.first_name} {currentFarmer?.last_name}</div>
              <div className="user-loc">{currentFarmer?.location || "India"}</div>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. Main Work Panel */}
      <main className="chat-main-panel">
        <header className="chat-panel-header glass">
          <div className="header-info">
            <h2 className="header-title brand-font">{getHeaderTitle()}</h2>
            <p className="header-status">{getHeaderStatus()}</p>
          </div>
          <div className="header-actions">
            {farmsList.length > 0 ? (
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginRight: "16px" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "var(--text-secondary)", whiteSpace: "nowrap" }}>Active Farm:</span>
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
                    backgroundColor: "var(--bg-card)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-light)",
                    borderRadius: "var(--radius-sm)",
                    padding: "6px 12px",
                    fontSize: "0.85rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    outline: "none",
                    boxShadow: "var(--shadow-sm)",
                    fontFamily: "'Outfit', sans-serif"
                  }}
                >
                  {farmsList.map((f) => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              </div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginRight: "16px" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: "600", color: "var(--text-muted)", whiteSpace: "nowrap" }}>No Active Farm</span>
              </div>
            )}
            <button
              className={`btn btn-secondary ${activeTab === "notifications" ? "btn-active" : ""}`}
              onClick={() => {
                setActiveTab("notifications");
                setShowProfileSettings(false);
              }}
              style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", width: "42px", height: "42px", padding: 0 }}
              title="Alert Center"
            >
              🔔
              {unreadCount > 0 && (
                <span
                  style={{
                    position: "absolute",
                    top: "-4px",
                    right: "-4px",
                    backgroundColor: "#e53e3e",
                    color: "white",
                    borderRadius: "50%",
                    minWidth: "18px",
                    height: "18px",
                    fontSize: "0.65rem",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    padding: "0 4px"
                  }}
                >
                  {unreadCount}
                </span>
              )}
            </button>
            <button
              className={`btn btn-secondary ${showProfileSettings ? "btn-active" : ""}`}
              onClick={() => setShowProfileSettings(!showProfileSettings)}
            >
              ⚙️ Settings
            </button>
            <button className="btn btn-secondary logout-btn" onClick={logout}>
              🚪 Logout
            </button>
          </div>
        </header>

        {showProfileSettings ? (
          /* Profile Settings Screen */
          <div className="profile-view-wrapper animate-fade-in">
            <div className="profile-form-card glass">
              <h3 className="form-card-title">User Information</h3>
              <p className="form-card-subtitle">Keep details up to date for relevant local guidance.</p>
              
              {profileAlert.text && (
                <div className={`profile-alert profile-alert-${profileAlert.type} animate-fade-in`}>
                  {profileAlert.text}
                </div>
              )}

              <form onSubmit={handleProfileUpdate} className="profile-form">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label" htmlFor="first_name">First Name</label>
                    <input
                      type="text"
                      id="first_name"
                      className="form-input"
                      value={profileForm.first_name}
                      onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="last_name">Last Name</label>
                    <input
                      type="text"
                      id="last_name"
                      className="form-input"
                      value={profileForm.last_name}
                      onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Email Address (Cannot change)</label>
                  <input type="text" className="form-input" value={currentFarmer?.email || ""} disabled style={{ backgroundColor: "#f4f6f5", color: "var(--text-muted)" }} />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label" htmlFor="location">Location (State/District)</label>
                    <input
                      type="text"
                      id="location"
                      className="form-input"
                      value={profileForm.location}
                      onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="contact_number">Contact Number</label>
                    <input
                      type="text"
                      id="contact_number"
                      className="form-input"
                      value={profileForm.contact_number}
                      onChange={(e) => setProfileForm({ ...profileForm, contact_number: e.target.value })}
                    />
                  </div>
                </div>

                <button type="submit" className="btn btn-primary">Save Profile</button>
              </form>
            </div>
          </div>
        ) : activeTab === "dashboard" ? (
          /* Dashboard Home Overview Tab */
          <DashboardOverview
            key={currentFarmer?.active_farm_id}
            onNavigateToChat={() => setActiveTab("chat")}
            onNavigateToSoil={() => setActiveTab("soil")}
            onNavigateToMarket={() => setActiveTab("market-intelligence")}
            onNavigateToYield={() => setActiveTab("yield-prediction")}
            onNavigateToPlanner={() => setActiveTab("farm-planner")}
            onNavigateToRisk={() => setActiveTab("risk-intelligence")}
            onNavigateToConsultant={() => setActiveTab("consult-agent")}
            onNavigateToNotifications={() => setActiveTab("notifications")}
            onNavigateToAnalytics={() => setActiveTab("analytics")}
            onNavigateToPortfolio={() => setActiveTab("portfolio")}
          />
        ) : activeTab === "portfolio" ? (
          /* Farm Portfolio Page Tab */
          <FarmPortfolioPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "analytics" ? (
          /* Farm Analytics Page Tab */
          <FarmAnalyticsPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "soil" ? (
          /* Soil Health Analysis Tab */
          <SoilAnalyzerPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "disease" ? (
          /* Disease Detection Page Tab */
          <DiseaseDetectionPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "crop-recommendations" ? (
          /* Smart Crop Recommendations Tab */
          <CropRecommendationsPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "market-intelligence" ? (
          /* Market Intelligence Dashboard Tab */
          <MarketIntelligencePage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "yield-prediction" ? (
          /* Crop Yield Prediction Dashboard Tab */
          <YieldPredictionPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "farm-planner" ? (
          /* Farm Planner Dashboard Tab */
          <FarmPlannerPage key={currentFarmer?.active_farm_id} />
        ) : activeTab === "risk-intelligence" ? (
          /* Risk Warning Dashboard Tab */
          <RiskWarningPage key={currentFarmer?.active_farm_id} onNavigateToPlanner={() => setActiveTab("farm-planner")} />
        ) : activeTab === "consult-agent" ? (
          /* Virtual Agronomist Tab */
          <ConsultAgentPage key={currentFarmer?.active_farm_id} onNavigateToPlanner={() => setActiveTab("farm-planner")} />
        ) : activeTab === "notifications" ? (
          /* Notification Center Page Tab */
          <NotificationCenterPage key={currentFarmer?.active_farm_id} onUpdateUnread={setUnreadCount} />
        ) : (
          /* Consult Agent Chat Window Screen Tab */
          <div className="chat-window-wrapper">
            <div className="chat-messages-container">
              {isMessagesLoading ? (
                <div className="chat-loader">
                  <span className="pulse-ring"></span> Initializing conversation logs...
                </div>
              ) : messages.length === 0 ? (
                <div className="chat-welcome-hero animate-fade-in">
                  <div className="hero-badge">🌱 Virtual Agronomist</div>
                  <h1 className="hero-title">Namaste, {currentFarmer?.first_name}!</h1>
                  <p className="hero-subtitle">
                    How can I assist you with your farming today? Ask me about crop yields, soil testing, weed management, or fertilizer suggestions.
                  </p>
                  <div className="quick-suggestions-grid">
                    <div className="suggestion-card glass" onClick={() => setInputMessage("What is the best NPK ratio for tomatoes?")}>
                      <span className="card-icon">🍅</span>
                      <h4>Tomatoes</h4>
                      <p>Ask about fertilizer suggestions</p>
                    </div>
                    <div className="suggestion-card glass" onClick={() => setInputMessage("How do I control black spot disease on cotton leaves?")}>
                      <span className="card-icon">🌿</span>
                      <h4>Cotton Pest</h4>
                      <p>Ask about handling leaf diseases</p>
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
                      <div className="message-bubble glass">
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
                      <div className="message-bubble glass bubble-loading">
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

            {/* Message Input Controls */}
            {activeSessionId && (
              <form onSubmit={handleSendMessage} className="chat-input-bar glass">
                <input
                  type="text"
                  className="chat-text-input"
                  placeholder="Ask a question (e.g. 'How often should I water wheat crops?')..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  disabled={isSending}
                />
                <button type="submit" className="btn btn-primary send-button" disabled={isSending || !inputMessage.trim()}>
                  {isSending ? "..." : "Send ➔"}
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
