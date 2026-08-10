// src/components/billing/InvoiceDetail.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getInvoice, initializePaystackPayment, transitionInvoiceStatus } from '../../api/billingAPI';
import { StatusBadge } from '../common/StatusBadge';
import { useAuth } from '../../context/AuthContext'; // <-- import
import './InvoiceDetail.css';

export const InvoiceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth(); // <-- get current user

  const { data: invoice, isLoading, error } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => getInvoice(id).then((res) => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  // ─── Helpers ──────────────────────────────────────────────────
  const getEmail = (inv) => {
    if (!inv) return null;
    if (inv.customer_detail?.email) return inv.customer_detail.email;
    if (inv.customer?.email) return inv.customer.email;
    if (inv.billing_email) return inv.billing_email;
    if (inv.email) return inv.email;
    if (inv.customer_email) return inv.customer_email;
    const keys = Object.keys(inv);
    for (const key of keys) {
      if (key.toLowerCase().includes('email')) {
        const val = inv[key];
        if (val && typeof val === 'string' && val.includes('@')) {
          return val;
        }
      }
    }
    return null;
  };

  const getPhone = (inv) => {
    if (!inv) return null;
    if (inv.customer_detail?.phone) return inv.customer_detail.phone;
    if (inv.customer?.phone) return inv.customer.phone;
    if (inv.billing_phone) return inv.billing_phone;
    if (inv.phone) return inv.phone;
    if (inv.customer_phone) return inv.customer_phone;
    const keys = Object.keys(inv);
    for (const key of keys) {
      if (key.toLowerCase().includes('phone')) {
        const val = inv[key];
        if (val) return val;
      }
    }
    return null;
  };

  // ─── Materials (purchased items) ──────────────────────────
  const getMaterials = (inv) => {
    if (!inv) return [];
    if (Array.isArray(inv.purchased_items) && inv.purchased_items.length > 0) {
      return inv.purchased_items;
    }
    const candidates = [
      inv.materials,
      inv.items_purchased,
      inv.material_items,
      inv.reimbursable_items,
    ];
    const found = candidates.find((c) => Array.isArray(c) && c.length > 0);
    return found || [];
  };

  // ─── Mutations ──────────────────────────────────────────────
  const payMutation = useMutation({
    mutationFn: () => initializePaystackPayment(id, {}),
    onSuccess: (response) => {
      const authUrl = response.data?.data?.authorization_url || response.data?.authorization_url;
      if (authUrl) {
        window.location.href = authUrl;
      } else {
        console.error('No authorization URL in response:', response);
        alert('Payment initiation failed: No authorization URL returned.');
      }
    },
    onError: (err) => {
      console.error('Payment error:', err);
      const backendMsg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.response?.data ||
        'Payment initiation failed. Please try again.';
      alert(backendMsg);
    },
  });

  const statusMutation = useMutation({
    mutationFn: (data) => transitionInvoiceStatus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoice', id] });
    },
    onError: (err) => {
      console.error('Status transition error:', err);
      const backendMsg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.response?.data?.new_status?.[0] ||
        'Failed to send invoice. Please try again.';
      alert(backendMsg);
    },
  });

  // ─── Loading & error ──────────────────────────────────────
  if (isLoading) return <div className="invoice-detail__state">Loading…</div>;
  if (error) return <div className="invoice-detail__state invoice-detail__state--error">Failed to load invoice.</div>;
  if (!invoice) return <div className="invoice-detail__state invoice-detail__state--error">Invoice not found.</div>;

  const statusLower = invoice.status?.toLowerCase();

  const statusColorMap = {
    draft: 'default',
    sent: 'info',
    paid: 'success',
    overdue: 'error',
    cancelled: 'inactive',
    void: 'inactive',
  };

  const formatCurrency = (value) => {
    const num = Number(value);
    return isNaN(num) ? '₵0.00' : `₵${num.toFixed(2)}`;
  };

  // ─── Compute discount if missing ──────────────────────────
  let discount = invoice.discount_amount || 0;
  if (discount === 0 && invoice.subtotal !== undefined && invoice.tax_amount !== undefined && invoice.grand_total !== undefined) {
    const computed = Number(invoice.subtotal) + Number(invoice.tax_amount) - Number(invoice.grand_total);
    if (computed > 0) discount = computed;
  }

  const email = getEmail(invoice) || '—';
  const phone = getPhone(invoice) || '—';

  // ─── Materials purchased on the customer's behalf ──────────
  const materials = getMaterials(invoice);
  const materialsTotal = invoice.materials_total !== undefined
    ? Number(invoice.materials_total)
    : materials.reduce((sum, m) => {
        const qty = Number(m.quantity) || 0;
        const unitCost = Number(m.unit_cost ?? m.unit_price) || 0;
        return sum + qty * unitCost;
      }, 0);

  // ─── Transport cost ─────────────────────────────────────────
  const transportCost = Number(invoice.transport_cost) || 0;

  // ─── Admin check ────────────────────────────────────────────
  const isAdmin = user?.is_staff || user?.user_type === 'ADMIN';

  return (
    <div className="invoice-detail">
      {/* ─── Header ────────────────────────────────────────────── */}
      <div className="invoice-detail__header">
        <div>
          <h1 className="invoice-detail__number">{invoice.invoice_number}</h1>
          <p className="invoice-detail__status-row">
            Status: <StatusBadge status={statusColorMap[statusLower] || 'default'}>{invoice.status}</StatusBadge>
          </p>
        </div>
        <div className="invoice-detail__actions">
          <button onClick={() => navigate('/billing/invoices')} className="btn btn-outline">
            Back
          </button>

          {/* ─── Only admins can send invoices ──────────────── */}
          {isAdmin && statusLower === 'draft' && (
            <button
              onClick={() => statusMutation.mutate({ new_status: 'SENT' })}
              disabled={statusMutation.isPending}
              className="btn btn-primary"
            >
              {statusMutation.isPending ? 'Sending…' : 'Send Invoice'}
            </button>
          )}

          {statusLower === 'sent' && (
            <button onClick={() => payMutation.mutate()} disabled={payMutation.isPending} className="btn btn-success">
              {payMutation.isPending ? 'Processing…' : 'Pay Now'}
            </button>
          )}
        </div>
      </div>

      {/* ─── Invoice Details ───────────────────────────────────── */}
      <div className="invoice-detail__card">
        <div className="invoice-detail__meta">
          <dl>
            <div className="meta-row">
              <dt>Customer</dt>
              <dd>{invoice.customer_name || invoice.customer || '—'}</dd>
            </div>
            <div className="meta-row">
              <dt>Email</dt>
              <dd>{email}</dd>
            </div>
            <div className="meta-row">
              <dt>Phone</dt>
              <dd>{phone}</dd>
            </div>
          </dl>
          <dl>
            <div className="meta-row">
              <dt>Invoice date</dt>
              <dd>{invoice.issued_date ? new Date(invoice.issued_date).toLocaleDateString() : '—'}</dd>
            </div>
            <div className="meta-row">
              <dt>Due date</dt>
              <dd>{invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : '—'}</dd>
            </div>
            <div className="meta-row">
              <dt>Created</dt>
              <dd>{new Date(invoice.created_at).toLocaleString()}</dd>
            </div>
          </dl>
        </div>

        <hr className="invoice-detail__divider" />

        {/* ─── Line Items ──────────────────────────────────────── */}
        <div>
          <h3 className="invoice-detail__section-title">Line items</h3>
          {invoice.items?.length > 0 ? (
            <table className="line-items-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Qty</th>
                  <th>Unit price</th>
                  <th>Tax</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {invoice.items.map((item, idx) => {
                  const qty = Number(item.quantity) || 0;
                  const unitPrice = Number(item.unit_price) || 0;
                  const taxRate = Number(item.tax_rate) || 0;
                  const total = qty * unitPrice;

                  return (
                    <tr key={idx}>
                      <td>{item.description}</td>
                      <td>{qty}</td>
                      <td>{formatCurrency(unitPrice)}</td>
                      <td>{taxRate}%</td>
                      <td className="line-item-total">{formatCurrency(total)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p className="invoice-detail__empty">No line items.</p>
          )}
        </div>

        {/* ─── Materials purchased on the customer's behalf ────── */}
        {materials.length > 0 && (
          <>
            <hr className="invoice-detail__divider" />
            <div>
              <h3 className="invoice-detail__section-title">Materials &amp; supplies purchased</h3>
              <p className="invoice-detail__section-subtitle">
                Items bought on your behalf for this job, added to your invoice total.
              </p>
              <table className="line-items-table">
                <thead>
                  <tr>
                    <th>Item description</th>
                    <th>Qty</th>
                    <th>Unit cost</th>
                    <th>Total cost</th>
                  </tr>
                </thead>
                <tbody>
                  {materials.map((m, idx) => {
                    const total = m.total_cost !== undefined
                      ? Number(m.total_cost)
                      : (Number(m.quantity) || 0) * (Number(m.unit_cost ?? m.unit_price) || 0);

                    return (
                      <tr key={m.id ?? idx}>
                        <td>{m.description}</td>
                        <td>{Number(m.quantity) || 0}</td>
                        <td>{formatCurrency(m.unit_cost ?? m.unit_price)}</td>
                        <td className="line-item-total">{formatCurrency(total)}</td>
                      </tr>
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={3} className="line-item-total" style={{ textAlign: 'right' }}>
                      Materials subtotal
                    </td>
                    <td className="line-item-total">{formatCurrency(materialsTotal)}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </>
        )}

        <hr className="invoice-detail__divider" />

        {/* ─── Totals ───────────────────────────────────────────── */}
        <div className="invoice-detail__totals">
          <div className="totals-row">
            <span>Subtotal</span>
            <span>{formatCurrency(invoice.subtotal)}</span>
          </div>
          {materialsTotal > 0 && (
            <div className="totals-row">
              <span>Materials &amp; supplies</span>
              <span>{formatCurrency(materialsTotal)}</span>
            </div>
          )}
          {transportCost > 0 && (
            <div className="totals-row">
              <span>Transport / delivery</span>
              <span>{formatCurrency(transportCost)}</span>
            </div>
          )}
          <div className="totals-row">
            <span>Tax</span>
            <span>{formatCurrency(invoice.tax_amount)}</span>
          </div>
          {discount > 0 && (
            <div className="totals-row totals-row--discount">
              <span>Discount</span>
              <span>- {formatCurrency(discount)}</span>
            </div>
          )}
          <div className="totals-row totals-row--total">
            <span>Total</span>
            <span>{formatCurrency(invoice.grand_total)}</span>
          </div>
          {invoice.amount_paid > 0 && (
            <div className="totals-row totals-row--paid">
              <span>Amount paid</span>
              <span>{formatCurrency(invoice.amount_paid)}</span>
            </div>
          )}
          {invoice.balance_due > 0 && (
            <div className="totals-row totals-row--balance">
              <span>Balance due</span>
              <span>{formatCurrency(invoice.balance_due)}</span>
            </div>
          )}
        </div>

        {invoice.notes && (
          <div className="invoice-detail__notes">
            <p>Notes</p>
            <p>{invoice.notes}</p>
          </div>
        )}
      </div>
    </div>
  );
};