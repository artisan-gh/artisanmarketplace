import { useState } from 'react';
import PropTypes from 'prop-types';
import { patchIncident } from '../../api/incidentsAPI';

export const IncidentStatusUpdate = ({ incidentId, currentStatus, onStatusUpdated }) => {
  const [status, setStatus] = useState(currentStatus || '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!status) return;
    setLoading(true);
    try {
      await patchIncident(incidentId, { status });
      if (onStatusUpdated) onStatusUpdated(status);
    } catch {
      console.error('Status update failed');
      alert('Failed to update status.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center space-x-2">
      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-md"
      >
        <option value="">Select new status</option>
        <option value="NEW">New</option>
        <option value="OPEN">Open</option>
        <option value="ASSIGNED">Assigned</option>
        <option value="RESOLVED">Resolved</option>
        <option value="CLOSED">Closed</option>
        <option value="CANCELLED">Cancelled</option>
      </select>
      <button
        type="submit"
        disabled={loading || !status}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Updating...' : 'Update Status'}
      </button>
    </form>
  );
};

IncidentStatusUpdate.propTypes = {
  incidentId: PropTypes.string.isRequired,
  currentStatus: PropTypes.string,
  onStatusUpdated: PropTypes.func,
};