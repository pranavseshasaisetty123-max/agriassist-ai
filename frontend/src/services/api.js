import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1", // Default FastAPI address or Docker config
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Inject JWT token and selected language into header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("agriassist_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    const lang = localStorage.getItem("agri_lang") || "en";
    config.headers["Accept-Language"] = lang;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Catch auth errors (e.g. 401 expired tokens)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and reload or trigger redirect
      localStorage.removeItem("agriassist_token");
      // Optional: Dispatch event to trigger state logout
      window.dispatchEvent(new Event("unauthorized"));
    }
    return Promise.reject(error);
  }
);

export default api;
