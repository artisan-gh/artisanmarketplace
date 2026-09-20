
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { FaCircleNotch, FaMapMarkerAlt, FaCamera } from 'react-icons/fa';
import { createMyIncident } from '../../api/clientIncidents';
import './client.css';

const PRIORITIES = [
  { value: 'URGENT', label: 'As soon as possible' },
  { value: 'HIGH', label: 'Today' },
  { value: 'MEDIUM', label: 'This week' },
  { value: 'LOW', label: 'Whenever possible' },
];

export default function NewRequestScreen() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ title: '', description: '', priority: 'MEDIUM', address: '' });
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: createMyIncident,
    onSuccess: (data) => navigate(`/client/requests/${data.id}`),
    onError: (e) => setError(e?.response?.data?.detail || 'Could not create request.'),
  });

  const handleChange = (e) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleUseLocation = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setForm((p) => ({ ...p, address: `${p.address ? p.address + ' · ' : ''}${latitude.toFixed(5)}, ${longitude.toFixed(5)}` }));
      },
      () => setError('Could not access your location.'),
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.title.trim()) { setError('Please tell us what you need help with.'); return; }
    mutation.mutate(form);
  };

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaCamera /></div>
          <div>
            <span className="cp-eyebrow">New request</span>
            <h1>How can we help?</h1>
            <p>Tell us what you need and we'll send the right artisan.</p>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="cp-form">
          <div className="cp-field">
            <label htmlFor="title">What's the issue? *</label>
            <input id="title" name="title" value={form.title} onChange={handleChange}
                   placeholder="e.g. Kitchen socket sparks when I plug in the kettle"
                   className={error && !form.title.trim() ? 'has-error' : ''} />
          </div>

          <div className="cp-field">
            <label htmlFor="description">More details</label>
            <textarea id="description" name="description" value={form.description}
                      onChange={handleChange} rows={4}
                      placeholder="Anything else we should know?" />
          </div>

          <div className="cp-field">
            <label>When do you need it?</label>
            <div className="cp-chips">
              {PRIORITIES.map((p) => (
                <button key={p.value} type="button"
                        className={`cp-chip ${form.priority === p.value ? 'is-active' : ''}`}
                        onClick={() => setForm((prev) => ({ ...prev, priority: p.value }))}>
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div className="cp-field">
            <label htmlFor="address">Where is it happening?</label>
            <div className="cp-input-group">
              <FaMapMarkerAlt />
              <input id="address" name="address" value={form.address}
                     onChange={handleChange} placeholder="Address or GPS coordinates" />
              <button type="button" className="cp-btn cp-btn--ghost cp-btn--sm"
                      onClick={handleUseLocation}>Use my location</button>
            </div>
          </div>

          {error && <p className="cp-error">{error}</p>}

          <button type="submit" className="cp-btn cp-btn--primary cp-btn--block"
                  disabled={mutation.isLoading}>
            {mutation.isLoading
              ? <><FaCircleNotch className="cp-spin" /> Sending request…</>
              : 'Request a service'}
          </button>
        </form>
      </div>
    </div>
  );
}
