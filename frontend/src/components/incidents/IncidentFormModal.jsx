// src/components/incidents/IncidentFormModal.jsx
import { useEffect } from 'react';
import { IncidentForm } from './IncidentForm';
import { createIncident } from '../../api/incidentsAPI';
import { useNavigate } from 'react-router-dom';

export const IncidentFormModal = ({ isOpen, onClose, onSuccess }) => {
  const navigate = useNavigate();

  // ─── Handle form submission ──────────────────────────────
  const handleSubmit = async (data) => {
    try {
      const res = await createIncident(data);
      let incidentId = res?.data?.id || res?.id || res?.data?.incident_id;
      if (incidentId) {
        onSuccess(incidentId);
        onClose();
        navigate(`/incidents/${incidentId}`);
      } else {
        onClose();
        navigate('/incidents', { state: { success: 'Incident created successfully!' } });
      }
    } catch (err) {
      console.error('Error creating incident:', err);
      throw err; // Let the form handle the error display
    }
  };

  // ─── Close on Escape key ─────────────────────────────────
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <IncidentForm
          onSubmit={handleSubmit}
          onCancel={onClose}
          isEditing={false}
        />
      </div>
    </div>
  );
};