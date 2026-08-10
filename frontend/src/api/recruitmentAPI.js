import api from './axios';

/**
 * Recruitment API client
 */

// ─── Job Categories ─────────────────────────────────────────

export const getJobCategories = (params = {}) => api.get('/recruitment/categories/', { params });
export const getJobCategory = (id) => api.get(`/recruitment/categories/${id}/`);
export const createJobCategory = (data) => api.post('/recruitment/categories/', data);
export const updateJobCategory = (id, data) => api.put(`/recruitment/categories/${id}/`, data);
export const deleteJobCategory = (id) => api.delete(`/recruitment/categories/${id}/`);

// ─── Jobs ──────────────────────────────────────────────────

export const getJobs = (params = {}) => api.get('/recruitment/jobs/', { params });
export const getJob = (id) => api.get(`/recruitment/jobs/${id}/`);
export const createJob = (data) => api.post('/recruitment/jobs/', data);
export const updateJob = (id, data) => api.put(`/recruitment/jobs/${id}/`, data);
export const patchJob = (id, data) => api.patch(`/recruitment/jobs/${id}/`, data);
export const deleteJob = (id) => api.delete(`/recruitment/jobs/${id}/`);

// ─── Job Actions ──────────────────────────────────────────

export const applyToJob = (jobId, data) =>
  api.post(`/recruitment/jobs/${jobId}/apply/`, data);
export const saveJob = (jobId) =>
  api.post(`/recruitment/jobs/${jobId}/save_job/`);
export const unsaveJob = (jobId) =>
  api.post(`/recruitment/jobs/${jobId}/unsave_job/`);
export const incrementJobView = (jobId) =>
  api.post(`/recruitment/jobs/${jobId}/increment_view/`);
export const getMyJobs = () =>
  api.get('/recruitment/jobs/my_jobs/');

// ─── Applications ─────────────────────────────────────────

export const getApplications = (params = {}) =>
  api.get('/recruitment/applications/', { params });
export const getApplication = (id) =>
  api.get(`/recruitment/applications/${id}/`);
export const updateApplicationStatus = (id, status) =>
  api.post(`/recruitment/applications/${id}/update_status/`, { status });
export const getMyApplications = () =>
  api.get('/recruitment/applications/my_applications/');

// ─── Saved Jobs ───────────────────────────────────────────

export const getSavedJobs = (params = {}) =>
  api.get('/recruitment/saved/', { params });
export const deleteSavedJob = (id) =>
  api.delete(`/recruitment/saved/${id}/`);

// ─── Convenience ─────────────────────────────────────────

export const toggleJobStatus = (jobId, status) =>
  patchJob(jobId, { status });

// ─── Export all ──────────────────────────────────────────

export default {
  getJobCategories,
  getJobCategory,
  createJobCategory,
  updateJobCategory,
  deleteJobCategory,
  getJobs,
  getJob,
  createJob,
  updateJob,
  patchJob,
  deleteJob,
  applyToJob,
  saveJob,
  unsaveJob,
  incrementJobView,
  getMyJobs,
  getApplications,
  getApplication,
  updateApplicationStatus,
  getMyApplications,
  getSavedJobs,
  deleteSavedJob,
  toggleJobStatus,
};