// src/components/dashboard/AgentDashboard.jsx
import { useQuery } from '@tanstack/react-query';
import { getAgentDashboard } from '../../api/dashboardAPI';
import { useNavigate } from "react-router-dom";
import { useAuth } from '../../context/AuthContext';
import './Agentdashboard.css';

// ─── Incident-focused icons ──────────────────────────────────
const IconIncident = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M12 2a10 10 0 11-10 10A10 10 0 0112 2z" />
    <path d="M12 6v8M12 18h.01" />
  </svg>
);
const IconCreated = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M7 3h7l4 4v14a1 1 0 01-1 1H7a1 1 0 01-1-1V4a1 1 0 011-1z" />
    <path d="M11 12h4M13 10v4" />
  </svg>
);
const IconAssigned = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 00-3-3.87" />
    <path d="M16 3.13a4 4 0 010 7.75" />
  </svg>
);
const IconOpen = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 6v6l4 2" />
  </svg>
);
const IconResolved = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M8.5 12.5l2.5 2.5 5-5" />
  </svg>
);
const IconCalendar = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="3" y="5" width="18" height="16" rx="2" />
    <path d="M8 3v4M16 3v4M3 10h18" />
  </svg>
);
const IconAlertCircle = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8v5M12 16h.01" />
  </svg>
);
const IconClipboard = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="6" y="4" width="12" height="17" rx="2" />
    <path d="M9 4V3a1 1 0 011-1h4a1 1 0 011 1v1" />
    <path d="M9 11h6M9 15h6" />
  </svg>
);
const IconLogout = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </svg>
);

// ─── Status → accent color (robust to unknown values) ────────
const STATUS_COLORS = {
  new: '#60a5fa',
  open: '#f59e0b',
  assigned: '#8b5cf6',
  in_progress: '#8b5cf6',
  'in progress': '#8b5cf6',
  resolved: '#22c55e',
  closed: '#22c55e',
  cancelled: '#f87171',
};
const getStatusColor = (status) =>
  STATUS_COLORS[(status || '').toLowerCase()] || '#94a3b8';

const StatCard = ({ icon: Icon, color, value, label }) => (
  <div className="stat-card">
    <div className="stat-card__icon-wrap" style={{ '--stat-color': color }}>
      <Icon className="stat-card__icon" />
    </div>
    <div className="stat-card__body">
      <div className="stat-card__value">{value}</div>
      <div className="stat-card__label">{label}</div>
    </div>
  </div>
);

export const AgentDashboard = () => {
  const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
      logout();
      navigate("/login", { replace: true });
    };

  const { data, isLoading, error } = useQuery({
    queryKey: ['agentDashboard'],
    queryFn: () => getAgentDashboard().then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <div className="agent-dashboard">
        <div className="profile-skeleton" />
        <div className="stat-grid">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="stat-skeleton" />
          ))}
        </div>
        <div className="panel-skeleton" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="agent-dashboard">
        <div className="state-banner state-banner--error">
          <IconAlertCircle className="state-banner__icon" />
          <p>Couldn&apos;t load your dashboard. Try refreshing the page.</p>
        </div>
      </div>
    );
  }

  const summary = data?.summary || {};
  const agent = data?.agent || {};
  const recentIncidents = data?.recent_incidents || [];

  // ─── Profile picture / name ──────────────────────────────
  const avatarUrl = agent.profile_picture || agent.avatar_url || null;
  const fullName = agent.full_name || agent.name || 'Agent';
  const role = agent.role || 'Call Center Agent';

  return (
    <div className="agent-dashboard">
      {/* ─── Header: profile + title ─────────────────────────── */}
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
              {agent.email && (
                <>
                  <span className="agent-profile__dot" aria-hidden="true" />
                  <span className="agent-profile__email">{agent.email}</span>
                </>
              )}
            </div>
          </div>
        </div>
        <h1 className="agent-dashboard__title">Agent Dashboard – Incidents</h1>
        <button type="button" onClick={handleLogout} className="logout-btn">
          <IconLogout className="logout-btn__icon" />
          Log out
        </button>
      </header>

      {/* ─── Incident Stats ──────────────────────────────────── */}
      <div className="stat-grid">
        <StatCard
          icon={IconCreated}
          color="#3b82f6"
          value={summary.total_incidents_created || 0}
          label="Incidents created"
        />
        <StatCard
          icon={IconCalendar}
          color="#6366f1"
          value={summary.incidents_created_today || 0}
          label="Created today"
        />
        <StatCard
          icon={IconIncident}
          color="#8b5cf6"
          value={summary.incidents_created_week || 0}
          label="Created this week"
        />
        <StatCard
          icon={IconAssigned}
          color="#eab308"
          value={summary.total_assigned || 0}
          label="Assigned to me"
        />
        <StatCard
          icon={IconOpen}
          color="#ef4444"
          value={summary.assigned_open || 0}
          label="Open (assigned)"
        />
        <StatCard
          icon={IconResolved}
          color="#22c55e"
          value={summary.assigned_resolved || 0}
          label="Resolved (assigned)"
        />
      </div>

      {/* ─── Recent Incidents ────────────────────────────────── */}
      <div className="panel">
        <div className="panel__header">
          <h3 className="panel__title">Recent Incidents</h3>
          <span className="panel__count">{recentIncidents.length}</span>
        </div>

        {recentIncidents.length > 0 ? (
          <ul className="call-list">
            {recentIncidents.map((inc) => (
              <li key={inc.id} className="call-row">
                <div className="call-row__ref">
                  <span className="call-row__link call-row__link--static">{inc.incident_number}</span>
                  <span className="call-row__customer">– {inc.title}</span>
                </div>
                <span className="call-row__time">
                  <span
                    className="status-pill"
                    style={{ '--status-color': getStatusColor(inc.status) }}
                  >
                    {inc.status}
                  </span>
                  <span className="call-row__date">
                    {new Date(inc.created_at).toLocaleString()}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="empty-state">
            <IconClipboard className="empty-state__icon" />
            <p>No recent incidents. New reports you create will show up here.</p>
          </div>
        )}
      </div>
    </div>
  );
};