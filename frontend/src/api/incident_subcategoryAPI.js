import api from './api';

export const getSubcategories = (params) => api.get('incident-subcategories/', { params });
export const getSubcategoriesByCategory = (categoryId) =>
  api.get(`incident-subcategories/?category=${categoryId}`);

export default {
  getSubcategories,
  getSubcategoriesByCategory,
};