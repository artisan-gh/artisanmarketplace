// src/api/notificationsAPI.js
import api from './api';

/**
 * Notifications API Client
 * Provides access to user notifications.
 */

// ─── List & Detail ────────────────────────────────────────────

export const getNotifications = (params = {}) =>
  api.get('/notifications/', { params });

export const getNotification = (id) =>
  api.get(`/notifications/${id}/`);

// ─── Actions ──────────────────────────────────────────────────

export const markNotificationRead = (id) =>
  api.post(`/notifications/${id}/mark_read/`);

export const markAllNotificationsRead = () =>
  api.post('/notifications/mark_all_read/');

export const getUnreadCount = () =>
  api.get('/notifications/unread_count/');

// ─── Default Export ──────────────────────────────────────────

export default {
  getNotifications,
  getNotification,
  markNotificationRead,
  markAllNotificationsRead,
  getUnreadCount,
};