// src/screens/client/RequestsListScreen.jsx
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FaClipboardList, FaCircleNotch, FaPlus } from 'react-icons/fa';
import { listMyIncidents } from '../../api/clientIncidents';
import './client.css';

const STATUS_LABELS = {
  NEW: 'New',
  OPEN: 'Open',
  ASSIGNED: 'Assigned',
  IN_PROGRESS: 'In progress',
  RESOLVED: 'Resolved',
  CLOSED: 'Closed',
};

export default function RequestsListScreen() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['myIncidents'],
    queryFn: listMyIncidents,
  });
  const incidents = data?.results || data || [];

  if (isLoading) {
    return <div className="cp-page cp-page--center"><FaCircleNotch className="cp-spin" /></div>;
  }
  if (error) {
    return <div className="cp-page cp-page--center"><p className="cp-error">Could not load requests.</p></div>;
  }

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaClipboardList /></div>
          <div>
            <span className="cp-eyebrow">Requests</span>
            <h1>My requests</h1>
            <p>{incidents.length} request{incidents.length === 1 ? '' : 's'}</p>
          </div>
        </header>

        <Link to="/client/requests/new" className="cp-btn cp-btn--primary cp-btn--block">
          <FaPlus /> Request a service
        </Link>

        {incidents.length === 0 ? (
          <div className="cp-empty">
            <FaClipboardList className="cp-empty__icon" />
            <p>You have no requests yet.</p>
          </div>
        ) : (
          <ul className="cp-list">
            {incidents.map((inc) => (
              <li key={inc.id} className="cp-list-row">
                <div className="cp-list-row__main">
                  <Link to={`/client/requests/${inc.id}`} className="cp-list-row__ref">
                    {inc.incident_number}
                  </Link>
                  <span className={`cp-status cp-status--${(inc.status || '').toLowerCase()}`}>
                    {STATUS_LABELS[inc.status] || inc.status}
                  </span>
                  <div className="cp-list-row__meta">
                    <span>{inc.title}</span>
                  </div>
                </div>
                <div className="cp-list-row__amount">
                  <strong>{inc.priority}</strong>
                  <span className="cp-list-row__due">
                    {new Date(inc.created_at).toLocaleDateString()}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}