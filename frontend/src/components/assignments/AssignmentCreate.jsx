import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getIncident } from '../../api/incidentsAPI';
import { getAvailableArtisans } from '../../api/artisansAPI';
import { createAssignment } from '../../api/assignmentsAPI';
import { StatusBadge } from '../common/StatusBadge';
import './AssignmentCreate.css';

export const AssignmentCreate = () => {
  const { incidentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedArtisan, setSelectedArtisan] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');

  const { data: incident, isLoading: loadingIncident } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: () => getIncident(incidentId).then((res) => res.data),
    enabled: !!incidentId,
  });

  const { data: artisans = [], isLoading: loadingArtisans } = useQuery({
    queryKey: ['availableArtisans'],
    queryFn: () => getAvailableArtisans().then((res) => res.data),
    staleTime: 2 * 60 * 1000,
  });

  const mutation = useMutation({
    mutationFn: (data) => createAssignment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
      navigate('/assignments');
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Failed to create assignment.');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedArtisan) {
      setError('Please select an artisan.');
      return;
    }
    mutation.mutate({
      incident: incidentId,
      artisan: selectedArtisan,
      notes: notes,
    });
  };

  if (loadingIncident || loadingArtisans) {
    return (
      <div className="assign-create-loading">
        <div className="loading-spinner" />
        <span>Loading...</span>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="assign-create-error">
        <p>Incident not found.</p>
        <button onClick={() => navigate('/incidents')} className="btn btn-primary">
          Back to Incidents
        </button>
      </div>
    );
  }

  const customerName = incident.customer_detail?.name || incident.customer_name || '—';

  return (
    <div className="assign-create-container">
      <div className="assign-create-card">
        <h1 className="assign-create-title">Assign Artisan</h1>

        {/* ─── Incident Summary ────────────────────────────────── */}
        <div className="assign-incident-summary">
          <div className="assign-incident-header">
            <span className="assign-incident-number">{incident.incident_number}</span>
            <div className="assign-incident-badges">
              <StatusBadge status={incident.priority?.toLowerCase()}>
                {incident.priority || 'Medium'}
              </StatusBadge>
              <StatusBadge status={incident.status?.toLowerCase()}>
                {incident.status || 'New'}
              </StatusBadge>
            </div>
          </div>
          <h3 className="assign-incident-title">{incident.title}</h3>
          <p className="assign-incident-customer">
            <strong>Customer:</strong> {customerName}
          </p>
          {incident.description && (
            <p className="assign-incident-description">{incident.description}</p>
          )}
        </div>

        {/* ─── Form ────────────────────────────────────────────── */}
        <form onSubmit={handleSubmit} className="assign-create-form">
          <div className="form-group">
            <label className="form-label">Select Artisan</label>
            <select
              value={selectedArtisan}
              onChange={(e) => setSelectedArtisan(e.target.value)}
              className="form-select"
              required
            >
              <option value="">Choose an artisan...</option>
              {artisans.map((artisan) => (
                <option key={artisan.id} value={artisan.user}>
                  {artisan.user_detail?.full_name} (
                  {artisan.skills_list?.map((s) => s.name).join(', ') || 'No skills'}) —{' '}
                  {artisan.current_workload}/{artisan.max_concurrent_jobs} jobs
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows="3"
              className="form-textarea"
              placeholder="Any additional instructions for the artisan..."
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate(`/incidents/${incidentId}`)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="btn btn-primary"
            >
              {mutation.isPending ? 'Assigning...' : 'Assign Artisan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};