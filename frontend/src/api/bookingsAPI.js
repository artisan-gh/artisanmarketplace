import api from './axios';

/**
 * Booking API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getBookings = (params = {}) => api.get('/bookings/', { params });
export const getBooking = (id) => api.get(`/bookings/${id}/`);
export const createBooking = (data) => api.post('/bookings/', data);
export const updateBooking = (id, data) => api.put(`/bookings/${id}/`, data);
export const patchBooking = (id, data) => api.patch(`/bookings/${id}/`, data);
export const deleteBooking = (id) => api.delete(`/bookings/${id}/`);

// ─── Status Actions ──────────────────────────────────────────

export const acceptBooking = (id) => api.post(`/bookings/${id}/accept/`);
export const rejectBooking = (id, reason = '') => api.post(`/bookings/${id}/reject/`, { reason });
export const startBooking = (id) => api.post(`/bookings/${id}/start/`);
export const completeBooking = (id) => api.post(`/bookings/${id}/complete/`);
export const cancelBooking = (id, reason = '') => api.post(`/bookings/${id}/cancel/`, { reason });

// ─── Current User ────────────────────────────────────────────

export const getMyBookings = () => api.get('/bookings/my_bookings/');
export const getUpcomingBookings = () => api.get('/bookings/upcoming/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getBookings,
  getBooking,
  createBooking,
  updateBooking,
  patchBooking,
  deleteBooking,
  acceptBooking,
  rejectBooking,
  startBooking,
  completeBooking,
  cancelBooking,
  getMyBookings,
  getUpcomingBookings,
};