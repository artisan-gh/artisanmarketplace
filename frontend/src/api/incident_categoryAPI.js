import api from './api';

export const getIncidentCategories = (params) => api.get('incident-categories/', { params });
export const getIncidentCategory = (id) => api.get(`incident-categories/${id}/`);
export const createIncidentCategory = (data) => api.post('incident-categories/', data);
export const updateIncidentCategory = (id, data) => api.put(`incident-categories/${id}/`, data);
export const patchIncidentCategory = (id, data) => api.patch(`incident-categories/${id}/`, data);
export const deleteIncidentCategory = (id) => api.delete(`incident-categories/${id}/`);

export const getSubcategoriesByCategory = (categoryId) =>
  api.get(`incident-categories/subcategories/?category=${categoryId}`);

export default {
  getIncidentCategories,
  getIncidentCategory,
  createIncidentCategory,
  updateIncidentCategory,
  patchIncidentCategory,
  deleteIncidentCategory,
  getSubcategoriesByCategory,
};