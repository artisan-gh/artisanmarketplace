import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FaHammer, FaUser, FaBuilding, FaUserCircle, FaSignOutAlt,
  FaArrowRight, FaBolt, FaLock, FaWallet,
} from 'react-icons/fa';
import { getMyWallet } from '../api/walletsAPI';
import './Dashboard.css';

const ROLE_CARDS = {
  ARTISAN: {
    icon: FaHammer,
    title: 'Artisan dashboard',
    description: 'Manage your services, requests, and customer orders.',
    to: '/services',
    cta: 'Manage services',
  },
  CLIENT: {
    icon: FaUser,
    title: 'Client dashboard',
    description: 'Find artisans and manage your service requests.',
    to: '/artisans',
    cta: 'Browse artisans',
  },
  COMPANY: {
    icon: FaBuilding,
    title: 'Company dashboard',
    description: 'Manage your company profile and service offerings.',
    to: '/company',
    cta: 'Manage company',
  },
};

export default function Dashboard() {
  const { user, logout, loading } = useAuth();
  const [walletBalance, setWalletBalance] = useState(null);
  const [walletLoading, setWalletLoading] = useState(true);

  // ─── Fetch wallet balance ──────────────────────────────────
  useEffect(() => {
    const fetchBalance = async () => {
      if (!user) return;
      try {
        const response = await getMyWallet();
        setWalletBalance(response.data.balance);
      } catch {
        // ignore – wallet might not exist yet
      } finally {
        setWalletLoading(false);
      }
    };
    fetchBalance();
  }, [user]);

  if (loading) {
    return (
      <div className="dash-page">
        <div className="glow-field" aria-hidden="true">
          <div className="glow glow-blue" />
          <div className="glow glow-purple" />
          <div className="glow glow-indigo" />
        </div>
        <div className="dash-loading">
          <div className="dash-loading-spinner" aria-hidden="true" />
          <p>Loading…</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="dash-page">
        <div className="glow-field" aria-hidden="true">
          <div className="glow glow-blue" />
          <div className="glow glow-purple" />
          <div className="glow glow-indigo" />
        </div>
        <div className="dash-guard">
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="dash-guard-card"
          >
            <div className="dash-guard-badge">
              <FaLock aria-hidden="true" />
            </div>
            <h2>Sign in required</h2>
            <p>Please log in to access your dashboard.</p>
            <Link to="/login" className="dash-guard-cta">
              Go to login
              <FaArrowRight aria-hidden="true" />
            </Link>
          </motion.div>
        </div>
      </div>
    );
  }

  const roleCard = ROLE_CARDS[user.user_type];
  const roleLabel = user.user_type?.toLowerCase() || 'user';

  return (
    <div className="dash-page">
      <div className="glow-field" aria-hidden="true">
        <div className="glow glow-blue" />
        <div className="glow glow-purple" />
        <div className="glow glow-indigo" />
      </div>

      {/* Navigation */}
      <nav className="dash-nav">
        <div className="dash-brand">
          <div className="dash-brand-badge">
            <FaBolt aria-hidden="true" />
          </div>
          <h1>Artisan Marketplace</h1>
        </div>
        <div className="dash-nav-actions">
          <span className="dash-welcome">
            Welcome, <strong>{user.full_name || user.email}</strong>
          </span>
          <Link to="/profile" className="dash-nav-link">
            <FaUserCircle aria-hidden="true" />
            Profile
          </Link>
          <button onClick={logout} className="dash-logout-btn">
            <FaSignOutAlt aria-hidden="true" />
            Logout
          </button>
        </div>
      </nav>

      {/* Main content */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="dash-main"
      >
        <div className="dash-heading">
          <h2>Dashboard</h2>
          <p>
            You are logged in as
            <span className="role-pill">
              <FaUser aria-hidden="true" />
              {roleLabel}
            </span>
          </p>
        </div>

        <div className="dash-grid">
          {/* Role card */}
          {roleCard ? (
            <div className="dash-card">
              <div className="dash-card-icon">
                <roleCard.icon aria-hidden="true" />
              </div>
              <h3>{roleCard.title}</h3>
              <p>{roleCard.description}</p>
              <Link to={roleCard.to} className="dash-card-link">
                {roleCard.cta}
                <FaArrowRight aria-hidden="true" />
              </Link>
            </div>
          ) : (
            <div className="dash-fallback">
              <p>You have a {roleLabel} account. Customize your dashboard here.</p>
            </div>
          )}

          {/* Wallet card */}
          {!walletLoading && walletBalance !== null && (
            <div className="dash-card dash-card--wallet">
              <div className="dash-card-icon dash-card-icon--wallet">
                <FaWallet aria-hidden="true" />
              </div>
              <h3>Wallet Balance</h3>
              <p className="dash-wallet-amount">
                GHS {Number(walletBalance).toFixed(2)}
              </p>
              <Link to="/wallet" className="dash-card-link">
                View Wallet
                <FaArrowRight aria-hidden="true" />
              </Link>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}