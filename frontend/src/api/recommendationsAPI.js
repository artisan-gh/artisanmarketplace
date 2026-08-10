import api from './axios';

/**
 * Recommendations API client
 */

// ─── User Preferences ────────────────────────────────────────

/**
 * Get the current user's preferences
 * @returns {Promise} Response with user preferences
 */
export const getMyPreferences = () => {
  return api.get('/recommendations/preferences/mine/');
};

/**
 * Create or update user preferences (POST)
 * @param {Object} data - Preference data
 * @param {string} data.preferred_location - Preferred location
 * @param {number} data.max_distance_km - Max distance in km
 * @param {number} data.min_price - Minimum price
 * @param {number} data.max_price - Maximum price (0 = no limit)
 * @param {number[]} data.preferred_categories - Array of category IDs
 * @param {number} data.min_rating - Minimum rating (0-5)
 * @param {string} data.preferred_contact - 'email', 'phone', or 'chat'
 * @param {boolean} data.receive_recommendations - Opt in/out
 * @returns {Promise} Response with created preferences
 */
export const createPreferences = (data) => {
  return api.post('/recommendations/preferences/', data);
};

/**
 * Update user preferences (PUT)
 * @param {number} id - Preference ID
 * @param {Object} data - Full preference data
 * @returns {Promise} Response with updated preferences
 */
export const updatePreferences = (id, data) => {
  return api.put(`/recommendations/preferences/${id}/`, data);
};

/**
 * Partially update user preferences (PATCH)
 * @param {number} id - Preference ID
 * @param {Object} data - Partial preference data
 * @returns {Promise} Response with updated preferences
 */
export const patchPreferences = (id, data) => {
  return api.patch(`/recommendations/preferences/${id}/`, data);
};

/**
 * Delete user preferences
 * @param {number} id - Preference ID
 * @returns {Promise} Response (204 No Content)
 */
export const deletePreferences = (id) => {
  return api.delete(`/recommendations/preferences/${id}/`);
};

// ─── Interactions ─────────────────────────────────────────────

/**
 * List interactions for the current user
 * @param {Object} params - Query params (filters: interaction_type, artisan, service)
 * @returns {Promise} Response with list of interactions
 */
export const getInteractions = (params = {}) => {
  return api.get('/recommendations/interactions/', { params });
};

/**
 * Create a new interaction
 * @param {Object} data - Interaction data
 * @param {number} [data.artisan] - Artisan ID (if applicable)
 * @param {number} [data.service] - Service ID (if applicable)
 * @param {string} data.interaction_type - 'view', 'click', 'like', 'bookmark', 'message', 'booking', 'rating'
 * @param {number} data.value - Weight or rating (optional, default 0)
 * @param {Object} data.metadata - Additional metadata (optional)
 * @returns {Promise} Response with created interaction
 */
export const createInteraction = (data) => {
  return api.post('/recommendations/interactions/', data);
};

/**
 * Get interactions for a specific artisan
 * @param {number} artisanId - Artisan ID
 * @param {Object} params - Optional query params
 * @returns {Promise} Response with interactions for that artisan
 */
export const getInteractionsForArtisan = (artisanId, params = {}) => {
  return api.get('/recommendations/interactions/for_artisan/', {
    params: { artisan_id: artisanId, ...params },
  });
};

/**
 * Get interactions for a specific service
 * @param {number} serviceId - Service ID
 * @param {Object} params - Optional query params
 * @returns {Promise} Response with interactions for that service
 */
export const getInteractionsForService = (serviceId, params = {}) => {
  return api.get('/recommendations/interactions/for_service/', {
    params: { service_id: serviceId, ...params },
  });
};

/**
 * Delete an interaction
 * @param {number} id - Interaction ID
 * @returns {Promise} Response (204 No Content)
 */
export const deleteInteraction = (id) => {
  return api.delete(`/recommendations/interactions/${id}/`);
};

// ─── Recommendations ─────────────────────────────────────────

/**
 * List recommendations for the current user
 * @param {Object} params - Query params (filters: recommendation_type, is_visible)
 * @returns {Promise} Response with list of recommendations
 */
export const getRecommendations = (params = {}) => {
  return api.get('/recommendations/', { params });
};

/**
 * Get a single recommendation by ID
 * @param {number} id - Recommendation ID
 * @returns {Promise} Response with recommendation details
 */
export const getRecommendation = (id) => {
  return api.get(`/recommendations/${id}/`);
};

/**
 * Track that a user clicked on a recommendation
 * @param {number} id - Recommendation ID
 * @returns {Promise} Response with impression record
 */
export const clickRecommendation = (id) => {
  return api.post(`/recommendations/${id}/click/`);
};

/**
 * Track that a recommendation led to a conversion (e.g., booking)
 * @param {number} id - Recommendation ID
 * @returns {Promise} Response with impression record
 */
export const convertRecommendation = (id) => {
  return api.post(`/recommendations/${id}/convert/`);
};

/**
 * Get recommendations similar to a specific one
 * @param {number} id - Recommendation ID
 * @param {Object} params - Optional query params
 * @returns {Promise} Response with similar recommendations
 */
export const getSimilarRecommendations = (id, params = {}) => {
  return api.get(`/recommendations/${id}/similar/`, { params });
};

// ─── Convenience Utilities ──────────────────────────────────

/**
 * Log an interaction with a single helper function
 * @param {Object} target - { artisan_id, service_id }
 * @param {string} type - Interaction type
 * @param {number} [value=0] - Value or rating
 * @param {Object} [metadata={}] - Additional metadata
 * @returns {Promise} Response with created interaction
 */
export const logInteraction = (target, type, value = 0, metadata = {}) => {
  const data = { interaction_type: type, value, metadata };
  if (target.artisan_id) data.artisan = target.artisan_id;
  if (target.service_id) data.service = target.service_id;
  return createInteraction(data);
};

/**
 * Log a view interaction
 * @param {number} [artisanId] - Artisan ID (if viewing an artisan)
 * @param {number} [serviceId] - Service ID (if viewing a service)
 * @param {Object} [metadata={}] - Additional metadata
 * @returns {Promise} Response with created interaction
 */
export const logView = (artisanId, serviceId, metadata = {}) => {
  return logInteraction(
    { artisan_id: artisanId, service_id: serviceId },
    'view',
    0,
    metadata
  );
};

/**
 * Log a like interaction
 * @param {number} [artisanId] - Artisan ID
 * @param {number} [serviceId] - Service ID
 * @param {Object} [metadata={}] - Additional metadata
 * @returns {Promise} Response with created interaction
 */
export const logLike = (artisanId, serviceId, metadata = {}) => {
  return logInteraction(
    { artisan_id: artisanId, service_id: serviceId },
    'like',
    1,
    metadata
  );
};

/**
 * Log a bookmark interaction
 * @param {number} [artisanId] - Artisan ID
 * @param {number} [serviceId] - Service ID
 * @param {Object} [metadata={}] - Additional metadata
 * @returns {Promise} Response with created interaction
 */
export const logBookmark = (artisanId, serviceId, metadata = {}) => {
  return logInteraction(
    { artisan_id: artisanId, service_id: serviceId },
    'bookmark',
    1,
    metadata
  );
};

/**
 * Log a booking interaction
 * @param {number} [artisanId] - Artisan ID
 * @param {number} [serviceId] - Service ID
 * @param {Object} [metadata={}] - Additional metadata (e.g., booking_id)
 * @returns {Promise} Response with created interaction
 */
export const logBooking = (artisanId, serviceId, metadata = {}) => {
  return logInteraction(
    { artisan_id: artisanId, service_id: serviceId },
    'booking',
    1,
    metadata
  );
};

/**
 * Log a rating interaction
 * @param {number} [artisanId] - Artisan ID
 * @param {number} [serviceId] - Service ID
 * @param {number} rating - Rating value (1-5)
 * @param {Object} [metadata={}] - Additional metadata
 * @returns {Promise} Response with created interaction
 */
export const logRating = (artisanId, serviceId, rating, metadata = {}) => {
  return logInteraction(
    { artisan_id: artisanId, service_id: serviceId },
    'rating',
    rating,
    metadata
  );
};

// ─── Default export ──────────────────────────────────────────

export default {
  // Preferences
  getMyPreferences,
  createPreferences,
  updatePreferences,
  patchPreferences,
  deletePreferences,

  // Interactions
  getInteractions,
  createInteraction,
  getInteractionsForArtisan,
  getInteractionsForService,
  deleteInteraction,

  // Recommendations
  getRecommendations,
  getRecommendation,
  clickRecommendation,
  convertRecommendation,
  getSimilarRecommendations,

  // Utilities
  logInteraction,
  logView,
  logLike,
  logBookmark,
  logBooking,
  logRating,
};