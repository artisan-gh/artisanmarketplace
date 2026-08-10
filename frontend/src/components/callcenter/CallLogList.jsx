import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getCallLogs } from '../../api/call_centerAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { SearchBar } from '../common/SearchBar';

export const CallLogList = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [dispositionFilter, setDispositionFilter] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['callLogs', { page, pageSize, search, dispositionFilter }],
    queryFn: () =>
      getCallLogs({
        page,
        page_size: pageSize,
        search: search || undefined,
        disposition: dispositionFilter || undefined,
      }).then(res => ({
        logs: res.data.results || [],
        total: res.data.count,
      })),
    staleTime: 5 * 60 * 1000,
  });

  const logs = data?.logs || [];
  const total = data?.total || 0;

  const columns = [
    {
      key: 'reference',
      label: 'Reference',
      render: (val, row) => (
        <span
          className="text-blue-600 hover:underline cursor-pointer"
          onClick={() => navigate(`/call-center/logs/${row.id}`)}
        >
          {val}
        </span>
      ),
    },
    {
      key: 'customer_name',
      label: 'Customer',
      render: (val) => val || '—',
    },
    {
      key: 'call_type',
      label: 'Direction',
    },
    {
      key: 'phone_number',
      label: 'Phone',
    },
    {
      key: 'disposition',
      label: 'Disposition',
      render: (val) => <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>,
    },
    {
      key: 'started_at',
      label: 'Started',
      render: (val) => new Date(val).toLocaleString(),
    },
    {
      key: 'duration_seconds',
      label: 'Duration',
      render: (val) => val ? `${Math.floor(val / 60)}m ${val % 60}s` : '—',
    },
    {
      key: 'is_resolved',
      label: 'Resolved',
      render: (val) => val ? '✅' : '❌',
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <button
          onClick={() => navigate(`/call-center/logs/${row.id}`)}
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          View
        </button>
      ),
    },
  ];

  if (error) return <div className="text-red-500">Failed to load call logs.</div>;

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="flex-1 min-w-[200px]">
          <SearchBar value={search} onChange={setSearch} placeholder="Search by reference or phone..." />
        </div>
        <select
          value={dispositionFilter}
          onChange={(e) => setDispositionFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All Dispositions</option>
          <option value="RESOLVED">Resolved</option>
          <option value="ESCALATED">Escalated</option>
          <option value="PENDING">Pending</option>
          <option value="CALLBACK">Callback</option>
          <option value="NO_ANSWER">No Answer</option>
          <option value="VOICEMAIL">Voicemail</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={logs}
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
  );
};