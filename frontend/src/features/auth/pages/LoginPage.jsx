import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";
import "./Auth.css"; // We will create a local stylesheet for auth features

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    
    try {
      await login(email, password);
      navigate("/chat");
    } catch (err) {
      setError(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card glass animate-fade-in">
        <div className="auth-header">
          <div className="auth-logo">🌱</div>
          <h1 className="auth-title">Welcome to AgriAssist AI</h1>
          <p className="auth-subtitle">Log in to consult your virtual agronomist</p>
        </div>

        {error && <div className="auth-error animate-fade-in">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              className="form-input"
              placeholder="farmer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="spinner-container">
                <span className="spinner"></span> Logging in...
              </span>
            ) : (
              "Log In"
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            New to AgriAssist?{" "}
            <Link to="/register" className="auth-link">
              Register Here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
