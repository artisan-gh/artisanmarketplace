import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCustomer, deleteCustomer } from '../../api/customersAPI';
import { IncidentList } from '../incidents/IncidentList';

export const CustomerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // ─── Fetch customer ──────────────────────────────────────
  const {
    data: customer,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => getCustomer(id).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  // ─── Delete mutation ────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: () => deleteCustomer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      navigate('/customers');
    },
    onError: () => {
      alert('Failed to delete customer.');
    },
  });

  const handleDelete = () => {
    if (window.confirm('Delete this customer?')) {
      deleteMutation.mutate();
    }
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-500">Failed to load customer.</div>;
  if (!customer) return <div className="text-center py-8">Customer not found</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold">{customer.name}</h1>
          <p className="text-gray-600">{customer.phone} · {customer.email}</p>
          <p className="text-sm text-gray-500">{customer.address}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => navigate(`/customers/${id}/edit`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Incident History</h2>
        <IncidentList filters={{ customer: id }} />
      </div>
    </div>
  );
};