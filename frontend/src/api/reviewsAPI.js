import api from './axios';

/**
 * Review API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getReviews = (params = {}) => api.get('/reviews/', { params });
export const getReview = (id) => api.get(`/reviews/${id}/`);
export const createReview = (data) => api.post('/reviews/', data);
export const updateReview = (id, data) => api.put(`/reviews/${id}/`, data);
export const patchReview = (id, data) => api.patch(`/reviews/${id}/`, data);
export const deleteReview = (id) => api.delete(`/reviews/${id}/`);

// ─── Moderation ──────────────────────────────────────────────

export const moderateReview = (id, action, reason = '') =>
  api.post(`/reviews/${id}/moderate/`, { action, reason });

// ─── Helpfulness ─────────────────────────────────────────────

export const markReviewHelpful = (id) =>
  api.post(`/reviews/${id}/helpful/`, { helpful: true });

export const markReviewNotHelpful = (id) =>
  api.post(`/reviews/${id}/helpful/`, { helpful: false });

// ─── Current User ────────────────────────────────────────────

export const getMyReviews = () => api.get('/reviews/my_reviews/');

// ─── Artisan Reviews ─────────────────────────────────────────

export const getArtisanReviews = (artisanId) =>
  api.get('/reviews/for_artisan/', { params: { artisan_id: artisanId } });

// ─── Export all ──────────────────────────────────────────────

export default {
  getReviews,
  getReview,
  createReview,
  updateReview,
  patchReview,
  deleteReview,
  moderateReview,
  markReviewHelpful,
  markReviewNotHelpful,
  getMyReviews,
  getArtisanReviews,
};