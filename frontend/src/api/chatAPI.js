import api from './axios';

/**
 * Chat API client
 */

// ─── Conversations ─────────────────────────────────────────

export const getConversations = (params = {}) => api.get('/chat/conversations/', { params });
export const getConversation = (id) => api.get(`/chat/conversations/${id}/`);
export const createConversation = (data) => api.post('/chat/conversations/', data);
export const updateConversation = (id, data) => api.patch(`/chat/conversations/${id}/`, data);
export const deleteConversation = (id) => api.delete(`/chat/conversations/${id}/`);

// ─── Conversation Actions ──────────────────────────────────

export const addParticipant = (conversationId, userId) =>
  api.post(`/chat/conversations/${conversationId}/add_participant/`, { user_id: userId });
export const leaveConversation = (conversationId) =>
  api.post(`/chat/conversations/${conversationId}/leave/`);
export const markConversationRead = (conversationId) =>
  api.post(`/chat/conversations/${conversationId}/mark_read/`);

// ─── Messages ──────────────────────────────────────────────

export const getMessages = (params = {}) => api.get('/chat/messages/', { params });
export const getMessage = (id) => api.get(`/chat/messages/${id}/`);
export const sendMessage = (data) => api.post('/chat/messages/', data);
export const deleteMessage = (id) => api.post(`/chat/messages/${id}/delete_for_me/`);

// ─── WebSocket ─────────────────────────────────────────────

// For WebSocket connection, you need to build the URL:
// `ws://localhost:8000/ws/chat/${conversationId}/`
// (or wss:// in production)

// ─── Export all ──────────────────────────────────────────────

export default {
  getConversations,
  getConversation,
  createConversation,
  updateConversation,
  deleteConversation,
  addParticipant,
  leaveConversation,
  markConversationRead,
  getMessages,
  getMessage,
  sendMessage,
  deleteMessage,
};