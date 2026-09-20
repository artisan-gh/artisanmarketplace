
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  FaFileInvoiceDollar, FaCircleNotch, FaCheckCircle,
  FaExclamationTriangle, FaLock,
} from 'react-icons/fa';
import { getPublicInvoice, payPublicInvoice } from '../../api/clientBilling';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;

export default function PublicInvoicePage() {
  const { token } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getPublicInvoice(token);
        if (!cancelled) setInvoice(data);
      } catch (e) {
        if (!cancelled) setError(e?.response?.data?.detail || 'Invoice not found.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [token]);

  const handlePay = async () => {
    setPaying(true); setError('');
    try {
      const res = await payPublicInvoice(token);
      if (res?.authorization_url) window.location.href = res.authorization_url;
      else setError('Could not initialize payment.');
    } catch (e) {
      setError(e?.response?.data?.detail || 'Payment initialization failed.');
    } finally { setPaying(false); }
  };

  if (loading) return (
    <div className="cp-page cp-page--center">
      <FaCircleNotch className="cp-spin" /><p>Loading invoice…</p>
    </div>
  );

  if (error && !invoice) return (
    <div className="cp-page cp-page--center">
      <div className="cp-alert cp-alert--error">
        <FaExclamationTriangle />
        <div><strong>Invoice unavailable</strong><p>{error}</p></div>
      </div>
    </div>
  );

  const isPaid = invoice.status === 'PAID';
  const isCancelled = ['CANCELLED', 'VOID'].includes(invoice.status);

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaFileInvoiceDollar /></div>
          <div>
            <span className="cp-eyebrow">Invoice</span>
            <h1>{invoice.invoice_number}</h1>
            <p>{invoice.customer_name || 'Thank you for your business'}</p>
          </div>
        </header>

        {isPaid && (
          <div className="cp-banner cp-banner--success">
            <FaCheckCircle />
            <div><strong>Payment received</strong><p>This invoice has been paid in full.</p></div>
          </div>
        )}
        {isCancelled && (
          <div className="cp-banner cp-banner--warn">
            <FaExclamationTriangle />
            <div><strong>Invoice {invoice.status.toLowerCase()}</strong>
              <p>Contact the business if you believe this is a mistake.</p></div>
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
            {(!invoice.items || invoice.items.length === 0) && (
              <li className="cp-item cp-item--empty">No line items</li>
            )}
          </ul>
          <div className="cp-totals">
            <div><span>Subtotal</span><strong>{fmt(invoice.subtotal, invoice.currency)}</strong></div>
            {Number(invoice.tax_amount) > 0 && (
              <div><span>Tax</span><strong>{fmt(invoice.tax_amount, invoice.currency)}</strong></div>
            )}
            {Number(invoice.transport_cost) > 0 && (
              <div><span>Transport</span><strong>{fmt(invoice.transport_cost, invoice.currency)}</strong></div>
            )}
            {Number(invoice.discount_amount) > 0 && (
              <div><span>Discount</span><strong>− {fmt(invoice.discount_amount, invoice.currency)}</strong></div>
            )}
            <div className="cp-totals__grand">
              <span>Total</span><strong>{fmt(invoice.grand_total, invoice.currency)}</strong>
            </div>
            <div className="cp-totals__due">
              <span>Amount due</span><strong>{fmt(invoice.balance_due, invoice.currency)}</strong>
            </div>
          </div>
        </section>

        {!isPaid && !isCancelled && (
          <div className="cp-pay">
            <div className="cp-pay__secure">
              <FaLock /> Secure payment via Paystack · Card or Mobile Money
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
