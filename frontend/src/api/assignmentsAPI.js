import api from './api';

// ─── Assignments ──────────────────────────────────────────────
export const getAssignments = (params) => api.get('assignments/', { params });
export const getAssignment = (id) => api.get(`assignments/${id}/`);
export const createAssignment = (data) => api.post('assignments/', data);
export const updateAssignment = (id, data) => api.put(`assignments/${id}/`, data);
export const patchAssignment = (id, data) => api.patch(`assignments/${id}/`, data);
export const deleteAssignment = (id) => api.delete(`assignments/${id}/`);

// ─── Assignment Custom Actions ───────────────────────────────
export const acceptAssignment = (id) => api.post(`assignments/${id}/accept/`);
export const rejectAssignment = (id) => api.post(`assignments/${id}/reject/`);
export const startAssignment = (id) => api.post(`assignments/${id}/start/`);
export const completeAssignment = (id) => api.post(`assignments/${id}/complete/`);
export const getMyAssignments = () => api.get('assignments/my/');

// ─── 👇 ADD THIS ──────────────────────────────────────────────
export const rateAssignment = (id, data) => api.post(`assignments/${id}/rate/`, data);
export default {
  getAssignments,
  getAssignment,
  createAssignment,
  updateAssignment,
  patchAssignment,
  deleteAssignment,
  acceptAssignment,
  rejectAssignment,
  startAssignment,
  completeAssignment,
  getMyAssignments,
  rateAssignment,   // 👈 also add it here
};