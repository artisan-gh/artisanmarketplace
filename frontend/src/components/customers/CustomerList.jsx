import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCustomers, deleteCustomer } from '../../api/customersAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { SearchBar } from '../common/SearchBar';
import { Modal } from '../common/Modal';

export const CustomerList = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // ─── Filters & pagination state ──────────────────────────
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  // ─── Fetch customers ──────────────────────────────────────
  const {
    data,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['customers', { page, pageSize, search }],
    queryFn: () =>
      getCustomers({
        page,
        page_size: pageSize,
        search: search || undefined,
      }).then((res) => ({
        customers: res.data.results || [],
        total: res.data.count,
      })),
    staleTime: 5 * 60 * 1000,
  });

  const customers = data?.customers || [];
  const total = data?.total || 0;

  // ─── Delete mutation ──────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: deleteCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      setShowDeleteModal(false);
    },
    onError: () => {
      alert('Failed to delete customer.');
    },
  });

  const handleDelete = () => {
    if (!selectedCustomer) return;
    deleteMutation.mutate(selectedCustomer.id);
  };

  const columns = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'phone', label: 'Phone' },
    { key: 'email', label: 'Email' },
    {
      key: 'created_at',
      label: 'Created',
      render: (val) => new Date(val).toLocaleDateString(),
    },
    {
      key: 'is_deleted',
      label: 'Status',
      render: (val) => (val ? <StatusBadge status="deleted" /> : <StatusBadge status="active" />),
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <div className="flex space-x-2">
          <button
            onClick={() => navigate(`/customers/${row.id}`)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            View
          </button>
          <button
            onClick={() => {
              setSelectedCustomer(row);
              setShowDeleteModal(true);
            }}
            className="text-red-600 hover:text-red-800 text-sm"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  // ─── Error state ──────────────────────────────────────────
  if (error) {
    return <div className="text-red-500 text-center py-8">Failed to load customers.</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Customers</h2>
        <button
          onClick={() => navigate('/customers/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add Customer
        </button>
      </div>

      <div className="mb-4 max-w-md">
        <SearchBar value={search} onChange={setSearch} placeholder="Search customers..." />
      </div>

      <DataTable
        columns={columns}
        data={customers}
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total,
          onPageChange: setPage,
          onPageSizeChange: setPageSize,
        }}
        onRowClick={(row) => navigate(`/customers/${row.id}`)}
      />

      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Confirm Delete"
      >
        <p className="text-gray-700">
          Are you sure you want to delete <strong>{selectedCustomer?.name}</strong>? This action can be undone.
        </p>
        <div className="mt-4 flex justify-end space-x-2">
          <button
            onClick={() => setShowDeleteModal(false)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </Modal>
    </div>
  );
};