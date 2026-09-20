// src/components/dashboard/ArtisanDashboard.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getArtisanDashboard } from '../../api/dashboardAPI';
import { acceptAssignment } from '../../api/assignmentsAPI';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FaThLarge,
  FaRegEdit,
  FaRegClipboard,
  FaBookOpen,
  FaLock,
  FaChevronRight,
  FaCheckCircle,
  FaBolt,
  FaStar,
  FaClock,
  FaCircleNotch,
  FaShieldAlt,
  FaArrowUp,
  FaPlay,
  FaTools,
  FaSignOutAlt,
} from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';
import './Artisandashboard.css';

// ─── Helpers ──────────────────────────────────────────────
const rateColor = (percent) => {
  if (percent >= 70) return { color: '#10b981', soft: 'rgba(16, 185, 129, 0.12)' };
  if (percent >= 40) return { color: '#f59e0b', soft: 'rgba(245, 158, 11, 0.12)' };
  return { color: '#ef4444', soft: 'rgba(239, 68, 68, 0.12)' };
};

const STATUS_LABEL = {
  pending: { label: 'Pending', color: '#f59e0b', soft: 'rgba(245, 158, 11, 0.12)' },
  assigned: { label: 'Assigned', color: '#6366f1', soft: 'rgba(99, 102, 241, 0.12)' },
  in_progress: { label: 'In progress', color: '#8b5cf6', soft: 'rgba(139, 92, 246, 0.12)' },
  'in progress': { label: 'In progress', color: '#8b5cf6', soft: 'rgba(139, 92, 246, 0.12)' },
  completed: { label: 'Completed', color: '#10b981', soft: 'rgba(16, 185, 129, 0.12)' },
  cancelled: { label: 'Cancelled', color: '#ef4444', soft: 'rgba(239, 68, 68, 0.12)' },
};

const getStatusMeta = (status) => {
  const key = (status || '').toLowerCase();
  return (
    STATUS_LABEL[key] || {
      label: status || '—',
      color: '#64748b',
      soft: 'rgba(100, 116, 139, 0.12)',
    }
  );
};

// Flat nav — matches the Ayuda sidebar style
const NAV_ITEMS = [
  { to: '/artisan/dashboard', label: 'Dashboard', icon: FaThLarge, end: true },
  { to: '/artisan/profile', label: 'My details', icon: FaRegEdit },
  { to: '/provider/test-centre', label: 'Test centre', icon: FaRegClipboard },
  { to: '/provider/training-centre', label: 'Training centre', icon: FaBookOpen, locked: true },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

export const ArtisanDashboard = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ['artisanDashboard'],
    queryFn: () => getArtisanDashboard().then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const acceptMutation = useMutation({
    mutationFn: (id) => acceptAssignment(id),
    onSuccess: () => queryClient.invalidateQueries(['artisanDashboard']),
    onError: (err) => console.error('Failed to accept assignment:', err),
  });

  const handleAccept = (id) => {
    if (window.confirm('Accept this job assignment?')) {
      acceptMutation.mutate(id);
    }
  };

  const summary = data?.summary || {};
  const artisan = data?.artisan || {};
  const currentAssignment = data?.current_assignment;
  const recentAssignments = data?.recent_assignments || [];

  const avatarUrl = artisan.profile_picture || null;
  const fullName = artisan.full_name || artisan.name || user?.full_name || 'Artisan';
  const firstName = fullName.split(' ')[0] || 'Artisan';
  const role = 'Artisan';

  const completionRate = summary.completion_rate || 0;
  const { color: rateCol } = rateColor(completionRate);
  const completed = summary.completed || 0;
  const totalAssignments = summary.total_assignments || 0;
  const pending = summary.pending || 0;
  const inProgress = summary.in_progress || 0;

  const averageRating = summary.average_rating || 0;
  const totalEarnings = summary.total_earnings || 0;
  const currentWorkload = summary.current_workload || 0;
  const maxWorkload = artisan.max_concurrent_jobs || 5;

  const onTimeRate = summary.on_time_rate || 0;

  const canAccept =
    currentAssignment &&
    ['pending', 'assigned'].includes(currentAssignment.status?.toLowerCase());

  const currentStatus = currentAssignment ? getStatusMeta(currentAssignment.status) : null;

  // Pipeline steps (adapted from Ayuda's verification pipeline)
  const pipeline = [
    {
      key: 'registration',
      title: 'Registration',
      subtitle: 'Provide your professional & account details for payments',
      state: 'complete',
    },
    {
      key: 'verification',
      title: 'Identity verification',
      subtitle: 'Upload your ID and address documents for review',
      state: currentAssignment ? 'ongoing' : 'pending',
    },
    {
      key: 'training',
      title: 'Training centre',
      subtitle: 'Complete the onboarding training modules',
      state: 'locked',
    },
  ];

  if (isLoading) {
    return (
      <div className="ay-layout">
        <aside className="ay-sidebar">
          <div className="ay-sidebar__brand">
            <div className="ay-sidebar__logo">
              <span className="ay-sidebar__logo-mark" />
              <span className="ay-sidebar__logo-text">tumakonect</span>
            </div>
            <p className="ay-sidebar__brand-sub">…here to help</p>
          </div>
          <div className="ay-skel ay-skel--nav" />
          <div className="ay-skel ay-skel--nav" />
          <div className="ay-skel ay-skel--nav" />
        </aside>
        <main className="ay-main">
          <div className="ay-loading">
            <FaCircleNotch className="ay-loading__spin" />
            <span>Loading your portal…</span>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ay-layout">
        <aside className="ay-sidebar">
          <div className="ay-sidebar__brand">
            <div className="ay-sidebar__logo">
              <span className="ay-sidebar__logo-mark" />
              <span className="ay-sidebar__logo-text">tumakonect</span>
            </div>
            <p className="ay-sidebar__brand-sub">…here to help</p>
          </div>
        </aside>
        <main className="ay-main">
          <div className="ay-error">
            <FaShieldAlt />
            <div>
              <strong>Couldn&apos;t load your dashboard</strong>
              <p>Try refreshing the page or check your connection.</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="ay-layout">
      {/* ─── Sidebar ──────────────────────────────────────── */}
      <aside className="ay-sidebar">
        <div className="ay-sidebar__brand">
          <div className="ay-sidebar__logo">
            <span className="ay-sidebar__logo-mark" />
            <span className="ay-sidebar__logo-text">tumakonect</span>
          </div>
          <p className="ay-sidebar__brand-sub">…here to help</p>
          <p className="ay-sidebar__brand-title">Service provider portal</p>
        </div>

        <nav className="ay-nav" aria-label="Primary">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end, locked }) => (
            <Link
              key={to}
              to={locked ? '#' : to}
              end={end}
              className={({ isActive }) =>
                `ay-nav__item ${isActive && !locked ? 'is-active' : ''} ${
                  locked ? 'is-locked' : ''
                }`
              }
              onClick={(e) => locked && e.preventDefault()}
            >
              <span className="ay-nav__icon">
                <Icon />
              </span>
              <span className="ay-nav__label">{label}</span>
              {locked && <FaLock className="ay-nav__lock" />}
            </Link>
          ))}
        </nav>

        <div className="ay-sidebar__footer">
          <div className="ay-sidebar__avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt={fullName} />
            ) : (
              <span>{firstName.charAt(0).toUpperCase()}</span>
            )}
            <span className="ay-sidebar__avatar-dot" aria-hidden="true" />
          </div>
          <div className="ay-sidebar__profile">
            <strong>{fullName}</strong>
            <span>{role}</span>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="ay-sidebar__chev"
            aria-label="Sign out"
            title="Sign out"
          >
            <FaSignOutAlt />
          </button>
        </div>
      </aside>

      {/* ─── Main ─────────────────────────────────────────── */}
      <main className="ay-main">
        <motion.div
          className="ay-main__inner"
          variants={containerVariants}
          initial="hidden"
          animate="show"
        >
          {/* Hero */}
          <motion.header className="ay-hero" variants={itemVariants}>
            <div className="ay-hero__left">
              <h1>
                Welcome, <span className="ay-hero__name">{firstName}</span>
              </h1>
              <p>Everything is set for your next professional move.</p>
            </div>

            <div className="ay-hero__phase">
              <span className="ay-phase__dot" />
              <div>
                <span className="ay-phase__label">Current phase</span>
                <strong className="ay-phase__value">
                  {totalAssignments > 0 ? 'Testing' : 'Onboarding'}
                </strong>
              </div>
            </div>
          </motion.header>

          {/* Stat cards */}
          <motion.section className="ay-stats" variants={itemVariants}>
            <article className="ay-stat ay-stat--blue">
              <div className="ay-stat__top">
                <span className="ay-stat__icon">
                  <FaArrowUp />
                </span>
                <span className="ay-stat__pill ay-stat__pill--blue">
                  {totalEarnings > 0 ? '+12%' : 'NEW'}
                </span>
              </div>
              <p className="ay-stat__label">Avg. monthly earnings</p>
              <p className="ay-stat__value">
                GH₵{totalEarnings > 0 ? totalEarnings.toFixed(2) : '0.00'}
              </p>
            </article>

            <article className="ay-stat ay-stat--orange">
              <div className="ay-stat__top">
                <span className="ay-stat__icon ay-stat__icon--orange">
                  <FaStar />
                </span>
                <span className="ay-stat__pill ay-stat__pill--orange">
                  {averageRating > 0 ? 'LIVE' : 'NEW'}
                </span>
              </div>
              <p className="ay-stat__label">Overall rating</p>
              <p className="ay-stat__value">
                {averageRating > 0 ? averageRating.toFixed(1) : '0'}
              </p>
            </article>

            <article className="ay-stat ay-stat--green">
              <div className="ay-stat__top">
                <span className="ay-stat__icon ay-stat__icon--green">
                  <FaCheckCircle />
                </span>
                <span className="ay-stat__pill ay-stat__pill--green">
                  {onTimeRate > 0 ? `${onTimeRate}% on time` : 'READY'}
                </span>
              </div>
              <p className="ay-stat__label">Completed ayúdas</p>
              <p className="ay-stat__value">{completed}</p>
            </article>
          </motion.section>

          {/* Bottom grid */}
          <motion.section className="ay-grid" variants={itemVariants}>
            {/* Pipeline */}
            <div className="ay-panel">
              <div className="ay-panel__head">
                <span className="ay-panel__icon">
                  <FaShieldAlt />
                </span>
                <h2>Profile pipeline</h2>
              </div>

              <ul className="ay-pipeline">
                {pipeline.map((step) => (
                  <li key={step.key} className={`ay-pipeline__item is-${step.state}`}>
                    <span className="ay-pipeline__badge">
                      {step.state === 'complete' ? (
                        <FaCheckCircle />
                      ) : step.state === 'ongoing' ? (
                        <FaCircleNotch className="ay-pipeline__spin" />
                      ) : (
                        <FaLock />
                      )}
                    </span>
                    <div className="ay-pipeline__body">
                      <strong>{step.title}</strong>
                      <span>{step.subtitle}</span>
                    </div>
                    <span className="ay-pipeline__status">
                      {step.state === 'complete'
                        ? 'Complete'
                        : step.state === 'ongoing'
                        ? 'Ongoing'
                        : 'Locked'}
                    </span>
                  </li>
                ))}
              </ul>

              {/* Secondary metrics */}
              <div className="ay-mini-grid">
                <div className="ay-mini">
                  <span className="ay-mini__label">
                    <FaRegClipboard /> Total assignments
                  </span>
                  <span className="ay-mini__value">{totalAssignments}</span>
                </div>
                <div className="ay-mini">
                  <span className="ay-mini__label">
                    <FaClock /> Pending
                  </span>
                  <span className="ay-mini__value">{pending}</span>
                </div>
                <div className="ay-mini">
                  <span className="ay-mini__label">
                    <FaPlay /> In progress
                  </span>
                  <span className="ay-mini__value">{inProgress}</span>
                </div>
                <div className="ay-mini">
                  <span className="ay-mini__label">
                    <FaTools /> Workload
                  </span>
                  <span className="ay-mini__value">
                    {currentWorkload}/{maxWorkload}
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="ay-progress">
                <div className="ay-progress__head">
                  <span>Completion rate</span>
                  <strong>{completionRate}%</strong>
                </div>
                <div className="ay-progress__track">
                  <div
                    className="ay-progress__fill"
                    style={{
                      width: `${Math.min(100, Math.max(0, completionRate))}%`,
                      background: rateCol,
                    }}
                  />
                </div>
                <p className="ay-progress__hint">
                  {completed} of {totalAssignments} assignments completed
                </p>
              </div>
            </div>

            {/* Active milestone */}
            <div className="ay-milestone">
              <div className="ay-milestone__head">
                <FaBolt />
                <span>Active milestone</span>
              </div>

              <div className="ay-milestone__body">
                <span className="ay-milestone__step">
                  Step {currentAssignment ? 2 : 1} of 4
                </span>
                <h3>
                  {currentAssignment
                    ? currentAssignment.incident_number
                    : 'Accept your first assignment'}
                </h3>
                <p>
                  {currentAssignment
                    ? `Assigned to ${currentAssignment.customer || 'a customer'}`
                    : 'Once an incident is assigned to you, it will appear here.'}
                </p>

                {currentAssignment && currentStatus && (
                  <div className="ay-milestone__meta">
                    <span
                      className="ay-milestone__status"
                      style={{ '--status-color': currentStatus.color }}
                    >
                      <span className="ay-milestone__status-dot" />
                      {currentStatus.label}
                    </span>
                    {currentAssignment.assigned_at && (
                      <span className="ay-milestone__date">
                        {new Date(currentAssignment.assigned_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {canAccept ? (
                <button
                  type="button"
                  className="ay-milestone__cta"
                  onClick={() => handleAccept(currentAssignment.id)}
                  disabled={acceptMutation.isPending}
                >
                  {acceptMutation.isPending ? (
                    <>
                      <FaCircleNotch className="ay-pipeline__spin" />
                      Accepting…
                    </>
                  ) : (
                    <>
                      <FaCheckCircle />
                      Accept job
                    </>
                  )}
                </button>
              ) : (
                <Link to="/assignments/my" className="ay-milestone__cta">
                  View my assignments
                  <FaChevronRight />
                </Link>
              )}
            </div>
          </motion.section>

          {/* Recent assignments */}
          {recentAssignments.length > 0 && (
            <motion.section className="ay-panel ay-panel--list" variants={itemVariants}>
              <div className="ay-panel__head">
                <span className="ay-panel__icon">
                  <FaRegClipboard />
                </span>
                <h2>Recent assignments</h2>
                <Link to="/assignments/my" className="ay-panel__more">
                  View all <FaChevronRight />
                </Link>
              </div>

              <ul className="ay-list">
                {recentAssignments.slice(0, 5).map((a) => {
                  const meta = getStatusMeta(a.status);
                  return (
                    <li key={a.id} className="ay-list__row">
                      <Link
                        to={`/incidents/${a.incident || a.incident_id}`}
                        className="ay-list__ref"
                      >
                        {a.incident_number}
                      </Link>
                      <span className="ay-list__customer">{a.customer || '—'}</span>
                      <span
                        className="ay-list__status"
                        style={{ '--status-color': meta.color, '--status-soft': meta.soft }}
                      >
                        {meta.label}
                      </span>
                      {a.assigned_at && (
                        <span className="ay-list__date">
                          {new Date(a.assigned_at).toLocaleDateString()}
                        </span>
                      )}
                    </li>
                  );
                })}
              </ul>
            </motion.section>
          )}

          {/* Logout */}
          <motion.div className="ay-signout" variants={itemVariants}>
            <button type="button" onClick={handleLogout} className="ay-signout__btn">
              Sign out of your account
            </button>
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
};