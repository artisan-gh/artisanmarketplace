// src/components/audit/AuditLogList.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAuditLogs, exportAuditLogs } from '../../api/auditAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';

export const AuditLogList = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // ─── Fetch logs ─────────────────────────────────────────────
  const { data, isLoading, error } = useQuery({
    queryKey: [
      'auditLogs',
      { page, pageSize, search, user: userFilter, action: actionFilter, date_from: dateFrom, date_to: dateTo },
    ],
    queryFn: () =>
      getAuditLogs({
        page,
        page_size: pageSize,
        search: search || undefined,
        user: userFilter || undefined,
        action: actionFilter || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }).then((res) => res.data),
    staleTime: 2 * 60 * 1000,
  });

  // ─── Export ──────────────────────────────────────────────────
  const handleExport = async () => {
    try {
      const blob = await exportAuditLogs({
        user: userFilter || undefined,
        action: actionFilter || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'audit_logs.csv';
      link.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // ✅ Removed unused `err` variable
      alert('Export failed. Please try again.');
    }
  };

  const columns = [
    {
      key: 'timestamp',
      label: 'Timestamp',
      render: (val) => (val ? format(new Date(val), 'PPpp') : '—'),
    },
    {
      key: 'user_email',
      label: 'User',
      render: (val, row) => (
        <span className="font-medium">{val || row.user || 'System'}</span>
      ),
    },
    {
      key: 'action',
      label: 'Action',
      render: (val) => (
        <StatusBadge status={val?.toLowerCase().replace('_', '-')}>
          {val?.replace('_', ' ')}
        </StatusBadge>
      ),
    },
    {
      key: 'object_repr',
      label: 'Object',
      render: (val, row) => (
        <span>
          {row.object_type}: {val || '—'}
        </span>
      ),
    },
    {
      key: 'changes',
      label: 'Changes',
      render: (val) => {
        if (!val) return '—';
        const changes = typeof val === 'string' ? JSON.parse(val) : val;
        const keys = Object.keys(changes);
        if (keys.length === 0) return '—';
        return (
          <div className="text-sm">
            {keys.slice(0, 2).map((key) => (
              <div key={key}>
                <span className="text-gray-500">{key}:</span>{' '}
                <span className="font-mono text-xs">
                  {changes[key]?.old || '—'} → {changes[key]?.new || '—'}
                </span>
              </div>
            ))}
            {keys.length > 2 && <span className="text-gray-400">+{keys.length - 2} more</span>}
          </div>
        );
      },
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <Link
          to={`/audit/logs/${row.id}`}
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          View
        </Link>
      ),
    },
  ];

  if (error) return <div className="text-red-500">Failed to load audit logs.</div>;

  return (
    <div>
      {/* ─── Filters ────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <input
          type="text"
          placeholder="Search by user, object, action..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md flex-1 min-w-[200px]"
        />
        <input
          type="text"
          placeholder="User email"
          value={userFilter}
          onChange={(e) => setUserFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        />
        <input
          type="text"
          placeholder="Action"
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        />
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        />
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        />
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Export CSV
        </button>
      </div>

      {/* ─── Table ──────────────────────────────────────────── */}
      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.count || 0,
          onPageChange: setPage,
          onPageSizeChange: setPageSize,
        }}
      />
    </div>
  );
};