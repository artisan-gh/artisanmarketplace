import api from './axios';

/**
 * Wallet API client
 */

// ─── CRUD ────────────────────────────────────────────────────

export const getWallets = (params = {}) => api.get('/wallets/', { params });
export const getWallet = (id) => api.get(`/wallets/${id}/`);
export const createWallet = () => api.post('/wallets/');

// ─── Current User ────────────────────────────────────────────

export const getMyWallet = () => api.get('/wallets/my_wallet/');
export const getMyTransactions = (params = {}) => api.get('/wallets/transactions/', { params });

// ─── Admin Operations ────────────────────────────────────────

export const creditWallet = (data) => api.post('/wallets/credit/', data);
export const debitWallet = (data) => api.post('/wallets/debit/', data);

// ─── Withdrawal ─────────────────────────────────────────────

export const withdraw = (amount) => api.post('/wallets/withdraw/', { amount });
export const approveWithdrawal = (walletId, transactionId) =>
  api.post(`/wallets/${walletId}/approve_withdrawal/`, { transaction_id: transactionId });

// ─── Export all ──────────────────────────────────────────────

export default {
  getWallets,
  getWallet,
  createWallet,
  getMyWallet,
  getMyTransactions,
  creditWallet,
  debitWallet,
  withdraw,
  approveWithdrawal,
};