// src/components/assignments/MyAssignments.jsx
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getMyAssignments } from '../../api/assignmentsAPI';
import { acceptAssignment, startAssignment, completeAssignment } from '../../api/assignmentsAPI';
import { StatusBadge } from '../common/StatusBadge';
import './MyAssignments.css';

// ─── Priority color mapping ──────────────────────────────────
const PRIORITY_COLORS = {
  LOW: '#64748b',
  MEDIUM: '#3b82f6',
  HIGH: '#f59e0b',
  CRITICAL: '#f87171',
  URGENT: '#f87171',
};

const getPriorityColor = (priority) =>
  PRIORITY_COLORS[priority?.toUpperCase()] || '#94a3b8';

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
  const stats = useMemo(() => ({
    total: assignments.length,
    pending: assignments.filter((a) => a.status?.toLowerCase() === 'pending').length,
    inProgress: assignments.filter((a) => a.status?.toLowerCase() === 'in_progress').length,
    completed: assignments.filter((a) => a.status?.toLowerCase() === 'completed').length,
  }), [assignments]);

  const handleAction = (id, mutation, actionName) => {
    if (window.confirm(`Are you sure you want to ${actionName} this assignment?`)) {
      mutation.mutate(id);
    }
  };

  if (isLoading) return <div className="my-assignments__loading">Loading your assignments...</div>;
  if (error) return <div className="my-assignments__error">Failed to load assignments.</div>;

  return (
    <div className="my-assignments">
      <div className="my-assignments__header">
        <h1>My Assignments</h1>
        <div className="my-assignments__stats">
          <span className="stat-badge">Total: {stats.total}</span>
          <span className="stat-badge stat-badge--pending">Pending: {stats.pending}</span>
          <span className="stat-badge stat-badge--progress">In Progress: {stats.inProgress}</span>
          <span className="stat-badge stat-badge--completed">Completed: {stats.completed}</span>
        </div>
        <button className="refresh-btn" onClick={() => refetch()}>
          ↻ Refresh
        </button>
      </div>

      <div className="my-assignments__filters">
        <div className="filter-tabs">
          {['all', 'pending', 'in_progress', 'completed'].map((status) => (
            <button
              key={status}
              className={`filter-tab ${filterStatus === status ? 'active' : ''}`}
              onClick={() => setFilterStatus(status)}
            >
              {status.replace('_', ' ').charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by incident or customer..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {filteredAssignments.length === 0 ? (
        <div className="my-assignments__empty">
          <p>
            {searchTerm || filterStatus !== 'all'
              ? 'No assignments match your filters.'
              : 'You have no assignments yet.'}
          </p>
        </div>
      ) : (
        <ul className="assignment-list">
          {filteredAssignments.map((assignment) => {
            const isPending = assignment.status?.toLowerCase() === 'pending';
            const isInProgress = assignment.status?.toLowerCase() === 'in_progress';

            return (
              <li key={assignment.id} className="assignment-item">
                <div className="assignment-item__main">
                  <div className="assignment-item__ref">
                    {/* ✅ FIX: use the incident UUID for routing */}
                    <Link
                      to={`/incidents/${assignment.incident || assignment.incident_id}`}
                      className="assignment-item__link"
                    >
                      {assignment.incident_number}
                    </Link>
                    <span
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(assignment.priority) }}
                    >
                      {assignment.priority || 'N/A'}
                    </span>
                    <StatusBadge status={assignment.status?.toLowerCase()}>
                      {assignment.status}
                    </StatusBadge>
                  </div>
                  <div className="assignment-item__customer">
                    <span className="customer-name">{assignment.customer || '—'}</span>
                    {assignment.customer_phone && (
                      <span className="customer-phone">📞 {assignment.customer_phone}</span>
                    )}
                  </div>
                  <div className="assignment-item__dates">
                    <span className="date-label">Assigned:</span>
                    <span>{new Date(assignment.assigned_at).toLocaleDateString()}</span>
                    {assignment.target_resolution && (
                      <>
                        <span className="date-label">Due:</span>
                        <span className="due-date">
                          {new Date(assignment.target_resolution).toLocaleDateString()}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="assignment-item__actions">
                  {isPending && (
                    <>
                      <button
                        className="btn btn-sm btn-success"
                        onClick={() => handleAction(assignment.id, acceptMutation, 'accept')}
                        disabled={acceptMutation.isPending}
                      >
                        {acceptMutation.isPending ? '...' : 'Accept'}
                      </button>
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => handleAction(assignment.id, startMutation, 'start')}
                        disabled={startMutation.isPending}
                      >
                        {startMutation.isPending ? '...' : 'Start'}
                      </button>
                    </>
                  )}
                  {isInProgress && (
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => handleAction(assignment.id, completeMutation, 'complete')}
                      disabled={completeMutation.isPending}
                    >
                      {completeMutation.isPending ? '...' : 'Complete'}
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <div className="my-assignments__footer">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <span className="count-info">Showing {filteredAssignments.length} of {assignments.length} assignments</span>
      </div>
    </div>
  );
};