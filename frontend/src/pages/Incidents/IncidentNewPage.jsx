// src/pages/Incidents/IncidentNewPage.jsx
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { IncidentForm } from '../../components/incidents/IncidentForm';
import { createIncident } from '../../api/incidentsAPI';

export const IncidentNewPage = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSubmit = async (data) => {
    try {
      console.log('📤 Creating incident with data:', data);
      const res = await createIncident(data);
      console.log('✅ Raw response:', res);

      // ─── Extract the ID from the response ──────────────────
      let incidentId = null;

      if (res?.data) {
        incidentId = res.data.id || res.data.uuid || res.data.incident_id || res.data.data?.id;
      }
      if (!incidentId && res?.id) incidentId = res.id;
      if (!incidentId && res?.uuid) incidentId = res.uuid;

      // If we have an ID, go to detail; otherwise go to list with success message
      if (incidentId) {
        navigate(`/incidents/${incidentId}`);
      } else {
        console.warn('⚠️ Could not extract ID. Redirecting to list.');
        navigate('/incidents', { state: { success: 'Incident created successfully!' } });
      }
    } catch (err) {
      console.error('❌ Error creating incident:', err);
      navigate('/incidents', { state: { error: 'Failed to create incident. Please try again.' } });
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">New Incident</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        >
          Logout
        </button>
      </div>
      <IncidentForm onSubmit={handleSubmit} onCancel={() => navigate('/incidents')} />
    </div>
  );
};