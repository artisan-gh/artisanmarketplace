import api from './api';

/**
 * SLA API Client
 * Provides access to SLA policies and trackers.
 */

// ─── SLA Policies (CRUD) ─────────────────────────────────────

/**
 * Get a list of SLA policies with optional filters.
 * @param {Object} params - Query parameters (is_active, priority, search, etc.)
 * @returns {Promise} Paginated list of policies
 */
export const getSLAPolicies = (params = {}) =>
  api.get('/sla/policies/', { params });

/**
 * Get a single SLA policy by ID.
 * @param {string} id - Policy UUID
 * @returns {Promise} Policy detail
 */
export const getSLAPolicy = (id) =>
  api.get(`/sla/policies/${id}/`);

/**
 * Create a new SLA policy (admin only).
 * @param {Object} data - Policy data
 * @returns {Promise} Created policy
 */
export const createSLAPolicy = (data) =>
  api.post('/sla/policies/', data);

/**
 * Update an SLA policy (admin only).
 * @param {string} id - Policy UUID
 * @param {Object} data - Updated data
 * @returns {Promise} Updated policy
 */
export const updateSLAPolicy = (id, data) =>
  api.put(`/sla/policies/${id}/`, data);

/**
 * Partial update an SLA policy (admin only).
 * @param {string} id - Policy UUID
 * @param {Object} data - Partial data
 * @returns {Promise} Updated policy
 */
export const patchSLAPolicy = (id, data) =>
  api.patch(`/sla/policies/${id}/`, data);

/**
 * Delete an SLA policy (admin only).
 * @param {string} id - Policy UUID
 * @returns {Promise} Deletion confirmation
 */
export const deleteSLAPolicy = (id) =>
  api.delete(`/sla/policies/${id}/`);

// ─── SLA Trackers (Read‑only) ─────────────────────────────────

/**
 * Get a list of SLA trackers with optional filters.
 * @param {Object} params - Query parameters (status, incident, search, etc.)
 * @returns {Promise} Paginated list of trackers
 */
export const getSLATrackers = (params = {}) =>
  api.get('/sla/trackers/', { params });

/**
 * Get a single SLA tracker by ID.
 * @param {string} id - Tracker UUID
 * @returns {Promise} Tracker detail
 */
export const getSLATracker = (id) =>
  api.get(`/sla/trackers/${id}/`);

// ─── SLA Tracker Custom Actions ──────────────────────────────

/**
 * Get all breached SLAs.
 * @returns {Promise} List of breached trackers
 */
export const getBreachedSLAs = () =>
  api.get('/sla/trackers/breached/');

/**
 * Get all at‑risk SLAs.
 * @returns {Promise} List of at‑risk trackers
 */
export const getAtRiskSLAs = () =>
  api.get('/sla/trackers/at-risk/');

// ─── NEW: Get SLA by Incident ─────────────────────────────────

/**
 * Get SLA tracker for a specific incident.
 * @param {string} incidentId - Incident UUID
 * @returns {Promise} SLA tracker data
 */
export const getIncidentSLA = (incidentId) =>
  api.get(`/sla/trackers/incident/${incidentId}/`);

// ─── Default Export ──────────────────────────────────────────

export default {
  // Policies
  getSLAPolicies,
  getSLAPolicy,
  createSLAPolicy,
  updateSLAPolicy,
  patchSLAPolicy,
  deleteSLAPolicy,

  // Trackers
  getSLATrackers,
  getSLATracker,
  getBreachedSLAs,
  getAtRiskSLAs,

  // Incident
  getIncidentSLA,        // <-- ADDED
};