
import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FaFileInvoiceDollar, FaCircleNotch, FaCheckCircle, FaArrowLeft, FaLock } from 'react-icons/fa';
import { getMyInvoice, payMyInvoice } from '../../api/clientBilling';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;

export default function InvoiceDetailScreen() {
  const { id } = useParams();
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState('');
  const { data: invoice, isLoading, error: loadErr } = useQuery({
    queryKey: ['myInvoice', id], queryFn: () => getMyInvoice(id),
  });

  const handlePay = async () => {
    setPaying(true); setError('');
    try {
      const res = await payMyInvoice(id);
      if (res?.authorization_url) window.location.href = res.authorization_url;
    } catch (e) {
      setError(e?.response?.data?.detail || 'Payment initialization failed.');
    } finally { setPaying(false); }
  };

  if (isLoading) return <div className="cp-page cp-page--center"><FaCircleNotch className="cp-spin" /></div>;
  if (loadErr || !invoice) return <div className="cp-page cp-page--center"><p className="cp-error">Invoice not found.</p></div>;

  const isPaid = invoice.status === 'PAID';
  return (
    <div className="cp-page">
      <div className="cp-shell">
        <Link to="/client/invoices" className="cp-back"><FaArrowLeft /> Back</Link>
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaFileInvoiceDollar /></div>
          <div>
            <span className="cp-eyebrow">Invoice</span>
            <h1>{invoice.invoice_number}</h1>
            <p>{isPaid ? 'Paid in full' : 'Awaiting payment'}</p>
          </div>
        </header>

        {isPaid && (
          <div className="cp-banner cp-banner--success">
            <FaCheckCircle />
            <div><strong>Paid</strong><p>Thank you for your payment.</p></div>
          </div>
        )}

        <section className="cp-card">
          <h3>Line items</h3>
          <ul className="cp-items">
            {(invoice.items || []).map((item, i) => (
              <li key={i} className="cp-item">
                <div>
                  <strong>{item.description}</strong>
                  <span>{item.quantity} × {fmt(item.unit_price, invoice.currency)}</span>
                </div>
                <span>{fmt(item.line_total, invoice.currency)}</span>
              </li>
            ))}
          </ul>
          <div className="cp-totals">
            <div><span>Subtotal</span><strong>{fmt(invoice.subtotal, invoice.currency)}</strong></div>
            <div className="cp-totals__grand">
              <span>Total</span><strong>{fmt(invoice.grand_total, invoice.currency)}</strong>
            </div>
            <div className="cp-totals__due">
              <span>Amount due</span><strong>{fmt(invoice.balance_due, invoice.currency)}</strong>
            </div>
          </div>
        </section>

        {!isPaid && (
          <div className="cp-pay">
            <div className="cp-pay__secure">
              <FaLock /> Secure payment via Paystack
            </div>
            <button type="button" className="cp-btn cp-btn--primary cp-btn--block"
                    onClick={handlePay}
                    disabled={paying || Number(invoice.balance_due) <= 0}>
              {paying
                ? <><FaCircleNotch className="cp-spin" /> Opening checkout…</>
                : <>Pay {fmt(invoice.balance_due, invoice.currency)}</>}
            </button>
            {error && <p className="cp-error">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
