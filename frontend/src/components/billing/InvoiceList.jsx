// src/components/billing/InvoiceList.jsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getInvoices, deleteInvoice, transitionInvoiceStatus } from '../../api/billingAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { Link } from 'react-router-dom';
import './InvoiceList.css';

const STATUS_STYLES = {
  draft: { badge: 'default', accent: 'draft' },
  sent: { badge: 'info', accent: 'sent' },
  paid: { badge: 'success', accent: 'paid' },
  overdue: { badge: 'error', accent: 'overdue' },
  cancelled: { badge: 'inactive', accent: 'inactive' },
  void: { badge: 'inactive', accent: 'inactive' },
};

const formatAmount = (row) => {
  const amount = Number(row.amount ?? row.total ?? row.total_amount ?? row.grand_total ?? 0);
  const [whole, decimals] = amount.toFixed(2).split('.');
  return (
    <span className="invoice-amount">
      <span className="invoice-amount__symbol">₵</span>
      <span className="invoice-amount__whole">{Number(whole).toLocaleString()}</span>
      <span className="invoice-amount__decimals">.{decimals}</span>
    </span>
  );
};

const SearchIcon = () => (
  <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="9" cy="9" r="6.5" stroke="currentColor" strokeWidth="1.5" />
    <path d="M18 18l-4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

export const InvoiceList = () => {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const { data, isLoading } = useQuery({
    queryKey: ['invoices', { page, pageSize, status: statusFilter, search }],
    queryFn: () =>
      getInvoices({
        page,
        page_size: pageSize,
        status: statusFilter || undefined,
        search: search || undefined,
      }).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteInvoice,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['invoices'] }),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, data }) => transitionInvoiceStatus(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['invoices'] }),
  });

  const columns = [
    {
      key: 'invoice_number',
      label: 'Invoice #',
      render: (val, row) => (
        <Link to={`/billing/invoices/${row.id}`} className="invoice-number-link">
          {val}
        </Link>
      ),
    },
    {
      key: 'customer_name',
      label: 'Customer',
      render: (val) => <span className="invoice-customer">{val}</span>,
    },
    {
      key: 'amount',
      label: 'Amount',
      render: (_, row) => formatAmount(row),
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => {
        const style = STATUS_STYLES[val?.toLowerCase()] || STATUS_STYLES.draft;
        return (
          <span className={`invoice-status invoice-status--${style.accent}`}>
            <StatusBadge status={style.badge}>{val}</StatusBadge>
          </span>
        );
      },
    },
    {
      key: 'due_date',
      label: 'Due Date',
      render: (val) => (
        <span className="invoice-due-date">{val ? new Date(val).toLocaleDateString() : '—'}</span>
      ),
    },
    {
      key: 'actions',
      label: '',
      render: (_, row) => (
        <div className="invoice-actions">
          <Link to={`/billing/invoices/${row.id}`} className="invoice-action invoice-action--view">
            View
          </Link>
          {row.status === 'draft' && (
            <>
              <Link
                to={`/billing/invoices/${row.id}/edit`}
                className="invoice-action invoice-action--edit"
              >
                Edit
              </Link>
              <button
                onClick={() => statusMutation.mutate({ id: row.id, data: { status: 'sent' } })}
                className="invoice-action invoice-action--positive"
              >
                Send
              </button>
              <button
                onClick={() => {
                  if (window.confirm('Delete this invoice?')) deleteMutation.mutate(row.id);
                }}
                className="invoice-action invoice-action--danger"
              >
                Delete
              </button>
            </>
          )}
          {row.status === 'sent' && (
            <button
              onClick={() => statusMutation.mutate({ id: row.id, data: { status: 'paid' } })}
              className="invoice-action invoice-action--positive"
            >
              Mark Paid
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="invoice-list">
      <div className="invoice-toolbar">
        <div className="invoice-search">
          <SearchIcon />
          <input
            type="text"
            placeholder="Search by invoice # or customer..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="invoice-status-select"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="paid">Paid</option>
          <option value="overdue">Overdue</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <Link to="/billing/invoices/new" className="invoice-new-btn">
          New Invoice
        </Link>
      </div>
      <div className="invoice-table-wrapper">
        <DataTable
          columns={columns}
          data={data?.results || []}
          loading={isLoading}
          pagination={{
            current: page,
            pageSize,
            total: data?.count || 0,
            onPageChange: setPage,
            onPageSizeChange: setPageSize,
          }}
        />
      </div>
    </div>
  );
};