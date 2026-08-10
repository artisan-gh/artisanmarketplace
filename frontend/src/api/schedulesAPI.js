import api from './axios';

/**
 * Schedule API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getSchedules = (params = {}) => api.get('/schedules/', { params });
export const getSchedule = (id) => api.get(`/schedules/${id}/`);
export const createSchedule = (data) => api.post('/schedules/', data);
export const updateSchedule = (id, data) => api.put(`/schedules/${id}/`, data);
export const patchSchedule = (id, data) => api.patch(`/schedules/${id}/`, data);
export const deleteSchedule = (id) => api.delete(`/schedules/${id}/`);

// ─── Actions ─────────────────────────────────────────────────

export const confirmSchedule = (id) => api.post(`/schedules/${id}/confirm/`);
export const cancelSchedule = (id) => api.post(`/schedules/${id}/cancel/`);
export const completeSchedule = (id) => api.post(`/schedules/${id}/complete/`);

// ─── Current User ────────────────────────────────────────────

export const getUpcomingSchedules = () => api.get('/schedules/upcoming/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getSchedules,
  getSchedule,
  createSchedule,
  updateSchedule,
  patchSchedule,
  deleteSchedule,
  confirmSchedule,
  cancelSchedule,
  completeSchedule,
  getUpcomingSchedules,
};