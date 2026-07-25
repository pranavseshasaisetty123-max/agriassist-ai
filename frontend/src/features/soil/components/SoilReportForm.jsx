import React, { useState } from "react";
import api from "../../../services/api";
import { useLanguage } from "../../../context/LanguageContext";

const SoilReportForm = ({ isOpen, onClose, onReportCreated }) => {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    ph: 6.5,
    nitrogen: 40.0,
    phosphorus: 20.0,
    potassium: 120.0,
    organic_matter: "",
    crop_planned: "Wheat",
    tested_at: new Date().toISOString().substring(0, 10)
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Input validations
    if (formData.ph < 0.0 || formData.ph > 14.0) {
      setError(t("soil_err_ph"));
      setLoading(false);
      return;
    }
    if (formData.nitrogen < 0.0 || formData.phosphorus < 0.0 || formData.potassium < 0.0) {
      setError(t("soil_err_negative"));
      setLoading(false);
      return;
    }
    if (formData.organic_matter !== "" && (formData.organic_matter < 0.0 || formData.organic_matter > 100.0)) {
      setError(t("soil_err_om_pct"));
      setLoading(false);
      return;
    }

    try {
      const payload = {
        ...formData,
        ph: parseFloat(formData.ph),
        nitrogen: parseFloat(formData.nitrogen),
        phosphorus: parseFloat(formData.phosphorus),
        potassium: parseFloat(formData.potassium),
        organic_matter: formData.organic_matter !== "" ? parseFloat(formData.organic_matter) : null
      };

      const response = await api.post("/soil/reports", payload);
      onReportCreated(response.data);
      onClose();
    } catch (err) {
      console.error("Failed to save report:", err);
      setError(err.response?.data?.detail || t("soil_err_save"));
    } finally {
      setLoading(false);
    }
  };

  const cropsList = ["Wheat", "Rice", "Cotton", "Maize", "Tomatoes", "Potatoes", "Sugar Cane", "Onions", "Soybeans", "Other"];

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(28, 39, 33, 0.4)",
      backdropFilter: "blur(4px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 100,
      padding: "16px"
    }} onClick={onClose}>
      <div className="glass animate-fade-in" style={{
        backgroundColor: "var(--bg-card)",
        width: "100%",
        maxWidth: "540px",
        borderRadius: "var(--radius-md)",
        padding: "32px",
        boxShadow: "var(--shadow-lg)",
        maxHeight: "90vh",
        overflowY: "auto"
      }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2 style={{ fontSize: "1.35rem", color: "var(--text-primary)" }}>🧪 {t("soil_log_test")}</h2>
          <button onClick={onClose} style={{
            background: "none",
            border: "none",
            fontSize: "1.5rem",
            cursor: "pointer",
            color: "var(--text-muted)",
            lineHeight: "1"
          }}>×</button>
        </div>

        {error && (
          <div style={{
            backgroundColor: "#fff5f5",
            color: "#e53e3e",
            padding: "12px 16px",
            borderRadius: "var(--radius-sm)",
            fontSize: "0.875rem",
            marginBottom: "16px",
            borderLeft: "4px solid #e53e3e"
          }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div className="form-group">
              <label className="form-label" htmlFor="ph">{t("soil_ph_level")}</label>
              <input
                type="number"
                id="ph"
                step="0.1"
                min="0"
                max="14"
                className="form-input"
                value={formData.ph}
                onChange={(e) => setFormData({ ...formData, ph: e.target.value })}
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="organic_matter">{t("soil_organic_matter")}</label>
              <input
                type="number"
                id="organic_matter"
                step="0.1"
                min="0"
                max="100"
                className="form-input"
                placeholder={t("soil_optional")}
                value={formData.organic_matter}
                onChange={(e) => setFormData({ ...formData, organic_matter: e.target.value })}
              />
            </div>
          </div>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "12px",
            backgroundColor: "var(--bg-app)",
            padding: "16px",
            borderRadius: "var(--radius-sm)",
            marginBottom: "20px"
          }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="nitrogen" style={{ fontSize: "0.75rem" }}>{t("soil_nitrogen")}</label>
              <input
                type="number"
                id="nitrogen"
                step="0.1"
                min="0"
                className="form-input"
                value={formData.nitrogen}
                onChange={(e) => setFormData({ ...formData, nitrogen: e.target.value })}
                required
                style={{ padding: "8px 12px" }}
              />
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{t("soil_mg_kg")}</span>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="phosphorus" style={{ fontSize: "0.75rem" }}>{t("soil_phosphorus")}</label>
              <input
                type="number"
                id="phosphorus"
                step="0.1"
                min="0"
                className="form-input"
                value={formData.phosphorus}
                onChange={(e) => setFormData({ ...formData, phosphorus: e.target.value })}
                required
                style={{ padding: "8px 12px" }}
              />
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{t("soil_mg_kg")}</span>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="potassium" style={{ fontSize: "0.75rem" }}>{t("soil_potassium")}</label>
              <input
                type="number"
                id="potassium"
                step="0.1"
                min="0"
                className="form-input"
                value={formData.potassium}
                onChange={(e) => setFormData({ ...formData, potassium: e.target.value })}
                required
                style={{ padding: "8px 12px" }}
              />
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{t("soil_mg_kg")}</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="crop_planned">{t("form_crop_planned")}</label>
            <select
              id="crop_planned"
              className="form-input"
              value={formData.crop_planned}
              onChange={(e) => setFormData({ ...formData, crop_planned: e.target.value })}
              required
              style={{ appearance: "auto" }}
            >
              {cropsList.map((crop) => (
                <option key={crop} value={crop}>{crop}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="tested_at">{t("soil_testing_date")}</label>
            <input
              type="date"
              id="tested_at"
              className="form-input"
              value={formData.tested_at}
              onChange={(e) => setFormData({ ...formData, tested_at: e.target.value })}
              required
            />
          </div>

          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "24px" }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              {t("btn_cancel")}
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? t("btn_loading") : t("soil_log_test")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SoilReportForm;
