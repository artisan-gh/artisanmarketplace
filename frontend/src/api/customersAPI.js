import api from './api';

// ─── Customers ──────────────────────────────────────────────────
export const getCustomers = (params) => api.get('customers/', { params });
export const getCustomer = (id) => api.get(`customers/${id}/`);
export const createCustomer = (data) => api.post('customers/', data);
export const updateCustomer = (id, data) => api.put(`customers/${id}/`, data);
export const patchCustomer = (id, data) => api.patch(`customers/${id}/`, data);
export const deleteCustomer = (id) => api.delete(`customers/${id}/`);

// ─── Customer Custom Actions ──────────────────────────────────
export const restoreCustomer = (id) => api.post(`customers/${id}/restore/`);
export const searchCustomers = (query) => api.get('customers/search/', { params: { q: query } });

// ─── Customers by Organization ────────────────────────────────
export const getCustomersByOrganization = (organizationId) => 
  api.get('customers/', { params: { organization: organizationId } });

// ─── Default Export ──────────────────────────────────────────
export default {
  getCustomers,
  getCustomer,
  createCustomer,
  updateCustomer,
  patchCustomer,
  deleteCustomer,
  restoreCustomer,
  searchCustomers,
  getCustomersByOrganization,
};