// hooks/useWallet.js
import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export function useWallet() {
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingTransactions, setLoadingTransactions] = useState(true);

  const fetchWallet = useCallback(async (isActive = () => true) => {
    try {
      const response = await api.get('/wallets/my_wallet/');
      if (isActive()) setWallet(response.data);
    } catch (error) {
      console.warn('Wallet not found:', error.response?.status);
    } finally {
      if (isActive()) setLoading(false);
    }
  }, []);

  const fetchTransactions = useCallback(async (isActive = () => true) => {
    try {
      const response = await api.get('/wallets/transactions/');
      if (isActive()) setTransactions(response.data);
    } catch (error) {
      console.warn('Transactions not found:', error.response?.status);
    } finally {
      if (isActive()) setLoadingTransactions(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    const isActive = () => active;

// eslint-disable-next-line react-hooks/set-state-in-effect
    fetchWallet(isActive);
    fetchTransactions(isActive);

    return () => {
      active = false;
    };
  }, [fetchWallet, fetchTransactions]);

  const refetch = useCallback(() => {
    setLoading(true);
    setLoadingTransactions(true);
    fetchWallet();
    fetchTransactions();
  }, [fetchWallet, fetchTransactions]);

  return { wallet, transactions, loading, loadingTransactions, refetch };
}