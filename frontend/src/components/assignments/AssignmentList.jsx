// src/components/assignments/AssignmentList.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAssignments } from '../../api/assignmentsAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { SearchBar } from '../common/SearchBar';
import { useAuth } from '../../context/AuthContext';
import './AssignmentList.css';

// ─── Icons ──────────────────────────────────────────────────
const IconEye = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);
const IconEdit = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
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

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'PENDING', label: 'Pending' },
  { value: 'ACCEPTED', label: 'Accepted' },
  { value: 'REJECTED', label: 'Rejected' },
  { value: 'IN_PROGRESS', label: 'In progress' },
  { value: 'COMPLETED', label: 'Completed' },
];

export const AssignmentList = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();  // <-- get logout function
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('PENDING');

  const { data, isLoading, error } = useQuery({
    queryKey: ['assignments', { page, pageSize, search, statusFilter }],
    queryFn: () =>
      getAssignments({
        page,
        page_size: pageSize,
        search: search || undefined,
        status: statusFilter || undefined,
      }).then((res) => ({
        assignments: res.data.results || [],
        total: res.data.count,
      })),
    staleTime: 5 * 60 * 1000,
  });

  const assignments = data?.assignments || [];
  const total = data?.total || 0;

  const columns = [
    {
      key: 'incident_number',
      label: 'Incident',
      render: (val, row) => (
        <span
          className="assignment-link"
          onClick={() => navigate(`/incidents/${row.incident}`)}
        >
          {val || 'N/A'}
        </span>
      ),
    },
    {
      key: 'artisan_name',
      label: 'Artisan',
      render: (val) => val || <span className="assignment-unassigned">Unassigned</span>,
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>,
    },
    {
      key: 'assigned_at',
      label: 'Assigned At',
      render: (val) => <span className="assignment-date">{new Date(val).toLocaleString()}</span>,
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <div className="assignment-actions">
          <button
            onClick={() => navigate(`/assignments/${row.id}`)}
            className="assignment-action assignment-action--view"
          >
            <IconEye className="assignment-action__icon" />
            View
          </button>
          {row.status === 'PENDING' && (
            <button
              onClick={() => navigate(`/assignments/${row.id}/edit`)}
              className="assignment-action assignment-action--assign"
            >
              <IconEdit className="assignment-action__icon" />
              Assign
            </button>
          )}
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <div className="assignment-list-page">
        <div className="state-banner state-banner--error">
          <IconAlertCircle className="state-banner__icon" />
          <p>Failed to load assignments. Try refreshing the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="assignment-list-page">
      {/* ─── Header with logout ─────────────────────────────── */}
      <div className="assignment-list-header">
        <div>
          <h1 className="assignment-list-title">Assignments</h1>
          <span className="assignment-list-count">{total} total</span>
        </div>
        <button
          type="button"
          onClick={logout}
          className="logout-btn"
        >
          <IconLogout className="logout-btn__icon" />
          Log out
        </button>
      </div>

      <div className="assignment-filters">
        <div className="assignment-filters__search">
          <SearchBar value={search} onChange={setSearch} placeholder="Search by incident number..." />
        </div>
        <div className="assignment-filters__select-wrap">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="assignment-select"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="assignment-table-wrap">
        <DataTable
          columns={columns}
          data={assignments}
          loading={isLoading}
          pagination={{
            current: page,
            pageSize,
            total,
            onPageChange: setPage,
            onPageSizeChange: setPageSize,
          }}
        />
      </div>
    </div>
  );
};