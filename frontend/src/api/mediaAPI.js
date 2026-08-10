import api from './axios';

/**
 * Media API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getMediaFiles = (params = {}) => api.get('/media/', { params });
export const getMediaFile = (id) => api.get(`/media/${id}/`);
export const updateMediaFile = (id, data) => api.patch(`/media/${id}/`, data);
export const deleteMediaFile = (id) => api.delete(`/media/${id}/`);

// ─── Upload ──────────────────────────────────────────────────

/**
 * Upload a file (multipart/form-data)
 * @param {File} file - The file to upload
 * @param {Object} options - { category, is_public, expires_at, content_type, object_id }
 * @returns {Promise} Response with media file data
 */
export const uploadFile = (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  if (options.category) formData.append('category', options.category);
  if (options.is_public !== undefined) formData.append('is_public', options.is_public);
  if (options.expires_at) formData.append('expires_at', options.expires_at);
  if (options.content_type) formData.append('content_type', options.content_type);
  if (options.object_id) formData.append('object_id', options.object_id);
  return api.post('/media/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// ─── Actions ──────────────────────────────────────────────────

export const downloadFile = (id) => api.get(`/media/${id}/download/`, { responseType: 'blob' });
export const softDeleteFile = (id) => api.post(`/media/${id}/soft_delete/`);

// ─── Current User ────────────────────────────────────────────

export const getMyMediaFiles = () => api.get('/media/my_files/');
export const getRecentMediaFiles = () => api.get('/media/recent/');

// ─── Convenience ─────────────────────────────────────────────

export const uploadAvatar = (file) => {
  return uploadFile(file, { category: 'AVATAR', is_public: true });
};

export const uploadPortfolioImage = (file, objectId) => {
  return uploadFile(file, {
    category: 'PORTFOLIO',
    content_type: 'portfolio',
    object_id: objectId,
    is_public: true,
  });
};

// ─── Export all ──────────────────────────────────────────────

export default {
  getMediaFiles,
  getMediaFile,
  updateMediaFile,
  deleteMediaFile,
  uploadFile,
  downloadFile,
  softDeleteFile,
  getMyMediaFiles,
  getRecentMediaFiles,
  uploadAvatar,
  uploadPortfolioImage,
};