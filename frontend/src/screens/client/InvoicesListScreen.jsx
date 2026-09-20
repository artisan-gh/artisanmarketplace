
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FaFileInvoiceDollar, FaCircleNotch } from 'react-icons/fa';
import { listMyInvoices } from '../../api/clientBilling';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;
const STATUS_LABELS = { DRAFT: 'Draft', SENT: 'Unpaid', VIEWED: 'Unpaid',
  PARTIALLY_PAID: 'Partial', PAID: 'Paid', OVERDUE: 'Overdue' };

export default function InvoicesListScreen() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['myInvoices'], queryFn: listMyInvoices,
  });
  const invoices = data?.results || data || [];

  if (isLoading) return (
    <div className="cp-page cp-page--center"><FaCircleNotch className="cp-spin" /></div>
  );
  if (error) return (
    <div className="cp-page cp-page--center"><p className="cp-error">Could not load invoices.</p></div>
  );

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaFileInvoiceDollar /></div>
          <div>
            <span className="cp-eyebrow">Billing</span>
            <h1>My invoices</h1>
            <p>{invoices.length} invoice{invoices.length === 1 ? '' : 's'}</p>
          </div>
        </header>

        {invoices.length === 0 ? (
          <div className="cp-empty">
            <FaFileInvoiceDollar className="cp-empty__icon" />
            <p>You have no invoices yet.</p>
          </div>
        ) : (
          <ul className="cp-list">
            {invoices.map((inv) => {
              const isPaid = inv.status === 'PAID';
              return (
                <li key={inv.id} className="cp-list-row">
                  <div className="cp-list-row__main">
                    <Link to={`/client/invoices/${inv.id}`} className="cp-list-row__ref">
                      {inv.invoice_number}
                    </Link>
                    <span className={`cp-status cp-status--${(inv.status || '').toLowerCase()}`}>
                      {STATUS_LABELS[inv.status] || inv.status}
                    </span>
                    <div className="cp-list-row__meta">
                      <span>Issued {new Date(inv.issued_date).toLocaleDateString()}</span>
                      {inv.due_date && !isPaid && (
                        <span>· Due {new Date(inv.due_date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="cp-list-row__amount">
                    <strong>{fmt(inv.grand_total, inv.currency)}</strong>
                    {!isPaid && Number(inv.balance_due) > 0 && (
                      <span className="cp-list-row__due">Due {fmt(inv.balance_due, inv.currency)}</span>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
