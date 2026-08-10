import api from './api';

export const getIncidentReport = (params) => api.get('reports/incidents/', { params });
export const getArtisanPerformance = (params) => api.get('reports/artisans/', { params });
export const getCallCenterReport = (params) => api.get('reports/calls/', { params });
export const exportReport = (params) => api.get('reports/export/', { params, responseType: 'blob' });

export default {
  getIncidentReport,
  getArtisanPerformance,
  getCallCenterReport,
  exportReport,
};