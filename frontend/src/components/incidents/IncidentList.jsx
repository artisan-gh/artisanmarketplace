// src/components/incidents/IncidentList.jsx
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaSearch,
  FaFilter,
  FaTimes,
  FaExclamationTriangle,
  FaListAlt,
  FaClock,
  FaBolt,
} from 'react-icons/fa';
import { getIncidents } from '../../api/incidentsAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { SearchBar } from '../common/SearchBar';
import './IncidentList.css';

const STATUS_OPTIONS = [
  { value: 'NEW', label: 'New' },
  { value: 'OPEN', label: 'Open' },
  { value: 'ASSIGNED', label: 'Assigned' },
  { value: 'RESOLVED', label: 'Resolved' },
  { value: 'CLOSED', label: 'Closed' },
];

const PRIORITY_OPTIONS = [
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
  { value: 'CRITICAL', label: 'Critical' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
  },
};

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
  const { data, isLoading, error } = useQuery({
    queryKey: ['incidents', { page, pageSize, ...allFilters }],
    queryFn: () =>
      getIncidents({
        page,
        page_size: pageSize,
        ...allFilters,
      }).then((res) => ({
        incidents: res.results || [],
        total: res.count || 0,
      })),
    staleTime: 5 * 60 * 1000,
  });

  const incidents = data?.incidents || [];
  const total = data?.total || 0;
  const hasActiveFilters = search || statusFilter || priorityFilter;

  const activeFilterCount = useMemo(
    () => [statusFilter, priorityFilter].filter(Boolean).length + (search ? 1 : 0),
    [search, statusFilter, priorityFilter]
  );

  // ─── Handlers that reset page to 1 when filters change ──
  const handleSearch = (val) => {
    setSearch(val);
    setPage(1);
  };

  const handleStatusChange = (val) => {
    setStatusFilter(val);
    setPage(1);
  };

  const handlePriorityChange = (val) => {
    setPriorityFilter(val);
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
          className="il-ref"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/incidents/${row.id}`);
          }}
        >
          <span className="il-ref__dot" />
          {val}
        </span>
      ),
    },
    {
      key: 'title',
      label: 'Title',
      render: (val) => <span className="il-title">{val}</span>,
    },
    {
      key: 'customer_name',
      label: 'Customer',
      render: (val) => <span className="il-muted">{val || '—'}</span>,
    },
    {
      key: 'priority',
      label: 'Priority',
      render: (val) => (
        <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>
      ),
    },
    {
      key: 'status_name',
      label: 'Status',
      render: (val) => (
        <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (val) => (
        <span className="il-date">
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
      <div className="il-page">
        <motion.div
          className="il-state il-state--error"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="il-state__icon">
            <FaExclamationTriangle />
          </div>
          <div>
            <h3>Failed to load incidents</h3>
            <p>Something went wrong while fetching the incident list. Please try again.</p>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="il-page">
      <motion.div
        className="il-shell"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* ─── Hero header ────────────────────────────────── */}
        <motion.header className="il-hero" variants={itemVariants}>
          <div className="il-hero__left">
            <div className="il-hero__icon">
              <FaListAlt />
            </div>
            <div>
              <span className="il-eyebrow">Operations</span>
              <h1>Incident list</h1>
              <p>Track, filter, and manage every incident in one place.</p>
            </div>
          </div>

          <div className="il-hero__right">
            <div className="il-stat-chip">
              <div className="il-stat-chip__icon il-stat-chip__icon--primary">
                <FaListAlt />
              </div>
              <div>
                <span className="il-stat-chip__value">{total}</span>
                <span className="il-stat-chip__label">
                  {total === 1 ? 'Incident' : 'Incidents'}
                </span>
              </div>
            </div>

            <div className="il-stat-chip">
              <div className="il-stat-chip__icon il-stat-chip__icon--amber">
                <FaBolt />
              </div>
              <div>
                <span className="il-stat-chip__value">{activeFilterCount}</span>
                <span className="il-stat-chip__label">
                  {activeFilterCount === 1 ? 'Filter' : 'Filters'}
                </span>
              </div>
            </div>

            <div className="il-stat-chip">
              <div className="il-stat-chip__icon il-stat-chip__icon--violet">
                <FaClock />
              </div>
              <div>
                <span className="il-stat-chip__value">Live</span>
                <span className="il-stat-chip__label">Updates</span>
              </div>
            </div>
          </div>
        </motion.header>

        {/* ─── Toolbar ─────────────────────────────────────── */}
        <motion.section className="il-toolbar" variants={itemVariants}>
          <div className="il-toolbar__search">
            <div className="il-search">
              <FaSearch className="il-search__icon" aria-hidden="true" />
              <div className="il-search__inner">
                <SearchBar
                  value={search}
                  onChange={handleSearch}
                  placeholder="Search incidents by ref, title, or customer…"
                />
              </div>
            </div>
          </div>

          <div className="il-toolbar__filters">
            <div className="il-filter-group">
              <label className="il-filter-label">Status</label>
              <div className="il-chip-row">
                <button
                  type="button"
                  className={`il-chip ${!statusFilter ? 'is-active' : ''}`}
                  onClick={() => handleStatusChange('')}
                >
                  All
                </button>
                {STATUS_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    className={`il-chip ${statusFilter === opt.value ? 'is-active' : ''}`}
                    onClick={() => handleStatusChange(opt.value)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="il-filter-group">
              <label className="il-filter-label">Priority</label>
              <div className="il-chip-row">
                <button
                  type="button"
                  className={`il-chip ${!priorityFilter ? 'is-active' : ''}`}
                  onClick={() => handlePriorityChange('')}
                >
                  All
                </button>
                {PRIORITY_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    className={`il-chip il-chip--priority ${priorityFilter === opt.value ? 'is-active' : ''}`}
                    data-priority={opt.value.toLowerCase()}
                    onClick={() => handlePriorityChange(opt.value)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <AnimatePresence>
              {hasActiveFilters && (
                <motion.button
                  type="button"
                  className="il-clear"
                  onClick={clearFilters}
                  initial={{ opacity: 0, scale: 0.9, x: -8 }}
                  animate={{ opacity: 1, scale: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.9, x: -8 }}
                  transition={{ duration: 0.2 }}
                >
                  <FaTimes />
                  Clear filters
                </motion.button>
              )}
            </AnimatePresence>
          </div>
        </motion.section>

        {/* ─── Table ──────────────────────────────────────── */}
        <motion.section className="il-table-card" variants={itemVariants}>
          <div className="il-table-card__header">
            <div className="il-table-card__title">
              <FaFilter />
              <span>Results</span>
            </div>
            <div className="il-table-card__meta">
              {isLoading ? (
                <>
                  <span className="il-spinner" />
                  Loading…
                </>
              ) : (
                <>
                  Showing <strong>{incidents.length}</strong> of <strong>{total}</strong>
                </>
              )}
            </div>
          </div>

          <div className="il-table-card__body">
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
        </motion.section>
      </motion.div>
    </div>
  );
};

IncidentList.propTypes = {
  filters: PropTypes.object,
};