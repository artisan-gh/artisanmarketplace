import api from './api';

/**
 * Billing API Client
 * Provides access to invoices, payments, credit notes, and all billing-related endpoints.
 *
 * ─── Materials (purchased_items) ──────────────────────────────
 * The `createInvoice` and `updateInvoice` functions accept a `purchased_items` field
 * in the payload, which is an array of objects with:
 *   { description, quantity, unit_cost }
 * These are stored as `PurchasedItem` records on the backend.
 */

// ─── Invoices ──────────────────────────────────────────────────

export const getInvoices = (params) => api.get('billing/invoices/', { params });
export const getInvoice = (id) => api.get(`billing/invoices/${id}/`);

/**
 * Fetch an invoice by its public token (no authentication required).
 * Used for customers viewing invoices from email links.
 */
export const getPublicInvoice = (token) =>
  api.get(`billing/invoices/public/${token}/`);

export const createInvoice = (data) => api.post('billing/invoices/', data);
export const updateInvoice = (id, data) => api.put(`billing/invoices/${id}/`, data);
export const patchInvoice = (id, data) => api.patch(`billing/invoices/${id}/`, data);
export const deleteInvoice = (id) => api.delete(`billing/invoices/${id}/`);

// ─── Invoice Custom Actions ──────────────────────────────────

export const transitionInvoiceStatus = (id, data) =>
  api.post(`billing/invoices/${id}/transition_status/`, data);

export const addInvoiceComment = (id, data) =>
  api.post(`billing/invoices/${id}/add_comment/`, data);

export const addInvoiceAttachment = (id, data) =>
  api.post(`billing/invoices/${id}/add_attachment/`, data);

export const startInvoiceApproval = (id) =>
  api.post(`billing/invoices/${id}/start_approval/`);

export const approveInvoiceLevel = (id, data) =>
  api.post(`billing/invoices/${id}/approve_level/`, data);

export const initializePaystackPayment = (id, data) =>
  api.post(`billing/invoices/${id}/initialize_payment/`, data);

export const verifyPaystackPayment = (reference) =>
  api.get('billing/invoices/verify/', { params: { reference } });

// ─── Paystack Webhook (public) ──────────────────────────────

export const paystackWebhook = (data) =>
  api.post('billing/invoices/webhook/', data);

// ─── My Invoices ─────────────────────────────────────────────

export const getMyInvoices = () => api.get('billing/invoices/my/');
export const getOverdueInvoices = () => api.get('billing/invoices/overdue/');

// ─── Payments ─────────────────────────────────────────────────

export const getPayments = (params) => api.get('billing/payments/', { params });
export const getPayment = (id) => api.get(`billing/payments/${id}/`);
export const createPayment = (data) => api.post('billing/payments/', data);
export const updatePayment = (id, data) => api.put(`billing/payments/${id}/`, data);
export const patchPayment = (id, data) => api.patch(`billing/payments/${id}/`, data);
export const deletePayment = (id) => api.delete(`billing/payments/${id}/`);

// ─── Payment Custom Actions ──────────────────────────────────

export const refundPayment = (id, data) =>
  api.post(`billing/payments/${id}/refund/`, data);

export const allocatePayment = (id, data) =>
  api.post(`billing/payments/${id}/allocate/`, data);

export const getMyPayments = () => api.get('billing/payments/my/');

// ─── Credit Notes ─────────────────────────────────────────────

export const getCreditNotes = (params) => api.get('billing/credit-notes/', { params });
export const getCreditNote = (id) => api.get(`billing/credit-notes/${id}/`);
export const createCreditNote = (data) => api.post('billing/credit-notes/', data);
export const updateCreditNote = (id, data) => api.put(`billing/credit-notes/${id}/`, data);
export const patchCreditNote = (id, data) => api.patch(`billing/credit-notes/${id}/`, data);
export const deleteCreditNote = (id) => api.delete(`billing/credit-notes/${id}/`);

// ─── Recurring Invoices ──────────────────────────────────────

export const getRecurringInvoices = (params) =>
  api.get('billing/recurring-invoices/', { params });
export const getRecurringInvoice = (id) =>
  api.get(`billing/recurring-invoices/${id}/`);
export const createRecurringInvoice = (data) =>
  api.post('billing/recurring-invoices/', data);
export const updateRecurringInvoice = (id, data) =>
  api.put(`billing/recurring-invoices/${id}/`, data);
export const patchRecurringInvoice = (id, data) =>
  api.patch(`billing/recurring-invoices/${id}/`, data);
export const deleteRecurringInvoice = (id) =>
  api.delete(`billing/recurring-invoices/${id}/`);

// ─── Ledger Accounts ──────────────────────────────────────────

export const getLedgerAccounts = (params) =>
  api.get('billing/ledger-accounts/', { params });
export const getLedgerAccount = (id) =>
  api.get(`billing/ledger-accounts/${id}/`);
export const createLedgerAccount = (data) =>
  api.post('billing/ledger-accounts/', data);
export const updateLedgerAccount = (id, data) =>
  api.put(`billing/ledger-accounts/${id}/`, data);
export const patchLedgerAccount = (id, data) =>
  api.patch(`billing/ledger-accounts/${id}/`, data);
export const deleteLedgerAccount = (id) =>
  api.delete(`billing/ledger-accounts/${id}/`);

// ─── Journal Entries ──────────────────────────────────────────

export const getJournalEntries = (params) =>
  api.get('billing/journal-entries/', { params });
export const getJournalEntry = (id) =>
  api.get(`billing/journal-entries/${id}/`);

// ─── Billing Configuration ──────────────────────────────────

export const getBillingConfig = (params) =>
  api.get('billing/config/', { params });
export const getBillingConfigDetail = (id) =>
  api.get(`billing/config/${id}/`);
export const createBillingConfig = (data) =>
  api.post('billing/config/', data);
export const updateBillingConfig = (id, data) =>
  api.put(`billing/config/${id}/`, data);
export const patchBillingConfig = (id, data) =>
  api.patch(`billing/config/${id}/`, data);
export const deleteBillingConfig = (id) =>
  api.delete(`billing/config/${id}/`);

// ─── Taxes ────────────────────────────────────────────────────

export const getTaxes = (params) => api.get('billing/taxes/', { params });
export const getTax = (id) => api.get(`billing/taxes/${id}/`);
export const createTax = (data) => api.post('billing/taxes/', data);
export const updateTax = (id, data) => api.put(`billing/taxes/${id}/`, data);
export const patchTax = (id, data) => api.patch(`billing/taxes/${id}/`, data);
export const deleteTax = (id) => api.delete(`billing/taxes/${id}/`);

// ─── Invoice Tags ────────────────────────────────────────────

export const getInvoiceTags = (params) =>
  api.get('billing/tags/', { params });
export const getInvoiceTag = (id) => api.get(`billing/tags/${id}/`);
export const createInvoiceTag = (data) => api.post('billing/tags/', data);
export const updateInvoiceTag = (id, data) =>
  api.put(`billing/tags/${id}/`, data);
export const patchInvoiceTag = (id, data) =>
  api.patch(`billing/tags/${id}/`, data);
export const deleteInvoiceTag = (id) =>
  api.delete(`billing/tags/${id}/`);

// ─── Payment Intents ──────────────────────────────────────────

export const getPaymentIntents = (params) =>
  api.get('billing/payment-intents/', { params });
export const getPaymentIntent = (id) =>
  api.get(`billing/payment-intents/${id}/`);
export const createPaymentIntent = (data) =>
  api.post('billing/payment-intents/', data);
export const updatePaymentIntent = (id, data) =>
  api.put(`billing/payment-intents/${id}/`, data);
export const patchPaymentIntent = (id, data) =>
  api.patch(`billing/payment-intents/${id}/`, data);
export const deletePaymentIntent = (id) =>
  api.delete(`billing/payment-intents/${id}/`);

// ─── Default Export ──────────────────────────────────────────

export default {
  // Invoices
  getInvoices,
  getInvoice,
  getPublicInvoice,          // <-- new
  createInvoice,
  updateInvoice,
  patchInvoice,
  deleteInvoice,
  transitionInvoiceStatus,
  addInvoiceComment,
  addInvoiceAttachment,
  startInvoiceApproval,
  approveInvoiceLevel,
  initializePaystackPayment,
  verifyPaystackPayment,
  paystackWebhook,
  getMyInvoices,
  getOverdueInvoices,

  // Payments
  getPayments,
  getPayment,
  createPayment,
  updatePayment,
  patchPayment,
  deletePayment,
  refundPayment,
  allocatePayment,
  getMyPayments,

  // Credit Notes
  getCreditNotes,
  getCreditNote,
  createCreditNote,
  updateCreditNote,
  patchCreditNote,
  deleteCreditNote,

  // Recurring Invoices
  getRecurringInvoices,
  getRecurringInvoice,
  createRecurringInvoice,
  updateRecurringInvoice,
  patchRecurringInvoice,
  deleteRecurringInvoice,

  // Ledger Accounts
  getLedgerAccounts,
  getLedgerAccount,
  createLedgerAccount,
  updateLedgerAccount,
  patchLedgerAccount,
  deleteLedgerAccount,

  // Journal Entries
  getJournalEntries,
  getJournalEntry,

  // Billing Config
  getBillingConfig,
  getBillingConfigDetail,
  createBillingConfig,
  updateBillingConfig,
  patchBillingConfig,
  deleteBillingConfig,

  // Taxes
  getTaxes,
  getTax,
  createTax,
  updateTax,
  patchTax,
  deleteTax,

  // Invoice Tags
  getInvoiceTags,
  getInvoiceTag,
  createInvoiceTag,
  updateInvoiceTag,
  patchInvoiceTag,
  deleteInvoiceTag,

  // Payment Intents
  getPaymentIntents,
  getPaymentIntent,
  createPaymentIntent,
  updatePaymentIntent,
  patchPaymentIntent,
  deletePaymentIntent,
};