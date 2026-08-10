import api from './api';

/**
 * Analytics API Client
 * Provides access to advanced KPIs and metrics.
 * All endpoints are read‑only.
 */

// ─── KPIs ─────────────────────────────────────────────────────

/**
 * Get advanced KPIs with optional date range.
 * @param {Object} params - Query parameters
 * @param {number} params.days - Number of days to look back (default: 30)
 * @returns {Promise} KPI data for dashboards and charts
 */
export const getKPIs = (params = {}) =>
  api.get('/analytics/kpis/', { params });

// ─── Convenience Helpers ─────────────────────────────────────

/**
 * Get KPIs for a specific number of days.
 * @param {number} days - Number of days (e.g., 7, 30, 90)
 * @returns {Promise}
 */
export const getKPIsForDays = (days) =>
  getKPIs({ days });

/**
 * Get KPIs for the last 7 days.
 * @returns {Promise}
 */
export const getWeeklyKPIs = () =>
  getKPIs({ days: 7 });

/**
 * Get KPIs for the last 30 days.
 * @returns {Promise}
 */
export const getMonthlyKPIs = () =>
  getKPIs({ days: 30 });

/**
 * Get KPIs for the last 90 days.
 * @returns {Promise}
 */
export const getQuarterlyKPIs = () =>
  getKPIs({ days: 90 });

// ─── Default Export ──────────────────────────────────────────

export default {
  getKPIs,
  getKPIsForDays,
  getWeeklyKPIs,
  getMonthlyKPIs,
  getQuarterlyKPIs,
};