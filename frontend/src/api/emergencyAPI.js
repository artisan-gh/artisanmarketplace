import api from './axios';

/**
 * Emergency API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getEmergencies = (params = {}) => api.get('/emergency/', { params });
export const getEmergency = (id) => api.get(`/emergency/${id}/`);
export const createEmergency = (data) => api.post('/emergency/', data);
export const updateEmergency = (id, data) => api.put(`/emergency/${id}/`, data);
export const patchEmergency = (id, data) => api.patch(`/emergency/${id}/`, data);
export const deleteEmergency = (id) => api.delete(`/emergency/${id}/`);

// ─── Actions ──────────────────────────────────────────────────

/**
 * Perform an action on an emergency request.
 * @param {number} id - Emergency ID
 * @param {string} action - 'assign', 'accept', 'start', 'complete', 'cancel'
 * @param {Object} options - Additional data
 * @param {number} options.artisan_id - Required for 'assign'
 * @param {string} options.estimated_arrival_time - ISO datetime (optional)
 * @param {string} options.reason - Required for 'cancel'
 * @returns {Promise} Response with updated emergency
 */
export const performEmergencyAction = (id, action, options = {}) => {
  return api.post(`/emergency/${id}/action/`, { action, ...options });
};

// ─── Convenience ─────────────────────────────────────────────

export const assignEmergency = (id, artisanId, estimatedArrivalTime = null) => {
  return performEmergencyAction(id, 'assign', {
    artisan_id: artisanId,
    estimated_arrival_time: estimatedArrivalTime,
  });
};

export const acceptEmergency = (id) => performEmergencyAction(id, 'accept');
export const startEmergency = (id) => performEmergencyAction(id, 'start');
export const completeEmergency = (id) => performEmergencyAction(id, 'complete');
export const cancelEmergency = (id, reason = '') =>
  performEmergencyAction(id, 'cancel', { reason });

// ─── Current User ────────────────────────────────────────────

export const getMyEmergencies = () => api.get('/emergency/my_requests/');

// ─── Open Requests ───────────────────────────────────────────

export const getOpenEmergencies = () => api.get('/emergency/open_requests/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getEmergencies,
  getEmergency,
  createEmergency,
  updateEmergency,
  patchEmergency,
  deleteEmergency,
  performEmergencyAction,
  assignEmergency,
  acceptEmergency,
  startEmergency,
  completeEmergency,
  cancelEmergency,
  getMyEmergencies,
  getOpenEmergencies,
};