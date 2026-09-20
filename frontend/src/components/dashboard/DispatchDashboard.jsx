// src/components/dashboard/DispatchDashboard.jsx

import { useEffect, useReducer, useRef, useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';


import { useWebSocket } from '../../hooks/useWebSocket';
import { getIncidents, assignIncident } from '../../api/incidentsAPI';
import { getAvailableArtisans } from '../../api/artisansAPI';
import { getAssignments, rateAssignment } from '../../api/assignmentsAPI';
import { getCurrentUser } from '../../api/authAPI';
import { useAuth } from '../../context/AuthContext';
import { StatusBadge } from '../common/StatusBadge';

import './DispatchDashboard.css';


// ============================================================
// ICONS
// ============================================================
const IconClipboard = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="6" y="4" width="12" height="17" rx="2" />
    <path d="M9 4V3a1 1 0 011-1h4a1 1 0 011 1v1" />
    <path d="M9 11h6M9 15h6" />
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
const IconStar = (props) => (
  <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path d="M12 2.5l2.9 6.2 6.6.6-5 4.5 1.5 6.6L12 17l-5.9 3.4L7.6 13.8l-5-4.5 6.6-.6L12 2.5z" />
  </svg>
);
const IconStarOutline = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="M12 2.5l2.9 6.2 6.6.6-5 4.5 1.5 6.6L12 17l-5.9 3.4L7.6 13.8l-5-4.5 6.6-.6L12 2.5z" />
  </svg>
);
const IconWrench = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M14.7 6.3a4 4 0 10-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 005.4-5.4l-2.8 2.8-2-2 2.8-2.8z" />
  </svg>
);
const IconBriefcase = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="3" y="7" width="18" height="13" rx="2" />
    <path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2" />
  </svg>
);
const IconArrowRight = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);
const IconLogout = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </svg>
);
const IconRefresh = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M20 11a8.1 8.1 0 00-15.5-2M4 5v4h4" />
    <path d="M4 13a8.1 8.1 0 0015.5 2M20 19v-4h-4" />
  </svg>
);


// ============================================================
// STAT CARD
// ============================================================
const StatCard = ({ icon: Icon, color, value, label }) => (
  <div className="stat-card" style={{ '--stat-color': color }}>
    <div className="stat-card__icon-wrap">
      <Icon className="stat-card__icon" />
    </div>
    <div className="stat-card__body">
      <div className="stat-card__value">{value}</div>
      <div className="stat-card__label">{label}</div>
    </div>
  </div>
);


// ============================================================
// PRIORITY
// ============================================================
const PRIORITY_COLORS = {
  low: '#64748b',
  medium: '#3b82f6',
  high: '#f59e0b',
  critical: '#ef4444',
  urgent: '#ef4444',
};
const getPriorityColor = (priority) =>
  PRIORITY_COLORS[(priority || '').toLowerCase()] || '#64748b';


// ============================================================
// RATING STARS
// ============================================================
const RatingStars = ({ value, onChange, disabled, size = 20 }) => {
  const [hover, setHover] = useState(0);
  return (
    <div className="rating-stars" style={{ display: 'inline-flex', gap: '2px' }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          className="rating-star-btn"
          onClick={() => !disabled && onChange(star)}
          onMouseEnter={() => !disabled && setHover(star)}
          onMouseLeave={() => !disabled && setHover(0)}
          disabled={disabled}
          aria-label={`Rate ${star} stars`}
          style={{
            background: 'none',
            border: 'none',
            padding: 0,
            cursor: disabled ? 'default' : 'pointer',
            color: (hover ? star <= hover : star <= value) ? '#f59e0b' : '#d1d5db',
            transition: 'color 0.15s',
          }}
        >
          {star <= (hover || value) ? (
            <IconStar width={size} height={size} />
          ) : (
            <IconStarOutline width={size} height={size} />
          )}
        </button>
      ))}
    </div>
  );
};


// ============================================================
// REDUCER
// ============================================================
const initialState = {
  pendingIncidents: [],
  activeAssignments: [],
  incomingAlerts: [],
};

function dashboardReducer(state, action) {
  switch (action.type) {
    case 'SET_PENDING_INCIDENTS':
      return { ...state, pendingIncidents: action.payload };
    case 'SET_ACTIVE_ASSIGNMENTS':
      return { ...state, activeAssignments: action.payload };
    case 'ADD_INCIDENT':
      return { ...state, pendingIncidents: [action.payload, ...state.pendingIncidents] };
    case 'UPDATE_INCIDENT':
      return {
        ...state,
        pendingIncidents: state.pendingIncidents.map((inc) =>
          inc.id === action.payload.id ? { ...inc, ...action.payload.data } : inc
        ),
      };
    case 'REMOVE_INCIDENT':
      return {
        ...state,
        pendingIncidents: state.pendingIncidents.filter((inc) => inc.id !== action.payload),
      };
    case 'ADD_ASSIGNMENT':
      return { ...state, activeAssignments: [action.payload, ...state.activeAssignments] };
    case 'ADD_ALERT':
      return { ...state, incomingAlerts: [action.payload, ...state.incomingAlerts] };
    case 'REMOVE_ALERT':
      return { ...state, incomingAlerts: state.incomingAlerts.slice(1) };
    default:
      return state;
  }
}


// ============================================================
// MAIN
// ============================================================
export const DispatchDashboard = () => {
  const queryClient = useQueryClient();
  const { messages } = useWebSocket();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [state, dispatch] = useReducer(dashboardReducer, initialState);
  const { pendingIncidents, activeAssignments, incomingAlerts } = state;
  const alertTimeoutRef = useRef(null);

  const [ratings, setRatings] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedSubcategory, setSelectedSubcategory] = useState('All');

  // ─── Queries ─────────────────────────────────────────────
  const { data: userData, isLoading: userLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
    staleTime: 5 * 60 * 1000,
  });

  const { data: incidentsData, isLoading: incidentsLoading } = useQuery({
    queryKey: ['dispatchIncidents'],
    queryFn: () => getIncidents({ page_size: 100 }).then((res) => res.results || []),
    staleTime: 5 * 60 * 1000,
  });

  const { data: artisansData, isLoading: artisansLoading } = useQuery({
    queryKey: ['availableArtisans'],
    queryFn: () =>
      getAvailableArtisans().then((res) => (Array.isArray(res) ? res : res.results || [])),
    staleTime: 2 * 60 * 1000,
  });

  const { data: assignmentsData, isLoading: assignmentsLoading } = useQuery({
    queryKey: ['activeAssignments'],
    queryFn: () =>
      getAssignments().then((res) => {
        const responseData = res.data || res;
        const items = responseData.results || responseData || [];
        return items.filter(
          (a) =>
            a.status?.toLowerCase() !== 'completed' &&
            a.status?.toLowerCase() !== 'cancelled' &&
            a.status?.toLowerCase() !== 'closed'
        );
      }),
    staleTime: 2 * 60 * 1000,
  });

  // ─── Mutations ───────────────────────────────────────────
  const assignMutation = useMutation({
    mutationFn: ({ incidentId, artisanId }) =>
      assignIncident(incidentId, { assigned_to: artisanId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dispatchIncidents'] });
      queryClient.invalidateQueries({ queryKey: ['availableArtisans'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssignments'] });
    },
  });

  const rateMutation = useMutation({
    mutationFn: ({ assignmentId, rating }) => rateAssignment(assignmentId, { rating }),
    onSuccess: (data, variables) => {
      setRatings((prev) => ({ ...prev, [variables.assignmentId]: variables.rating }));
      queryClient.invalidateQueries({ queryKey: ['availableArtisans'] });
    },
    onError: (error) => console.error('Rating failed:', error),
  });

  // ─── Sync incidents ──────────────────────────────────────
  useEffect(() => {
    if (incidentsData) {
      const statuses = ['NEW', 'OPEN', 'ASSIGNED'];
      const pending = incidentsData.filter((inc) =>
        statuses.includes(inc.status_name || inc.status_display || inc.status)
      );
      dispatch({ type: 'SET_PENDING_INCIDENTS', payload: pending });
    }
  }, [incidentsData]);

  // ─── Sync assignments ────────────────────────────────────
  useEffect(() => {
    if (assignmentsData) {
      dispatch({ type: 'SET_ACTIVE_ASSIGNMENTS', payload: assignmentsData });
    }
  }, [assignmentsData]);

  // ─── WebSocket ───────────────────────────────────────────
  useEffect(() => {
    if (!messages.length) return;
    const latest = messages[messages.length - 1];

    if (latest.type === 'incident_update') {
      const { action, data } = latest.data;
      if (action === 'created') {
        dispatch({ type: 'ADD_INCIDENT', payload: data });
        dispatch({
          type: 'ADD_ALERT',
          payload: {
            id: Date.now(),
            message: `New incident ${data.incident_number}: ${data.title}`,
            severity: 'info',
          },
        });
        if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
        alertTimeoutRef.current = setTimeout(() => {
          dispatch({ type: 'REMOVE_ALERT' });
        }, 5000);
      }
      if (action === 'updated') {
        dispatch({ type: 'UPDATE_INCIDENT', payload: { id: data.incident_id, data } });
      }
    }

    if (latest.type === 'assignment_update') {
      const { action, data } = latest.data;
      if (action === 'assigned') {
        dispatch({ type: 'ADD_ASSIGNMENT', payload: data });
        dispatch({ type: 'REMOVE_INCIDENT', payload: data.incident_id });
      }
    }
  }, [messages]);

  useEffect(() => {
    return () => {
      if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    };
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // ─── Memos ───────────────────────────────────────────────
  const availableArtisans = useMemo(() => artisansData || [], [artisansData]);

  const categories = useMemo(() => {
    const cats = new Set();
    availableArtisans.forEach((artisan) => {
      cats.add(artisan.category_detail?.name || 'Uncategorized');
    });
    return ['All', ...Array.from(cats).sort()];
  }, [availableArtisans]);

  const artisansByCategory = useMemo(() => {
    if (selectedCategory === 'All') return availableArtisans;
    return availableArtisans.filter(
      (artisan) => (artisan.category_detail?.name || 'Uncategorized') === selectedCategory
    );
  }, [availableArtisans, selectedCategory]);

  const subcategories = useMemo(() => {
    const skills = new Set();
    artisansByCategory.forEach((artisan) => {
      (artisan.skills_detail || []).forEach((skill) => {
        if (skill.name) skills.add(skill.name);
      });
    });
    return ['All', ...Array.from(skills).sort()];
  }, [artisansByCategory]);

  const filteredArtisans = useMemo(() => {
    if (selectedSubcategory === 'All') return artisansByCategory;
    return artisansByCategory.filter((artisan) =>
      (artisan.skills_detail || []).some((skill) => skill.name === selectedSubcategory)
    );
  }, [artisansByCategory, selectedSubcategory]);

  const getCountForCategory = (cat) => {
    if (cat === 'All') return availableArtisans.length;
    return availableArtisans.filter(
      (a) => (a.category_detail?.name || 'Uncategorized') === cat
    ).length;
  };

  // ─── Loading ─────────────────────────────────────────────
  if (incidentsLoading || artisansLoading || userLoading || assignmentsLoading) {
    return (
      <div className="dispatch-dashboard">
        <div className="profile-skeleton" />
        <div className="stat-grid">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="stat-skeleton" />
          ))}
        </div>
        <div className="kanban">
          <div className="panel-skeleton" />
          <div className="panel-skeleton" />
          <div className="panel-skeleton" />
        </div>
      </div>
    );
  }

  // ─── User ────────────────────────────────────────────────
  const user = userData || {};
  const avatarUrl = user.profile_picture || null;
  const fullName = user.full_name || user.name || 'Dispatcher';
  const role = user.role || user.user_type_display || 'Dispatcher';

  const awaitingDispatch =
    incidentsData?.filter(
      (i) => (i.status_name || i.status_display || i.status) === 'NEW'
    ).length || 0;

  const handleRate = (assignmentId, rating) => {
    if (ratings[assignmentId]) return;
    rateMutation.mutate({ assignmentId, rating });
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setSelectedSubcategory('All');
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['dispatchIncidents'] });
    queryClient.invalidateQueries({ queryKey: ['availableArtisans'] });
    queryClient.invalidateQueries({ queryKey: ['activeAssignments'] });
    queryClient.invalidateQueries({ queryKey: ['currentUser'] });
  };

  // ─── Render ──────────────────────────────────────────────
  return (
    <div className="dispatch-dashboard">

      {/* ─── Header ──────────────────────────────────────── */}
      <header className="dispatch-header">
        <div className="agent-profile">
          <div className="agent-profile__avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt={fullName} />
            ) : (
              <div className="agent-profile__initial">
                {fullName.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <div className="agent-profile__info">
            <span className="agent-profile__welcome">Welcome back</span>
            <h2 className="agent-profile__name">{fullName}</h2>
            <div className="agent-profile__meta">
              <span className="agent-profile__role">{role}</span>
              {user.email && (
                <>
                  <span className="agent-profile__dot" aria-hidden="true" />
                  <span className="agent-profile__email">{user.email}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="dispatch-header__right">
          <div className="dispatch-header__title-group">
            <h1 className="dispatch-title">Dispatch Console</h1>
            <p className="dispatch-subtitle">Monitor incidents and coordinate artisans</p>
          </div>

          <div className="dispatch-header__actions">
            <span className="live-indicator">
              <span className="live-indicator__dot" aria-hidden="true" />
              Live
            </span>

            <button
              className="header-action-btn"
              onClick={handleRefresh}
              title="Refresh dashboard"
              aria-label="Refresh dashboard"
            >
              <IconRefresh width={18} height={18} />
            </button>

            <button
              className="logout-btn"
              onClick={handleLogout}
              aria-label="Logout"
              title="Logout"
            >
              <IconLogout className="logout-btn__icon" width={19} height={19} />
            </button>
          </div>
        </div>
      </header>

      {/* ─── Alerts ──────────────────────────────────────── */}
      {incomingAlerts.length > 0 && (
        <div className="alert-stack" role="status" aria-live="polite">
          {incomingAlerts.map((alert) => (
            <div key={alert.id} className="alert-toast">
              <span className="alert-toast__dot" aria-hidden="true" />
              <p className="alert-toast__message">{alert.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* ─── KPI strip (single horizontal row) ───────────── */}
      <section className="kpi-strip">
        <StatCard
          icon={IconClipboard}
          color="#f59e0b"
          value={pendingIncidents.length}
          label="Pending incidents"
        />
        <StatCard
          icon={IconUsers}
          color="#3b82f6"
          value={availableArtisans.length}
          label="Available artisans"
        />
        <StatCard
          icon={IconCheckCircle}
          color="#22c55e"
          value={activeAssignments.length}
          label="Active assignments"
        />
        <StatCard
          icon={IconClock}
          color="#ef4444"
          value={awaitingDispatch}
          label="Awaiting dispatch"
        />
      </section>

      {/* ─── Kanban workspace (3 horizontal columns) ────── */}
      <div className="kanban">

        {/* ─── Column 1: Pending incidents ──────────────── */}
        <section className="kanban__col kanban__col--incidents">
          <header className="kanban__head">
            <div className="kanban__head-left">
              <span className="kanban__dot kanban__dot--orange" />
              <h3>Pending Incidents</h3>
            </div>
            <span className="kanban__count kanban__count--orange">
              {pendingIncidents.length}
            </span>
          </header>

          <div className="kanban__scroll">
            {pendingIncidents.length === 0 ? (
              <div className="kanban__empty">
                <IconCheckCircle className="kanban__empty-icon" />
                <p>All caught up</p>
                <span>New reports appear here automatically.</span>
              </div>
            ) : (
              pendingIncidents.map((incident) => (
                <article
                  key={incident.id}
                  className="ticket ticket--incident"
                  style={{ '--priority-color': getPriorityColor(incident.priority) }}
                >
                  <div className="ticket__top">
                    <Link to={`/incidents/${incident.id}`} className="ticket__ref">
                      {incident.incident_number}
                    </Link>
                    <span className="ticket__priority">{incident.priority}</span>
                  </div>

                  <p className="ticket__title">{incident.title}</p>

                  <div className="ticket__badges">
                    <StatusBadge status={incident.status?.toLowerCase()}>
                      {incident.status}
                    </StatusBadge>
                    <StatusBadge status={incident.priority?.toLowerCase()}>
                      {incident.priority}
                    </StatusBadge>
                  </div>

                  <div className="ticket__actions">
                    <select
                      className="assign-select"
                      aria-label={`Assign an artisan to ${incident.incident_number}`}
                      onChange={(e) => {
                        if (e.target.value) {
                          assignMutation.mutate({
                            incidentId: incident.id,
                            artisanId: e.target.value,
                          });
                        }
                      }}
                      defaultValue=""
                    >
                      <option value="">Assign artisan</option>
                      {availableArtisans.map((artisan) => (
                        <option key={artisan.id} value={artisan.user}>
                          {artisan.user_detail?.full_name || artisan.user}
                        </option>
                      ))}
                    </select>

                    <Link
                      to={`/assignments/new/${incident.id}`}
                      className="advanced-link"
                    >
                      Advanced
                      <IconArrowRight className="advanced-link__icon" />
                    </Link>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        {/* ─── Column 2: Available artisans ─────────────── */}
        <section className="kanban__col kanban__col--artisans">
          <header className="kanban__head">
            <div className="kanban__head-left">
              <span className="kanban__dot kanban__dot--blue" />
              <h3>Available Artisans</h3>
            </div>
            <span className="kanban__count kanban__count--blue">
              {filteredArtisans.length}
            </span>
          </header>

          <div className="kanban__filters">
            <div className="filter-group">
              <label htmlFor="category-filter" className="filter-label">Category</label>
              <select
                id="category-filter"
                value={selectedCategory}
                onChange={handleCategoryChange}
                className="filter-select"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat} ({getCountForCategory(cat)})
                  </option>
                ))}
              </select>
            </div>

            {subcategories.length > 1 && (
              <div className="filter-group">
                <label htmlFor="subcategory-filter" className="filter-label">Skill</label>
                <select
                  id="subcategory-filter"
                  value={selectedSubcategory}
                  onChange={(e) => setSelectedSubcategory(e.target.value)}
                  className="filter-select"
                >
                  {subcategories.map((skill) => (
                    <option key={skill} value={skill}>{skill}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="kanban__scroll">
            {filteredArtisans.length === 0 ? (
              <div className="kanban__empty">
                <IconUsers className="kanban__empty-icon" />
                <p>No artisans found</p>
                <span>Try a different filter.</span>
              </div>
            ) : (
              filteredArtisans.map((artisan) => {
                const name = artisan.user_detail?.full_name || artisan.user;
                return (
                  <article key={artisan.id} className="ticket ticket--artisan">
                    <div className="ticket__artisan-top">
                      <div className="ticket__avatar">
                        {String(name).charAt(0).toUpperCase()}
                      </div>
                      <div className="ticket__artisan-info">
                        <p className="ticket__artisan-name">{name}</p>
                        <p className="ticket__artisan-cat">
                          {artisan.category_detail?.name || 'Uncategorized'}
                        </p>
                      </div>
                      <StatusBadge status="success">Available</StatusBadge>
                    </div>

                    <div className="ticket__meta">
                      <span className="meta-chip">
                        <IconWrench className="meta-chip__icon" />
                        {artisan.skills_detail?.length || 0} skills
                      </span>
                      <span className="meta-chip">
                        <IconBriefcase className="meta-chip__icon" />
                        {artisan.current_workload || 0} active
                      </span>
                      {artisan.average_rating > 0 && (
                        <span className="meta-chip meta-chip--rating">
                          <IconStar className="meta-chip__icon" />
                          {artisan.average_rating}
                        </span>
                      )}
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </section>

        {/* ─── Column 3: Active assignments ─────────────── */}
        <section className="kanban__col kanban__col--assignments">
          <header className="kanban__head">
            <div className="kanban__head-left">
              <span className="kanban__dot kanban__dot--green" />
              <h3>Active Assignments</h3>
            </div>
            <span className="kanban__count kanban__count--green">
              {activeAssignments.length}
            </span>
          </header>

          <div className="kanban__scroll">
            {activeAssignments.length === 0 ? (
              <div className="kanban__empty">
                <IconClipboard className="kanban__empty-icon" />
                <p>No active assignments</p>
                <span>Assign an incident to start tracking.</span>
              </div>
            ) : (
              activeAssignments.map((assignment) => {
                const isRated = !!ratings[assignment.id];
                const currentRating = ratings[assignment.id] || 0;
                const isSaving =
                  rateMutation.isLoading &&
                  rateMutation.variables?.assignmentId === assignment.id;

                return (
                  <article key={assignment.id} className="ticket ticket--assignment">
                    <div className="ticket__route">
                      <Link
                        to={`/incidents/${assignment.incident_id}`}
                        className="ticket__ref"
                      >
                        {assignment.incident_number}
                      </Link>
                      <IconArrowRight className="ticket__route-arrow" />
                      <span className="ticket__artisan-name">
                        {assignment.artisan_name || assignment.artisan}
                      </span>
                    </div>

                    <div className="ticket__rating">
                      <span className="ticket__rating-label">
                        {isRated ? 'Performance' : 'Rate performance'}
                      </span>
                      <RatingStars
                        value={currentRating}
                        onChange={(rating) => handleRate(assignment.id, rating)}
                        disabled={isRated || isSaving}
                        size={16}
                      />
                      {isRated && (
                        <span className="ticket__rated-check">✓</span>
                      )}
                      {isSaving && (
                        <span className="ticket__saving">saving…</span>
                      )}
                    </div>

                    <div className="ticket__footer">
                      <StatusBadge
                        status={assignment.status?.toLowerCase() || 'assigned'}
                      >
                        {assignment.status || 'Assigned'}
                      </StatusBadge>
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </section>
      </div>
    </div>
  );
};