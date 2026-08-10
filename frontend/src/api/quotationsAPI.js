import api from './axios';

/**
 * Quotation API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getQuotations = (params = {}) => api.get('/quotations/', { params });
export const getQuotation = (id) => api.get(`/quotations/${id}/`);
export const createQuotation = (data) => api.post('/quotations/', data);
export const updateQuotation = (id, data) => api.put(`/quotations/${id}/`, data);
export const patchQuotation = (id, data) => api.patch(`/quotations/${id}/`, data);
export const deleteQuotation = (id) => api.delete(`/quotations/${id}/`);

// ─── Status Actions ──────────────────────────────────────────

export const sendQuotation = (id) => api.post(`/quotations/${id}/send/`);
export const acceptQuotation = (id) => api.post(`/quotations/${id}/accept/`);
export const rejectQuotation = (id) => api.post(`/quotations/${id}/reject/`);
export const expireQuotation = (id) => api.post(`/quotations/${id}/expire/`);

// ─── Current User ────────────────────────────────────────────

export const getMyQuotations = () => api.get('/quotations/my_quotations/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getQuotations,
  getQuotation,
  createQuotation,
  updateQuotation,
  patchQuotation,
  deleteQuotation,
  sendQuotation,
  acceptQuotation,
  rejectQuotation,
  expireQuotation,
  getMyQuotations,
};