// src/api/artisanAPI.js
import api from './api';

/* ============================================================================
   ARTISAN PROFILES (via /artisans/profiles/)
============================================================================ */

/**
 * Get all artisan profiles
 */
export const getArtisans = (params = {}) =>
  api.get('/artisans/profiles/', { params }).then((res) => res.data);

/**
 * Get artisan profile details
 */
export const getArtisan = (id) =>
  api.get(`/artisans/profiles/${id}/`).then((res) => res.data);

/**
 * Create artisan profile (admin only)
 */
export const createArtisan = (data) =>
  api.post('/artisans/profiles/', data).then((res) => res.data);

/**
 * Update artisan profile
 */
export const updateArtisan = (id, data) =>
  api.put(`/artisans/profiles/${id}/`, data).then((res) => res.data);

/**
 * Partial update artisan profile
 */
export const patchArtisan = (id, data) =>
  api.patch(`/artisans/profiles/${id}/`, data).then((res) => res.data);

/**
 * Delete artisan profile (admin only)
 */
export const deleteArtisan = (id) =>
  api.delete(`/artisans/profiles/${id}/`).then((res) => res.data);

/* ============================================================================
   ARTISAN CUSTOM ACTIONS
============================================================================ */

/**
 * Get the current user's artisan profile
 * Endpoint: GET /artisans/profiles/my_profile/
 */
export const getMyArtisanProfile = () =>
  api.get('/artisans/profiles/my_profile/').then((res) => res.data);

/**
 * Get all available artisans
 * Endpoint: GET /artisans/profiles/available/
 */
export const getAvailableArtisans = (params = {}) =>
  api.get('/artisans/profiles/available/', { params }).then((res) => res.data);

/**
 * Get an artisan's availability schedule
 * Endpoint: GET /artisans/profiles/{id}/availability/
 */
export const getArtisanAvailability = (id) =>
  api.get(`/artisans/profiles/${id}/availability/`).then((res) => res.data);

/**
 * Set/update an artisan's availability schedule (artisan only)
 * Endpoint: POST /artisans/profiles/{id}/availability/
 * @param {string} id - Artisan profile UUID
 * @param {Object} data - { day_of_week, start_time, end_time, is_working }
 */
export const setArtisanAvailability = (id, data) =>
  api.post(`/artisans/profiles/${id}/availability/`, data).then((res) => res.data);

/* ============================================================================
   SKILLS (via /artisans/skills/)
============================================================================ */

/**
 * Get all skills
 */
export const getSkills = (params = {}) =>
  api.get('/artisans/skills/', { params }).then((res) => res.data);

/**
 * Get skill details
 */
export const getSkill = (id) =>
  api.get(`/artisans/skills/${id}/`).then((res) => res.data);

/**
 * Create skill (admin only)
 */
export const createSkill = (data) =>
  api.post('/artisans/skills/', data).then((res) => res.data);

/**
 * Update skill (admin only)
 */
export const updateSkill = (id, data) =>
  api.put(`/artisans/skills/${id}/`, data).then((res) => res.data);

/**
 * Partial update skill (admin only)
 */
export const patchSkill = (id, data) =>
  api.patch(`/artisans/skills/${id}/`, data).then((res) => res.data);

/**
 * Delete skill (admin only)
 */
export const deleteSkill = (id) =>
  api.delete(`/artisans/skills/${id}/`).then((res) => res.data);

/* ============================================================================
   SMART ARTISAN SUGGESTION (Placeholder – Phase 2)
============================================================================ */

/**
 * Suggest the best artisans based on service, location, and preferred time.
 * (Placeholder – returns empty array until Phase 2 is implemented)
 * @returns {Promise} Array of suggested artisans with scores
 */
export const suggestArtisans = () => Promise.resolve([]);

/* ============================================================================
   DEFAULT EXPORT
============================================================================ */

const ArtisanAPI = {
  // Profiles
  getArtisans,
  getArtisan,
  createArtisan,
  updateArtisan,
  patchArtisan,
  deleteArtisan,

  // Profile custom actions
  getMyArtisanProfile,
  getAvailableArtisans,
  getArtisanAvailability,
  setArtisanAvailability,

  // Skills
  getSkills,
  getSkill,
  createSkill,
  updateSkill,
  patchSkill,
  deleteSkill,

  // Smart suggestion (placeholder)
  suggestArtisans,
};

export default ArtisanAPI;