import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaWallet,
  FaArrowUp,
  FaArrowDown,
  FaHistory,
  FaPlus,
  FaTimes,
  FaSpinner,
  FaCheckCircle,
  FaExclamationCircle,
} from 'react-icons/fa';
import { useWallet } from '../hooks/useWallet';
import { withdraw } from '../api/walletsAPI';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';          // ✅ Axios instance with baseURL = '/api/'
import toast from 'react-hot-toast';
import './Wallet.css';

export default function Wallet() {
  const { user } = useAuth();
  const { wallet, transactions, loading, loadingTransactions, refetch } = useWallet();
  const [showTopUp, setShowTopUp] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('');
  const [topUpLoading, setTopUpLoading] = useState(false);
  const [showWithdraw, setShowWithdraw] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawLoading, setWithdrawLoading] = useState(false);

  const isArtisan = user?.user_type === 'ARTISAN';

  // ─── Top‑up handler – uses the new /api/payments/wallet_topup/ endpoint ───
  // Note: baseURL is already '/api/', so we only add 'payments/wallet_topup/'
  const handleTopUp = async (e) => {
    e.preventDefault();
    const amount = parseFloat(topUpAmount);
    if (!amount || amount <= 0) {
      toast.error('Please enter a valid amount.');
      return;
    }
    setTopUpLoading(true);
    try {
      const response = await api.post('payments/wallet_topup/', {
        amount: amount,
        currency: 'GHS',
        description: `Wallet top-up of GHS ${amount.toFixed(2)}`,
      });
      // Redirect to the payment gateway
      window.location.href = response.data.authorization_url;
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.error || 'Failed to initiate top-up.');
      setTopUpLoading(false);
    }
  };

  const handleWithdraw = async (e) => {
    e.preventDefault();
    const amount = parseFloat(withdrawAmount);
    if (!amount || amount <= 0) {
      toast.error('Please enter a valid amount.');
      return;
    }
    if (amount > wallet.balance) {
      toast.error('Insufficient balance.');
      return;
    }
    setWithdrawLoading(true);
    try {
      await withdraw(amount);
      toast.success('Withdrawal request submitted. Awaiting approval.');
      setShowWithdraw(false);
      setWithdrawAmount('');
      await refetch();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Withdrawal failed.');
    } finally {
      setWithdrawLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="wallet-page">
        <div className="wallet-loading">
          <div className="wallet-spinner" />
          <p>Loading wallet…</p>
        </div>
      </div>
    );
  }

  if (!wallet) {
    return (
      <div className="wallet-page">
        <div className="wallet-empty">
          <FaWallet className="wallet-empty-icon" />
          <h2>No wallet found</h2>
          <p>Please contact support to set up your wallet.</p>
        </div>
      </div>
    );
  }

  const { balance, total_earned, total_withdrawn, currency } = wallet;

  return (
    <div className="wallet-page">
      <div className="wallet-container">
        <div className="wallet-header">
          <h1 className="wallet-title">
            Wallet<span className="wallet-dot">.</span>
          </h1>
          <p className="wallet-subtitle">Manage your funds and transactions</p>
        </div>

        <div className="wallet-cards">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="wallet-card wallet-card--balance"
          >
            <div className="wallet-card-label">Available Balance</div>
            <div className="wallet-card-value">
              {currency} {Number(balance).toFixed(2)}
            </div>
            <div className="wallet-card-actions">
              <button
                onClick={() => setShowTopUp(true)}
                className="wallet-action-btn wallet-action-btn--topup"
              >
                <FaPlus /> Top up
              </button>
              {isArtisan && (
                <button
                  onClick={() => setShowWithdraw(true)}
                  className="wallet-action-btn wallet-action-btn--withdraw"
                >
                  <FaArrowDown /> Withdraw
                </button>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="wallet-card wallet-card--earned"
          >
            <div className="wallet-card-label">Total Earned</div>
            <div className="wallet-card-value">
              {currency} {Number(total_earned).toFixed(2)}
            </div>
            <div className="wallet-card-sub">
              <FaArrowUp className="text-emerald-400" /> Lifetime earnings
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="wallet-card wallet-card--withdrawn"
          >
            <div className="wallet-card-label">Total Withdrawn</div>
            <div className="wallet-card-value">
              {currency} {Number(total_withdrawn).toFixed(2)}
            </div>
            <div className="wallet-card-sub">
              <FaArrowDown className="text-rose-400" /> Withdrawn so far
            </div>
          </motion.div>
        </div>

        <div className="wallet-transactions">
          <div className="wallet-transactions-header">
            <h2 className="wallet-transactions-title">
              <FaHistory className="wallet-transactions-icon" />
              Transaction History
            </h2>
          </div>

          {loadingTransactions ? (
            <div className="wallet-transactions-loading">
              <div className="wallet-spinner-small" />
              <span>Loading transactions…</span>
            </div>
          ) : transactions.length === 0 ? (
            <div className="wallet-transactions-empty">
              <p>No transactions yet.</p>
            </div>
          ) : (
            <div className="wallet-transactions-list">
              {transactions.map((tx) => (
                <motion.div
                  key={tx.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="wallet-transaction-item"
                >
                  <div className="wallet-tx-icon">
                    {tx.transaction_type === 'CREDIT' ? (
                      <FaArrowUp className="text-emerald-400" />
                    ) : (
                      <FaArrowDown className="text-rose-400" />
                    )}
                  </div>
                  <div className="wallet-tx-info">
                    <div className="wallet-tx-description">{tx.description}</div>
                    <div className="wallet-tx-meta">
                      <span className="wallet-tx-reference">{tx.reference}</span>
                      <span className="wallet-tx-date">
                        {new Date(tx.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="wallet-tx-amount">
                    <span
                      className={
                        tx.transaction_type === 'CREDIT'
                          ? 'wallet-tx-amount--credit'
                          : 'wallet-tx-amount--debit'
                      }
                    >
                      {tx.transaction_type === 'CREDIT' ? '+' : '-'}
                      {currency} {Number(tx.amount).toFixed(2)}
                    </span>
                    <span className="wallet-tx-status">
                      {tx.status === 'COMPLETED' ? (
                        <FaCheckCircle className="text-emerald-400" />
                      ) : tx.status === 'PENDING' ? (
                        <FaSpinner className="animate-spin text-yellow-400" />
                      ) : (
                        <FaExclamationCircle className="text-rose-400" />
                      )}
                      {tx.status.toLowerCase()}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Top‑up Modal */}
      <AnimatePresence>
        {showTopUp && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="wallet-modal-overlay"
            onClick={() => setShowTopUp(false)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              className="wallet-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setShowTopUp(false)}
                className="wallet-modal-close"
              >
                <FaTimes />
              </button>
              <h2 className="wallet-modal-title">Top up wallet</h2>
              <p className="wallet-modal-sub">
                Enter the amount you want to add to your balance.
              </p>
              <form onSubmit={handleTopUp} className="wallet-modal-form">
                <div className="wallet-modal-field">
                  <label className="wallet-modal-label">Amount ({currency})</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    placeholder="0.00"
                    value={topUpAmount}
                    onChange={(e) => setTopUpAmount(e.target.value)}
                    className="wallet-modal-input"
                    required
                  />
                </div>
                <div className="wallet-modal-actions">
                  <button
                    type="button"
                    onClick={() => setShowTopUp(false)}
                    className="wallet-modal-btn wallet-modal-btn--cancel"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={topUpLoading}
                    className="wallet-modal-btn wallet-modal-btn--submit"
                  >
                    {topUpLoading ? (
                      <>
                        <FaSpinner className="animate-spin" />
                        Processing…
                      </>
                    ) : (
                      'Top up'
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Withdraw Modal */}
      <AnimatePresence>
        {showWithdraw && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="wallet-modal-overlay"
            onClick={() => setShowWithdraw(false)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              className="wallet-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setShowWithdraw(false)}
                className="wallet-modal-close"
              >
                <FaTimes />
              </button>
              <h2 className="wallet-modal-title">Withdraw funds</h2>
              <p className="wallet-modal-sub">
                Enter the amount you want to withdraw from your balance.
                {isArtisan && (
                  <span className="wallet-modal-hint">
                    {' '}Withdrawals require admin approval.
                  </span>
                )}
              </p>
              <form onSubmit={handleWithdraw} className="wallet-modal-form">
                <div className="wallet-modal-field">
                  <label className="wallet-modal-label">Amount ({currency})</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    placeholder="0.00"
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(e.target.value)}
                    className="wallet-modal-input"
                    required
                  />
                  <div className="wallet-modal-balance-hint">
                    Available: {currency} {Number(balance).toFixed(2)}
                  </div>
                </div>
                <div className="wallet-modal-actions">
                  <button
                    type="button"
                    onClick={() => setShowWithdraw(false)}
                    className="wallet-modal-btn wallet-modal-btn--cancel"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={withdrawLoading}
                    className="wallet-modal-btn wallet-modal-btn--withdraw"
                  >
                    {withdrawLoading ? (
                      <>
                        <FaSpinner className="animate-spin" />
                        Processing…
                      </>
                    ) : (
                      'Request withdrawal'
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}