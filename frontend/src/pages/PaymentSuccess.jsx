// src/pages/PaymentSuccess.jsx
import { useSearchParams, Link } from 'react-router-dom';
import './PaymentSuccess.css';

export const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const invoiceNumber = searchParams.get('invoice') || '—';
  const status = searchParams.get('status') || 'paid';
  const invoiceId = searchParams.get('invoiceId');
  const token = searchParams.get('token'); // public token from the verify endpoint

  return (
    <div className="payment-success">
      <div className="payment-success__card">
        <div className="payment-success__icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              className="payment-success__check-path"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h1 className="payment-success__title">Payment successful</h1>
        <p className="payment-success__subtitle">
          Thank you for your payment. Your transaction has been completed successfully.
        </p>

        <div className="payment-success__details">
          <div className="payment-success__detail-row">
            <span className="payment-success__detail-label">Invoice</span>
            <span className="payment-success__detail-value">{invoiceNumber}</span>
          </div>
          <div className="payment-success__detail-row">
            <span className="payment-success__detail-label">Status</span>
            <span className="payment-success__detail-value payment-success__detail-value--status">{status}</span>
          </div>
        </div>

        <div className="payment-success__actions">
          {/* ─── View all my invoices (filtered) ─────────────── */}
          {/* If token exists, the user is likely not logged in, so hide this link */}
          {!token && (
            <Link to="/billing/invoices?mine=true" className="btn btn-outline">
              View my invoices
            </Link>
          )}

          {/* ─── View this specific invoice ──────────────────── */}
          {token ? (
            <Link to={`/billing/invoices/public/${token}`} className="btn btn-primary">
              View this invoice
            </Link>
          ) : invoiceId ? (
            <Link to={`/billing/invoices/${invoiceId}`} className="btn btn-primary">
              View this invoice
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  );
};