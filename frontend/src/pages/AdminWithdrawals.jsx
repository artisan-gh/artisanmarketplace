import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FaCheckCircle, FaSpinner, FaTimes, FaWallet } from 'react-icons/fa';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './AdminWithdrawals.css';

export default function AdminWithdrawals() {
  const { user } = useAuth();
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState({});

  // ─── Fetch pending withdrawals ──────────────────────────────
  const fetchPending = useCallback(async () => {
    try {
      const response = await api.get('wallets/pending_withdrawals/');
      console.log('🔵 [fetchPending] Raw response:', response.data);
      setPending(response.data);
    } catch (error) {
      console.error('Failed to load pending withdrawals:', error);
      toast.error('Failed to load pending withdrawals.');
    } finally {
      setLoading(false);
    }
  }, []);

  // ─── Initial fetch ──────────────────────────────────────────
  useEffect(() => {
    if (!user?.is_staff) {
      toast.error('Access denied. Admin only.');
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchPending();
  }, [user, fetchPending]);

  // ─── Approve handler ────────────────────────────────────────
  const handleApprove = async (transaction) => {
    const walletId = transaction.wallet?.id;
    const txId = transaction.id;
    if (!walletId) {
      toast.error('Missing wallet ID – cannot approve.');
      return;
    }
    setProcessing(prev => ({ ...prev, [txId]: true }));
    try {
      await api.post(`wallets/${walletId}/approve_withdrawal/`, {
        transaction_id: txId
      });
      toast.success('Withdrawal approved!');
      setPending(prev => prev.filter(tx => tx.id !== txId));
    } catch (error) {
      console.error('Approval failed:', error);
      toast.error(error.response?.data?.error || 'Approval failed.');
    } finally {
      setProcessing(prev => ({ ...prev, [txId]: false }));
    }
  };

  // ─── Access denied ───────────────────────────────────────────
  if (!user?.is_staff) {
    return (
      <div className="admin-withdrawals-page">
        <div className="admin-withdrawals-access-denied">
          <FaTimes className="text-rose-400 text-4xl" />
          <h2>Access Denied</h2>
          <p>You must be an admin to view this page.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="admin-withdrawals-page">
        <div className="admin-withdrawals-loading">
          <FaSpinner className="animate-spin text-amber-400 text-3xl" />
          <p>Loading pending withdrawals…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-withdrawals-page">
      <div className="admin-withdrawals-container">
        <div className="admin-withdrawals-header">
          <h1 className="admin-withdrawals-title">
            Pending Withdrawals
            <span className="admin-withdrawals-count">{pending.length}</span>
          </h1>
          <p className="admin-withdrawals-sub">
            Approve artisan withdrawal requests.
          </p>
        </div>

        {pending.length === 0 ? (
          <div className="admin-withdrawals-empty">
            <FaCheckCircle className="text-emerald-400 text-4xl" />
            <h2>All clear</h2>
            <p>No pending withdrawal requests.</p>
          </div>
        ) : (
          <div className="admin-withdrawals-list">
            {pending.map((tx) => {
              // ✅ Safe access – wallet object from serializer includes user_email
              const wallet = tx.wallet || {};
              const currency = wallet.currency || 'GHS';
              const email = wallet.user_email || 'Unknown user';   // ✅ fixed

              return (
                <motion.div
                  key={tx.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="admin-withdrawal-item"
                >
                  <div className="admin-withdrawal-info">
                    <div className="admin-withdrawal-user">
                      <FaWallet className="text-amber-400" />
                      <span className="admin-withdrawal-email">{email}</span>
                    </div>
                    <div className="admin-withdrawal-details">
                      <span className="admin-withdrawal-amount">
                        {currency} {Number(tx.amount).toFixed(2)}
                      </span>
                      <span className="admin-withdrawal-reference">{tx.reference}</span>
                      <span className="admin-withdrawal-date">
                        {new Date(tx.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="admin-withdrawal-actions">
                    <button
                      onClick={() => handleApprove(tx)}
                      disabled={processing[tx.id]}
                      className="admin-withdrawal-btn admin-withdrawal-btn--approve"
                    >
                      {processing[tx.id] ? (
                        <FaSpinner className="animate-spin" />
                      ) : (
                        <FaCheckCircle />
                      )}
                      Approve
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}