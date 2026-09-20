// src/screens/client/RequestDetailScreen.jsx
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FaClipboardList, FaCircleNotch, FaArrowLeft } from 'react-icons/fa';
import { getMyIncident } from '../../api/clientIncidents';
import './client.css';

export default function RequestDetailScreen() {
  const { id } = useParams();
  const { data: inc, isLoading, error } = useQuery({
    queryKey: ['myIncident', id],
    queryFn: () => getMyIncident(id),
  });

  if (isLoading) {
    return <div className="cp-page cp-page--center"><FaCircleNotch className="cp-spin" /></div>;
  }
  if (error || !inc) {
    return <div className="cp-page cp-page--center"><p className="cp-error">Request not found.</p></div>;
  }

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <Link to="/client/requests" className="cp-back"><FaArrowLeft /> Back</Link>

        <header className="cp-hero">
          <div className="cp-hero__icon"><FaClipboardList /></div>
          <div>
            <span className="cp-eyebrow">Request</span>
            <h1>{inc.incident_number}</h1>
            <p>{inc.status}</p>
          </div>
        </header>

        <section className="cp-card">
          <h3>{inc.title}</h3>
          {inc.description && <p>{inc.description}</p>}
          {inc.address && <p><strong>Location:</strong> {inc.address}</p>}
          {inc.assigned_artisan_name && (
            <p><strong>Artisan:</strong> {inc.assigned_artisan_name}</p>
          )}
        </section>

        <section className="cp-card cp-card--muted">
          <p><strong>Priority:</strong> {inc.priority}</p>
          <p><strong>Created:</strong> {new Date(inc.created_at).toLocaleString()}</p>
          {inc.target_resolution && (
            <p><strong>Target:</strong> {new Date(inc.target_resolution).toLocaleString()}</p>
          )}
        </section>
      </div>
    </div>
  );
}