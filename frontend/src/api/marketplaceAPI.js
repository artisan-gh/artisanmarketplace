import api from './axios';

/**
 * Marketplace API client
 */

// ─── Categories ──────────────────────────────────────────────

export const getCategories = (params = {}) => api.get('/marketplace/categories/', { params });
export const getCategory = (id) => api.get(`/marketplace/categories/${id}/`);
export const createCategory = (data) => api.post('/marketplace/categories/', data);
export const updateCategory = (id, data) => api.put(`/marketplace/categories/${id}/`, data);
export const deleteCategory = (id) => api.delete(`/marketplace/categories/${id}/`);

// ─── Items ───────────────────────────────────────────────────

export const getItems = (params = {}) => api.get('/marketplace/items/', { params });
export const getItem = (id) => api.get(`/marketplace/items/${id}/`);
export const createItem = (data) => api.post('/marketplace/items/', data);
export const updateItem = (id, data) => api.put(`/marketplace/items/${id}/`, data);
export const patchItem = (id, data) => api.patch(`/marketplace/items/${id}/`, data);
export const deleteItem = (id) => api.delete(`/marketplace/items/${id}/`);

// ─── Item Actions ────────────────────────────────────────────

export const approveItem = (id) => api.post(`/marketplace/items/${id}/approve/`);
export const rejectItem = (id) => api.post(`/marketplace/items/${id}/reject/`);
export const featureItem = (id) => api.post(`/marketplace/items/${id}/feature/`);
export const incrementView = (id) => api.post(`/marketplace/items/${id}/increment_view/`);
export const likeItem = (id) => api.post(`/marketplace/items/${id}/like/`);

// ─── Current User ────────────────────────────────────────────

export const getMyItems = () => api.get('/marketplace/items/my_items/');

// ─── Staff ───────────────────────────────────────────────────

export const getPendingItems = () => api.get('/marketplace/items/pending/');

// ─── Cart ─────────────────────────────────────────────────────

export const getCart = () => api.get('/marketplace/cart/');
export const addToCart = (itemId, quantity = 1) =>
  api.post('/marketplace/cart/add/', { item_id: itemId, quantity });
export const removeFromCart = (itemId) =>
  api.post('/marketplace/cart/remove/', { item_id: itemId });
export const updateCartItem = (itemId, quantity) =>
  api.post('/marketplace/cart/update_item/', { item_id: itemId, quantity });
export const clearCart = () => api.post('/marketplace/cart/clear/');

// ─── Orders ──────────────────────────────────────────────────

export const getOrders = (params = {}) => api.get('/marketplace/orders/', { params });
export const getOrder = (id) => api.get(`/marketplace/orders/${id}/`);
export const checkout = (data) => api.post('/marketplace/orders/checkout/', data);
export const cancelOrder = (id) => api.post(`/marketplace/orders/${id}/cancel/`);

// ─── Convenience ─────────────────────────────────────────────

export const toggleItemActive = (id, isActive) =>
  patchItem(id, { is_active: isActive });

export default {
  getCategories,
  getCategory,
  createCategory,
  updateCategory,
  deleteCategory,
  getItems,
  getItem,
  createItem,
  updateItem,
  patchItem,
  deleteItem,
  approveItem,
  rejectItem,
  featureItem,
  incrementView,
  likeItem,
  getMyItems,
  getPendingItems,
  getCart,
  addToCart,
  removeFromCart,
  updateCartItem,
  clearCart,
  getOrders,
  getOrder,
  checkout,
  cancelOrder,
  toggleItemActive,
};