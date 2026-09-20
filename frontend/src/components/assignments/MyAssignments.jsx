// src/components/assignments/MyAssignments.jsx
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaSync,
  FaSearch,
  FaPhone,
  FaCalendarAlt,
  FaClock,
  FaPlay,
  FaCheck,
  FaExclamationTriangle,
  FaInbox,
  FaListAlt,
  FaArrowLeft,
} from 'react-icons/fa';
import {
  getMyAssignments,
  acceptAssignment,
  startAssignment,
  completeAssignment,
} from '../../api/assignmentsAPI';
import { StatusBadge } from '../common/StatusBadge';
import './MyAssignments.css';

// ─── Priority color mapping ──────────────────────────────────
const PRIORITY_COLORS = {
  LOW: '#64748b',
  MEDIUM: '#3b82f6',
  HIGH: '#f59e0b',
  CRITICAL: '#ef4444',
  URGENT: '#ef4444',
};

const getPriorityColor = (priority) =>
  PRIORITY_COLORS[priority?.toUpperCase()] || '#94a3b8';

const FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
};

export const MyAssignments = () => {
  const queryClient = useQueryClient();
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // ─── Fetch assignments ──────────────────────────────────────
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['myAssignments'],
    queryFn: () => getMyAssignments().then((res) => res.data),
    staleTime: 2 * 60 * 1000,
  });

  const assignments = useMemo(() => data?.results || data || [], [data]);

  // ─── Mutations ──────────────────────────────────────────────
  const acceptMutation = useMutation({
    mutationFn: (id) => acceptAssignment(id),
    onSuccess: () => queryClient.invalidateQueries(['myAssignments']),
  });
  const startMutation = useMutation({
    mutationFn: (id) => startAssignment(id),
    onSuccess: () => queryClient.invalidateQueries(['myAssignments']),
  });
  const completeMutation = useMutation({
    mutationFn: (id) => completeAssignment(id),
    onSuccess: () => queryClient.invalidateQueries(['myAssignments']),
  });

  // ─── Filter and search ──────────────────────────────────────
  const filteredAssignments = useMemo(() => {
    let result = assignments;
    if (filterStatus !== 'all') {
      result = result.filter((a) => a.status?.toLowerCase() === filterStatus);
    }
    if (searchTerm.trim()) {
      const term = searchTerm.trim().toLowerCase();
      result = result.filter(
        (a) =>
          a.incident_number?.toLowerCase().includes(term) ||
          a.customer?.toLowerCase().includes(term)
      );
    }
    return result;
  }, [assignments, filterStatus, searchTerm]);

  // ─── Stats ───────────────────────────────────────────────────
  const stats = useMemo(
    () => ({
      total: assignments.length,
      pending: assignments.filter((a) => a.status?.toLowerCase() === 'pending').length,
      inProgress: assignments.filter((a) => a.status?.toLowerCase() === 'in_progress').length,
      completed: assignments.filter((a) => a.status?.toLowerCase() === 'completed').length,
    }),
    [assignments]
  );

  const handleAction = (id, mutation, actionName) => {
    if (window.confirm(`Are you sure you want to ${actionName} this assignment?`)) {
      mutation.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <div className="ma-page">
        <div className="ma-shell">
          <div className="ma-skeleton ma-skeleton--header" />
          <div className="ma-skeleton ma-skeleton--panel" />
          <div className="ma-skeleton ma-skeleton--panel" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ma-page">
        <div className="ma-shell">
          <motion.div
            className="ma-state ma-state--error"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="ma-state__icon">
              <FaExclamationTriangle />
            </div>
            <div>
              <h3>Failed to load assignments</h3>
              <p>Something went wrong while fetching your assignments. Please try again.</p>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="ma-page">
      <motion.div className="ma-shell" variants={containerVariants} initial="hidden" animate="show">
        {/* ─── Hero header ─────────────────────────────── */}
        <motion.header className="ma-hero" variants={itemVariants}>
          <div className="ma-hero__left">
            <div className="ma-hero__icon">
              <FaListAlt />
            </div>
            <div>
              <span className="ma-eyebrow">Workspace</span>
              <h1>My assignments</h1>
              <p>Track every job you've been assigned, in one place.</p>
            </div>
          </div>

          <div className="ma-hero__right">
            <div className="ma-stat-chip">
              <div className="ma-stat-chip__icon ma-stat-chip__icon--primary">
                <FaListAlt />
              </div>
              <div>
                <span className="ma-stat-chip__value">{stats.total}</span>
                <span className="ma-stat-chip__label">Total</span>
              </div>
            </div>

            <div className="ma-stat-chip">
              <div className="ma-stat-chip__icon ma-stat-chip__icon--amber">
                <FaClock />
              </div>
              <div>
                <span className="ma-stat-chip__value">{stats.pending}</span>
                <span className="ma-stat-chip__label">Pending</span>
              </div>
            </div>

            <div className="ma-stat-chip">
              <div className="ma-stat-chip__icon ma-stat-chip__icon--violet">
                <FaPlay />
              </div>
              <div>
                <span className="ma-stat-chip__value">{stats.inProgress}</span>
                <span className="ma-stat-chip__label">In progress</span>
              </div>
            </div>

            <div className="ma-stat-chip">
              <div className="ma-stat-chip__icon ma-stat-chip__icon--success">
                <FaCheck />
              </div>
              <div>
                <span className="ma-stat-chip__value">{stats.completed}</span>
                <span className="ma-stat-chip__label">Completed</span>
              </div>
            </div>

            <button type="button" className="ma-refresh" onClick={() => refetch()}>
              <FaSync />
              Refresh
            </button>
          </div>
        </motion.header>

        {/* ─── Toolbar ─────────────────────────────────── */}
        <motion.section className="ma-toolbar" variants={itemVariants}>
          <div className="ma-search">
            <FaSearch className="ma-search__icon" aria-hidden="true" />
            <input
              type="text"
              placeholder="Search by incident or customer…"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="ma-chip-row">
            {FILTERS.map((f) => (
              <button
                key={f.value}
                type="button"
                className={`ma-chip ${filterStatus === f.value ? 'is-active' : ''}`}
                onClick={() => setFilterStatus(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </motion.section>

        {/* ─── List ────────────────────────────────────── */}
        <motion.section className="ma-list-card" variants={itemVariants}>
          <div className="ma-list-card__header">
            <div className="ma-list-card__title">
              <FaInbox />
              <span>Assignments</span>
            </div>
            <div className="ma-list-card__meta">
              Showing <strong>{filteredAssignments.length}</strong> of <strong>{assignments.length}</strong>
            </div>
          </div>

          {filteredAssignments.length === 0 ? (
            <div className="ma-empty">
              <FaInbox className="ma-empty__icon" />
              <p>
                {searchTerm || filterStatus !== 'all'
                  ? 'No assignments match your filters.'
                  : 'You have no assignments yet.'}
              </p>
            </div>
          ) : (
            <ul className="ma-list">
              <AnimatePresence initial={false}>
                {filteredAssignments.map((assignment) => {
                  const isPending = assignment.status?.toLowerCase() === 'pending';
                  const isInProgress = assignment.status?.toLowerCase() === 'in_progress';
                  const priorityColor = getPriorityColor(assignment.priority);

                  return (
                    <motion.li
                      key={assignment.id}
                      className="ma-item"
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.25 }}
                    >
                      {/* Left: ref + priority + status */}
                      <div className="ma-item__ref">
                        <Link
                          to={`/incidents/${assignment.incident || assignment.incident_id}`}
                          className="ma-item__link"
                        >
                          {assignment.incident_number}
                        </Link>

                        <span
                          className="ma-priority"
                          style={{ '--priority-color': priorityColor }}
                        >
                          <span className="ma-priority__dot" />
                          {assignment.priority || 'N/A'}
                        </span>

                        <StatusBadge status={assignment.status?.toLowerCase()}>
                          {assignment.status}
                        </StatusBadge>
                      </div>

                      {/* Middle: customer */}
                      <div className="ma-item__customer">
                        <strong>{assignment.customer || '—'}</strong>
                        {assignment.customer_phone && (
                          <span className="ma-item__phone">
                            <FaPhone /> {assignment.customer_phone}
                          </span>
                        )}
                      </div>

                      {/* Dates */}
                      <div className="ma-item__dates">
                        <div>
                          <span className="ma-item__date-label">Assigned</span>
                          <span className="ma-item__date-value">
                            <FaCalendarAlt />
                            {new Date(assignment.assigned_at).toLocaleDateString()}
                          </span>
                        </div>
                        {assignment.target_resolution && (
                          <div>
                            <span className="ma-item__date-label">Due</span>
                            <span className="ma-item__date-value">
                              <FaClock />
                              {new Date(assignment.target_resolution).toLocaleDateString()}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="ma-item__actions">
                        {isPending && (
                          <>
                            <button
                              type="button"
                              className="ma-btn ma-btn--success"
                              onClick={() => handleAction(assignment.id, acceptMutation, 'accept')}
                              disabled={acceptMutation.isPending}
                            >
                              {acceptMutation.isPending ? (
                                <span className="ma-spinner ma-spinner--sm" />
                              ) : (
                                <FaCheck />
                              )}
                              Accept
                            </button>
                            <button
                              type="button"
                              className="ma-btn ma-btn--ghost"
                              onClick={() => handleAction(assignment.id, startMutation, 'start')}
                              disabled={startMutation.isPending}
                            >
                              {startMutation.isPending ? (
                                <span className="ma-spinner ma-spinner--sm ma-spinner--dark" />
                              ) : (
                                <FaPlay />
                              )}
                              Start
                            </button>
                          </>
                        )}

                        {isInProgress && (
                          <button
                            type="button"
                            className="ma-btn ma-btn--primary"
                            onClick={() =>
                              handleAction(assignment.id, completeMutation, 'complete')
                            }
                            disabled={completeMutation.isPending}
                          >
                            {completeMutation.isPending ? (
                              <span className="ma-spinner ma-spinner--sm" />
                            ) : (
                              <FaCheck />
                            )}
                            Complete
                          </button>
                        )}
                      </div>
                    </motion.li>
                  );
                })}
              </AnimatePresence>
            </ul>
          )}
        </motion.section>

        {/* ─── Footer ──────────────────────────────────── */}
        <motion.div className="ma-footer" variants={itemVariants}>
          <Link to="/artisan/dashboard" className="ma-back-link">
            <FaArrowLeft />
            Back to dashboard
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
};