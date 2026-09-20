// src/components/dashboard/AdminDashboard.jsx
import { useQuery } from '@tanstack/react-query';
import { getDashboardSummary } from '../../api/dashboardAPI';
import { getBreachedSLAs, getAtRiskSLAs } from '../../api/slaAPI';
import { BillingWidget } from '../billing/BillingWidget';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import './Admindashboard.css';

import { getArtisans } from '../../api/artisansAPI';
import { getCustomers } from '../../api/customersAPI';
import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { FaFileInvoice, FaPlusCircle } from 'react-icons/fa';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const PRIORITY_NAMES = {
  1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical', 5: 'Urgent',
};

const getPriorityLabel = (value) => {
  if (value === undefined || value === null) return 'Unknown';
  if (typeof value === 'number') return PRIORITY_NAMES[value] || `Priority ${value}`;
  if (typeof value === 'string') return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
  return String(value);
};

const AXIS_TICK = { fill: '#94a3b8', fontSize: 12 };
const AXIS_LINE = { stroke: 'rgba(148, 163, 184, 0.25)' };
const GRID_STROKE = 'rgba(148, 163, 184, 0.15)';
const TOOLTIP_STYLE = {
  contentStyle: {
    background: '#ffffff',
    border: '1px solid #e6e9f2',
    borderRadius: '12px',
    fontSize: '0.8rem',
    color: '#0f172a',
    boxShadow: '0 12px 30px -10px rgba(15, 23, 42, 0.18)',
  },
  labelStyle: { color: '#64748b', fontWeight: 600 },
  itemStyle: { color: '#0f172a' },
  cursor: { fill: 'rgba(99, 102, 241, 0.06)' },
};

/* ─── Icons ──────────────────────────────────────────────── */
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

/* ─── Helpers ────────────────────────────────────────────── */
const rateColor = (percent) => {
  if (percent >= 70) return { color: '#10b981', soft: 'rgba(16, 185, 129, 0.12)' };
  if (percent >= 40) return { color: '#f59e0b', soft: 'rgba(245, 158, 11, 0.12)' };
  return { color: '#ef4444', soft: 'rgba(239, 68, 68, 0.12)' };
};

const StatCard = ({ icon: Icon, color, value, label, secondaryLabel, secondaryValue }) => (
  <div className="am-stat" style={{ '--stat-color': color }}>
    <div className="am-stat__top">
      <div className="am-stat__icon">
        <Icon />
      </div>
    </div>
    <div className="am-stat__value">{value}</div>
    <div className="am-stat__label">{label}</div>
    {secondaryLabel && (
      <div className="am-stat__secondary">
        <span>{secondaryLabel}</span>
        <strong>{secondaryValue}</strong>
      </div>
    )}
  </div>
);

const RatePanel = ({ label, percent, subtitle }) => {
  const { color, soft } = rateColor(percent);
  const clamped = Math.min(100, Math.max(0, percent));
  return (
    <div className="am-rate" style={{ '--rate-color': color, '--rate-soft': soft }}>
      <div className="am-rate__head">
        <div>
          <p className="am-rate__label">{label}</p>
          <p className="am-rate__value">
            {percent}
            <span>%</span>
          </p>
          <p className="am-rate__subtitle">{subtitle}</p>
        </div>
        <div className="am-rate__badge">
          <IconGauge />
        </div>
      </div>
      <div className="am-rate__track">
        <div className="am-rate__fill" style={{ width: `${clamped}%` }} />
        <div className="am-rate__dot" style={{ left: `${clamped}%` }} />
      </div>
    </div>
  );
};

export const AdminDashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

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

  const { data: breachesRaw, error: breachesError } = useQuery({
    queryKey: ['slaBreaches'],
    queryFn: async () => {
      const res = await getBreachedSLAs();
      return res.data || res;
    },
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  const { data: atRiskRaw, error: atRiskError } = useQuery({
    queryKey: ['slaAtRisk'],
    queryFn: async () => {
      const res = await getAtRiskSLAs();
      return res.data || res;
    },
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

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

  const artisans = Array.isArray(artisansData) ? artisansData : [];
  const customers = Array.isArray(customersData) ? customersData : [];

  const totalArtisans = artisans.length;
  const totalCustomers = customers.length;

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

  const isLoading = dashboardLoading || artisansLoading || customersLoading;

  if (isLoading) {
    return (
      <div className="am-dashboard">
        <div className="am-skeleton am-skeleton--header" />
        <div className="am-stat-grid">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="am-skeleton am-skeleton--stat" />
          ))}
        </div>
        <div className="am-skeleton am-skeleton--panel" />
      </div>
    );
  }

  if (dashboardError || breachesError || atRiskError || artisansError || customersError) {
    const errMsg =
      dashboardError?.message ||
      breachesError?.message ||
      atRiskError?.message ||
      artisansError?.message ||
      customersError?.message ||
      'Unknown error';
    console.error('[Dashboard] Error:', {
      dashboardError, breachesError, atRiskError, artisansError, customersError,
    });
    return (
      <div className="am-dashboard">
        <div className="am-state am-state--error">
          <IconAlertOctagon className="am-state__icon" />
          <div>
            <p className="am-state__title">Couldn&apos;t load your dashboard.</p>
            <p className="am-state__detail">{errMsg}</p>
            <p className="am-state__hint">Check the console for more details.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="am-dashboard">
      {/* ─── Header ─────────────────────────────────────────── */}
      <header className="am-header">
        <div className="am-header__profile">
          <div className="am-avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt={fullName} />
            ) : (
              <span>{fullName.charAt(0).toUpperCase()}</span>
            )}
          </div>
          <div className="am-header__info">
            <h2>{fullName}</h2>
            <div className="am-header__meta">
              <span className="am-badge am-badge--role">{role}</span>
              {email && <span className="am-header__email">{email}</span>}
            </div>
          </div>
        </div>

        <div className="am-header__title">
          <span className="am-eyebrow">Overview</span>
          <h1>Admin Dashboard</h1>
          <p>Incident operations, SLA performance and billing at a glance</p>
        </div>

        <div className="am-header__actions">
          <Link to="/billing/invoices" className="am-btn am-btn--ghost">
            <FaFileInvoice className="am-btn__icon" />
            Invoices
          </Link>
          <Link to="/billing/invoices/new" className="am-btn am-btn--primary">
            <FaPlusCircle className="am-btn__icon" />
            New Invoice
          </Link>
          <button type="button" onClick={handleLogout} className="am-btn am-btn--danger">
            <IconLogout className="am-btn__icon" />
            Sign out
          </button>
        </div>
      </header>

      {/* ─── Stat Cards ─────────────────────────────────────── */}
      <section className="am-stat-grid">
        <StatCard icon={IconClipboard} color="#6366f1" value={totalIncidents} label="Total incidents" />
        <StatCard icon={IconFolderOpen} color="#f59e0b" value={summary.open_incidents || 0} label="Open incidents" />
        <StatCard icon={IconCheckCircle} color="#10b981" value={resolvedIncidents} label="Resolved today" />
        <StatCard icon={IconClock} color="#ef4444" value={summary.pending_assignments || 0} label="Pending assignments" />
        <StatCard
          icon={IconAlertTriangle}
          color="#f59e0b"
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
        <StatCard icon={IconUsers} color="#8b5cf6" value={totalArtisans} label="Total artisans" />
        <StatCard icon={IconUser} color="#06b6d4" value={totalCustomers} label="Total customers" />
      </section>

      {/* ─── Rate Panels ────────────────────────────────────── */}
      <section className="am-rate-grid">
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
      </section>

      {/* ─── Billing Widget ─────────────────────────────────── */}
      <section className="am-panel am-panel--billing">
        <div className="am-panel__header">
          <div>
            <span className="am-panel__eyebrow">Finance</span>
            <h3 className="am-panel__title">Billing overview</h3>
          </div>
        </div>
        <BillingWidget />
      </section>

      {/* ─── Breached Incidents ─────────────────────────────── */}
      {breachCount > 0 && (
        <section className="am-panel">
          <div className="am-panel__header">
            <div>
              <span className="am-panel__eyebrow am-panel__eyebrow--danger">Attention</span>
              <h3 className="am-panel__title">Breached incidents</h3>
            </div>
            <span className="am-count am-count--danger">{breachCount}</span>
          </div>
          <ul className="am-breach-list">
            {breaches.slice(0, 5).map((item, idx) => (
              <li key={item.incident || idx} className="am-breach-row">
                <span className="am-breach-row__dot" />
                <span className="am-breach-row__ref">
                  {item.incident_number || item.incident || 'N/A'}
                </span>
                <span className="am-breach-row__status">Breached</span>
              </li>
            ))}
          </ul>
          {breachCount > 5 && (
            <p className="am-breach-more">+ {breachCount - 5} more breaches</p>
          )}
        </section>
      )}

      {/* ─── Charts ─────────────────────────────────────────── */}
      <section className="am-panel-grid">
        <div className="am-panel">
          <div className="am-panel__header">
            <div>
              <span className="am-panel__eyebrow">Trend</span>
              <h3 className="am-panel__title">Incident trend · 30 days</h3>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trends.incidents_daily || []}>
              <defs>
                <linearGradient id="amIncidentStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={GRID_STROKE} vertical={false} />
              <XAxis dataKey="day" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Line
                type="monotone"
                dataKey="count"
                stroke="url(#amIncidentStroke)"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5, fill: '#6366f1', stroke: '#fff', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="am-panel">
          <div className="am-panel__header">
            <div>
              <span className="am-panel__eyebrow">Volume</span>
              <h3 className="am-panel__title">Call volume · 30 days</h3>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trends.calls_daily || []}>
              <defs>
                <linearGradient id="amCallStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#fbbf24" />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={GRID_STROKE} vertical={false} />
              <XAxis dataKey="day" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Line
                type="monotone"
                dataKey="count"
                stroke="url(#amCallStroke)"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5, fill: '#f59e0b', stroke: '#fff', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="am-panel">
          <div className="am-panel__header">
            <div>
              <span className="am-panel__eyebrow">Distribution</span>
              <h3 className="am-panel__title">Incidents by priority</h3>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={distribution.priority || []}
                dataKey="count"
                nameKey="priority"
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={82}
                paddingAngle={3}
                label={({ priority }) => getPriorityLabel(priority)}
                labelLine={false}
              >
                {(distribution.priority || []).map((entry, index) => (
                  <Cell
                    key={index}
                    fill={COLORS[index % COLORS.length]}
                    stroke="#ffffff"
                    strokeWidth={2}
                  />
                ))}
              </Pie>
              <Tooltip
                {...TOOLTIP_STYLE}
                formatter={(value, name, props) => [value, getPriorityLabel(props.payload.priority)]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="am-panel">
          <div className="am-panel__header">
            <div>
              <span className="am-panel__eyebrow">Breakdown</span>
              <h3 className="am-panel__title">Incidents by status</h3>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={distribution.status || []}>
              <defs>
                <linearGradient id="amBarFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#a5b4fc" />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={GRID_STROKE} vertical={false} />
              <XAxis
                dataKey="status__name"
                tick={AXIS_TICK}
                axisLine={AXIS_LINE}
                tickLine={false}
              />
              <YAxis tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Bar dataKey="count" fill="url(#amBarFill)" radius={[6, 6, 0, 0]} maxBarSize={48} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* ─── Top Artisans ───────────────────────────────────── */}
      <section className="am-panel">
        <div className="am-panel__header">
          <div>
            <span className="am-panel__eyebrow">Performance</span>
            <h3 className="am-panel__title">Top artisans · completion rate</h3>
          </div>
        </div>

        {performance.top_artisans?.length > 0 ? (
          <div className="am-table-wrap">
            <table className="am-table">
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
                    <td data-label="Name">
                      <span className="am-table__name">{artisan.name}</span>
                    </td>
                    <td data-label="Total assignments">{artisan.total}</td>
                    <td data-label="Completed">{artisan.completed}</td>
                    <td data-label="Rate">
                      <span
                        className="am-pill"
                        style={{ '--pill-color': rateColor(artisan.rate).color }}
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
          <p className="am-empty">No artisan data yet.</p>
        )}
      </section>
    </div>
  );
};