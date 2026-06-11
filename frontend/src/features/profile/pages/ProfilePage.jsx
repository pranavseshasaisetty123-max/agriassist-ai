import React, { useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import "./Profile.css";

const ProfilePage = () => {
  const { currentFarmer, updateProfile } = useAuth();
  
  const [formData, setFormData] = useState({
    first_name: currentFarmer?.first_name || "",
    last_name: currentFarmer?.last_name || "",
    location: currentFarmer?.location || "",
    contact_number: currentFarmer?.contact_number || "",
  });
  
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");
    setIsSubmitting(true);

    try {
      await updateProfile(formData);
      setSuccessMessage("Your profile has been updated successfully.");
    } catch (err) {
      setError(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="profile-container animate-fade-in">
      <div className="profile-card glass">
        <h2 className="profile-title">Farmer Settings</h2>
        <p className="profile-subtitle">Update your location and contact info to get regional soil and crop suggestions.</p>

        {error && <div className="profile-alert profile-alert-error animate-fade-in">{error}</div>}
        {successMessage && (
          <div className="profile-alert profile-alert-success animate-fade-in">
            {successMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-group">
            <label className="form-label">Email Address (Cannot be changed)</label>
            <input
              type="email"
              className="form-input"
              value={currentFarmer?.email || ""}
              disabled
              style={{ backgroundColor: "var(--bg-app)", color: "var(--text-muted)" }}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="first_name">First Name</label>
              <input
                type="text"
                id="first_name"
                className="form-input"
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="last_name">Last Name</label>
              <input
                type="text"
                id="last_name"
                className="form-input"
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="location">Location (State/District)</label>
            <input
              type="text"
              id="location"
              className="form-input"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g. Karnataka"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="contact_number">Contact Number</label>
            <input
              type="tel"
              id="contact_number"
              className="form-input"
              value={formData.contact_number}
              onChange={handleChange}
              placeholder="e.g. +919876543210"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary profile-submit-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Saving Changes..." : "Save Settings"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
