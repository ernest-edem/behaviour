import axios from "axios";

/**
 * -----------------------------
 * BASE API CLIENT
 * -----------------------------
 */

export const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1", // adjust if needed
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * -----------------------------
 * REQUEST INTERCEPTOR
 * Inject JWT token automatically
 * -----------------------------
 */
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
}); 