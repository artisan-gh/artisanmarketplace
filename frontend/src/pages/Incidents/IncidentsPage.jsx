// src/pages/Incidents/IncidentsPage.jsx
import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { IncidentList } from '../../components/incidents/IncidentList';
import { IncidentFormModal } from '../../components/incidents/IncidentFormModal';
import './IncidentsPage.css';

export const IncidentsPage = () => {
  const location = useLocation();
  const queryClient = useQueryClient();
  const [successMessage, setSuccessMessage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // ─── Toast messages from navigation state ──────────────
  useEffect(() => {
    if (location.state?.success) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSuccessMessage(location.state.success);
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // ─── Handlers ─────────────────────────────────────────────
  const handleNewIncident = () => setIsModalOpen(true);
  const handleModalClose = () => setIsModalOpen(false);

  const handleModalSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['incidents'] });
    setSuccessMessage('Incident created successfully!');
  };

  return (
    <div className="incidents-page">
      {/* ─── Success toast ─────────────────────────────────── */}
      {successMessage && (
        <div className="incidents-page-toast">
          <div className="incidents-page-toast-content">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{successMessage}</span>
          </div>
          <button
            onClick={() => setSuccessMessage('')}
            className="incidents-page-toast-close"
            aria-label="Dismiss"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* ─── Header ────────────────────────────────────────── */}
      <div className="incidents-page-header">
        <div>
          <h1 className="incidents-page-title">Incidents</h1>
          <p className="incidents-page-subtitle">Track and manage reported incidents</p>
        </div>
        <button
          onClick={handleNewIncident}
          className="incidents-page-new-btn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          New Incident
        </button>
      </div>

      <IncidentList />

      {/* ─── Modal ────────────────────────────────────────── */}
      <IncidentFormModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
};