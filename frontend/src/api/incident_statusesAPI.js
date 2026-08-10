import api from './api';

// ─── Incident Statuses ─────────────────────────────────────────
export const getIncidentStatuses = (params) => api.get('incident-statuses/', { params });
export const getIncidentStatus = (id) => api.get(`incident-statuses/${id}/`);
export const createIncidentStatus = (data) => api.post('incident-statuses/', data);
export const updateIncidentStatus = (id, data) => api.put(`incident-statuses/${id}/`, data);
export const patchIncidentStatus = (id, data) => api.patch(`incident-statuses/${id}/`, data);
export const deleteIncidentStatus = (id) => api.delete(`incident-statuses/${id}/`);

// ─── Default Export ──────────────────────────────────────────
export default {
  getIncidentStatuses,
  getIncidentStatus,
  createIncidentStatus,
  updateIncidentStatus,
  patchIncidentStatus,
  deleteIncidentStatus,
};