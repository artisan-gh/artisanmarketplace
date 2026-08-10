// src/components/billing/BillingWidget.jsx
import { useState, useEffect, useMemo } from 'react';
import { getInvoices } from '../../api/invoicesAPI';
import { getPayments } from '../../api/paymentsAPI';
import './BillingWidget.css';

const formatCurrency = (amount) => {
  if (amount === undefined || amount === null) return '₵0.00';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '₵0.00';
  return new Intl.NumberFormat('en-GH', {
    style: 'currency',
    currency: 'GHS',
    minimumFractionDigits: 2,
  }).format(num);
};

export const BillingWidget = () => {
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [debugInfo, setDebugInfo] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // ─── Fetch invoices and payments ─────────────────────
        const invRes = await getInvoices({ limit: 1000 });
        const payRes = await getPayments({ limit: 1000 });

        console.log('🔴 [BillingWidget] invRes:', invRes);
        console.log('🔴 [BillingWidget] payRes:', payRes);

        // ─── Robust data extraction ──────────────────────────
        // Try multiple possible response structures:
        //   - { data: { results: [...] } }
        //   - { results: [...] }
        //   - { data: [...] }
        //   - plain array [...]
        const invoicesData = invRes?.data?.results || invRes?.results || invRes?.data || invRes || [];
        const paymentsData = payRes?.data?.results || payRes?.results || payRes?.data || payRes || [];

        console.log('📊 [BillingWidget] Invoices fetched:', invoicesData.length);
        console.log('📊 [BillingWidget] Payments fetched:', paymentsData.length);
        if (paymentsData.length > 0) {
          console.log('📊 [BillingWidget] First payment status:', paymentsData[0].status);
          console.log('📊 [BillingWidget] First payment amount:', paymentsData[0].amount);
        }
        if (invoicesData.length > 0) {
          console.log('📊 [BillingWidget] First invoice status:', invoicesData[0].status);
          console.log('📊 [BillingWidget] First invoice total:', invoicesData[0].total);
        }

        setInvoices(invoicesData);
        setPayments(paymentsData);
        setDebugInfo({
          invoiceCount: invoicesData.length,
          paymentCount: paymentsData.length,
          firstPaymentStatus: paymentsData.length > 0 ? paymentsData[0].status : 'none',
          firstPaymentAmount: paymentsData.length > 0 ? paymentsData[0].amount : 'none',
          invoiceStatuses: [...new Set(invoicesData.map(i => i.status))],
          paymentStatuses: [...new Set(paymentsData.map(p => p.status))],
          sampleInvoice: invoicesData.length > 0 ? invoicesData[0] : null,
          samplePayment: paymentsData.length > 0 ? paymentsData[0] : null,
        });
        setError(null);
      } catch (err) {
        console.error('[BillingWidget] Fetch error:', err);
        setError(err.message || 'Failed to load billing data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // ─── Compute statistics ──────────────────────────────────
  const stats = useMemo(() => {
    // Successful payments – status contains 'success' or 'paid' (case‑insensitive)
    const successfulPayments = payments.filter((p) => {
      const status = (p.status || '').toLowerCase();
      return status === 'success' || status === 'successful' || status === 'paid';
    });

    console.log('✅ [BillingWidget] Successful payments:', successfulPayments.length);

    const totalRevenue = successfulPayments.reduce((sum, p) => {
      const amount = typeof p.amount === 'string' ? parseFloat(p.amount) : p.amount;
      return sum + (isNaN(amount) ? 0 : amount);
    }, 0);

    // Overdue invoices
    const now = new Date();
    const overdueInvoices = invoices.filter((inv) => {
      const status = (inv.status || '').toLowerCase();
      if (status === 'overdue') return true;
      if (inv.due_date) {
        const due = new Date(inv.due_date);
        return due < now && status !== 'paid' && status !== 'cancelled' && status !== 'void';
      }
      return false;
    });

    const overdueTotal = overdueInvoices.reduce((sum, inv) => {
      const total = typeof inv.total === 'string' ? parseFloat(inv.total) : inv.total;
      return sum + (isNaN(total) ? 0 : total);
    }, 0);

    // Pending invoices
    const pendingInvoices = invoices.filter((inv) => {
      const status = (inv.status || '').toLowerCase();
      return status === 'draft' || status === 'sent' || status === 'pending';
    });

    const pendingTotal = pendingInvoices.reduce((sum, inv) => {
      const total = typeof inv.total === 'string' ? parseFloat(inv.total) : inv.total;
      return sum + (isNaN(total) ? 0 : total);
    }, 0);

    return {
      totalInvoices: invoices.length,
      totalPayments: payments.length,
      successfulPayments: successfulPayments.length,
      totalRevenue,
      overdueInvoices: overdueInvoices.length,
      overdueTotal,
      pendingInvoices: pendingInvoices.length,
      pendingTotal,
    };
  }, [invoices, payments]);

  if (loading) {
    return (
      <div className="billing-widget billing-widget--loading">
        <div className="billing-widget__spinner" />
        <span>Loading billing data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="billing-widget billing-widget--error">
        <p>Could not load billing data.</p>
        <p className="billing-widget__detail">{error}</p>
      </div>
    );
  }

  const {
    totalInvoices,
    totalPayments,
    successfulPayments,
    totalRevenue,
    overdueInvoices,
    overdueTotal,
    pendingInvoices,
    pendingTotal,
  } = stats;

  // ─── Show debug panel – set to false to hide after fixing ───
  const showDebug = true;

  return (
    <div className="billing-widget">
      <div className="billing-widget__header">
        <div>
          <h3 className="billing-widget__title">Billing overview</h3>
          <p className="billing-widget__subtitle">
            {totalInvoices} invoices · {totalPayments} payments on record
          </p>
        </div>
        <span className="billing-widget__updated">Updated just now</span>
      </div>

      <div className="billing-widget__stats">
        <div className="billing-stat">
          <span className="billing-stat__label">Total revenue</span>
          <span className="billing-stat__value">{formatCurrency(totalRevenue)}</span>
          <span className="billing-stat__sub">From {successfulPayments} successful payments</span>
        </div>

        <div className="billing-stat billing-stat--warning">
          <span className="billing-stat__label">Overdue invoices</span>
          <span className="billing-stat__value">{overdueInvoices}</span>
          <span className="billing-stat__sub">{formatCurrency(overdueTotal)} outstanding</span>
        </div>

        <div className="billing-stat billing-stat--info">
          <span className="billing-stat__label">Pending payments</span>
          <span className="billing-stat__value">{pendingInvoices}</span>
          <span className="billing-stat__sub">{formatCurrency(pendingTotal)} in progress</span>
        </div>

        <div className="billing-stat billing-stat--success">
          <span className="billing-stat__label">Successful payments</span>
          <span className="billing-stat__value">{successfulPayments}</span>
          <span className="billing-stat__sub">No failures recorded</span>
        </div>
      </div>

      {/* ─── 🔍 Debug Panel ──────────────────────────────────── */}
      {showDebug && (
        <div
          style={{
            marginTop: '1.5rem',
            padding: '1rem',
            background: '#0a0e1a',
            borderRadius: '8px',
            border: '1px solid #333',
          }}
        >
          <h4 style={{ color: '#f8fafc' }}>🔍 Debug Info</h4>
          <pre
            style={{
              color: '#94a3b8',
              fontSize: '12px',
              whiteSpace: 'pre-wrap',
              maxHeight: '250px',
              overflow: 'auto',
            }}
          >
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
          <div style={{ marginTop: '0.5rem', color: '#94a3b8', fontSize: '13px' }}>
            <p>
              <strong>Invoices:</strong> {invoices.length}
            </p>
            <p>
              <strong>Payments:</strong> {payments.length}
            </p>
            <p>
              <strong>First payment status:</strong> {debugInfo.firstPaymentStatus}
            </p>
            <p>
              <strong>Payment statuses seen:</strong>{' '}
              {debugInfo.paymentStatuses?.join(', ') || 'none'}
            </p>
            <p>
              <strong>Invoice statuses seen:</strong>{' '}
              {debugInfo.invoiceStatuses?.join(', ') || 'none'}
            </p>
          </div>
          <p style={{ color: '#f87171', fontSize: '12px' }}>
            💡 Check the browser console for detailed logs.
          </p>
        </div>
      )}
    </div>
  );
};

export default BillingWidget;