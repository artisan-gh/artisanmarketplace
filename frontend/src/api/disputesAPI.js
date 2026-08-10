import api from './axios';

/**
 * Dispute API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getDisputes = (params = {}) => api.get('/disputes/', { params });
export const getDispute = (id) => api.get(`/disputes/${id}/`);
export const createDispute = (data) => api.post('/disputes/', data);
export const updateDispute = (id, data) => api.put(`/disputes/${id}/`, data);
export const patchDispute = (id, data) => api.patch(`/disputes/${id}/`, data);
export const deleteDispute = (id) => api.delete(`/disputes/${id}/`);

// ─── Messages ────────────────────────────────────────────────

export const sendDisputeMessage = (disputeId, data) => api.post(`/disputes/${disputeId}/send_message/`, data);

// ─── Staff Actions ──────────────────────────────────────────

export const updateDisputeStatus = (disputeId, status, resolution = '') =>
  api.post(`/disputes/${disputeId}/update_status/`, { status, resolution });

export const assignDispute = (disputeId, userId) =>
  api.post(`/disputes/${disputeId}/assign/`, { assigned_to: userId });

// ─── Current User ────────────────────────────────────────────

export const getMyDisputes = () => api.get('/disputes/my_disputes/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getDisputes,
  getDispute,
  createDispute,
  updateDispute,
  patchDispute,
  deleteDispute,
  sendDisputeMessage,
  updateDisputeStatus,
  assignDispute,
  getMyDisputes,
};