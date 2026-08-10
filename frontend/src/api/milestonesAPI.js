import api from './axios';

/**
 * Milestone API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getMilestones = (params = {}) => api.get('/milestones/', { params });
export const getMilestone = (id) => api.get(`/milestones/${id}/`);
export const createMilestone = (data) => api.post('/milestones/', data);
export const updateMilestone = (id, data) => api.put(`/milestones/${id}/`, data);
export const patchMilestone = (id, data) => api.patch(`/milestones/${id}/`, data);
export const deleteMilestone = (id) => api.delete(`/milestones/${id}/`);

// ─── Status Actions ──────────────────────────────────────────

export const startMilestone = (id) => api.post(`/milestones/${id}/start/`);
export const completeMilestone = (id) => api.post(`/milestones/${id}/complete/`);
export const cancelMilestone = (id) => api.post(`/milestones/${id}/cancel/`);

// ─── Current User ────────────────────────────────────────────

export const getMyMilestones = () => api.get('/milestones/my_milestones/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getMilestones,
  getMilestone,
  createMilestone,
  updateMilestone,
  patchMilestone,
  deleteMilestone,
  startMilestone,
  completeMilestone,
  cancelMilestone,
  getMyMilestones,
};