import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./features/auth/pages/LoginPage";
import RegisterPage from "./features/auth/pages/RegisterPage";
import ChatPage from "./features/chat/pages/ChatPage";
import LandingPage from "./pages/LandingPage";
import { ToastContainer } from "./components/Toast";

// Component to protect authenticated routes
const ProtectedRoute = ({ children }) => {
  const { currentFarmer, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        backgroundColor: "var(--bg-app)",
        fontSize: "1.2rem",
        fontFamily: "'Outfit', sans-serif",
        color: "var(--primary)"
      }}>
        🌱 Loading AgriAssist AI...
      </div>
    );
  }

  if (!currentFarmer) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Component to redirect logged-in users away from login/register
const PublicRoute = ({ children }) => {
  const { currentFarmer, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (currentFarmer) {
    return <Navigate to="/chat" replace />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <ToastContainer />
      <Router>
        <Routes>
          {/* Public Landing Page */}
          <Route path="/" element={<LandingPage />} />

          {/* Public Authentication Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />

          {/* Protected Main Workspace Route */}
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />

          {/* Default Routing Redirects */}
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
