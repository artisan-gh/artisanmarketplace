import api from './api';

export const getDashboardSummary = () => api.get('dashboard/summary/');
export const getAgentDashboard = () => api.get('dashboard/agent/');
export const getArtisanDashboard = () => api.get('dashboard/artisan/');
export const getSupervisorDashboard = () => api.get('dashboard/supervisor/');

export default {
  getDashboardSummary,
  getAgentDashboard,
  getArtisanDashboard,
  getSupervisorDashboard,
};