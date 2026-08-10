// src/components/billing/PaymentList.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPayments } from '../../api/billingAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { Link } from 'react-router-dom';

export const PaymentList = () => {
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const { data, isLoading } = useQuery({
    queryKey: ['payments', { page, pageSize, status: statusFilter, search }],
    queryFn: () =>
      getPayments({
        page,
        page_size: pageSize,
        status: statusFilter || undefined,
        search: search || undefined,
      }).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const columns = [
    {
      key: 'reference',
      label: 'Reference',
      render: (val, row) => (
        <Link to={`/billing/payments/${row.id}`} className="text-blue-600 hover:underline">
          {val || row.payment_reference}
        </Link>
      ),
    },
    { key: 'customer_name', label: 'Customer' },
    {
      key: 'amount',
      label: 'Amount',
      render: (val) => `₵${val?.toFixed(2) || '0.00'}`,
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => {
        const colorMap = {
          pending: 'warning',
          processing: 'info',
          successful: 'success',
          failed: 'error',
          refunded: 'inactive',
        };
        return <StatusBadge status={colorMap[val?.toLowerCase()] || 'default'}>{val}</StatusBadge>;
      },
    },
    {
      key: 'paid_at',
      label: 'Paid At',
      render: (val) => (val ? new Date(val).toLocaleString() : '—'),
    },
    {
      key: 'gateway',
      label: 'Gateway',
      render: (val) => val || '—',
    },
  ];

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <input
          type="text"
          placeholder="Search by reference or customer..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md flex-1 min-w-[200px]"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="successful">Successful</option>
          <option value="failed">Failed</option>
          <option value="refunded">Refunded</option>
        </select>
        <Link to="/billing/payments/new" className="btn btn-primary">
          New Payment
        </Link>
      </div>
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