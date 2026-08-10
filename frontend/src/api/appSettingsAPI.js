import api from './axios';

/**
 * App Settings API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getSettings = (params = {}) => api.get('/app-settings/', { params });
export const getSetting = (id) => api.get(`/app-settings/${id}/`);
export const createSetting = (data) => api.post('/app-settings/', data);
export const updateSetting = (id, data) => api.put(`/app-settings/${id}/`, data);
export const patchSetting = (id, data) => api.patch(`/app-settings/${id}/`, data);
export const deleteSetting = (id) => api.delete(`/app-settings/${id}/`);

// ─── Public ──────────────────────────────────────────────────

export const getPublicSettings = () => api.get('/app-settings/public/');

// ─── Group ───────────────────────────────────────────────────

export const getSettingsByGroup = (group) =>
  api.get('/app-settings/by_group/', { params: { group } });

// ─── Cache ──────────────────────────────────────────────────

export const refreshSettingsCache = () => api.post('/app-settings/refresh_cache/');

// ─── Convenience ─────────────────────────────────────────────

export const getSettingValue = async (key) => {
  const response = await getSettings({ search: key });
  if (response.data.results && response.data.results.length > 0) {
    return response.data.results[0].parsed_value;
  }
  return null;
};

// ─── Export all ──────────────────────────────────────────────

export default {
  getSettings,
  getSetting,
  createSetting,
  updateSetting,
  patchSetting,
  deleteSetting,
  getPublicSettings,
  getSettingsByGroup,
  refreshSettingsCache,
  getSettingValue,
};