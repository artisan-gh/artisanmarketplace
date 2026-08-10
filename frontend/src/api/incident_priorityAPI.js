import api from './api';

export const getIncidentPriorities = (params) => api.get('incident-priorities/', { params });
export const getIncidentPriority = (id) => api.get(`incident-priorities/${id}/`);
export const createIncidentPriority = (data) => api.post('incident-priorities/', data);
export const updateIncidentPriority = (id, data) => api.put(`incident-priorities/${id}/`, data);
export const patchIncidentPriority = (id, data) => api.patch(`incident-priorities/${id}/`, data);
export const deleteIncidentPriority = (id) => api.delete(`incident-priorities/${id}/`);

export default {
  getIncidentPriorities,
  getIncidentPriority,
  createIncidentPriority,
  updateIncidentPriority,
  patchIncidentPriority,
  deleteIncidentPriority,
};