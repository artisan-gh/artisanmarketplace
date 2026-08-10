// src/components/billing/BillingWidget.jsx
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getInvoices, getPayments } from '../../api/billingAPI';
import './BillingWidget.css';

const STATUS_ORDER = ['draft', 'sent', 'paid', 'overdue', 'cancelled', 'void'];
const STATUS_BAR_COLOR = {
  draft: '#9aa1af',
  sent: '#2554c7',
  paid: '#0f8f5f',
  overdue: '#c02b2b',
  cancelled: '#c9cdd7',
  void: '#c9cdd7',
};

// ─── Payment status badge colors ───────────────────────────
const PAYMENT_STATUS_COLOR = {
  SUCCESS: '#22c55e',
  PENDING: '#eab308',
  FAILED: '#ef4444',
  REFUNDED: '#8b5cf6',
};

const formatCurrency = (value) => {
  const num = Number(value);
  return isNaN(num) ? '₵0.00' : `₵${num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

const daysOverdue = (dueDate) => {
  if (!dueDate) return null;
  const diff = Date.now() - new Date(dueDate).getTime();
  return Math.max(0, Math.ceil(diff / (24 * 60 * 60 * 1000)));
};

// ─── Truncate a UUID to first 8 characters ─────────────────
const truncateId = (id) => {
  if (!id) return '—';
  return id.length > 12 ? id.substring(0, 8) : id;
};

// ─── Get a display name for payment ────────────────────────
const getPaymentDisplay = (payment) => {
  if (payment.invoice_number) return payment.invoice_number;
  if (payment.invoice?.invoice_number) return payment.invoice.invoice_number;
  return `#${truncateId(payment.id)}`;
};

// ─── Extract data from response ────────────────────────────
const extractData = (response) => {
  return response?.data?.results || response?.results || response?.data || response || [];
};

export const BillingWidget = () => {
  const { data: invoicesResponse, isLoading: invoicesLoading } = useQuery({
    queryKey: ['billingDashboard', 'invoices'],
    queryFn: () => getInvoices({ page_size: 100 }),
    staleTime: 5 * 60 * 1000,
  });

  const { data: paymentsResponse, isLoading: paymentsLoading } = useQuery({
    queryKey: ['billingDashboard', 'payments'],
    queryFn: () => getPayments({ page_size: 100 }),
    staleTime: 5 * 60 * 1000,
  });

  const invoices = useMemo(() => extractData(invoicesResponse), [invoicesResponse]);
  const payments = useMemo(() => extractData(paymentsResponse), [paymentsResponse]);

  const stats = useMemo(() => {
    const successfulPayments = payments.filter((p) => {
      const status = p.status?.toLowerCase();
      return status === 'success' || status === 'successful' || status === 'paid';
    });

    const pendingPaymentsList = payments.filter((p) => p.status?.toLowerCase() === 'pending');
    const failedPaymentsList = payments.filter((p) => p.status?.toLowerCase() === 'failed');

    const totalRevenue = successfulPayments.reduce((sum, p) => sum + (Number(p.amount) || 0), 0);
    const pendingAmount = pendingPaymentsList.reduce((sum, p) => sum + (Number(p.amount) || 0), 0);

    const overdueInvoicesList = invoices.filter((inv) => inv.status?.toLowerCase() === 'overdue');
    const overdueAmount = overdueInvoicesList.reduce(
      (sum, inv) => sum + (Number(inv.balance_due ?? inv.grand_total) || 0),
      0
    );

    const statusCounts = STATUS_ORDER.reduce((acc, status) => {
      acc[status] = invoices.filter((inv) => inv.status?.toLowerCase() === status).length;
      return acc;
    }, {});

    const topOverdue = [...overdueInvoicesList]
      .sort((a, b) => new Date(a.due_date || 0) - new Date(b.due_date || 0))
      .slice(0, 5);

    const recentPayments = payments.slice(0, 5);

    return {
      totalRevenue,
      pendingAmount,
      overdueAmount,
      overdueCount: overdueInvoicesList.length,
      pendingCount: pendingPaymentsList.length,
      successfulCount: successfulPayments.length,
      failedCount: failedPaymentsList.length,
      statusCounts,
      topOverdue,
      recentPayments,
      totalInvoices: invoices.length,
    };
  }, [invoices, payments]);

  const isLoading = invoicesLoading || paymentsLoading;
  const maxStatusCount = Math.max(1, ...Object.values(stats.statusCounts || {}));

  if (isLoading) {
    return (
      <div className="billing-widget">
        <div className="kpi-grid">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="kpi-skeleton" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="billing-widget">
      <div className="billing-widget__header">
        <div>
          <h2 className="billing-widget__title">Billing overview</h2>
          <p className="billing-widget__subtitle">
            {stats.totalInvoices} invoices · {payments.length} payments on record
          </p>
        </div>
        <span className="billing-widget__updated">Updated just now</span>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card kpi-card--revenue">
          <p className="kpi-card__label">Total revenue</p>
          <p className="kpi-card__value">{formatCurrency(stats.totalRevenue)}</p>
          <p className="kpi-card__meta">From {stats.successfulCount} successful payments</p>
        </div>
        <div className="kpi-card kpi-card--overdue">
          <p className="kpi-card__label">Overdue invoices</p>
          <p className="kpi-card__value">{stats.overdueCount}</p>
          <p className="kpi-card__meta">{formatCurrency(stats.overdueAmount)} outstanding</p>
        </div>
        <div className="kpi-card kpi-card--pending">
          <p className="kpi-card__label">Pending payments</p>
          <p className="kpi-card__value">{stats.pendingCount}</p>
          <p className="kpi-card__meta">{formatCurrency(stats.pendingAmount)} in progress</p>
        </div>
        <div className="kpi-card kpi-card--success">
          <p className="kpi-card__label">Successful payments</p>
          <p className="kpi-card__value">{stats.successfulCount}</p>
          <p className="kpi-card__meta">
            {stats.failedCount > 0 ? `${stats.failedCount} failed` : 'No failures recorded'}
          </p>
        </div>
      </div>

      <div className="billing-widget__grid">
        <div className="panel">
          <h3 className="panel__title">Invoices by status</h3>
          {stats.totalInvoices > 0 ? (
            <div className="status-breakdown">
              {STATUS_ORDER.map((status) => {
                const count = stats.statusCounts[status] || 0;
                const widthPct = (count / maxStatusCount) * 100;
                return (
                  <div className="status-breakdown__row" key={status}>
                    <span className="status-breakdown__label">{status}</span>
                    <span className="status-breakdown__track">
                      <span
                        className="status-breakdown__fill"
                        style={{ width: `${widthPct}%`, '--bar-color': STATUS_BAR_COLOR[status] }}
                      />
                    </span>
                    <span className="status-breakdown__count">{count}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="empty-state">No invoices yet.</p>
          )}
        </div>

        <div className="panel">
          <h3 className="panel__title">Oldest overdue invoices</h3>
          {stats.topOverdue.length > 0 ? (
            <div className="dashboard-list">
              {stats.topOverdue.map((inv) => {
                const overdueDays = daysOverdue(inv.due_date);
                return (
                  <div className="list-row" key={inv.id}>
                    <div className="list-row__primary">
                      <span className="list-row__title">{inv.invoice_number}</span>
                      <span className="list-row__subtitle">{inv.customer_name || inv.customer || '—'}</span>
                      {overdueDays !== null && (
                        <span className="list-row__tag">{overdueDays}d overdue</span>
                      )}
                    </div>
                    <span className="list-row__value list-row__value--danger">
                      {formatCurrency(inv.balance_due ?? inv.grand_total)}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="empty-state">No overdue invoices — nice work.</p>
          )}
        </div>

        {/* ─── Recent Payments ────────────────────────────── */}
        <div className="panel panel--span-2">
          <h3 className="panel__title">Recent payments</h3>
          {stats.recentPayments.length > 0 ? (
            <div className="dashboard-list">
              {stats.recentPayments.map((p) => {
                const status = p.status?.toUpperCase() || 'UNKNOWN';
                const color = PAYMENT_STATUS_COLOR[status] || '#6b7280';
                return (
                  <div className="list-row" key={p.id}>
                    <div className="list-row__primary">
                      <span className="list-row__title">{getPaymentDisplay(p)}</span>
                      <span
                        className="payment-status-badge"
                        style={{ backgroundColor: color }}
                      >
                        {status}
                      </span>
                    </div>
                    <span className="list-row__value">{formatCurrency(p.amount)}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="empty-state">No payments recorded yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};