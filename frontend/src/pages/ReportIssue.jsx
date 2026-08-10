import { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaSave, FaTimes, FaSpinner } from 'react-icons/fa';
import { createCallLog, addBookingToCall } from '../api/call_centerAPI';
import { getCategories } from '../api/categoriesAPI';
import { getServices } from '../api/servicesAPI';
import toast from 'react-hot-toast';
import './ReportIssue.css';

export default function ReportIssue() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [loadingOptions, setLoadingOptions] = useState(true);

  // ─── Form state ──────────────────────────────────────────────
  const [form, setForm] = useState({
    call_type: 'INCOMING',
    caller_number: '',
    caller_name: '',
    alternative_phone: '',
    email: '',
    call_notes: '',

    client_name: '',
    client_phone: '',
    client_alt_phone: '',
    client_email: '',
    is_existing_client: false,

    problem_title: '',
    problem_description: '',
    problem_started: '',
    is_emergency: false,
    is_damage_involved: false,

    category: '',
    service: '',

    region: '',
    district: '',
    town: '',
    street: '',
    house_number: '',
    gps_location: '',
    landmark: '',
    address_full: '',

    preferred_date: new Date().toISOString().split('T')[0],
    preferred_time: new Date().toTimeString().slice(0, 5),
    alternative_date: '',
    alternative_time: '',
    flexible_appointment: false,

    urgency: 'FLEXIBLE',
    min_budget: '',
    max_budget: '',
    budget_unknown: false,

    property_type: 'HOUSE',
    preferred_artisan: '',
    estimated_cost: '',
    estimated_duration: '',
    agent_notes: '',
    follow_up_required: false,
    follow_up_date: '',
  });

  // ─── Fetch categories and services ──────────────────────────
  useEffect(() => {
    const fetchOptions = async () => {
      setLoadingOptions(true);
      try {
        const [catRes, servRes] = await Promise.all([
          getCategories(),
          getServices(),
        ]);
        console.log('✅ Categories response:', catRes.data);
        console.log('✅ Services response:', servRes.data);

        const cats = catRes.data?.results || catRes.data || [];
        const servs = servRes.data?.results || servRes.data || [];

        setCategories(cats);
        setServices(servs);

        if (cats.length === 0) {
          toast.error('No categories found. Please add categories in the admin panel.', { duration: 6000 });
        }
        if (servs.length === 0) {
          toast.error('No services found. Please add services in the admin panel.', { duration: 6000 });
        }
      } catch (error) {
        console.error('Failed to load options:', error);
        toast.error('Could not load categories/services. Please check your connection.');
      } finally {
        setLoadingOptions(false);
      }
    };
    fetchOptions();
  }, []);

  // ─── Compute filtered services using category name ─────────
  const filteredServices = useMemo(() => {
    if (form.category) {
      const selectedCategory = categories.find(c => c.id === parseInt(form.category));
      if (selectedCategory) {
        return services.filter(s => s.category === selectedCategory.name);
      }
      return [];
    }
    return services;
  }, [form.category, services, categories]);

  // ─── Handle change ──────────────────────────────────────────
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // ─── Build payload with proper null handling ────────────────
  const buildPayload = (form) => {
    return {
      client_name: form.client_name,
      client_phone: form.client_phone,
      client_alt_phone: form.client_alt_phone || null,
      client_email: form.client_email || null,
      is_existing_client: form.is_existing_client,

      problem_title: form.problem_title,
      problem_description: form.problem_description,
      problem_started: form.problem_started || null,
      is_emergency: form.is_emergency,
      is_damage_involved: form.is_damage_involved,

      category: form.category ? parseInt(form.category, 10) : null,
      service: form.service ? parseInt(form.service, 10) : null,

      region: form.region || null,
      district: form.district || null,
      town: form.town || null,
      street: form.street || null,
      house_number: form.house_number || null,
      gps_location: form.gps_location || null,
      landmark: form.landmark || null,
      address_full: form.address_full || null,

      preferred_date: form.preferred_date,
      preferred_time: form.preferred_time,
      alternative_date: form.alternative_date || null,
      alternative_time: form.alternative_time || null,
      flexible_appointment: form.flexible_appointment,

      urgency: form.urgency,
      min_budget: form.min_budget ? parseFloat(form.min_budget) : null,
      max_budget: form.max_budget ? parseFloat(form.max_budget) : null,
      budget_unknown: form.budget_unknown,
      property_type: form.property_type,

      preferred_artisan: form.preferred_artisan ? parseInt(form.preferred_artisan, 10) : null,
      estimated_cost: form.estimated_cost ? parseFloat(form.estimated_cost) : null,
      estimated_duration: form.estimated_duration ? parseFloat(form.estimated_duration) : null,

      agent_notes: form.agent_notes || null,
      follow_up_required: form.follow_up_required,
      follow_up_date: form.follow_up_date || null,
    };
  };

  // ─── Handle submit ──────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.caller_number || !form.client_name || !form.client_phone || !form.problem_title || !form.problem_description) {
      toast.error('Please fill in all required fields: Caller Number, Client Name, Client Phone, Problem Title, Problem Description.');
      return;
    }

    if (!form.category) {
      toast.error('Please select a Category.');
      return;
    }
    if (!form.service) {
      toast.error('Please select a Service.');
      return;
    }

    if (!form.preferred_date || !form.preferred_time) {
      toast.error('Please select a preferred date and time for the appointment.');
      return;
    }

    setSubmitting(true);

    try {
      // 1. Create Call Log
      const callPayload = {
        call_type: form.call_type,
        caller_number: form.caller_number,
        caller_name: form.caller_name || form.client_name,
        alternative_phone: form.alternative_phone,
        email: form.email || form.client_email,
        call_notes: form.call_notes,
      };
      const callRes = await createCallLog(callPayload);
      console.log('✅ Call log response:', callRes);

      let callId = callRes.data?.id || callRes.data?.data?.id || callRes.data?.pk;
      if (!callId) {
        if (typeof callRes.data === 'number') callId = callRes.data;
        else if (typeof callRes.data === 'string') callId = parseInt(callRes.data, 10);
      }
      if (!callId) {
        throw new Error('Could not extract call ID from response: ' + JSON.stringify(callRes.data));
      }

      // 2. Build booking payload
      const bookingPayload = buildPayload(form);
      console.log('📦 Booking payload (stringified):', JSON.stringify(bookingPayload, null, 2));

      // 3. Send request
      await addBookingToCall(callId, bookingPayload);

      toast.success('Call logged and booking created successfully!');
      navigate(`/call-center/logs/${callId}`);
    } catch (error) {
      console.error('❌ Error:', error);
      let errorMessage = 'Failed to log issue. Please try again.';
      if (error.response) {
        const errorData = error.response.data;
        console.error('Full error (stringified):', JSON.stringify(errorData, null, 2));
        // Try to extract a readable message
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (typeof errorData === 'object') {
          const errors = Object.entries(errorData)
            .map(([key, value]) => {
              if (Array.isArray(value)) {
                return `${key}: ${value.join(', ')}`;
              }
              return `${key}: ${value}`;
            })
            .join('; ');
          if (errors) errorMessage = errors;
        }
      }
      toast.error(errorMessage, { duration: 10000 });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="report-issue-page">
      <div className="report-container">
        <div className="report-header">
          <Link to="/call-center/logs" className="back-link">
            <FaArrowLeft /> Back to logs
          </Link>
          <h1>📝 Report Client Issue</h1>
          <p className="subtitle">Log the call and create a booking in one step.</p>
        </div>

        <motion.form
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="report-form"
          onSubmit={handleSubmit}
        >
          {/* ─── Section 1: Call Details ─── */}
          <fieldset className="form-section">
            <legend>Call Details</legend>
            <div className="form-grid">
              <div className="form-group">
                <label>Call Type</label>
                <select name="call_type" value={form.call_type} onChange={handleChange}>
                  <option value="INCOMING">Incoming</option>
                  <option value="OUTGOING">Outgoing</option>
                </select>
              </div>
              <div className="form-group">
                <label>Caller Number *</label>
                <input
                  type="text"
                  name="caller_number"
                  value={form.caller_number}
                  onChange={handleChange}
                  placeholder="0244123456"
                  required
                />
              </div>
              <div className="form-group">
                <label>Caller Name</label>
                <input
                  type="text"
                  name="caller_name"
                  value={form.caller_name}
                  onChange={handleChange}
                  placeholder="John Doe"
                />
              </div>
              <div className="form-group">
                <label>Alternative Phone</label>
                <input
                  type="text"
                  name="alternative_phone"
                  value={form.alternative_phone}
                  onChange={handleChange}
                  placeholder="0201234567"
                />
              </div>
              <div className="form-group full-width">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="client@example.com"
                />
              </div>
              <div className="form-group full-width">
                <label>Call Notes</label>
                <textarea
                  name="call_notes"
                  value={form.call_notes}
                  onChange={handleChange}
                  rows="3"
                  placeholder="Initial notes about the call"
                />
              </div>
            </div>
          </fieldset>

          {/* ─── Section 2: Client Information ─── */}
          <fieldset className="form-section">
            <legend>Client Information</legend>
            <div className="form-grid">
              <div className="form-group">
                <label>Client Full Name *</label>
                <input
                  type="text"
                  name="client_name"
                  value={form.client_name}
                  onChange={handleChange}
                  placeholder="Jane Doe"
                  required
                />
              </div>
              <div className="form-group">
                <label>Client Phone *</label>
                <input
                  type="text"
                  name="client_phone"
                  value={form.client_phone}
                  onChange={handleChange}
                  placeholder="0244987654"
                  required
                />
              </div>
              <div className="form-group">
                <label>Alternative Phone</label>
                <input
                  type="text"
                  name="client_alt_phone"
                  value={form.client_alt_phone}
                  onChange={handleChange}
                  placeholder="0201987654"
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="client_email"
                  value={form.client_email}
                  onChange={handleChange}
                  placeholder="client@domain.com"
                />
              </div>
              <div className="form-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="is_existing_client"
                    checked={form.is_existing_client}
                    onChange={handleChange}
                  />
                  Existing Client
                </label>
              </div>
            </div>
          </fieldset>

          {/* ─── Section 3: Problem & Service ─── */}
          <fieldset className="form-section">
            <legend>Problem & Service</legend>
            <div className="form-grid">
              <div className="form-group full-width">
                <label>Problem Title *</label>
                <input
                  type="text"
                  name="problem_title"
                  value={form.problem_title}
                  onChange={handleChange}
                  placeholder="e.g., Leaking Sink"
                  required
                />
              </div>
              <div className="form-group full-width">
                <label>Detailed Description *</label>
                <textarea
                  name="problem_description"
                  value={form.problem_description}
                  onChange={handleChange}
                  rows="4"
                  placeholder="Full description of the issue"
                  required
                />
              </div>
              <div className="form-group">
                <label>Started On</label>
                <input
                  type="date"
                  name="problem_started"
                  value={form.problem_started}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="is_emergency"
                    checked={form.is_emergency}
                    onChange={handleChange}
                  />
                  Emergency
                </label>
              </div>
              <div className="form-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="is_damage_involved"
                    checked={form.is_damage_involved}
                    onChange={handleChange}
                  />
                  Damage Involved
                </label>
              </div>

              <div className="form-group">
                <label>Category *</label>
                {loadingOptions ? (
                  <div style={{ padding: '0.6rem 0.75rem', color: '#64748b' }}>Loading categories…</div>
                ) : (
                  <select
                    name="category"
                    value={form.category}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select category</option>
                    {categories.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                )}
                {!loadingOptions && categories.length === 0 && (
                  <small style={{ color: '#dc2626' }}>
                    No categories found. Please add categories in the admin panel.
                  </small>
                )}
              </div>
              <div className="form-group">
                <label>Service *</label>
                {loadingOptions ? (
                  <div style={{ padding: '0.6rem 0.75rem', color: '#64748b' }}>Loading services…</div>
                ) : (
                  <select
                    name="service"
                    value={form.service}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select service</option>
                    {filteredServices.map(s => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                )}
                {!loadingOptions && services.length === 0 && (
                  <small style={{ color: '#dc2626' }}>
                    No services found. Please add services in the admin panel.
                  </small>
                )}
              </div>
            </div>
          </fieldset>

          {/* ─── Section 4: Location ─── */}
          <fieldset className="form-section">
            <legend>Location</legend>
            <div className="form-grid">
              <div className="form-group"><label>Region</label><input name="region" value={form.region} onChange={handleChange} /></div>
              <div className="form-group"><label>District</label><input name="district" value={form.district} onChange={handleChange} /></div>
              <div className="form-group"><label>Town</label><input name="town" value={form.town} onChange={handleChange} /></div>
              <div className="form-group"><label>Street</label><input name="street" value={form.street} onChange={handleChange} /></div>
              <div className="form-group"><label>House Number</label><input name="house_number" value={form.house_number} onChange={handleChange} /></div>
              <div className="form-group"><label>GPS Location</label><input name="gps_location" value={form.gps_location} onChange={handleChange} placeholder="GA-123-4567" /></div>
              <div className="form-group"><label>Landmark</label><input name="landmark" value={form.landmark} onChange={handleChange} /></div>
              <div className="form-group full-width">
                <label>Full Address</label>
                <textarea name="address_full" value={form.address_full} onChange={handleChange} rows="2" />
              </div>
            </div>
          </fieldset>

          {/* ─── Section 5: Appointment ─── */}
          <fieldset className="form-section">
            <legend>Appointment Preferences</legend>
            <div className="form-grid">
              <div className="form-group">
                <label>Preferred Date *</label>
                <input type="date" name="preferred_date" value={form.preferred_date} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Preferred Time *</label>
                <input type="time" name="preferred_time" value={form.preferred_time} onChange={handleChange} required />
              </div>
              <div className="form-group"><label>Alternative Date</label><input type="date" name="alternative_date" value={form.alternative_date} onChange={handleChange} /></div>
              <div className="form-group"><label>Alternative Time</label><input type="time" name="alternative_time" value={form.alternative_time} onChange={handleChange} /></div>
              <div className="form-group checkbox">
                <label>
                  <input type="checkbox" name="flexible_appointment" checked={form.flexible_appointment} onChange={handleChange} />
                  Flexible Appointment
                </label>
              </div>
            </div>
          </fieldset>

          {/* ─── Section 6: Urgency, Budget & Property ─── */}
          <fieldset className="form-section">
            <legend>Urgency, Budget & Property</legend>
            <div className="form-grid">
              <div className="form-group">
                <label>Urgency</label>
                <select name="urgency" value={form.urgency} onChange={handleChange}>
                  <option value="EMERGENCY">Emergency</option>
                  <option value="TODAY">Today</option>
                  <option value="WITHIN_24_HOURS">Within 24 Hours</option>
                  <option value="THIS_WEEK">This Week</option>
                  <option value="FLEXIBLE">Flexible</option>
                </select>
              </div>
              <div className="form-group"><label>Min Budget (GHS)</label><input type="number" step="0.01" name="min_budget" value={form.min_budget} onChange={handleChange} /></div>
              <div className="form-group"><label>Max Budget (GHS)</label><input type="number" step="0.01" name="max_budget" value={form.max_budget} onChange={handleChange} /></div>
              <div className="form-group checkbox">
                <label>
                  <input type="checkbox" name="budget_unknown" checked={form.budget_unknown} onChange={handleChange} />
                  Budget Unknown
                </label>
              </div>
              <div className="form-group">
                <label>Property Type</label>
                <select name="property_type" value={form.property_type} onChange={handleChange}>
                  <option value="HOUSE">House</option>
                  <option value="APARTMENT">Apartment</option>
                  <option value="OFFICE">Office</option>
                  <option value="SHOP">Shop</option>
                  <option value="FACTORY">Factory</option>
                  <option value="SCHOOL">School</option>
                  <option value="HOSPITAL">Hospital</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
            </div>
          </fieldset>

          {/* ─── Section 7: Artisan & Estimates ─── */}
          <fieldset className="form-section">
            <legend>Artisan & Estimates</legend>
            <div className="form-grid">
              <div className="form-group">
                <label>Preferred Artisan</label>
                <input
                  type="text"
                  name="preferred_artisan"
                  value={form.preferred_artisan}
                  onChange={handleChange}
                  placeholder="Artisan ID (optional)"
                />
              </div>
              <div className="form-group"><label>Estimated Cost (GHS)</label><input type="number" step="0.01" name="estimated_cost" value={form.estimated_cost} onChange={handleChange} /></div>
              <div className="form-group"><label>Estimated Duration (hours)</label><input type="number" step="0.5" name="estimated_duration" value={form.estimated_duration} onChange={handleChange} /></div>
            </div>
          </fieldset>

          {/* ─── Section 8: Agent Notes ─── */}
          <fieldset className="form-section">
            <legend>Agent Notes & Follow‑up</legend>
            <div className="form-grid">
              <div className="form-group full-width">
                <label>Agent Notes</label>
                <textarea name="agent_notes" value={form.agent_notes} onChange={handleChange} rows="3" placeholder="Private notes for follow-up, etc." />
              </div>
              <div className="form-group checkbox">
                <label>
                  <input type="checkbox" name="follow_up_required" checked={form.follow_up_required} onChange={handleChange} />
                  Follow‑up Required
                </label>
              </div>
              <div className="form-group"><label>Follow‑up Date</label><input type="date" name="follow_up_date" value={form.follow_up_date} onChange={handleChange} /></div>
            </div>
          </fieldset>

          {/* ─── Actions ────────────────────────────────────────── */}
          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/call-center/logs')}
              className="btn-cancel"
            >
              <FaTimes /> Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-submit"
            >
              {submitting ? <FaSpinner className="spin" /> : <FaSave />}
              {submitting ? 'Submitting…' : 'Log Issue & Create Booking'}
            </button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}