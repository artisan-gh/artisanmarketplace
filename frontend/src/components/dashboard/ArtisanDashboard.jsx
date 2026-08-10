// src/components/dashboard/ArtisanDashboard.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getArtisanDashboard } from '../../api/dashboardAPI';
import { acceptAssignment } from '../../api/assignmentsAPI';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Artisandashboard.css';

// ─── Icons ──────────────────────────────────────────────────
const IconClipboardList = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="6" y="4" width="12" height="17" rx="2" />
    <path d="M9 4V3a1 1 0 011-1h4a1 1 0 011 1v1" />
    <path d="M9 11h6M9 15h4" />
  </svg>
);
const IconClock = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3.5 2" />
  </svg>
);
const IconRefresh = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M4 4v6h6" />
    <path d="M20 20v-6h-6" />
    <path d="M5 14a8 8 0 0014.9 2M19 10A8 8 0 004.1 8" />
  </svg>
);
const IconCheckCircle = (props) => (
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
const IconGauge = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M12 20a8 8 0 10-8-8" />
    <path d="M12 12l3-4" />
    <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none" />
  </svg>
);
const IconArrowRight = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);
const IconUser = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20c0-4 3.5-7 8-7s8 3 8 7" />
  </svg>
);
const IconAlertCircle = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8v5M12 16h.01" />
  </svg>
);
const IconLogout = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </svg>
);
const IconCheck = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="M5 13l4 4L19 7" />
  </svg>
);

// ─── Additional icons for new metrics ──────────────────────
const IconStar = (props) => (
  <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path d="M12 2.5l2.9 6.2 6.6.6-5 4.5 1.5 6.6L12 17l-5.9 3.4L7.6 13.8l-5-4.5 6.6-.6L12 2.5z" />
  </svg>
);
const IconDollarSign = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M12 2v20M8 8h6a3 3 0 010 6h-4a3 3 0 010-6h6" />
  </svg>
);
const IconBriefcase = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="3" y="7" width="18" height="13" rx="2" />
    <path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2" />
  </svg>
);
const IconTimer = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
    <path d="M16 3l-2 2M8 3l2 2" />
    <path d="M9 14l2 2 4-4" />
  </svg>
);

// ─── Helpers ──────────────────────────────────────────────
const rateColor = (percent) => {
  if (percent >= 70) return { color: '#22c55e', soft: 'rgba(34, 197, 94, 0.12)' };
  if (percent >= 40) return { color: '#eab308', soft: 'rgba(234, 179, 8, 0.12)' };
  return { color: '#ef4444', soft: 'rgba(239, 68, 68, 0.12)' };
};

const STATUS_COLORS = {
  pending: '#f59e0b',
  assigned: '#60a5fa',
  in_progress: '#8b5cf6',
  'in progress': '#8b5cf6',
  completed: '#22c55e',
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

export const ArtisanDashboard = () => {
  const { logout } = useAuth();
  const queryClient = useQueryClient();

  // ─── Main Dashboard Data ──────────────────────────────────
  const { data, isLoading, error } = useQuery({
    queryKey: ['artisanDashboard'],
    queryFn: () => getArtisanDashboard().then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  // ─── Accept Assignment Mutation ──────────────────────────
  const acceptMutation = useMutation({
    mutationFn: (assignmentId) => acceptAssignment(assignmentId),
    onSuccess: () => {
      queryClient.invalidateQueries(['artisanDashboard']);
    },
    onError: (err) => {
      console.error('Failed to accept assignment:', err);
    },
  });

  const handleAccept = (assignmentId) => {
    if (window.confirm('Accept this job assignment?')) {
      acceptMutation.mutate(assignmentId);
    }
  };

  if (isLoading) {
    return (
      <div className="artisan-dashboard">
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

  if (error) {
    return (
      <div className="artisan-dashboard">
        <div className="state-banner state-banner--error">
          <IconAlertCircle className="state-banner__icon" />
          <p>Couldn&apos;t load your dashboard. Try refreshing the page.</p>
        </div>
      </div>
    );
  }

  const summary = data?.summary || {};
  const artisan = data?.artisan || {};
  const currentAssignment = data?.current_assignment;
  const recentAssignments = data?.recent_assignments || [];

  // ─── Profile picture / name ──────────────────────────────
  const avatarUrl = artisan.profile_picture || null;
  const fullName = artisan.full_name || artisan.name || 'Artisan';
  const email = artisan.email || '';
  const role = 'Artisan';

  const completionRate = summary.completion_rate || 0;
  const { color, soft } = rateColor(completionRate);
  const completed = summary.completed || 0;
  const totalAssignments = summary.total_assignments || 0;

  // ─── Metrics ──────────────────────────────────────────────
  const averageRating = summary.average_rating || 0;
  const totalEarnings = summary.total_earnings || 0;
  const currentWorkload = summary.current_workload || 0;
  const maxWorkload = artisan.max_concurrent_jobs || 5;
  const workloadPercent = maxWorkload > 0 ? Math.min(100, (currentWorkload / maxWorkload) * 100) : 0;
  const onTimeRate = summary.on_time_rate || 0;

  const canAccept = currentAssignment &&
    ['pending', 'assigned'].includes(currentAssignment.status?.toLowerCase());

  return (
    <div className="artisan-dashboard">
      {/* ─── Header ──────────────────────────────────────────── */}
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
        <h1 className="artisan-dashboard__title">Artisan Dashboard</h1>
        <button type="button" onClick={logout} className="logout-btn">
          <IconLogout className="logout-btn__icon" />
          Log out
        </button>
      </header>

      {/* ─── Stat Cards ────────────────────────────────────── */}
      <div className="stat-grid">
        <StatCard icon={IconClipboardList} color="#3b82f6" value={totalAssignments} label="Total assignments" />
        <StatCard icon={IconClock} color="#eab308" value={summary.pending || 0} label="Pending" />
        <StatCard icon={IconRefresh} color="#8b5cf6" value={summary.in_progress || 0} label="In progress" />
        <StatCard icon={IconCheckCircle} color="#22c55e" value={completed} label="Completed" />
        <StatCard icon={IconCalendar} color="#6366f1" value={summary.today_assignments || 0} label="Today's assignments" />
        <StatCard icon={IconStar} color="#f59e0b" value={averageRating > 0 ? averageRating.toFixed(1) : '—'} label="Avg rating" />
        <StatCard icon={IconDollarSign} color="#22c55e" value={totalEarnings > 0 ? `₵${totalEarnings.toFixed(2)}` : '—'} label="Total earnings" />
        <StatCard icon={IconTimer} color="#06b6d4" value={onTimeRate > 0 ? `${onTimeRate}%` : '—'} label="On-time rate" />
      </div>

      {/* ─── Completion Rate Panel ────────────────────────── */}
      <div className="progress-panel">
        <div className="progress-panel__top">
          <div>
            <p className="progress-panel__label">Completion Rate</p>
            <p className="progress-panel__value">{completionRate}%</p>
            <p className="progress-panel__subtitle">{completed} of {totalAssignments} assignments completed</p>
          </div>
          <div className="progress-panel__badge" style={{ '--rate-color': color, '--rate-soft': soft }}>
            <IconGauge />
          </div>
        </div>
        <div className="progress-panel__track">
          <div
            className="progress-panel__fill"
            style={{ width: `${Math.min(100, Math.max(0, completionRate))}%`, '--rate-color': color }}
          />
          <div
            className="progress-panel__dot"
            style={{ left: `${Math.min(100, Math.max(0, completionRate))}%`, '--rate-color': color }}
          />
        </div>
      </div>

      {/* ─── Workload Capacity Panel ────────────────────────── */}
      <div className="progress-panel">
        <div className="progress-panel__top">
          <div>
            <p className="progress-panel__label">Workload capacity</p>
            <p className="progress-panel__value">
              {currentWorkload} / {maxWorkload}
            </p>
            <p className="progress-panel__subtitle">
              {maxWorkload - currentWorkload} slots available
            </p>
          </div>
          <div className="progress-panel__badge" style={{ '--rate-color': '#6366f1', '--rate-soft': 'rgba(99, 102, 241, 0.12)' }}>
            <IconBriefcase />
          </div>
        </div>
        <div className="progress-panel__track">
          <div
            className="progress-panel__fill"
            style={{
              width: `${workloadPercent}%`,
              '--rate-color': workloadPercent >= 80 ? '#ef4444' : workloadPercent >= 50 ? '#eab308' : '#6366f1'
            }}
          />
          <div
            className="progress-panel__dot"
            style={{
              left: `${workloadPercent}%`,
              '--rate-color': workloadPercent >= 80 ? '#ef4444' : workloadPercent >= 50 ? '#eab308' : '#6366f1'
            }}
          />
        </div>
      </div>

      {/* ─── Current Assignment ────────────────────────────── */}
      {currentAssignment ? (
        <div className="panel">
          <div className="panel__header">
            <h3 className="panel__title">Current assignment</h3>
            <span className="live-pill">
              <span className="live-pill__dot" aria-hidden="true" />
              Active
            </span>
          </div>
          <dl className="assignment-meta">
            <div className="assignment-meta__row">
              <dt>Incident</dt>
              <dd>{currentAssignment.incident_number}</dd>
            </div>
            <div className="assignment-meta__row">
              <dt>Customer</dt>
              <dd>
                <IconUser className="assignment-meta__icon" />
                {currentAssignment.customer}
              </dd>
            </div>
            <div className="assignment-meta__row">
              <dt>Status</dt>
              <dd>
                <span
                  className="status-pill"
                  style={{ '--status-color': getStatusColor(currentAssignment.status) }}
                >
                  {currentAssignment.status}
                </span>
              </dd>
            </div>
            {currentAssignment.assigned_at && (
              <div className="assignment-meta__row">
                <dt>Assigned</dt>
                <dd>{new Date(currentAssignment.assigned_at).toLocaleString()}</dd>
              </div>
            )}
          </dl>

          {canAccept && (
            <div className="assignment-actions">
              <button
                type="button"
                onClick={() => handleAccept(currentAssignment.id)}
                disabled={acceptMutation.isPending}
                className="btn btn-success accept-btn"
              >
                {acceptMutation.isPending ? (
                  <>
                    <span className="spinner" aria-hidden="true" />
                    Accepting…
                  </>
                ) : (
                  <>
                    <IconCheck className="accept-btn__icon" />
                    Accept Job
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="panel">
          <div className="empty-state">
            <IconCheckCircle className="empty-state__icon" />
            <p>No active assignment right now. Check back later, or take a well-earned break.</p>
          </div>
        </div>
      )}

      {/* ─── Recent Assignments ────────────────────────────── */}
      <div className="panel">
        <div className="panel__header">
          <h3 className="panel__title">Recent assignments</h3>
          <span className="panel__count">{recentAssignments.length}</span>
        </div>

        {recentAssignments.length === 0 ? (
          <div className="empty-state">
            <IconClipboardList className="empty-state__icon" />
            <p>No assignments yet. They will appear here once you are assigned.</p>
          </div>
        ) : (
          <>
            <ul className="call-list">
              {recentAssignments.map((assignment) => (
                <li key={assignment.id} className="call-row">
                  <div className="call-row__ref">
                    <Link to={`/incidents/${assignment.incident_id}`} className="call-row__link">
                      {assignment.incident_number}
                    </Link>
                    <span className="call-row__customer">– {assignment.customer || 'No customer'}</span>
                  </div>
                  <span className="call-row__time">
                    <span
                      className="status-pill"
                      style={{ '--status-color': getStatusColor(assignment.status) }}
                    >
                      {assignment.status}
                    </span>
                    {assignment.assigned_at && (
                      <span className="call-row__date">
                        {new Date(assignment.assigned_at).toLocaleDateString()}
                      </span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
            <div className="view-all-row">
              {/* ✅ Link now points to artisan's own assignments */}
              <Link to="/assignments/my" className="view-all-link">
                View all <IconArrowRight className="view-all-link__icon" />
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
};