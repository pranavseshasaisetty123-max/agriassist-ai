import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";
import "./Auth.css";

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    location: "",
    contact_number: "",
  });
  
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    
    try {
      // 1. Trigger signup request
      await register(formData);
      
      // 2. Auto login user after registration
      await login(formData.email, formData.password);
      
      navigate("/chat");
    } catch (err) {
      setError(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card glass animate-fade-in registration-card">
        <div className="auth-header">
          <div className="auth-logo">🌱</div>
          <h1 className="auth-title">Farmer Registration</h1>
          <p className="auth-subtitle">Join AgriAssist AI to receive specialized agricultural guides</p>
        </div>

        {error && <div className="auth-error animate-fade-in">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form registration-form">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="first_name">First Name</label>
              <input
                type="text"
                id="first_name"
                className="form-input"
                placeholder="Ramesh"
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
                placeholder="Kumar"
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              className="form-input"
              placeholder="farmer@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password (min 6 characters)</label>
            <input
              type="password"
              id="password"
              className="form-input"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              minLength={6}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="location">Location (State/District)</label>
              <input
                type="text"
                id="location"
                className="form-input"
                placeholder="Karnataka"
                value={formData.location}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="contact_number">Contact Number</label>
              <input
                type="tel"
                id="contact_number"
                className="form-input"
                placeholder="+919876543210"
                value={formData.contact_number}
                onChange={handleChange}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="spinner-container">
                <span className="spinner"></span> Creating Account...
              </span>
            ) : (
              "Register & Log In"
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already registered?{" "}
            <Link to="/login" className="auth-link">
              Log In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
