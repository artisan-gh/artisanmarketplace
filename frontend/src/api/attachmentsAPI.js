import api from './api';

// ─── Attachments ──────────────────────────────────────────────
export const getAttachments = (params) => api.get('attachments/', { params });
export const getAttachment = (id) => api.get(`attachments/${id}/`);
export const createAttachment = (data) => api.post('attachments/', data);
export const updateAttachment = (id, data) => api.put(`attachments/${id}/`, data);
export const patchAttachment = (id, data) => api.patch(`attachments/${id}/`, data);
export const deleteAttachment = (id) => api.delete(`attachments/${id}/`);

// ─── Default Export ──────────────────────────────────────────
export default {
  getAttachments,
  getAttachment,
  createAttachment,
  updateAttachment,
  patchAttachment,
  deleteAttachment,
};