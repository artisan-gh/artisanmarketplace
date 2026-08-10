import api from './axios';

/**
 * Companies API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getCompanies = (params = {}) => api.get('/companies/', { params });
export const getCompany = (id) => api.get(`/companies/${id}/`);
export const createCompany = (data) => api.post('/companies/', data);
export const updateCompany = (id, data) => api.put(`/companies/${id}/`, data);
export const patchCompany = (id, data) => api.patch(`/companies/${id}/`, data);
export const deleteCompany = (id) => api.delete(`/companies/${id}/`);

// ─── Current User ────────────────────────────────────────────

export const getMyCompanies = () => api.get('/companies/my_companies/');

// ─── Members ──────────────────────────────────────────────────

export const getCompanyMembers = (companyId) => api.get(`/companies/${companyId}/members/`);
export const addCompanyMember = (companyId, userId, role = 'MEMBER') =>
  api.post(`/companies/${companyId}/add_member/`, { user_id: userId, role });
export const removeCompanyMember = (companyId, userId) =>
  api.post(`/companies/${companyId}/remove_member/`, { user_id: userId });

// ─── Convenience ─────────────────────────────────────────────

export const toggleCompanyStatus = (companyId, active) =>
  patchCompany(companyId, { is_active: active });

// ─── Export all ──────────────────────────────────────────────

export default {
  getCompanies,
  getCompany,
  createCompany,
  updateCompany,
  patchCompany,
  deleteCompany,
  getMyCompanies,
  getCompanyMembers,
  addCompanyMember,
  removeCompanyMember,
  toggleCompanyStatus,
};