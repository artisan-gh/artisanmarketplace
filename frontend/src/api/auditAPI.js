// src/api/auditAPI.js
import api from './api';

/**
 * Audit API Client
 * Provides access to audit logs.
 * All endpoints are read‑only and require staff/admin permissions.
 */

// ─── Audit Logs ───────────────────────────────────────────────

/**
 * Get a list of audit logs with optional filters.
 * @param {Object} params - Query parameters (see below)
 * @param {string} params.user - User UUID
 * @param {string} params.action - Action type (CREATE, UPDATE, DELETE, etc.)
 * @param {string} params.severity - Severity (LOW, MEDIUM, HIGH, CRITICAL)
 * @param {string} params.module - App module name (e.g., 'incidents')
 * @param {string} params.created_at_after - ISO date (e.g., 2026-07-01T00:00:00Z)
 * @param {string} params.created_at_before - ISO date
 * @param {boolean} params.success - true/false
 * @param {boolean} params.archived - true/false
 * @param {string} params.search - Search term (searches user email, module, object_repr, description)
 * @param {string} params.ordering - Field ordering (e.g., '-created_at')
 * @param {number} params.page - Page number
 * @param {number} params.page_size - Items per page
 * @returns {Promise} Paginated list of audit logs
 */
export const getAuditLogs = (params = {}) =>
  api.get('/audit/logs/', { params });

/**
 * Get a single audit log by ID.
 * @param {string} id - Audit log UUID
 * @returns {Promise} Audit log detail
 */
export const getAuditLog = (id) =>
  api.get(`/audit/logs/${id}/`);

/**
 * Export audit logs as CSV.
 * @param {Object} params - Same filters as getAuditLogs
 * @returns {Promise<Blob>} CSV file blob
 */
export const exportAuditLogs = (params = {}) =>
  api.get('/audit/export/', { params, responseType: 'blob' });

// ─── Convenience Helpers ──────────────────────────────────────

/**
 * Get audit logs for a specific user.
 * @param {string} userId - User UUID
 * @param {Object} extraParams - Additional query params
 * @returns {Promise}
 */
export const getAuditLogsByUser = (userId, extraParams = {}) =>
  getAuditLogs({ user: userId, ...extraParams });

/**
 * Get audit logs for a specific module.
 * @param {string} module - Module name (e.g., 'incidents')
 * @param {Object} extraParams - Additional query params
 * @returns {Promise}
 */
export const getAuditLogsByModule = (module, extraParams = {}) =>
  getAuditLogs({ module, ...extraParams });

/**
 * Get audit logs for a specific action.
 * @param {string} action - Action type (e.g., 'CREATE', 'UPDATE')
 * @param {Object} extraParams - Additional query params
 * @returns {Promise}
 */
export const getAuditLogsByAction = (action, extraParams = {}) =>
  getAuditLogs({ action, ...extraParams });

/**
 * Get failed audit logs (success=false).
 * @param {Object} params - Additional query params
 * @returns {Promise}
 */
export const getFailedAuditLogs = (params = {}) =>
  getAuditLogs({ success: false, ...params });

/**
 * Get successful audit logs (success=true).
 * @param {Object} params - Additional query params
 * @returns {Promise}
 */
export const getSuccessfulAuditLogs = (params = {}) =>
  getAuditLogs({ success: true, ...params });

/**
 * Get high severity logs.
 * @param {Object} params - Additional query params
 * @returns {Promise}
 */
export const getHighSeverityLogs = (params = {}) =>
  getAuditLogs({ severity: 'HIGH', ...params });

/**
 * Get critical severity logs.
 * @param {Object} params - Additional query params
 * @returns {Promise}
 */
export const getCriticalSeverityLogs = (params = {}) =>
  getAuditLogs({ severity: 'CRITICAL', ...params });

/**
 * Get today's audit logs.
 * @param {Object} extraParams - Additional query params
 * @returns {Promise}
 */
export const getTodayAuditLogs = (extraParams = {}) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return getAuditLogs({
    created_at_after: today.toISOString(),
    ...extraParams,
  });
};

/**
 * Get audit logs for a specific date range.
 * @param {Date|string} from - Start date
 * @param {Date|string} to - End date
 * @param {Object} extraParams - Additional query params
 * @returns {Promise}
 */
export const getAuditLogsByDateRange = (from, to, extraParams = {}) => {
  const fromDate = new Date(from);
  const toDate = new Date(to);
  toDate.setHours(23, 59, 59, 999);
  return getAuditLogs({
    created_at_after: fromDate.toISOString(),
    created_at_before: toDate.toISOString(),
    ...extraParams,
  });
};

/**
 * Get recent audit logs (last N days).
 * @param {number} days - Number of days to look back
 * @param {Object} extraParams - Additional query params
 * @returns {Promise}
 */
export const getRecentAuditLogs = (days = 7, extraParams = {}) => {
  const from = new Date();
  from.setDate(from.getDate() - days);
  return getAuditLogs({
    created_at_after: from.toISOString(),
    ...extraParams,
  });
};

// ─── Default Export ──────────────────────────────────────────

export default {
  getAuditLogs,
  getAuditLog,
  exportAuditLogs,
  getAuditLogsByUser,
  getAuditLogsByModule,
  getAuditLogsByAction,
  getFailedAuditLogs,
  getSuccessfulAuditLogs,
  getHighSeverityLogs,
  getCriticalSeverityLogs,
  getTodayAuditLogs,
  getAuditLogsByDateRange,
  getRecentAuditLogs,
};