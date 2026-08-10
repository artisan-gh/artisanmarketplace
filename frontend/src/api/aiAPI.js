import api from './axios';

/**
 * AI API client
 */

// ─── Models ───────────────────────────────────────────────────

export const getModels = (params = {}) => api.get('/ai/models/', { params });
export const getModel = (id) => api.get(`/ai/models/${id}/`);
export const createModel = (data) => api.post('/ai/models/', data);
export const updateModel = (id, data) => api.put(`/ai/models/${id}/`, data);
export const patchModel = (id, data) => api.patch(`/ai/models/${id}/`, data);
export const deleteModel = (id) => api.delete(`/ai/models/${id}/`);

// ─── Requests ─────────────────────────────────────────────────

export const getRequests = (params = {}) => api.get('/ai/requests/', { params });
export const getRequest = (id) => api.get(`/ai/requests/${id}/`);
export const createRequest = (data) => api.post('/ai/requests/', data);
export const cancelRequest = (id) => api.post(`/ai/requests/${id}/cancel/`);

// ─── Stats ────────────────────────────────────────────────────

export const getAIStats = () => api.get('/ai/requests/stats/');

// ─── Current User ────────────────────────────────────────────

export const getMyRequests = () => api.get('/ai/requests/my_requests/');

// ─── Convenience ─────────────────────────────────────────────

export const sendChatRequest = async (modelId, messages, metadata = {}) => {
  return createRequest({
    model: modelId,
    request_type: 'chat',
    input_data: { messages },
    metadata,
  });
};

// ─── Export all ──────────────────────────────────────────────

export default {
  getModels,
  getModel,
  createModel,
  updateModel,
  patchModel,
  deleteModel,
  getRequests,
  getRequest,
  createRequest,
  cancelRequest,
  getAIStats,
  getMyRequests,
  sendChatRequest,
};