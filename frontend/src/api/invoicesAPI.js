import api from './axios';

/**
 * Invoice API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getInvoices = (params = {}) => api.get('/invoices/', { params });
export const getInvoice = (id) => api.get(`/invoices/${id}/`);
export const createInvoice = (data) => api.post('/invoices/', data);
export const updateInvoice = (id, data) => api.put(`/invoices/${id}/`, data);
export const patchInvoice = (id, data) => api.patch(`/invoices/${id}/`, data);
export const deleteInvoice = (id) => api.delete(`/invoices/${id}/`);

// ─── Actions ─────────────────────────────────────────────────

export const sendInvoice = (id, options = {}) => api.post(`/invoices/${id}/send/`, options);
export const markInvoicePaid = (id, paymentId = null) => api.post(`/invoices/${id}/mark_paid/`, { payment_id: paymentId });
export const cancelInvoice = (id) => api.post(`/invoices/${id}/cancel/`);

// ─── PDF ─────────────────────────────────────────────────────

export const downloadInvoicePDF = (id) => api.get(`/invoices/${id}/download_pdf/`);

// ─── Current User ────────────────────────────────────────────

export const getMyInvoices = () => api.get('/invoices/my_invoices/');
export const getOverdueInvoices = () => api.get('/invoices/overdue/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getInvoices,
  getInvoice,
  createInvoice,
  updateInvoice,
  patchInvoice,
  deleteInvoice,
  sendInvoice,
  markInvoicePaid,
  cancelInvoice,
  downloadInvoicePDF,
  getMyInvoices,
  getOverdueInvoices,
};