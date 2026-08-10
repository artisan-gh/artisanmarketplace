import api from './api';

// ─── Call Logs ──────────────────────────────────────────────────
export const getCallLogs = (params) => api.get('call-center/call-logs/', { params });
export const getCallLog = (id) => api.get(`call-center/call-logs/${id}/`);
export const createCallLog = (data) => api.post('call-center/call-logs/', data);
export const updateCallLog = (id, data) => api.put(`call-center/call-logs/${id}/`, data);
export const patchCallLog = (id, data) => api.patch(`call-center/call-logs/${id}/`, data);
export const deleteCallLog = (id) => api.delete(`call-center/call-logs/${id}/`);

// ─── Call Log Custom Actions ──────────────────────────────────
export const endCall = (id) => api.post(`call-center/call-logs/${id}/end-call/`);
export const missCall = (id) => api.post(`call-center/call-logs/${id}/miss/`);
export const cancelCall = (id) => api.post(`call-center/call-logs/${id}/cancel/`);
export const scheduleFollowUp = (id, data) => api.post(`call-center/call-logs/${id}/schedule-followup/`, data);
export const getMyCalls = () => api.get('call-center/call-logs/my-calls/');
export const getTodayCalls = () => api.get('call-center/call-logs/today/');
export const getPendingFollowUps = () => api.get('call-center/call-logs/pending-followup/');

// ─── Default Export ──────────────────────────────────────────
export default {
  getCallLogs,
  getCallLog,
  createCallLog,
  updateCallLog,
  patchCallLog,
  deleteCallLog,
  endCall,
  missCall,
  cancelCall,
  scheduleFollowUp,
  getMyCalls,
  getTodayCalls,
  getPendingFollowUps,
};