// src/components/sla/SLAPolicyList.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getSLAPolicies, deleteSLAPolicy } from '../../api/slaAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';

export const SLAPolicyList = () => {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['slaPolicies'],
    queryFn: () => getSLAPolicies().then(res => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteSLAPolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['slaPolicies'] });
    },
  });

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'priority', label: 'Priority' },
    { key: 'resolution_hours', label: 'Resolution (hrs)' },
    { key: 'escalation_hours', label: 'Escalation (hrs)', render: (val) => val || '—' },
    {
      key: 'is_active',
      label: 'Active',
      render: (val) => (
        <StatusBadge status={val ? 'success' : 'inactive'}>{val ? 'Yes' : 'No'}</StatusBadge>
      ),
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <div className="flex gap-2">
          <Link
            to={`/sla/policies/${row.id}`}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            Edit
          </Link>
          <button
            onClick={() => {
              if (window.confirm('Delete this SLA policy?')) {
                deleteMutation.mutate(row.id);
              }
            }}
            className="text-red-600 hover:text-red-800 text-sm"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">SLA Policies</h2>
        <Link to="/sla/policies/new" className="btn btn-primary">
          New Policy
        </Link>
      </div>
      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
      />
    </div>
  );
};