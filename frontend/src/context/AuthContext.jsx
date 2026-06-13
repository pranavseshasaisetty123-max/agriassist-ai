import React, { createContext, useState, useEffect, useContext } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentFarmer, setCurrentFarmer] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch current profile using active token
  const fetchProfile = async () => {
    try {
      const response = await api.get("/farmers/me");
      setCurrentFarmer(response.data);
    } catch (error) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  // Check token on mount
  useEffect(() => {
    const token = localStorage.getItem("agriassist_token");
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }

    // Listen to unauthorized interceptor event
    const handleUnauthorized = () => {
      setCurrentFarmer(null);
    };
    window.addEventListener("unauthorized", handleUnauthorized);
    return () => window.removeEventListener("unauthorized", handleUnauthorized);
  }, []);

  // Login handler
  const login = async (email, password) => {
    setLoading(true);
    try {
      // API expects form-encoded body (OAuth2 Password flow)
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token } = response.data;
      localStorage.setItem("agriassist_token", access_token);
      
      // Fetch profile details
      const profileResponse = await api.get("/farmers/me");
      setCurrentFarmer(profileResponse.data);
      return profileResponse.data;
    } catch (error) {
      setLoading(false);
      throw error.response?.data?.detail || "Login failed. Please check your credentials.";
    } finally {
      setLoading(false);
    }
  };

  // Register handler
  const register = async (farmerData) => {
    setLoading(true);
    try {
      const response = await api.post("/auth/register", farmerData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Registration failed. Please check the fields.";
    } finally {
      setLoading(false);
    }
  };

  // Logout handler
  const logout = () => {
    localStorage.removeItem("agriassist_token");
    setCurrentFarmer(null);
  };

  // Update profile locally & db
  const updateProfile = async (profileData) => {
    try {
      const response = await api.put("/farmers/me", profileData);
      setCurrentFarmer(response.data);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Profile update failed.";
    }
  };

  const reloadProfile = async () => {
    try {
      const response = await api.get("/farmers/me");
      setCurrentFarmer(response.data);
      return response.data;
    } catch (error) {
      console.error("Failed to reload profile:", error);
    }
  };

  const value = {
    currentFarmer,
    loading,
    login,
    register,
    logout,
    updateProfile,
    reloadProfile,
    isAuthenticated: !!currentFarmer,
  };


  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
