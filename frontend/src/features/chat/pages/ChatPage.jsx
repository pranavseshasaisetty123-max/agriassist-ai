import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../../../context/AuthContext";
import api from "../../../services/api";
import "./Chat.css";

const ChatPage = () => {
  const { currentFarmer, logout } = useAuth();
  
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  
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
    scrollToBottom();
  }, [messages, isSending]);

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
    if (activeSessionId) {
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
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  // Handle creating a new chat session
  const handleCreateSession = async () => {
    try {
      const title = prompt("Enter topic name (optional):") || "New Agricultural Query";
      const response = await api.post("/chat/sessions", { title });
      setSessions([response.data, ...sessions]);
      setActiveSessionId(response.data.id);
      setShowProfileSettings(false);
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

  return (
    <div className="chat-layout-container">
      {/* 1. Sidebar Panel */}
      <aside className="chat-sidebar glass">
        <div className="sidebar-brand">
          <span className="brand-icon">🌱</span>
          <span className="brand-title brand-font">AgriAssist AI</span>
        </div>
        
        <button className="btn btn-primary new-session-btn" onClick={handleCreateSession}>
          ➕ New Consult
        </button>

        <div className="sidebar-sessions-list">
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
                className={`session-item-row ${activeSessionId === session.id && !showProfileSettings ? "active-item" : ""}`}
                onClick={() => {
                  setActiveSessionId(session.id);
                  setShowProfileSettings(false);
                }}
              >
                <span className="session-icon">💬</span>
                <span className="session-title-text">{session.title}</span>
              </div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
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
            <h2 className="header-title brand-font">
              {showProfileSettings ? "Farmer Settings" : sessions.find((s) => s.id === activeSessionId)?.title || "AgriAssist Agent"}
            </h2>
            <p className="header-status">
              {showProfileSettings ? "Manage personal parameters" : "AI Agronomist Active"}
            </p>
          </div>
          <div className="header-actions">
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
        ) : (
          /* Chat Window Screen */
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
