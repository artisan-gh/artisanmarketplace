// src/components/incidents/IncidentList.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { getIncidents } from '../../api/incidentsAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { SearchBar } from '../common/SearchBar';
import './IncidentList.css';

export const IncidentList = ({ filters: externalFilters = {} }) => {
  const navigate = useNavigate();

  // ─── Local filter state ──────────────────────────────────
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  // ─── Merge external filters ──────────────────────────────
  const allFilters = {
    ...externalFilters,
    search: search || undefined,
    status: statusFilter || undefined,
    priority: priorityFilter || undefined,
  };

  // ─── Fetch incidents ──────────────────────────────────────
  const {
    data,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['incidents', { page, pageSize, ...allFilters }],
    queryFn: () =>
      getIncidents({
        page,
        page_size: pageSize,
        ...allFilters,
      }).then((res) => {
        // ✅ FIX: res is already the parsed JSON body
        return {
          incidents: res.results || [],
          total: res.count || 0,
        };
      }),
    staleTime: 5 * 60 * 1000,
  });

  const incidents = data?.incidents || [];
  const total = data?.total || 0;
  const hasActiveFilters = search || statusFilter || priorityFilter;

  // ─── Handlers that reset page to 1 when filters change ──
  const handleSearch = (val) => {
    setSearch(val);
    setPage(1);
  };

  const handleStatusChange = (e) => {
    setStatusFilter(e.target.value);
    setPage(1);
  };

  const handlePriorityChange = (e) => {
    setPriorityFilter(e.target.value);
    setPage(1);
  };

  const clearFilters = () => {
    setSearch('');
    setStatusFilter('');
    setPriorityFilter('');
    setPage(1);
  };

  const columns = [
    {
      key: 'incident_number',
      label: 'Incident',
      render: (val, row) => (
        <span
          className="incident-list-link"
          onClick={() => navigate(`/incidents/${row.id}`)}
        >
          {val}
        </span>
      ),
    },
    {
      key: 'title',
      label: 'Title',
      render: (val) => <span className="incident-list-title">{val}</span>,
    },
    {
      key: 'customer_name',
      label: 'Customer',
      render: (val) => <span className="incident-list-muted">{val || '—'}</span>,
    },
    {
      key: 'priority',
      label: 'Priority',
      render: (val) => <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>,
    },
    {
      key: 'status_name',
      label: 'Status',
      render: (val) => <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>,
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (val) => (
        <span className="incident-list-date">
          {new Date(val).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          })}
        </span>
      ),
    },
  ];

  if (error) {
    console.error('IncidentList error:', error);
    return (
      <div className="incident-list-error">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <span>Failed to load incidents. Please try again.</span>
      </div>
    );
  }

  return (
    <div className="incident-list-page">
      {/* ─── Filter toolbar ─────────────────────────────── */}
      <div className="incident-list-toolbar">
        <div className="incident-list-search">
          <SearchBar value={search} onChange={handleSearch} placeholder="Search incidents..." />
        </div>

        <select value={statusFilter} onChange={handleStatusChange} className="incident-list-select">
          <option value="">All Statuses</option>
          <option value="NEW">New</option>
          <option value="OPEN">Open</option>
          <option value="ASSIGNED">Assigned</option>
          <option value="RESOLVED">Resolved</option>
          <option value="CLOSED">Closed</option>
        </select>

        <select value={priorityFilter} onChange={handlePriorityChange} className="incident-list-select">
          <option value="">All Priorities</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
        </select>

        {hasActiveFilters && (
          <button onClick={clearFilters} className="incident-list-clear">
            Clear filters
          </button>
        )}

        <div className="incident-list-count">
          {total} {total === 1 ? 'incident' : 'incidents'}
        </div>
      </div>

      {/* ─── Table ──────────────────────────────────────── */}
      <div className="incident-list-table-card">
        <DataTable
          columns={columns}
          data={incidents}
          loading={isLoading}
          pagination={{
            current: page,
            pageSize,
            total,
            onPageChange: setPage,
            onPageSizeChange: setPageSize,
          }}
          onRowClick={(row) => navigate(`/incidents/${row.id}`)}
        />
      </div>
    </div>
  );
};

IncidentList.propTypes = {
  filters: PropTypes.object,
};