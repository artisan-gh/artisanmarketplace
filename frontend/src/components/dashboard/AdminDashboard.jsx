// src/components/dashboard/AdminDashboard.jsx
import { useQuery } from '@tanstack/react-query';

import { getDashboardSummary } from '../../api/dashboardAPI';
import { getBreachedSLAs, getAtRiskSLAs } from '../../api/slaAPI';
import { BillingWidget } from '../billing/BillingWidget';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import './Admindashboard.css';

// ─── Real API functions ──────────────────────────────────────
import { getArtisans } from '../../api/artisansAPI';
import { getCustomers } from '../../api/customersAPI';
import { useAuth } from "../../context/AuthContext";
import { Link, useNavigate } from "react-router-dom";

// ─── Icons ──────────────────────────────────────────────────
import { FaFileInvoice, FaPlusCircle } from 'react-icons/fa'; // <-- added

const COLORS = ['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#8b5cf6'];

// ─── Priority label mapping ──────────────────────────────────
const PRIORITY_NAMES = {
  1: 'Low',
  2: 'Medium',
  3: 'High',
  4: 'Critical',
  5: 'Urgent',
};

const getPriorityLabel = (value) => {
  if (value === undefined || value === null) return 'Unknown';
  if (typeof value === 'number') {
    return PRIORITY_NAMES[value] || `Priority ${value}`;
  }
  if (typeof value === 'string') {
    return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
  }
  return String(value);
};

// ─── Shared dark styling for Recharts ─────────────────────────
const AXIS_TICK = { fill: '#94a3b8', fontSize: 12 };
const AXIS_LINE = { stroke: 'rgba(255,255,255,0.09)' };
const GRID_STROKE = 'rgba(255,255,255,0.06)';
const TOOLTIP_STYLE = {
  contentStyle: {
    background: '#131a2c',
    border: '1px solid rgba(255,255,255,0.12)',
    borderRadius: '10px',
    fontSize: '0.8rem',
    color: '#f8fafc',
  },
  labelStyle: { color: '#cbd5e1' },
  itemStyle: { color: '#f8fafc' },
  cursor: { fill: 'rgba(255,255,255,0.04)' },
};

// ─── Icons ──────────────────────────────────────────────────
const IconClipboard = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="6" y="4" width="12" height="17" rx="2" />
    <path d="M9 4V3a1 1 0 011-1h4a1 1 0 011 1v1" />
    <path d="M9 11h6M9 15h6" />
  </svg>
);
const IconFolderOpen = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v1H5" />
    <path d="M3 8l1.5 10a2 2 0 002 2h11a2 2 0 002-2L21 9H5" />
  </svg>
);
const IconCheckCircle = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M8.5 12.5l2.5 2.5 5-5" />
  </svg>
);
const IconClock = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3.5 2" />
  </svg>
);
const IconAlertTriangle = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M12 3l10 18H2L12 3z" />
    <path d="M12 10v4M12 17.5h.01" />
  </svg>
);
const IconAlertOctagon = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M7.86 2h8.28L22 7.86v8.28L16.14 22H7.86L2 16.14V7.86L7.86 2z" />
    <path d="M12 8v5M12 16.5h.01" />
  </svg>
);
const IconGauge = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M12 20a8 8 0 10-8-8" />
    <path d="M12 12l3-4" />
    <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none" />
  </svg>
);
const IconLogout = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </svg>
);
const IconUser = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);
const IconUsers = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 00-3-3.87" />
    <path d="M16 3.13a4 4 0 010 7.75" />
  </svg>
);

// ─── Helpers ──────────────────────────────────────────────
const rateColor = (percent) => {
  if (percent >= 70) return { color: '#22c55e', soft: 'rgba(34, 197, 94, 0.12)' };
  if (percent >= 40) return { color: '#eab308', soft: 'rgba(234, 179, 8, 0.12)' };
  return { color: '#ef4444', soft: 'rgba(239, 68, 68, 0.12)' };
};

const StatCard = ({ icon: Icon, color, value, label, secondaryLabel, secondaryValue }) => (
  <div className="stat-card">
    <div className="stat-card__icon-wrap" style={{ '--stat-color': color }}>
      <Icon className="stat-card__icon" />
    </div>
    <div className="stat-card__body">
      <div className="stat-card__value">{value}</div>
      <div className="stat-card__label">{label}</div>
      {secondaryLabel && (
        <div className="stat-card__secondary">
          <span className="stat-card__secondary-label">{secondaryLabel}</span>
          <span className="stat-card__secondary-value">{secondaryValue}</span>
        </div>
      )}
    </div>
  </div>
);

const RatePanel = ({ label, percent, subtitle }) => {
  const { color, soft } = rateColor(percent);
  const clamped = Math.min(100, Math.max(0, percent));
  return (
    <div className="progress-panel">
      <div className="progress-panel__top">
        <div>
          <p className="progress-panel__label">{label}</p>
          <p className="progress-panel__value">{percent}%</p>
          <p className="progress-panel__subtitle">{subtitle}</p>
        </div>
        <div className="progress-panel__badge" style={{ '--rate-color': color, '--rate-soft': soft }}>
          <IconGauge />
        </div>
      </div>
      <div className="progress-panel__track">
        <div className="progress-panel__fill" style={{ width: `${clamped}%`, '--rate-color': color }} />
        <div className="progress-panel__dot" style={{ left: `${clamped}%`, '--rate-color': color }} />
      </div>
    </div>
  );
};

export const AdminDashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  // ─── Handle logout ────────────────────────────────────────
  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  // ─── Main Dashboard Data ──────────────────────────────────
  const {
    data: dashboardData,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: async () => {
      const res = await getDashboardSummary();
      return res.data || res;
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  // ─── SLA Data ──────────────────────────────────────────────
  const {
    data: breachesRaw,
    error: breachesError,
  } = useQuery({
    queryKey: ['slaBreaches'],
    queryFn: async () => {
      const res = await getBreachedSLAs();
      return res.data || res;
    },
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  const {
    data: atRiskRaw,
    error: atRiskError,
  } = useQuery({
    queryKey: ['slaAtRisk'],
    queryFn: async () => {
      const res = await getAtRiskSLAs();
      return res.data || res;
    },
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  // ─── Real Artisans count ──────────────────────────────────
  const {
    data: artisansData,
    isLoading: artisansLoading,
    error: artisansError,
  } = useQuery({
    queryKey: ['allArtisans'],
    queryFn: async () => {
      const res = await getArtisans({ page_size: 1000 });
      return res.results || res || [];
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  // ─── Real Customers count ──────────────────────────────────
  const {
    data: customersData,
    isLoading: customersLoading,
    error: customersError,
  } = useQuery({
    queryKey: ['allCustomers'],
    queryFn: async () => {
      const res = await getCustomers({ page_size: 1000 });
      return res.data?.results || res.results || res.data || res || [];
    },
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  // ─── Data extraction ──────────────────────────────────────
  const data = dashboardData || {};
  const summary = data.summary || {};
  const distribution = data.distribution || {};
  const trends = data.trends || {};
  const user = data.user || {};
  const sla = data.sla || {};
  const performance = data.performance || {};

  const breaches = Array.isArray(breachesRaw)
    ? breachesRaw
    : breachesRaw?.results || breachesRaw?.data || [];

  const atRisk = Array.isArray(atRiskRaw)
    ? atRiskRaw
    : atRiskRaw?.results || atRiskRaw?.data || [];

  // ─── User counts (real) ────────────────────────────────────
  const artisans = Array.isArray(artisansData) ? artisansData : [];
  const customers = Array.isArray(customersData) ? customersData : [];

  const totalArtisans = artisans.length;
  const totalCustomers = customers.length;

  // ─── Derived values ──────────────────────────────────────
  const avatarUrl = user.profile_picture || null;
  const fullName = user.full_name || 'Administrator';
  const email = user.email || '';
  const role = user.role || 'Administrator';

  const breachCount = breaches.length;
  const atRiskCount = atRisk.length;
  const totalIncidents = summary.total_incidents || 0;
  const resolvedIncidents = summary.resolved_incidents || 0;

  const slaCompliance =
    sla?.compliance_percent !== undefined
      ? sla.compliance_percent
      : totalIncidents > 0
      ? Math.round(((totalIncidents - breachCount) / totalIncidents) * 100)
      : 100;

  const resolutionRate =
    totalIncidents > 0 ? Math.round((resolvedIncidents / totalIncidents) * 100) : 0;

  const pctOfTotal = (count) =>
    totalIncidents > 0 ? `${Math.round((count / totalIncidents) * 100)}% of total` : '—';

  // ─── Loading ─────────────────────────────────────────────
  const isLoading = dashboardLoading || artisansLoading || customersLoading;

  if (isLoading) {
    return (
      <div className="admin-dashboard">
        <div className="profile-skeleton" />
        <div className="stat-grid">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="stat-skeleton" />
          ))}
        </div>
        <div className="panel-skeleton" />
      </div>
    );
  }

  // ─── Error ────────────────────────────────────────────────
  if (dashboardError || breachesError || atRiskError || artisansError || customersError) {
    const errMsg =
      dashboardError?.message ||
      breachesError?.message ||
      atRiskError?.message ||
      artisansError?.message ||
      customersError?.message ||
      'Unknown error';
    console.error('[Dashboard] Error:', { dashboardError, breachesError, atRiskError, artisansError, customersError });
    return (
      <div className="admin-dashboard">
        <div className="state-banner state-banner--error">
          <IconAlertOctagon className="state-banner__icon" />
          <div>
            <p>Couldn&apos;t load your dashboard.</p>
            <p className="state-banner__detail">{errMsg}</p>
            <p className="state-banner__hint">Check the console for more details.</p>
          </div>
        </div>
      </div>
    );
  }

  // ─── Render ──────────────────────────────────────────────
  return (
    <div className="admin-dashboard">
      {/* ─── Header ─────────────────────────────────────────── */}
      <header className="dashboard-header">
        <div className="agent-profile">
          <div className="agent-profile__avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt={fullName} />
            ) : (
              <div className="agent-profile__initial">{fullName.charAt(0).toUpperCase()}</div>
            )}
          </div>
          <div className="agent-profile__info">
            <h2 className="agent-profile__name">{fullName}</h2>
            <div className="agent-profile__meta">
              <span className="agent-profile__role">{role}</span>
              {email && (
                <>
                  <span className="agent-profile__dot" aria-hidden="true" />
                  <span className="agent-profile__email">{email}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="admin-dashboard__header">
          <h1>Admin Dashboard</h1>
          <p>Incident operations, SLA performance and billing at a glance</p>
        </div>

        <div className="admin-dashboard__actions">
          {/* ─── Invoices button ────────────────────────────── */}
          <Link to="/billing/invoices" className="btn btn-primary">
            <FaFileInvoice className="btn-icon" />
            Invoices
          </Link>
          <Link to="/billing/invoices/new" className="btn btn-success">
            <FaPlusCircle className="btn-icon" />
            New Invoice
          </Link>
          <button type="button" onClick={handleLogout} className="logout-btn">
            <IconLogout className="logout-btn__icon" />
            Sign out
          </button>
        </div>
      </header>

      {/* ─── Stat Cards (8 cards in 4×2 grid) ─────────────── */}
      <div className="stat-grid">
        <StatCard
          icon={IconClipboard}
          color="#3b82f6"
          value={totalIncidents}
          label="Total incidents"
        />
        <StatCard
          icon={IconFolderOpen}
          color="#eab308"
          value={summary.open_incidents || 0}
          label="Open incidents"
        />
        <StatCard
          icon={IconCheckCircle}
          color="#22c55e"
          value={resolvedIncidents}
          label="Resolved today"
        />
        <StatCard
          icon={IconClock}
          color="#ef4444"
          value={summary.pending_assignments || 0}
          label="Pending assignments"
        />
        <StatCard
          icon={IconAlertTriangle}
          color="#eab308"
          value={atRiskCount}
          label="At risk"
          secondaryLabel="Share of total"
          secondaryValue={pctOfTotal(atRiskCount)}
        />
        <StatCard
          icon={IconAlertOctagon}
          color="#ef4444"
          value={breachCount}
          label="Breached"
          secondaryLabel="Share of total"
          secondaryValue={pctOfTotal(breachCount)}
        />
        <StatCard
          icon={IconUsers}
          color="#8b5cf6"
          value={totalArtisans}
          label="Total artisans"
        />
        <StatCard
          icon={IconUser}
          color="#06b6d4"
          value={totalCustomers}
          label="Total customers"
        />
      </div>

      {/* ─── Rate Panels ─────────────────────────────────────── */}
      <div className="progress-grid">
        <RatePanel
          label="Incident Resolution Rate"
          percent={resolutionRate}
          subtitle={`${resolvedIncidents} of ${totalIncidents} incidents resolved`}
        />
        <RatePanel
          label="SLA Compliance Rate"
          percent={slaCompliance}
          subtitle={`${Math.max(totalIncidents - breachCount, 0)} of ${totalIncidents} incidents within SLA`}
        />
      </div>

      {/* ─── Billing Widget ───────────────────────────────────── */}
      <div className="billing-widget-wrap">
        <BillingWidget />
      </div>

      {/* ─── Breached Incidents List ────────────────────────── */}
      {breachCount > 0 && (
        <div className="panel">
          <div className="panel__header">
            <h3 className="panel__title">Breached incidents</h3>
            <span className="panel__count">{breachCount}</span>
          </div>
          <div className="breach-list">
            {breaches.slice(0, 5).map((item, idx) => (
              <div key={item.incident || idx} className="breach-row">
                <span className="breach-row__ref">
                  {item.incident_number || item.incident || 'N/A'}
                </span>
                <span className="breach-row__status">Breached</span>
              </div>
            ))}
            {breachCount > 5 && (
              <p className="breach-row__more">+ {breachCount - 5} more breaches</p>
            )}
          </div>
        </div>
      )}

      {/* ─── Charts ──────────────────────────────────────────── */}
      <div className="panel-grid">
        <div className="panel">
          <h3 className="panel__title">Incident trend (last 30 days)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trends.incidents_daily || []}>
              <CartesianGrid stroke={GRID_STROKE} vertical={false} />
              <XAxis dataKey="day" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#60a5fa"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <h3 className="panel__title">Call volume (last 30 days)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trends.calls_daily || []}>
              <CartesianGrid stroke={GRID_STROKE} vertical={false} />
              <XAxis dataKey="day" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#a78bfa"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* ─── Incidents by priority ────────────────────────── */}
        <div className="panel">
          <h3 className="panel__title">Incidents by priority</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={distribution.priority || []}
                dataKey="count"
                nameKey="priority"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={({ priority }) => getPriorityLabel(priority)}
                labelLine={false}
              >
                {(distribution.priority || []).map((entry, index) => (
                  <Cell
                    key={index}
                    fill={COLORS[index % COLORS.length]}
                    stroke="#0a0e1a"
                    strokeWidth={2}
                  />
                ))}
              </Pie>
              <Tooltip
                {...TOOLTIP_STYLE}
                formatter={(value, name, props) => {
                  const label = getPriorityLabel(props.payload.priority);
                  return [value, label];
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* ─── Incidents by status ──────────────────────────── */}
        <div className="panel">
          <h3 className="panel__title">Incidents by status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={distribution.status || []}>
              <CartesianGrid stroke={GRID_STROKE} vertical={false} />
              <XAxis
                dataKey="status__name"
                tick={AXIS_TICK}
                axisLine={AXIS_LINE}
                tickLine={false}
              />
              <YAxis tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── Top Artisans ────────────────────────────────────── */}
      <div className="panel">
        <h3 className="panel__title">Top artisans (completion rate)</h3>
        {performance.top_artisans?.length > 0 ? (
          <div className="panel-table-wrap">
            <table className="panel-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Total assignments</th>
                  <th>Completed</th>
                  <th>Rate</th>
                </tr>
              </thead>
              <tbody>
                {performance.top_artisans.map((artisan, idx) => (
                  <tr key={idx}>
                    <td>{artisan.name}</td>
                    <td>{artisan.total}</td>
                    <td>{artisan.completed}</td>
                    <td>
                      <span
                        className="rate-pill"
                        style={{ '--rate-color': rateColor(artisan.rate).color }}
                      >
                        {artisan.rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="panel-empty">No artisan data yet.</p>
        )}
      </div>
    </div>
  );
};