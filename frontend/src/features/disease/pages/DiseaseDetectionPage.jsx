import React, { useState, useEffect } from "react";
import api from "../../../services/api";

const API_HOST = "http://localhost:8000"; // Host for local static files

const DiseaseDetectionPage = () => {
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [activeScan, setActiveScan] = useState(null);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  // Fetch scan history on mount
  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await api.get("/disease/scans");
      setHistory(response.data);
    } catch (err) {
      console.error("Failed to fetch scan history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleFile = (file) => {
    setError("");
    if (!file) return;

    // Validate type
    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!validTypes.includes(file.type)) {
      setError("Please select a valid image file (JPEG, PNG, or WEBP).");
      return;
    }

    // Validate size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("File size exceeds 5MB limit. Please upload a smaller image.");
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setActiveScan(null); // Clear active scan when new file is chosen
  };

  const handleFileChange = (e) => {
    handleFile(e.target.files[0]);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleScanSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || scanning) return;

    setScanning(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.post("/disease/scan", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      const newScan = response.data;
      setActiveScan(newScan);
      setHistory((prev) => [newScan, ...prev]);
      
      // Reset upload selection
      setSelectedFile(null);
      setPreviewUrl("");
    } catch (err) {
      console.error("Analysis failure:", err);
      setError(
        err.response?.data?.detail || 
        "Failed to analyze image. Please verify your connection or try again."
      );
    } finally {
      setScanning(false);
    }
  };

  const handleSelectScan = (scan) => {
    setError("");
    setSelectedFile(null);
    setPreviewUrl("");
    setActiveScan(scan);
  };

  const handleDeleteScan = async (e, scanId) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this diagnosis record?")) return;

    try {
      await api.delete(`/disease/scans/${scanId}`);
      setHistory((prev) => prev.filter((s) => s.id !== scanId));
      if (activeScan && activeScan.id === scanId) {
        setActiveScan(null);
      }
    } catch (err) {
      console.error("Failed to delete scan:", err);
      alert("Failed to delete the scan diagnostics record.");
    }
  };

  const getSeverityStyles = (sev) => {
    switch (sev.toLowerCase()) {
      case "high":
      case "critical":
        return { color: "#e53e3e", bg: "#fff5f5", border: "#f8b4b4", badgeText: "High Severity" };
      case "medium":
      case "warning":
        return { color: "#dd6b20", bg: "#fffaf0", border: "#fbd38d", badgeText: "Medium Severity" };
      default:
        return { color: "var(--primary)", bg: "var(--primary-soft)", border: "var(--border-light)", badgeText: "Low Severity" };
    }
  };

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 320px",
      gap: "24px",
      padding: "32px",
      height: "calc(100vh - 100px)",
      overflow: "hidden"
    }}>
      {/* Left Panel: Upload and Results */}
      <div style={{ display: "flex", flexDirection: "column", gap: "24px", overflowY: "auto", paddingRight: "8px" }}>
        
        {/* Upload Container */}
        <div className="glass" style={{ padding: "28px", borderRadius: "var(--radius-md)" }}>
          <h3 style={{ fontSize: "1.2rem", marginBottom: "16px", color: "var(--text-primary)" }}>
            📸 Upload Crop Leaf Photo
          </h3>
          <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", marginBottom: "20px" }}>
            Select or drag a clear, close-up photo of the infected crop leaf. Gemini Vision will identify symptoms, suggest chemical or organic treatments, and list prevention strategies.
          </p>

          <form onSubmit={handleScanSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div 
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              style={{
                border: dragActive ? "2px dashed var(--primary)" : "2px dashed var(--text-muted)",
                borderRadius: "var(--radius-md)",
                backgroundColor: dragActive ? "var(--primary-glow)" : "rgba(255, 255, 255, 0.4)",
                padding: "40px 20px",
                textAlign: "center",
                cursor: "pointer",
                position: "relative",
                transition: "var(--transition-smooth)"
              }}
            >
              <input 
                type="file" 
                id="leaf-file-upload" 
                onChange={handleFileChange} 
                accept="image/*"
                style={{ display: "none" }}
              />
              
              <label htmlFor="leaf-file-upload" style={{ cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: "12px" }}>
                <span style={{ fontSize: "3rem" }}>🍃</span>
                <span style={{ fontWeight: "600", color: "var(--text-primary)" }}>
                  Click to select or drag leaf image here
                </span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                  Supports JPEG, PNG, WEBP (Max 5MB)
                </span>
              </label>
            </div>

            {error && (
              <div style={{ padding: "12px 16px", backgroundColor: "#fff5f5", color: "#e53e3e", borderRadius: "var(--radius-sm)", fontSize: "0.875rem", borderLeft: "4px solid #e53e3e" }}>
                ⚠️ {error}
              </div>
            )}

            {previewUrl && (
              <div className="glass" style={{ padding: "20px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", alignItems: "center", gap: "16px" }}>
                <img 
                  src={previewUrl} 
                  alt="Crop leaf preview" 
                  style={{
                    maxHeight: "240px",
                    maxWidth: "100%",
                    borderRadius: "var(--radius-sm)",
                    objectFit: "cover",
                    boxShadow: "var(--shadow-sm)"
                  }}
                />
                <div style={{ display: "flex", gap: "12px" }}>
                  <button 
                    type="submit" 
                    className="btn btn-primary" 
                    disabled={scanning}
                    style={{ minWidth: "160px" }}
                  >
                    {scanning ? (
                      <>
                        <span className="dot-spinner"></span> Analyzing Image...
                      </>
                    ) : "🔍 Analyze Crop Leaf"}
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl("");
                    }}
                    disabled={scanning}
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Diagnostic Results Card */}
        {activeScan && (
          <div className="glass animate-fade-in" style={{
            padding: "32px",
            borderRadius: "var(--radius-md)",
            borderLeft: `5px solid ${getSeverityStyles(activeScan.severity).color}`,
            display: "flex",
            flexDirection: "column",
            gap: "24px"
          }}>
            {/* Header info */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
              <div>
                <span style={{
                  fontSize: "0.75rem",
                  fontWeight: "700",
                  textTransform: "uppercase",
                  padding: "4px 10px",
                  borderRadius: "var(--radius-full)",
                  backgroundColor: getSeverityStyles(activeScan.severity).bg,
                  color: getSeverityStyles(activeScan.severity).color,
                  border: `1px solid ${getSeverityStyles(activeScan.severity).border}`,
                  display: "inline-block",
                  marginBottom: "8px"
                }}>
                  {getSeverityStyles(activeScan.severity).badgeText}
                </span>
                <h2 style={{ fontSize: "1.8rem", color: "var(--text-primary)", fontWeight: "800" }}>
                  {activeScan.disease_name}
                </h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Diagnosed on {new Date(activeScan.created_at).toLocaleString()} | Confidence: <strong>{(activeScan.confidence * 100).toFixed(0)}%</strong>
                </p>
              </div>

              {/* Uploaded Leaf view */}
              <div style={{ position: "relative" }}>
                <img 
                  src={activeScan.image_path.startsWith("http") ? activeScan.image_path : `${API_HOST}${activeScan.image_path}`}
                  alt={activeScan.disease_name}
                  style={{
                    width: "120px",
                    height: "120px",
                    borderRadius: "var(--radius-sm)",
                    objectFit: "cover",
                    boxShadow: "var(--shadow-md)",
                    border: "2px solid #fff"
                  }}
                />
              </div>
            </div>

            <hr style={{ border: "none", borderTop: "1px solid var(--border-light)" }} />

            {/* Symptoms Grid */}
            <div>
              <h4 style={{ color: "var(--text-primary)", fontSize: "1rem", fontWeight: "700", marginBottom: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
                👁️ Symptoms Observed
              </h4>
              <ul style={{ paddingLeft: "20px", fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {activeScan.symptoms.map((pt, i) => (
                  <li key={i} style={{ marginBottom: "4px" }}>{pt}</li>
                ))}
              </ul>
            </div>

            {/* Treatment recommendations */}
            <div>
              <h4 style={{ color: "var(--text-primary)", fontSize: "1rem", fontWeight: "700", marginBottom: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
                💊 Recommended Treatments
              </h4>
              <ul style={{ paddingLeft: "20px", fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {activeScan.treatment.map((pt, i) => (
                  <li key={i} style={{ marginBottom: "4px" }}>{pt}</li>
                ))}
              </ul>
            </div>

            {/* Preventive measures */}
            <div>
              <h4 style={{ color: "var(--text-primary)", fontSize: "1rem", fontWeight: "700", marginBottom: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
                🛡️ Preventive Actions
              </h4>
              <ul style={{ paddingLeft: "20px", fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {activeScan.preventive_measures.map((pt, i) => (
                  <li key={i} style={{ marginBottom: "4px" }}>{pt}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Right Side: Scan History List */}
      <div className="glass" style={{
        borderRadius: "var(--radius-md)",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        overflowY: "hidden"
      }}>
        <h3 style={{ fontSize: "1.1rem", padding: "0 8px", color: "var(--text-primary)", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
          📜 Diagnostic History
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", overflowY: "auto", flex: 1, padding: "2px" }}>
          {loadingHistory ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              <span className="dot-spinner"></span> Loading history...
            </div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              No crop leaves scanned yet. Upload above to diagnose!
            </div>
          ) : (
            history.map((scan) => {
              const styles = getSeverityStyles(scan.severity);
              const isSelected = activeScan && activeScan.id === scan.id;
              
              return (
                <div 
                  key={scan.id}
                  onClick={() => handleSelectScan(scan)}
                  className="glass"
                  style={{
                    display: "flex",
                    gap: "12px",
                    padding: "10px",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    borderLeft: `3px solid ${styles.color}`,
                    backgroundColor: isSelected ? "var(--primary-soft)" : "var(--bg-card)",
                    transition: "var(--transition-bounce)",
                    position: "relative"
                  }}
                >
                  <img 
                    src={scan.image_path.startsWith("http") ? scan.image_path : `${API_HOST}${scan.image_path}`}
                    alt={scan.disease_name}
                    style={{
                      width: "48px",
                      height: "48px",
                      borderRadius: "6px",
                      objectFit: "cover"
                    }}
                  />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h4 style={{
                      fontSize: "0.85rem",
                      fontWeight: "700",
                      color: "var(--text-primary)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis"
                    }}>
                      {scan.disease_name}
                    </h4>
                    <span style={{ fontSize: "0.7rem", color: styles.color, fontWeight: "600", display: "block", marginTop: "2px" }}>
                      {(scan.confidence * 100).toFixed(0)}% Match | {scan.severity}
                    </span>
                    <span style={{ fontSize: "0.65rem", color: "var(--text-secondary)", display: "block", marginTop: "1px" }}>
                      {new Date(scan.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button 
                    onClick={(e) => handleDeleteScan(e, scan.id)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#e53e3e",
                      cursor: "pointer",
                      fontSize: "0.9rem",
                      padding: "4px",
                      display: "flex",
                      alignItems: "center",
                      alignSelf: "center"
                    }}
                    title="Delete record"
                  >
                    🗑️
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default DiseaseDetectionPage;
