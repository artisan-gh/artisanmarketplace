import api from './axios';

/**
 * Payment API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getPayments = (params = {}) => api.get('/payments/', { params });
export const getPayment = (id) => api.get(`/payments/${id}/`);
export const createPayment = (data) => api.post('/payments/', data);
export const updatePayment = (id, data) => api.put(`/payments/${id}/`, data);
export const patchPayment = (id, data) => api.patch(`/payments/${id}/`, data);
export const deletePayment = (id) => api.delete(`/payments/${id}/`);

// ─── Initiate ────────────────────────────────────────────────

export const initiatePayment = (data) => api.post('/payments/initiate/', data);

// ─── Refund ──────────────────────────────────────────────────

export const refundPayment = (id, data = {}) => api.post(`/payments/${id}/refund/`, data);

// ─── Webhook ─────────────────────────────────────────────────

export const paymentWebhook = (data) => api.post('/payments/webhook/', data);

// ─── Current User ────────────────────────────────────────────

export const getMyPayments = () => api.get('/payments/my_payments/');
export const getBookingPayments = (bookingId) =>
  api.get('/payments/booking_payments/', { params: { booking_id: bookingId } });

// ─── Export all ──────────────────────────────────────────────

export default {
  getPayments,
  getPayment,
  createPayment,
  updatePayment,
  patchPayment,
  deletePayment,
  initiatePayment,
  refundPayment,
  paymentWebhook,
  getMyPayments,
  getBookingPayments,
};