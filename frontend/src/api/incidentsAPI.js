// src/api/incidentsAPI.js
import api from './api';

// ─── Incidents ─────────────────────────────────────────────────
export const getIncidents = (params) =>
  api.get('incidents/', { params }).then((res) => res.data);

export const getIncident = (id) =>
  api.get(`incidents/${id}/`).then((res) => res.data);

export const createIncident = (data) =>
  api.post('incidents/', data).then((res) => res.data);

export const updateIncident = (id, data) =>
  api.put(`incidents/${id}/`, data).then((res) => res.data);

export const patchIncident = (id, data) =>
  api.patch(`incidents/${id}/`, data).then((res) => res.data);

export const deleteIncident = (id) =>
  api.delete(`incidents/${id}/`).then((res) => res.data);

// ─── Incident Custom Actions ──────────────────────────────────
export const assignIncident = (id, data) =>
  api.post(`incidents/${id}/assign/`, data).then((res) => res.data);

export const acceptIncident = (id) =>
  api.post(`incidents/${id}/accept/`).then((res) => res.data);

export const startIncident = (id) =>
  api.post(`incidents/${id}/start/`).then((res) => res.data);

export const completeIncident = (id) =>
  api.post(`incidents/${id}/complete/`).then((res) => res.data);

// ─── Default Export ──────────────────────────────────────────
export default {
  getIncidents,
  getIncident,
  createIncident,
  updateIncident,
  patchIncident,
  deleteIncident,
  assignIncident,
  acceptIncident,
  startIncident,
  completeIncident,
};