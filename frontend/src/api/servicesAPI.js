import api from './axios';

/**
 * Service API client
 * All functions return Promises with the response data
 * Authentication is handled automatically via the axios interceptor
 */

// ─── Base CRUD ───────────────────────────────────────────────

/**
 * Get all services (paginated)
 * @param {Object} params - Query parameters (filters, search, ordering)
 * @returns {Promise} Response with list of services
 */
export const getServices = (params = {}) => {
  return api.get('/services/', { params });
};

/**
 * Get a single service by ID
 * @param {number|string} id - Service ID
 * @returns {Promise} Response with service details
 */
export const getService = (id) => {
  return api.get(`/services/${id}/`);
};

/**
 * Create a new service
 * @param {Object} data - Service data (name, description, category, etc.)
 * @returns {Promise} Response with created service
 */
export const createService = (data) => {
  return api.post('/services/', data);
};

/**
 * Update a service (full update)
 * @param {number|string} id - Service ID
 * @param {Object} data - Updated service data
 * @returns {Promise} Response with updated service
 */
export const updateService = (id, data) => {
  return api.put(`/services/${id}/`, data);
};

/**
 * Partially update a service
 * @param {number|string} id - Service ID
 * @param {Object} data - Partial update data
 * @returns {Promise} Response with updated service
 */
export const patchService = (id, data) => {
  return api.patch(`/services/${id}/`, data);
};

/**
 * Delete a service
 * @param {number|string} id - Service ID
 * @returns {Promise} Response (204 No Content)
 */
export const deleteService = (id) => {
  return api.delete(`/services/${id}/`);
};

// ─── Custom Actions ──────────────────────────────────────────

/**
 * Get active services
 * @param {Object} params - Optional query params (filter, search, etc.)
 * @returns {Promise} Response with list of active services
 */
export const getActiveServices = (params = {}) => {
  return api.get('/services/active/', { params });
};

/**
 * Get featured services
 * @param {Object} params - Optional query params
 * @returns {Promise} Response with list of featured services
 */
export const getFeaturedServices = (params = {}) => {
  return api.get('/services/featured/', { params });
};

/**
 * Get services by category
 * @param {number|string} categoryId - Category ID
 * @param {Object} params - Optional query params
 * @returns {Promise} Response with list of services in that category
 */
export const getServicesByCategory = (categoryId, params = {}) => {
  return api.get(`/services/category/${categoryId}/`, { params });
};

/**
 * Get services by subcategory
 * @param {number|string} subcategoryId - SubCategory ID
 * @param {Object} params - Optional query params
 * @returns {Promise} Response with list of services in that subcategory
 */
export const getServicesBySubcategory = (subcategoryId, params = {}) => {
  return api.get(`/services/subcategory/${subcategoryId}/`, { params });
};

/**
 * Get service statistics (admin only)
 * @returns {Promise} Response with total, active, featured, inactive counts
 */
export const getServiceStatistics = () => {
  return api.get('/services/statistics/');
};

// ─── Convenience exports ─────────────────────────────────────

export default {
  getServices,
  getService,
  createService,
  updateService,
  patchService,
  deleteService,
  getActiveServices,
  getFeaturedServices,
  getServicesByCategory,
  getServicesBySubcategory,
  getServiceStatistics,
};