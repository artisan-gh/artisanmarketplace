import api from './axios';

/**
 * Portfolio API client
 */

// ─── Portfolios ──────────────────────────────────────────────

export const getPortfolios = (params = {}) => api.get('/portfolios/', { params });
export const getPortfolio = (id) => api.get(`/portfolios/${id}/`);
export const createPortfolio = (data) => api.post('/portfolios/', data);
export const updatePortfolio = (id, data) => api.put(`/portfolios/${id}/`, data);
export const patchPortfolio = (id, data) => api.patch(`/portfolios/${id}/`, data);
export const deletePortfolio = (id) => api.delete(`/portfolios/${id}/`);

// ─── Current User ────────────────────────────────────────────

export const getMyPortfolios = () => api.get('/portfolios/my_portfolios/');

// ─── Portfolio Media ─────────────────────────────────────────

export const getPortfolioMedia = (params = {}) => api.get('/portfolios/media/', { params });
export const getPortfolioMediaItem = (id) => api.get(`/portfolios/media/${id}/`);
export const createPortfolioMedia = (data) => api.post('/portfolios/media/', data);
export const updatePortfolioMedia = (id, data) => api.put(`/portfolios/media/${id}/`, data);
export const patchPortfolioMedia = (id, data) => api.patch(`/portfolios/media/${id}/`, data);
export const deletePortfolioMedia = (id) => api.delete(`/portfolios/media/${id}/`);

// ─── Add media to portfolio ──────────────────────────────────

export const addMediaToPortfolio = (portfolioId, data) => {
  return api.post(`/portfolios/${portfolioId}/media/`, data);
};

// ─── Export all ──────────────────────────────────────────────

export default {
  getPortfolios,
  getPortfolio,
  createPortfolio,
  updatePortfolio,
  patchPortfolio,
  deletePortfolio,
  getMyPortfolios,
  getPortfolioMedia,
  getPortfolioMediaItem,
  createPortfolioMedia,
  updatePortfolioMedia,
  patchPortfolioMedia,
  deletePortfolioMedia,
  addMediaToPortfolio,
};