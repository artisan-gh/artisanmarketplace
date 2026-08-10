import api from './axios';

/**
 * Inventory API client
 */

// ─── Categories ──────────────────────────────────────────────

export const getCategories = (params = {}) => api.get('/inventory/categories/', { params });
export const getCategory = (id) => api.get(`/inventory/categories/${id}/`);
export const createCategory = (data) => api.post('/inventory/categories/', data);
export const updateCategory = (id, data) => api.put(`/inventory/categories/${id}/`, data);
export const deleteCategory = (id) => api.delete(`/inventory/categories/${id}/`);

// ─── Inventory Items ─────────────────────────────────────────

export const getItems = (params = {}) => api.get('/inventory/items/', { params });
export const getItem = (id) => api.get(`/inventory/items/${id}/`);
export const createItem = (data) => api.post('/inventory/items/', data);
export const updateItem = (id, data) => api.put(`/inventory/items/${id}/`, data);
export const patchItem = (id, data) => api.patch(`/inventory/items/${id}/`, data);
export const deleteItem = (id) => api.delete(`/inventory/items/${id}/`);

// ─── Stock Management ────────────────────────────────────────

export const addStock = (id, quantity, note = '', reference = '') =>
  api.post(`/inventory/items/${id}/add_stock/`, { quantity, note, reference });

export const removeStock = (id, quantity, note = '', reference = '') =>
  api.post(`/inventory/items/${id}/remove_stock/`, { quantity, note, reference });

// ─── Transactions ────────────────────────────────────────────

export const getTransactions = (itemId) =>
  api.get(`/inventory/items/${itemId}/transactions/`);

// ─── Current User ────────────────────────────────────────────

export const getMyItems = () => api.get('/inventory/items/my_items/');
export const getLowStockItems = () => api.get('/inventory/items/low_stock/');

// ─── Convenience ─────────────────────────────────────────────

export const toggleItemAvailability = (id, isAvailable) =>
  patchItem(id, { is_available: isAvailable });

// ─── Export all ──────────────────────────────────────────────

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
  addStock,
  removeStock,
  getTransactions,
  getMyItems,
  getLowStockItems,
  toggleItemAvailability,
};