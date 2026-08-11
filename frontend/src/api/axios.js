import axios from 'axios';

// Use environment variable for base URL (e.g., https://backendapi-tv2v.onrender.com)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://backendapi-tv2v.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ---- Request interceptor: attach access token ----
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---- Response interceptor: refresh token on 401 ----
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Prevent infinite loops
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Call the token refresh endpoint (Simple JWT default)
        const { data } = await axios.post(
          `${API_BASE_URL}/accounts/token/refresh/`,
          { refresh: refreshToken }
        );

        // Store new access token
        localStorage.setItem('accessToken', data.access);
        // Optionally update refresh token if the backend issues a new one
        if (data.refresh) {
          localStorage.setItem('refreshToken', data.refresh);
        }

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed – clear tokens and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        // Optional: clear other user data
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;