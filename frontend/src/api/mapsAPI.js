import api from './axios';

/**
 * Maps/Location API client
 */

// ─── Location ────────────────────────────────────────────────

export const getLocations = (params = {}) => api.get('/maps/locations/', { params });
export const getLocation = (id) => api.get(`/maps/locations/${id}/`);
export const createLocation = (data) => api.post('/maps/locations/', data);
export const updateLocation = (id, data) => api.put(`/maps/locations/${id}/`, data);
export const patchLocation = (id, data) => api.patch(`/maps/locations/${id}/`, data);
export const deleteLocation = (id) => api.delete(`/maps/locations/${id}/`);

// ─── Current User ────────────────────────────────────────────

export const getMyLocation = () => api.get('/maps/locations/my_location/');

// ─── Nearby Search ───────────────────────────────────────────

export const findNearbyArtisans = (latitude, longitude, radiusKm = 10) => {
  return api.post('/maps/locations/nearby_artisans/', {
    latitude,
    longitude,
    radius_km: radiusKm,
  });
};

export const findNearbyClients = (latitude, longitude, radiusKm = 10) => {
  return api.post('/maps/locations/nearby_clients/', {
    latitude,
    longitude,
    radius_km: radiusKm,
  });
};

// ─── Convenience ─────────────────────────────────────────────

export const updateMyLocation = (data) => {
  return api.patch('/maps/locations/my_location/', data);
};

// ─── Export all ──────────────────────────────────────────────

export default {
  getLocations,
  getLocation,
  createLocation,
  updateLocation,
  patchLocation,
  deleteLocation,
  getMyLocation,
  findNearbyArtisans,
  findNearbyClients,
  updateMyLocation,
};