// src/screens/client/WalletScreen.jsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FaWallet, FaArrowUp, FaArrowDown, FaCircleNotch, FaLock } from 'react-icons/fa';
import api from '../../api/client';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;

export default function WalletScreen() {
  const qc = useQueryClient();
  const [amount, setAmount] = useState('');

  const { data: wallet, isLoading: wLoading } = useQuery({
    queryKey: ['wallet'],
    queryFn: () => api.get('/wallets/my_wallet/').then((r) => r.data),
  });

  const { data: transactionsRaw, isLoading: tLoading } = useQuery({
    queryKey: ['wallet-transactions'],
    queryFn: () => api.get('/wallets/transactions/').then((r) => r.data),
  });

  const withdrawMutation = useMutation({
    mutationFn: (amt) =>
      api.post('/wallets/withdraw/', { amount: amt }).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['wallet'] });
      qc.invalidateQueries({ queryKey: ['wallet-transactions'] });
      setAmount('');
      alert('Withdrawal requested. An admin will review it shortly.');
    },
    onError: (err) => alert(err?.response?.data?.error || 'Withdrawal failed.'),
  });

  if (wLoading || tLoading) {
    return (
      <div className="cp-page cp-page--center">
        <FaCircleNotch className="cp-spin" />
        <p>Loading wallet…</p>
      </div>
    );
  }

  const transactions = Array.isArray(transactionsRaw)
    ? transactionsRaw
    : transactionsRaw?.results || [];

  // Pending withdrawals = debit transactions still pending
  const pendingWithdrawals = transactions.filter(
    (t) => t.transaction_type === 'DEBIT' && t.status === 'PENDING'
  );
  const pendingTotal = pendingWithdrawals.reduce(
    (sum, t) => sum + Number(t.amount || 0),
    0
  );

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaWallet /></div>
          <div>
            <span className="cp-eyebrow">Earnings</span>
            <h1>Wallet</h1>
            <p>Balance, payouts, and your ledger.</p>
          </div>
        </header>

        {/* Balance card */}
        <section className="cp-wallet-hero">
          <div className="cp-wallet-hero__value">{fmt(wallet?.balance)}</div>
          <div className="cp-wallet-hero__label">Available balance</div>

          {pendingTotal > 0 && (
            <div className="cp-wallet-hero__pending">
              Pending withdrawal: <strong>{fmt(pendingTotal)}</strong>
            </div>
          )}

          <div className="cp-wallet-hero__form">
            <input
              type="number"
              min="1"
              step="0.01"
              placeholder="Amount to withdraw"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <button
              type="button"
              className="cp-btn cp-btn--primary"
              disabled={withdrawMutation.isLoading || !amount}
              onClick={() => withdrawMutation.mutate(parseFloat(amount))}
            >
              {withdrawMutation.isLoading ? (
                <><FaCircleNotch className="cp-spin" /> Processing…</>
              ) : (
                <><FaArrowUp /> Withdraw</>
              )}
            </button>
          </div>

          <p className="cp-wallet-hero__hint">
            Withdrawals are reviewed by an admin before payout.
          </p>
        </section>

        {/* Stats */}
        <section className="cp-wallet-stats">
          <div className="cp-wallet-stat">
            <span className="cp-wallet-stat__label">Total earned</span>
            <strong>{fmt(wallet?.total_earned)}</strong>
          </div>
          <div className="cp-wallet-stat">
            <span className="cp-wallet-stat__label">Total withdrawn</span>
            <strong>{fmt(wallet?.total_withdrawn)}</strong>
          </div>
        </section>

        {/* Ledger */}
        <section className="cp-card">
          <h3>Ledger</h3>
          {transactions.length === 0 ? (
            <p className="cp-empty-inline">No transactions yet.</p>
          ) : (
            <ul className="cp-list cp-list--flat">
              {transactions.map((t) => {
                const isCredit = t.transaction_type === 'CREDIT';
                return (
                  <li key={t.id} className="cp-list-row">
                    <div className="cp-list-row__main">
                      <span className={`cp-tx-icon cp-tx-icon--${isCredit ? 'credit' : 'payout'}`}>
                        {isCredit ? <FaArrowDown /> : <FaArrowUp />}
                      </span>
                      <div>
                        <strong>{t.description || 'Transaction'}</strong>
                        <div className="cp-list-row__meta">
                          <span>{t.reference}</span>
                          <span>·</span>
                          <span>
                            {new Date(t.created_at || t.processed_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="cp-list-row__amount">
                      <strong className={isCredit ? 'cp-amount--in' : 'cp-amount--out'}>
                        {isCredit ? '+' : '−'}
                        {fmt(t.amount)}
                      </strong>
                      <span className={`cp-status cp-status--${(t.status || '').toLowerCase()}`}>
                        {t.status}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <div className="cp-wallet-secure">
          <FaLock /> Withdrawals are processed within 1 business day.
        </div>
      </div>
    </div>
  );
}