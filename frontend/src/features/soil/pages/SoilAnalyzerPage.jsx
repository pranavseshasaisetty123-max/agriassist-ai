import React, { useEffect, useState } from "react";
import api from "../../../services/api";
import SoilReportForm from "../components/SoilReportForm";

const SoilAnalyzerPage = () => {
  const [reports, setReports] = useState([]);
  const [selectedReportId, setSelectedReportId] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [isReportsLoading, setIsReportsLoading] = useState(true);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);

  // Fetch all reports
  const fetchReports = async () => {
    setIsReportsLoading(true);
    try {
      const response = await api.get("/soil/reports?limit=100");
      setReports(response.data);
      if (response.data.length > 0 && !selectedReportId) {
        setSelectedReportId(response.data[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch reports:", error);
    } finally {
      setIsReportsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // Fetch details when selected report ID changes
  useEffect(() => {
    if (selectedReportId) {
      const fetchReportDetails = async () => {
        setIsDetailsLoading(true);
        try {
          const response = await api.get(`/soil/reports/${selectedReportId}`);
          setSelectedReport(response.data);
        } catch (error) {
          console.error("Failed to load report details:", error);
        } finally {
          setIsDetailsLoading(false);
        }
      };
      fetchReportDetails();
    } else {
      setSelectedReport(null);
    }
  }, [selectedReportId]);

  const handleReportCreated = (newReport) => {
    setReports([newReport, ...reports]);
    setSelectedReportId(newReport.id);
  };

  const handleDeleteReport = async () => {
    if (!selectedReport || !window.confirm("Are you sure you want to delete this soil report entry?")) return;
    try {
      await api.delete(`/soil/reports/${selectedReport.id}`);
      const remainingReports = reports.filter((r) => r.id !== selectedReport.id);
      setReports(remainingReports);
      setSelectedReportId(remainingReports.length > 0 ? remainingReports[0].id : null);
    } catch (error) {
      console.error("Failed to delete report:", error);
      alert("Failed to delete report entry.");
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedReport || isAnalyzing) return;
    setIsAnalyzing(true);
    try {
      const response = await api.post(`/soil/reports/${selectedReport.id}/analyze`);
      // Update selected report details in-place
      setSelectedReport({
        ...selectedReport,
        recommendation: response.data
      });
      // Also update in list
      setReports(reports.map((r) => r.id === selectedReport.id ? { ...r, recommendation: response.data } : r));
    } catch (error) {
      console.error("Failed to run AI analysis:", error);
      alert(error.response?.data?.detail || "Gemini service failed to analyze metrics. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getDialColor = (val) => {
    if (val < 30) return "#e53e3e"; // Red
    if (val < 80) return "#d69e2e"; // Yellow
    return "#38a169"; // Green
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", height: "100%", width: "100%", overflow: "hidden" }}>
      {/* Left sidebar: Reports list */}
      <div style={{
        width: "320px",
        borderRight: "1px solid var(--border-light)",
        display: "flex",
        flexDirection: "column",
        height: "100%",
        backgroundColor: "var(--bg-card)",
        flexShrink: 0
      }}>
        <div style={{ padding: "20px", borderBottom: "1px solid var(--border-light)" }}>
          <button className="btn btn-primary" onClick={() => setIsFormOpen(true)} style={{ width: "100%" }}>
            ➕ Log Soil Test
          </button>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "12px" }}>
          {isReportsLoading ? (
            <div style={{ textAlign: "center", padding: "24px", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Loading test records...
            </div>
          ) : reports.length === 0 ? (
            <div style={{ textAlign: "center", padding: "24px", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              No logged soil tests yet.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {reports.map((report) => (
                <div
                  key={report.id}
                  onClick={() => setSelectedReportId(report.id)}
                  style={{
                    padding: "16px",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    border: "1px solid",
                    borderColor: selectedReportId === report.id ? "var(--primary)" : "var(--border-light)",
                    backgroundColor: selectedReportId === report.id ? "var(--primary-soft)" : "transparent",
                    transition: "var(--transition-smooth)"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                    <span style={{ fontWeight: "600", fontSize: "0.95rem", color: "var(--text-primary)" }}>
                      {report.crop_planned}
                    </span>
                    <span style={{
                      fontSize: "0.75rem",
                      fontWeight: "600",
                      padding: "2px 8px",
                      borderRadius: "var(--radius-full)",
                      backgroundColor: report.recommendation ? "hsl(142, 40%, 90%)" : "#fffdf5",
                      color: report.recommendation ? "var(--primary)" : "var(--accent)"
                    }}>
                      {report.recommendation ? "Analyzed" : "Pending AI"}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    Tested on {new Date(report.tested_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right side: Report Details */}
      <div style={{ flex: 1, height: "100%", overflowY: "auto", padding: "32px", backgroundColor: "var(--bg-app)" }}>
        {isDetailsLoading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-secondary)" }}>
            <span className="pulse-ring"></span> Fetching details...
          </div>
        ) : !selectedReport ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-secondary)", textAlign: "center" }}>
            <span style={{ fontSize: "3rem", marginBottom: "16px" }}>🧪</span>
            <h3>No Report Selected</h3>
            <p style={{ maxWidth: "300px", fontSize: "0.875rem", marginTop: "4px" }}>
              Select a logged test report on the left or create a new test log.
            </p>
          </div>
        ) : (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "800px", margin: "0 auto" }}>
            <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "20px", borderBottom: "1px solid var(--border-light)", paddingBottom: "16px" }}>
                <div>
                  <h2 style={{ fontSize: "1.4rem", color: "var(--text-primary)" }}>Soil Report for {selectedReport.crop_planned}</h2>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Tested on {new Date(selectedReport.tested_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <button className="btn btn-secondary logout-btn" onClick={handleDeleteReport} style={{ padding: "8px 16px", fontSize: "0.85rem" }}>
                    🗑️ Delete
                  </button>
                </div>
              </div>

              {/* Metrics Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "16px" }}>
                <div style={{ padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>pH Level</span>
                  <div style={{ fontSize: "1.6rem", fontWeight: "800", marginTop: "4px" }}>{selectedReport.ph}</div>
                </div>

                <div style={{ padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Nitrogen (N)</span>
                  <div style={{ fontSize: "1.6rem", fontWeight: "800", marginTop: "4px", color: getDialColor(selectedReport.nitrogen) }}>
                    {selectedReport.nitrogen} <span style={{ fontSize: "0.7rem", fontWeight: "500" }}>mg/kg</span>
                  </div>
                </div>

                <div style={{ padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Phosphorus (P)</span>
                  <div style={{ fontSize: "1.6rem", fontWeight: "800", marginTop: "4px", color: getDialColor(selectedReport.phosphorus) }}>
                    {selectedReport.phosphorus} <span style={{ fontSize: "0.7rem", fontWeight: "500" }}>mg/kg</span>
                  </div>
                </div>

                <div style={{ padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Potassium (K)</span>
                  <div style={{ fontSize: "1.6rem", fontWeight: "800", marginTop: "4px", color: getDialColor(selectedReport.potassium) }}>
                    {selectedReport.potassium} <span style={{ fontSize: "0.7rem", fontWeight: "500" }}>mg/kg</span>
                  </div>
                </div>

                <div style={{ padding: "16px", backgroundColor: "var(--bg-app)", borderRadius: "var(--radius-sm)", textAlign: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", fontWeight: "700" }}>Organic Matter</span>
                  <div style={{ fontSize: "1.6rem", fontWeight: "800", marginTop: "4px" }}>
                    {selectedReport.organic_matter !== null ? `${selectedReport.organic_matter}%` : "N/A"}
                  </div>
                </div>
              </div>
            </div>

            {/* AI Recommendation Panel */}
            {selectedReport.recommendation ? (
              <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "20px" }}>
                <h3 style={{ color: "var(--primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>🌿 AI Agronomist Analysis</h3>
                
                <div>
                  <h4 style={{ fontSize: "0.95rem", color: "var(--text-primary)", marginBottom: "4px", fontWeight: "700" }}>Diagnostics Summary</h4>
                  <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                    {selectedReport.recommendation.ai_raw_analysis}
                  </p>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
                  <div style={{ padding: "16px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)" }}>
                    <h5 style={{ color: getDialColor(selectedReport.nitrogen), fontSize: "0.9rem", fontWeight: "700" }}>Nitrogen Advice</h5>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "6px", lineHeight: "1.4" }}>
                      {selectedReport.recommendation.nitrogen_recommendation}
                    </p>
                  </div>
                  <div style={{ padding: "16px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)" }}>
                    <h5 style={{ color: getDialColor(selectedReport.phosphorus), fontSize: "0.9rem", fontWeight: "700" }}>Phosphorus Advice</h5>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "6px", lineHeight: "1.4" }}>
                      {selectedReport.recommendation.phosphorus_recommendation}
                    </p>
                  </div>
                  <div style={{ padding: "16px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)" }}>
                    <h5 style={{ color: getDialColor(selectedReport.potassium), fontSize: "0.9rem", fontWeight: "700" }}>Potassium Advice</h5>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "6px", lineHeight: "1.4" }}>
                      {selectedReport.recommendation.potassium_recommendation}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 style={{ fontSize: "0.95rem", color: "var(--text-primary)", marginBottom: "10px", fontWeight: "700" }}>📅 Recommended Treatment Schedule</h4>
                  <div style={{
                    padding: "16px 20px",
                    backgroundColor: "var(--primary-soft)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.9rem",
                    lineHeight: "1.6",
                    color: "var(--text-primary)",
                    whiteSpace: "pre-wrap"
                  }}>
                    {selectedReport.recommendation.fertilizer_schedule}
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass" style={{ padding: "32px", borderRadius: "var(--radius-md)", textAlign: "center" }}>
                <span style={{ fontSize: "2.5rem", display: "block", marginBottom: "12px" }}>🤖</span>
                <h3>AI Recommendation Pending</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", maxWidth: "400px", margin: "8px auto 20px" }}>
                  Get expert AI agronomist suggestions for crop-planned soil fertilizers, mineral balances, and a feeding schedule.
                </p>
                <button className="btn btn-primary" onClick={handleRunAnalysis} disabled={isAnalyzing}>
                  {isAnalyzing ? (
                    <>
                      <span className="dot-spinner" style={{ marginRight: "8px" }}></span> Analyzing Metrics...
                    </>
                  ) : (
                    "Generate AI Assessment"
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Log Form Modal */}
      <SoilReportForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onReportCreated={handleReportCreated}
      />
    </div>
  );
};

export default SoilAnalyzerPage;
