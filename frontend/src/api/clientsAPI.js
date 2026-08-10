import api from './axios';

export const getClients = (params = {}) => api.get('/clients/', { params });
export const getClient = (id) => api.get(`/clients/${id}/`);
export const createClient = (data) => api.post('/clients/', data);
export const updateClient = (id, data) => api.put(`/clients/${id}/`, data);
export const patchClient = (id, data) => api.patch(`/clients/${id}/`, data);
export const deleteClient = (id) => api.delete(`/clients/${id}/`);
export const getMyClientProfile = () => api.get('/clients/me/');
export const updateMyClientProfile = (data) => api.patch('/clients/update_me/', data);

export default {
  getClients,
  getClient,
  createClient,
  updateClient,
  patchClient,
  deleteClient,
  getMyClientProfile,
  updateMyClientProfile,
};