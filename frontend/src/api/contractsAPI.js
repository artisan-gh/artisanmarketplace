import api from './axios';

/**
 * Contract API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getContracts = (params = {}) => api.get('/contracts/', { params });
export const getContract = (id) => api.get(`/contracts/${id}/`);
export const createContract = (data) => api.post('/contracts/', data);
export const updateContract = (id, data) => api.put(`/contracts/${id}/`, data);
export const patchContract = (id, data) => api.patch(`/contracts/${id}/`, data);
export const deleteContract = (id) => api.delete(`/contracts/${id}/`);

// ─── Signature Actions ───────────────────────────────────────

export const signContractAsClient = (id) => api.post(`/contracts/${id}/sign_client/`);
export const signContractAsArtisan = (id) => api.post(`/contracts/${id}/sign_artisan/`);

// ─── Status Actions ──────────────────────────────────────────

export const completeContract = (id) => api.post(`/contracts/${id}/complete/`);
export const terminateContract = (id) => api.post(`/contracts/${id}/terminate/`);

// ─── Current User ────────────────────────────────────────────

export const getMyContracts = () => api.get('/contracts/my_contracts/');

// ─── Export all ──────────────────────────────────────────────

export default {
  getContracts,
  getContract,
  createContract,
  updateContract,
  patchContract,
  deleteContract,
  signContractAsClient,
  signContractAsArtisan,
  completeContract,
  terminateContract,
  getMyContracts,
};