import api from './axios';

/**
 * Verification API client
 */

// ─── Document Types ──────────────────────────────────────────

export const getDocumentTypes = (params = {}) =>
  api.get('/verification/document-types/', { params });

export const getDocumentType = (id) =>
  api.get(`/verification/document-types/${id}/`);

// ─── Verification Requests ──────────────────────────────────

export const getVerificationRequests = (params = {}) =>
  api.get('/verification/', { params });

export const getVerificationRequest = (id) =>
  api.get(`/verification/${id}/`);

export const createVerificationRequest = (data) =>
  api.post('/verification/', data);

export const updateVerificationRequest = (id, data) =>
  api.put(`/verification/${id}/`, data);

export const patchVerificationRequest = (id, data) =>
  api.patch(`/verification/${id}/`, data);

export const deleteVerificationRequest = (id) =>
  api.delete(`/verification/${id}/`);

// ─── Actions ──────────────────────────────────────────────────

export const performVerificationAction = (id, action, reason = '') =>
  api.post(`/verification/${id}/action/`, { action, reason });

export const approveVerification = (id) =>
  performVerificationAction(id, 'approve');

export const rejectVerification = (id, reason = '') =>
  performVerificationAction(id, 'reject', reason);

export const startReviewVerification = (id) =>
  performVerificationAction(id, 'start_review');

export const cancelVerification = (id) =>
  performVerificationAction(id, 'cancel');

export const expireVerification = (id) =>
  performVerificationAction(id, 'expire');

// ─── Current User ────────────────────────────────────────────

export const getMyVerificationRequests = () =>
  api.get('/verification/my_requests/');

export const getMyVerificationStatus = () =>
  api.get('/verification/status/');

// ─── Staff ──────────────────────────────────────────────────

export const getPendingVerifications = () =>
  api.get('/verification/pending/');

// ─── Export all ──────────────────────────────────────────────

export default {
  // Document Types
  getDocumentTypes,
  getDocumentType,

  // Verification Requests
  getVerificationRequests,
  getVerificationRequest,
  createVerificationRequest,
  updateVerificationRequest,
  patchVerificationRequest,
  deleteVerificationRequest,

  // Actions
  performVerificationAction,
  approveVerification,
  rejectVerification,
  startReviewVerification,
  cancelVerification,
  expireVerification,

  // Current User
  getMyVerificationRequests,
  getMyVerificationStatus,

  // Staff
  getPendingVerifications,
};