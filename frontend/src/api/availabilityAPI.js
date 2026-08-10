import api from './axios';

/**
 * Availability API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getAvailability = (params = {}) => api.get('/availability/', { params });
export const getAvailabilityItem = (id) => api.get(`/availability/${id}/`);
export const createAvailability = (data) => api.post('/availability/', data);
export const updateAvailability = (id, data) => api.put(`/availability/${id}/`, data);
export const patchAvailability = (id, data) => api.patch(`/availability/${id}/`, data);
export const deleteAvailability = (id) => api.delete(`/availability/${id}/`);

// ─── Current User ────────────────────────────────────────────

export const getMyAvailability = () => api.get('/availability/my_availability/');

/**
 * Create multiple availability entries at once.
 * @param {Array} data - List of {day, start_time, end_time, available}
 */
export const bulkCreateAvailability = (data) => {
  return api.post('/availability/bulk_create/', data);
};

// ─── Export all ──────────────────────────────────────────────

export default {
  getAvailability,
  getAvailabilityItem,
  createAvailability,
  updateAvailability,
  patchAvailability,
  deleteAvailability,
  getMyAvailability,
  bulkCreateAvailability,
};