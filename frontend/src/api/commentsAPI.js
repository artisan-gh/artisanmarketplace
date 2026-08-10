import api from './api';

// ─── Comments ──────────────────────────────────────────────────
export const getComments = (params) => api.get('comments/', { params });
export const getComment = (id) => api.get(`comments/${id}/`);
export const createComment = (data) => api.post('comments/', data);
export const updateComment = (id, data) => api.put(`comments/${id}/`, data);
export const patchComment = (id, data) => api.patch(`comments/${id}/`, data);
export const deleteComment = (id) => api.delete(`comments/${id}/`);

// ─── Default Export ──────────────────────────────────────────
export default {
  getComments,
  getComment,
  createComment,
  updateComment,
  patchComment,
  deleteComment,
};