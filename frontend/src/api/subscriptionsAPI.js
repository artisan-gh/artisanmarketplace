import api from './axios';

/**
 * Subscription API client
 */

// ─── Subscription Plans ─────────────────────────────────────

export const getPlans = (params = {}) => api.get('/subscriptions/plans/', { params });
export const getPlan = (id) => api.get(`/subscriptions/plans/${id}/`);
export const createPlan = (data) => api.post('/subscriptions/plans/', data);
export const updatePlan = (id, data) => api.put(`/subscriptions/plans/${id}/`, data);
export const patchPlan = (id, data) => api.patch(`/subscriptions/plans/${id}/`, data);
export const deletePlan = (id) => api.delete(`/subscriptions/plans/${id}/`);

// ─── Subscriptions ───────────────────────────────────────────

export const getSubscriptions = (params = {}) => api.get('/subscriptions/', { params });
export const getSubscription = (id) => api.get(`/subscriptions/${id}/`);
export const activateSubscription = (data) => api.post('/subscriptions/activate/', data);
export const renewSubscription = (id, data = {}) => api.post(`/subscriptions/${id}/renew/`, data);
export const cancelSubscription = (id, reason = '') => api.post(`/subscriptions/${id}/cancel/`, { reason });
export const toggleAutoRenew = (id) => api.post(`/subscriptions/${id}/toggle_auto_renew/`);

// ─── Current User ────────────────────────────────────────────

export const getMySubscription = () => api.get('/subscriptions/my_subscription/');
export const getMySubscriptions = () => api.get('/subscriptions/my_subscriptions/');

// ─── Export all ──────────────────────────────────────────────

export default {
  // Plans
  getPlans,
  getPlan,
  createPlan,
  updatePlan,
  patchPlan,
  deletePlan,

  // Subscriptions
  getSubscriptions,
  getSubscription,
  activateSubscription,
  renewSubscription,
  cancelSubscription,
  toggleAutoRenew,

  // Current user
  getMySubscription,
  getMySubscriptions,
};