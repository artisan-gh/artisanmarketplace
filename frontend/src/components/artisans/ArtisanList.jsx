import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getArtisans } from '../../api/artisansAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { SearchBar } from '../common/SearchBar';

export const ArtisanList = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [availabilityFilter, setAvailabilityFilter] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['artisans', { page, pageSize, search, availabilityFilter }],
    queryFn: () =>
      getArtisans({
        page,
        page_size: pageSize,
        search: search || undefined,
        is_available: availabilityFilter || undefined,
      }).then((res) => ({
        artisans: res.data.results || [],
        total: res.data.count,
      })),
    staleTime: 5 * 60 * 1000,
  });

  const artisans = data?.artisans || [];
  const total = data?.total || 0;

  const columns = [
    {
      key: 'user_detail',
      label: 'Artisan',
      render: (val, row) => (
        <span
          className="text-blue-600 hover:underline cursor-pointer"
          onClick={() => navigate(`/artisans/${row.id}`)}
        >
          {row.user_detail?.full_name || 'Unknown'}
        </span>
      ),
    },
    {
      key: 'user_detail.email',
      label: 'Email',
      render: (val, row) => row.user_detail?.email || '—',
    },
    {
      key: 'skills_list',
      label: 'Skills',
      render: (val) =>
        val?.length > 0 ? val.map((s) => s.name).join(', ') : '—',
    },
    {
      key: 'is_available',
      label: 'Availability',
      render: (val) => (val ? <StatusBadge status="active">Available</StatusBadge> : <StatusBadge status="inactive">Busy</StatusBadge>),
    },
    {
      key: 'average_rating',
      label: 'Rating',
      render: (val) => (val > 0 ? `${val.toFixed(1)} ★` : '—'),
    },
    {
      key: 'current_workload',
      label: 'Current Jobs',
      render: (val) => `${val || 0}`,
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <button
          onClick={() => navigate(`/artisans/${row.id}`)}
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          View
        </button>
      ),
    },
  ];

  if (error) {
    return <div className="text-red-500">Failed to load artisans.</div>;
  }

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="flex-1 min-w-[200px]">
          <SearchBar value={search} onChange={setSearch} placeholder="Search artisans..." />
        </div>
        <select
          value={availabilityFilter}
          onChange={(e) => setAvailabilityFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All</option>
          <option value="true">Available</option>
          <option value="false">Busy</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={artisans}
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