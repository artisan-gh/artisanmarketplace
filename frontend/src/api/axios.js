
import axios from "axios";

// ============================================================
// API BASE URL
// ============================================================
// In production, Render should provide:
// VITE_API_BASE_URL=https://backendapi-tv2v.onrender.com/api
//
// The fallback below ensures the correct production URL is used
// even if the environment variable is missing.
//
// IMPORTANT:
// Do NOT add /api to individual API calls because /api is already
// included in this base URL.
// ============================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://backendapi-tv2v.onrender.com/api";

// ============================================================
// AXIOS INSTANCE
// ============================================================

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================
// REQUEST INTERCEPTOR
// Attach access token to authenticated requests
// ============================================================

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");

    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================
// RESPONSE INTERCEPTOR
// Automatically refresh expired access tokens
// ============================================================

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    // If there is no request configuration, just reject
    if (!originalRequest) {
      return Promise.reject(error);
    }

    // ========================================================
    // Do NOT attempt token refresh for authentication endpoints
    // ========================================================

    const requestUrl = originalRequest.url || "";

    const isLoginRequest = requestUrl.includes("/auth/token/");
    const isRefreshRequest = requestUrl.includes("/auth/token/refresh/");
    const isRegisterRequest = requestUrl.includes("/auth/register/");

    // ========================================================
    // Handle expired access token
    // ========================================================

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isLoginRequest &&
      !isRefreshRequest &&
      !isRegisterRequest
    ) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refreshToken");

        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        // ====================================================
        // Refresh token
        // ====================================================

        const { data } = await axios.post(
          `${API_BASE_URL}/auth/token/refresh/`,
          {
            refresh: refreshToken,
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        // ====================================================
        // Store new access token
        // ====================================================

        localStorage.setItem("accessToken", data.access);

        // Some SimpleJWT configurations rotate refresh tokens.
        if (data.refresh) {
          localStorage.setItem("refreshToken", data.refresh);
        }

        // ====================================================
        // Retry original request with new access token
        // ====================================================

        originalRequest.headers = originalRequest.headers || {};

        originalRequest.headers.Authorization =
          `Bearer ${data.access}`;

        return api(originalRequest);
      } catch (refreshError) {
        // ====================================================
        // Refresh failed
        // Clear authentication data and return to login
        // ====================================================

        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("user_type");

        window.location.href = "/login";

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;



