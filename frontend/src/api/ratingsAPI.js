import api from './axios';

/**
 * Ratings API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getRatings = (params = {}) => api.get('/ratings/', { params });
export const getRating = (id) => api.get(`/ratings/${id}/`);
export const createRating = (data) => api.post('/ratings/', data);
export const updateRating = (id, data) => api.put(`/ratings/${id}/`, data);
export const patchRating = (id, data) => api.patch(`/ratings/${id}/`, data);
export const deleteRating = (id) => api.delete(`/ratings/${id}/`);

// ─── Current User ────────────────────────────────────────────

export const getMyRatings = () => api.get('/ratings/my_ratings/');

// ─── Artisan Ratings ─────────────────────────────────────────

export const getArtisanRatings = (artisanId) => 
  api.get('/ratings/for_artisan/', { params: { artisan_id: artisanId } });

export const getArtisanRatingStats = (artisanId) => 
  api.get('/ratings/stats/', { params: { artisan_id: artisanId } });

// ─── Export all ──────────────────────────────────────────────

export default {
  getRatings,
  getRating,
  createRating,
  updateRating,
  patchRating,
  deleteRating,
  getMyRatings,
  getArtisanRatings,
  getArtisanRatingStats,
};