// src/components/billing/PaymentDetail.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getPayment } from '../../api/billingAPI';
import { StatusBadge } from '../common/StatusBadge';
import { Link } from 'react-router-dom';

export const PaymentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: payment, isLoading } = useQuery({
    queryKey: ['payment', id],
    queryFn: () => getPayment(id).then((res) => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (!payment) return <div className="text-center py-8 text-red-500">Payment not found.</div>;

  const statusColorMap = {
    pending: 'warning',
    processing: 'info',
    successful: 'success',
    failed: 'error',
    refunded: 'inactive',
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex justify-between items-start mb-6">
        <h1 className="text-2xl font-bold">Payment Details</h1>
        <button
          onClick={() => navigate('/billing/payments')}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p><strong>Reference:</strong> {payment.reference || payment.payment_reference}</p>
            <p><strong>Customer:</strong> {payment.customer?.name || '—'}</p>
            <p><strong>Amount:</strong> ₵{payment.amount?.toFixed(2) || '0.00'}</p>
            <p>
              <strong>Status:</strong>{' '}
              <StatusBadge status={statusColorMap[payment.status?.toLowerCase()] || 'default'}>
                {payment.status}
              </StatusBadge>
            </p>
          </div>
          <div>
            <p><strong>Gateway:</strong> {payment.gateway || '—'}</p>
            <p><strong>Gateway Reference:</strong> {payment.gateway_reference || '—'}</p>
            <p><strong>Paid At:</strong> {payment.paid_at ? new Date(payment.paid_at).toLocaleString() : '—'}</p>
            <p><strong>Created:</strong> {new Date(payment.created_at).toLocaleString()}</p>
          </div>
        </div>

        {payment.notes && (
          <div>
            <p><strong>Notes:</strong></p>
            <p className="text-gray-700">{payment.notes}</p>
          </div>
        )}

        {payment.invoice && (
          <div>
            <p><strong>Invoice:</strong> <Link to={`/billing/invoices/${payment.invoice}`} className="text-blue-600 hover:underline">{payment.invoice_number || payment.invoice}</Link></p>
          </div>
        )}

        {payment.allocations?.length > 0 && (
          <div>
            <p><strong>Allocations:</strong></p>
            <ul className="list-disc list-inside">
              {payment.allocations.map((alloc) => (
                <li key={alloc.id}>
                  {alloc.invoice_number}: ₵{alloc.amount?.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};