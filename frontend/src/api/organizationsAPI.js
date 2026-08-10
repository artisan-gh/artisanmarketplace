import api from './api';

// ─── Organizations ──────────────────────────────────────────────
export const getOrganizations = (params) => api.get('organizations/', { params });
export const getOrganization = (id) => api.get(`organizations/${id}/`);
export const createOrganization = (data) => api.post('organizations/', data);
export const updateOrganization = (id, data) => api.put(`organizations/${id}/`, data);
export const patchOrganization = (id, data) => api.patch(`organizations/${id}/`, data);
export const deleteOrganization = (id) => api.delete(`organizations/${id}/`);

// ─── Organization Members ─────────────────────────────────────
export const getOrganizationMembers = (organizationId) => 
  api.get(`organizations/${organizationId}/members/`);
export const addOrganizationMember = (organizationId, data) => 
  api.post(`organizations/${organizationId}/members/add/`, data);

// ─── Organization Invites ─────────────────────────────────────
export const getOrganizationInvites = (organizationId) => 
  api.get(`organizations/${organizationId}/invites/`);
export const createOrganizationInvite = (organizationId, data) => 
  api.post(`organizations/${organizationId}/invites/create/`, data);

// ─── Memberships (CRUD) ──────────────────────────────────────
export const getMemberships = (params) => api.get('organizations/members/', { params });
export const getMembership = (id) => api.get(`organizations/members/${id}/`);
export const createMembership = (data) => api.post('organizations/members/', data);
export const updateMembership = (id, data) => api.put(`organizations/members/${id}/`, data);
export const patchMembership = (id, data) => api.patch(`organizations/members/${id}/`, data);
export const deleteMembership = (id) => api.delete(`organizations/members/${id}/`);

// ─── Invites (CRUD) ───────────────────────────────────────────
export const getInvites = (params) => api.get('organizations/invites/', { params });
export const getInvite = (id) => api.get(`organizations/invites/${id}/`);
export const createInvite = (data) => api.post('organizations/invites/', data);
export const deleteInvite = (id) => api.delete(`organizations/invites/${id}/`);

// ─── Invite Actions ───────────────────────────────────────────
export const acceptInvite = (id) => api.post(`organizations/invites/${id}/accept/`);
export const rejectInvite = (id) => api.post(`organizations/invites/${id}/reject/`);

// ─── Convenience ─────────────────────────────────────────────
export const inviteUserToOrganization = (organizationId, email, role = 'MEMBER') => {
  return createOrganizationInvite(organizationId, { email, role });
};

// ─── Default Export ──────────────────────────────────────────
export default {
  // Organizations
  getOrganizations,
  getOrganization,
  createOrganization,
  updateOrganization,
  patchOrganization,
  deleteOrganization,
  
  // Organization Members
  getOrganizationMembers,
  addOrganizationMember,
  
  // Organization Invites
  getOrganizationInvites,
  createOrganizationInvite,
  
  // Memberships
  getMemberships,
  getMembership,
  createMembership,
  updateMembership,
  patchMembership,
  deleteMembership,
  
  // Invites
  getInvites,
  getInvite,
  createInvite,
  deleteInvite,
  
  // Invite Actions
  acceptInvite,
  rejectInvite,
  
  // Convenience
  inviteUserToOrganization,
};