import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getMyAssignments } from '../../api/assignmentsAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';

export const ArtisanJobs = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const { data, isLoading, error } = useQuery({
    queryKey: ['myAssignments', { page, pageSize }],
    queryFn: () =>
      getMyAssignments().then((res) => ({
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
          className="text-blue-600 hover:underline cursor-pointer"
          onClick={() => navigate(`/incidents/${row.incident}`)}
        >
          {val || 'N/A'}
        </span>
      ),
    },
    {
      key: 'incident.title',
      label: 'Title',
      render: (val, row) => row.incident?.title || '—',
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>,
    },
    {
      key: 'assigned_at',
      label: 'Assigned',
      render: (val) => new Date(val).toLocaleString(),
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <button
          onClick={() => navigate(`/jobs/${row.id}`)}
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          View
        </button>
      ),
    },
  ];

  if (error) {
    return <div className="text-red-500">Failed to load your jobs.</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">My Jobs</h2>
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
  );
};