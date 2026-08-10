import api from './axios';

/**
 * Support API client
 */

// ─── Tickets ─────────────────────────────────────────────────

export const getTickets = (params = {}) => api.get('/support/tickets/', { params });
export const getTicket = (id) => api.get(`/support/tickets/${id}/`);
export const createTicket = (data) => api.post('/support/tickets/', data);
export const updateTicket = (id, data) => api.put(`/support/tickets/${id}/`, data);
export const patchTicket = (id, data) => api.patch(`/support/tickets/${id}/`, data);
export const deleteTicket = (id) => api.delete(`/support/tickets/${id}/`);

// ─── Actions ─────────────────────────────────────────────────

export const replyToTicket = (ticketId, data) => api.post(`/support/tickets/${ticketId}/reply/`, data);
export const updateTicketStatus = (ticketId, status) => api.post(`/support/tickets/${ticketId}/update_status/`, { status });
export const assignTicket = (ticketId, userId) => api.post(`/support/tickets/${ticketId}/assign/`, { user_id: userId });

// ─── Current User ────────────────────────────────────────────

export const getMyTickets = () => api.get('/support/tickets/my_tickets/');
export const getUnassignedTickets = () => api.get('/support/tickets/unassigned/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getTickets,
  getTicket,
  createTicket,
  updateTicket,
  patchTicket,
  deleteTicket,
  replyToTicket,
  updateTicketStatus,
  assignTicket,
  getMyTickets,
  getUnassignedTickets,
};