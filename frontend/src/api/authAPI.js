// src/api/authAPI.js
import api from './api';

/**
 * Get the currently authenticated user's details.
 * @returns {Promise} User object with id, email, full_name, profile_picture, etc.
 */
export const getCurrentUser = () =>
  api.get('/auth/users/me/').then((res) => res.data);

/**
 * Alias for consistency (some parts might use `getMe`).
 */
export const getMe = getCurrentUser;

/**
 * Refresh the JWT token (if you need to call it manually).
 * @param {string} refreshToken - The refresh token.
 * @returns {Promise} New access token.
 */
export const refreshToken = (refreshToken) =>
  api.post('/accounts/token/refresh/', { refresh: refreshToken }).then((res) => res.data);

/**
 * Logout – clears tokens from localStorage (client-side only).
 */
export const logout = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  // Optionally call a backend logout endpoint
  return Promise.resolve({ success: true });
};

export default {
  getCurrentUser,
  getMe,
  refreshToken,
  logout,
};