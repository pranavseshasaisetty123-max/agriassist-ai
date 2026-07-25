import React, { useState, useEffect } from "react";
import api from "../services/api";
import EmptyState from "../components/EmptyState";
import { TextSkeleton } from "../components/Skeleton";
import { useLanguage } from "../context/LanguageContext";

const HelpCenterPage = () => {
  const { t } = useLanguage();
  const [helpData, setHelpData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [error, setError] = useState(false);

  const fetchHelpData = async () => {
    try {
      setError(false);
      const resp = await api.get("/system/help");
      setHelpData(resp.data);
    } catch (err) {
      console.error("Failed to load help center documentation:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHelpData();
  }, []);

  const toggleFaq = (index) => {
    if (expandedFaq === index) {
      setExpandedFaq(null);
    } else {
      setExpandedFaq(index);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "32px", display: "flex", flexDirection: "column", gap: "20px" }}>
        <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.5rem" }}>📖 {t("help_title")}</h2>
        <TextSkeleton />
        <TextSkeleton />
      </div>
    );
  }

  if (error || !helpData) {
    return (
      <div style={{ padding: "32px" }}>
        <EmptyState
          icon="📖"
          title={t("msg_no_data")}
          description={t("msg_no_data")}
          actionLabel={t("dis_recovery_steps") || "Retry"}
          onAction={fetchHelpData}
        />
      </div>
    );
  }

  // Filter FAQs and Guides by search query
  const filteredFaqs = helpData.faqs.filter(
    (faq) =>
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredGuides = Object.entries(helpData.guides).filter(
    ([key, value]) =>
      key.toLowerCase().replace("_", " ").includes(searchQuery.toLowerCase()) ||
      value.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="animate-fade-in" style={{ padding: "32px", overflowY: "auto", height: "100%", display: "flex", flexDirection: "column", gap: "28px" }}>
       {/* Header */}
      <div>
        <h1 style={{ fontSize: "1.8rem", color: "var(--text-primary)", fontWeight: "800", margin: 0 }}>📖 {t("help_title")}</h1>
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "4px" }}>
          {t("help_subtitle")}
        </p>
      </div>

      {/* Search Input */}
      <div className="glass" style={{ padding: "16px", borderRadius: "var(--radius-md)" }}>
        <input
          type="text"
          className="form-input"
          placeholder={`🔍 ${t("help_search")}`}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "28px" }}>
        {/* Main Content Area: Guides & FAQs */}
        <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
          
          {/* Diagnostic Guides */}
          <div>
            <h2 style={{ fontSize: "1.25rem", color: "var(--text-primary)", marginBottom: "16px", fontWeight: "700" }}>📖 {t("help_guides_title")}</h2>
            
            {filteredGuides.length === 0 ? (
              <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>{t("help_no_guides")}</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {filteredGuides.map(([key, content]) => (
                  <div key={key} className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)" }}>
                    <h3 style={{
                      fontSize: "1.05rem",
                      color: "var(--primary)",
                      fontWeight: "700",
                      textTransform: "capitalize",
                      marginBottom: "8px",
                      fontFamily: "'Outfit', sans-serif"
                    }}>
                      {key.replace("_", " ")} {t("help_guide_suffix")}
                    </h3>
                    <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: "1.5", margin: 0 }}>
                      {content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Frequently Asked Questions */}
          <div>
            <h2 style={{ fontSize: "1.25rem", color: "var(--text-primary)", marginBottom: "16px", fontWeight: "700" }}>❓ {t("help_faqs_title")}</h2>
            
            {filteredFaqs.length === 0 ? (
              <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>{t("help_no_faqs")}</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {filteredFaqs.map((faq, idx) => {
                  const isExpanded = expandedFaq === idx;
                  return (
                    <div
                      key={idx}
                      className="glass"
                      style={{
                        padding: "16px 20px",
                        borderRadius: "var(--radius-sm)",
                        cursor: "pointer",
                        transition: "var(--transition-smooth)"
                      }}
                      onClick={() => toggleFaq(idx)}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <h4 style={{ fontSize: "0.95rem", color: "var(--text-primary)", margin: 0, fontWeight: "600" }}>
                          {faq.question}
                        </h4>
                        <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                          {isExpanded ? "▲" : "▼"}
                        </span>
                      </div>
                      
                      {isExpanded && (
                        <p style={{
                          fontSize: "0.875rem",
                          color: "var(--text-secondary)",
                          lineHeight: "1.5",
                          marginTop: "12px",
                          marginBottom: 0,
                          borderTop: "1px solid var(--border-light)",
                          paddingTop: "12px"
                        }}>
                          {faq.answer}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>

        {/* Sidebar: Troubleshooting & Diagnostics */}
        <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
          
          {/* Troubleshooting Card */}
          <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
            <h3 style={{ fontSize: "1.1rem", color: "var(--text-primary)", marginBottom: "16px", fontWeight: "700", fontFamily: "'Outfit', sans-serif" }}>
              🛠️ {t("help_troubleshoot")}
            </h3>
            <ul style={{
              fontSize: "0.85rem",
              color: "var(--text-secondary)",
              lineHeight: "1.6",
              paddingLeft: "20px",
              margin: 0,
              display: "flex",
              flexDirection: "column",
              gap: "12px"
            }}>
              {helpData.troubleshooting.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Quick Contact Card */}
          <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", backgroundColor: "rgba(56, 161, 105, 0.03)", border: "1px solid rgba(56, 161, 105, 0.15)" }}>
            <h3 style={{ fontSize: "1.1rem", color: "var(--primary)", marginBottom: "8px", fontWeight: "700", fontFamily: "'Outfit', sans-serif" }}>
              ✉ {t("help_support_title")}
            </h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: "1.4", marginBottom: "16px" }}>
              {t("help_support_desc")}
            </p>
            <a
              href="mailto:support@agriassist.ai"
              className="btn btn-primary"
              style={{
                width: "100%",
                padding: "8px 12px",
                fontSize: "0.8rem",
                textDecoration: "none",
                display: "inline-flex",
                justifyContent: "center"
              }}
            >
              {t("help_support_btn")}
            </a>
          </div>

        </div>
      </div>
    </div>
  );
};

export default HelpCenterPage;
