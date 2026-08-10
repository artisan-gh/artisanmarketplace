// src/pages/PublicInvoicePage.jsx
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../api/api';
import './PublicInvoicePage.css';

export const PublicInvoicePage = () => {
  const { token } = useParams();

  const { data, isLoading, error } = useQuery({
    queryKey: ['publicInvoice', token],
    queryFn: async () => {
      const res = await api.get(`/billing/invoices/public/${token}/`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="invoice-loading">
        <div className="spinner" />
        <p>Loading invoice…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="invoice-error">
        <h2>Invoice not found</h2>
        <p>The invoice you're looking for doesn't exist or may have expired.</p>
        <p className="error-detail">{error.message}</p>
      </div>
    );
  }

  const invoice = data;

  // ─── Customer ──────────────────────────────────────────────
  const customer = invoice.customer_detail || invoice.customer || {};
  const customerName = invoice.customer_name || customer.name || 'N/A';
  const customerEmail = customer.email || invoice.billing_email || '';
  const customerPhone = customer.phone || invoice.billing_phone || '';
  const customerAddress = customer.address || invoice.billing_address || '';

  // ─── Currency formatting ────────────────────────────────────
  const currency = invoice.currency || 'GHS';
  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined || isNaN(amount)) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // ─── Items ──────────────────────────────────────────────────
  const items = invoice.items || [];
  const hasItems = items.length > 0;

  // ─── Materials (purchased on behalf) ──────────────────────
  const purchasedItems = invoice.purchased_items || [];
  const hasMaterials = purchasedItems.length > 0;
  const materialsTotal = invoice.materials_total !== undefined
    ? Number(invoice.materials_total)
    : purchasedItems.reduce((sum, m) => {
        const qty = Number(m.quantity) || 0;
        const cost = Number(m.unit_cost ?? m.unit_price) || 0;
        return sum + qty * cost;
      }, 0);

  // ─── Transport cost ─────────────────────────────────────────
  const transportCost = Number(invoice.transport_cost) || 0;

  // ─── Totals ──────────────────────────────────────────────────
  const subtotal = invoice.subtotal || 0;
  const taxAmount = invoice.tax_amount || 0;
  const discountAmount = invoice.discount_amount || 0;
  const grandTotal = invoice.grand_total || 0;
  const amountPaid = invoice.amount_paid || 0;
  const balanceDue = invoice.balance_due !== undefined ? invoice.balance_due : grandTotal - amountPaid;

  return (
    <div className="public-invoice">
      <div className="invoice-header">
        <div className="invoice-brand">
          <h1>INVOICE</h1>
          <p className="invoice-number">#{invoice.invoice_number}</p>
        </div>
        <div className="invoice-status">
          <span className={`status-badge status-${invoice.status?.toLowerCase() || 'draft'}`}>
            {invoice.status_name || invoice.status || 'Draft'}
          </span>
          <p className="invoice-date">
            Issued: {invoice.issued_date ? new Date(invoice.issued_date).toLocaleDateString() : '—'}
          </p>
          <p className="invoice-due">
            Due: {invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : '—'}
          </p>
        </div>
      </div>

      <div className="invoice-customer">
        <h3>Bill To</h3>
        <div className="customer-details">
          <p className="customer-name">{customerName}</p>
          {customerEmail && <p className="customer-email">{customerEmail}</p>}
          {customerPhone && <p className="customer-phone">{customerPhone}</p>}
          {customerAddress && <p className="customer-address">{customerAddress}</p>}
          
          {invoice.billing_name && invoice.billing_name !== customerName && (
            <div className="billing-info">
              <p className="billing-label">Billing Info:</p>
              <p>{invoice.billing_name}</p>
              {invoice.billing_address && <p>{invoice.billing_address}</p>}
              {invoice.billing_email && <p>{invoice.billing_email}</p>}
              {invoice.billing_phone && <p>{invoice.billing_phone}</p>}
              {invoice.billing_tax_id && <p>Tax ID: {invoice.billing_tax_id}</p>}
            </div>
          )}
        </div>
      </div>

      {/* ─── Line Items ──────────────────────────────────────── */}
      {hasItems && (
        <div className="invoice-items">
          <h3 className="section-title">Labour Charges</h3>
          <table className="items-table">
            <thead>
              <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => {
                let itemTotal = item.total;
                if (itemTotal === undefined || itemTotal === null || isNaN(parseFloat(itemTotal))) {
                  const qty = parseFloat(item.quantity) || 0;
                  const price = parseFloat(item.unit_price) || 0;
                  itemTotal = qty * price;
                }
                return (
                  <tr key={idx}>
                    <td>{item.description || item.name || '—'}</td>
                    <td>{item.quantity ?? '—'}</td>
                    <td>{formatCurrency(item.unit_price)}</td>
                    <td>{formatCurrency(itemTotal)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ─── Materials ──────────────────────────────────────── */}
      {hasMaterials && (
        <div className="invoice-materials">
          <h3 className="section-title">Materials &amp; supplies purchased</h3>
          <p className="materials-subtitle">
            Items bought on your behalf for this job, added to your invoice total.
          </p>
          <table className="items-table">
            <thead>
              <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit cost</th>
                <th>Total cost</th>
              </tr>
            </thead>
            <tbody>
              {purchasedItems.map((m, idx) => {
                const total = m.total_cost !== undefined
                  ? Number(m.total_cost)
                  : (Number(m.quantity) || 0) * (Number(m.unit_cost ?? m.unit_price) || 0);
                return (
                  <tr key={m.id ?? idx}>
                    <td>{m.description}</td>
                    <td>{Number(m.quantity) || 0}</td>
                    <td>{formatCurrency(m.unit_cost ?? m.unit_price)}</td>
                    <td>{formatCurrency(total)}</td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={3} className="subtotal-label">Materials subtotal</td>
                <td>{formatCurrency(materialsTotal)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {/* ─── Totals Summary ────────────────────────────────── */}
      <div className="invoice-summary">
        <div className="summary-row">
          <span>Subtotal</span>
          <span>{formatCurrency(subtotal)}</span>
        </div>
        {hasMaterials && materialsTotal > 0 && (
          <div className="summary-row summary-materials">
            <span>Materials &amp; supplies</span>
            <span>{formatCurrency(materialsTotal)}</span>
          </div>
        )}
        {transportCost > 0 && (
          <div className="summary-row summary-transport">
            <span>Transport / delivery</span>
            <span>{formatCurrency(transportCost)}</span>
          </div>
        )}
        {taxAmount > 0 && (
          <div className="summary-row">
            <span>Tax</span>
            <span>{formatCurrency(taxAmount)}</span>
          </div>
        )}
        {discountAmount > 0 && (
          <div className="summary-row summary-discount">
            <span>Discount</span>
            <span>-{formatCurrency(discountAmount)}</span>
          </div>
        )}
        <div className="summary-row grand-total">
          <span>Grand Total</span>
          <span>{formatCurrency(grandTotal)}</span>
        </div>
      </div>

      {amountPaid > 0 && (
        <div className="invoice-payment">
          <p><strong>Amount Paid:</strong> {formatCurrency(amountPaid)}</p>
          <p><strong>Balance Due:</strong> {formatCurrency(balanceDue)}</p>
        </div>
      )}

      {/* ─── Notes and Terms ────────────────────────────────── */}
      {invoice.notes && (
        <div className="invoice-notes">
          <h4>Notes</h4>
          <p>{invoice.notes}</p>
        </div>
      )}
      {invoice.terms && (
        <div className="invoice-terms">
          <h4>Terms</h4>
          <p>{invoice.terms}</p>
        </div>
      )}

      {invoice.status !== 'PAID' && invoice.status !== 'paid' && (
        <div className="invoice-actions">
          <a
            href={`/billing/invoices/pay/${invoice.public_token || token}`}
            className="btn-pay"
          >
            Pay Now
          </a>
        </div>
      )}
    </div>
  );
};