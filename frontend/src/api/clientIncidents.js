
import api from './client';

export const listMyIncidents = () => api.get('/client/incidents/').then(r => r.data);
export const getMyIncident = (id) => api.get(`/client/incidents/${id}/`).then(r => r.data);
export const createMyIncident = (payload) =>
  api.post('/client/incidents/', payload).then(r => r.data);
export const getMyCustomerProfile = () => api.get('/customers/me/').then(r => r.data);
