import api from './axios';

/**
 * Search API client
 */

export const search = (params) => api.get('/search/search/', { params });

// ─── Convenience ─────────────────────────────────────────────

export const searchArtisans = (query, filters = {}) => {
  return search({ q: query, type: 'artisan', ...filters });
};

export const searchServices = (query, filters = {}) => {
  return search({ q: query, type: 'service', ...filters });
};

// ─── Export all ──────────────────────────────────────────────

export default {
  search,
  searchArtisans,
  searchServices,
};