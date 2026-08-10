// components/CallLogFormModal.jsx
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSave, FaTimes, FaSpinner } from 'react-icons/fa';
import { getCategories } from '../api/categoriesAPI';
import { getServices } from '../api/servicesAPI';
import { getArtisans, suggestArtisans } from '../api/artisansAPI';
import ArtisanCalendar from './ArtisanCalendar';
import toast from 'react-hot-toast';
import './CallLogFormModal.css';

const INITIAL_FORM = {
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
};

export default function CallLogFormModal({ isOpen, onClose, initialData, onSubmit, submitting }) {
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [suggestedArtisans, setSuggestedArtisans] = useState([]);
  const [loadingArtisans, setLoadingArtisans] = useState(false);
  const [allArtisans, setAllArtisans] = useState([]);
  const [form, setForm] = useState(INITIAL_FORM);
  const abortControllerRef = useRef(null);
  const mounted = useRef(true);
  const firstInputRef = useRef(null);
  const hasInitializedRef = useRef(false);

  // ─── Focus the first input when modal opens ──────────────
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        if (firstInputRef.current) firstInputRef.current.focus();
      }, 100);
    }
  }, [isOpen]);

  // ─── Cleanup mounted ref ─────────────────────────────────
  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  // ─── Reset form to initial state ────────────────────────────
  const resetForm = useCallback(() => {
    setForm(INITIAL_FORM);
    setSuggestedArtisans([]);
    hasInitializedRef.current = false;
  }, []);

  // ─── Fetch all artisans once when modal opens ──────────────
  useEffect(() => {
    if (!isOpen) return;
    const fetchAllArtisans = async () => {
      try {
        const data = await getArtisans({ limit: 100 });
        if (mounted.current) setAllArtisans(data.results || data || []);
      } catch (error) {
        console.error('Failed to fetch artisans:', error);
      }
    };
    fetchAllArtisans();
  }, [isOpen]);

  // ─── Fetch artisan suggestions ──────────────────────────────
  useEffect(() => {
    if (abortControllerRef.current) abortControllerRef.current.abort();

    if (!form.service || !form.preferred_date || !form.preferred_time) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      if (suggestedArtisans.length > 0) setSuggestedArtisans([]);
      return;
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const fetchSuggestions = async () => {
      setLoadingArtisans(true);
      try {
        let lat = 5.6037, lng = -0.1870;
        if (navigator.geolocation) {
          const pos = await new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(resolve, () => resolve(null));
          });
          if (pos) { lat = pos.coords.latitude; lng = pos.coords.longitude; }
        }
        const datetime = `${form.preferred_date}T${form.preferred_time}`;
        const data = await suggestArtisans({
          service_id: form.service,
          lat, lng, datetime,
        }, { signal: controller.signal });
        if (mounted.current) setSuggestedArtisans(data);
      } catch (error) {
        if (error.name === 'AbortError') return;
        console.error('Failed to fetch suggestions:', error);
        toast.error('Could not load artisan suggestions.');
      } finally {
        if (mounted.current) setLoadingArtisans(false);
      }
    };

    fetchSuggestions();

    return () => { controller.abort(); };
  }, [form.service, form.preferred_date, form.preferred_time, suggestedArtisans.length]);

  // ─── Populate form when editing ─────────────────────────────
  useEffect(() => {
    if (initialData) {
      hasInitializedRef.current = true;
      const data = initialData;
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setForm({
        call_type: data.call_type || 'INCOMING',
        caller_number: data.caller_number || '',
        caller_name: data.caller_name || '',
        alternative_phone: data.alternative_phone || '',
        email: data.email || '',
        call_notes: data.call_notes || '',
        client_name: data.booking_data?.client_name || '',
        client_phone: data.booking_data?.client_phone || '',
        client_alt_phone: data.booking_data?.client_alt_phone || '',
        client_email: data.booking_data?.client_email || '',
        is_existing_client: data.booking_data?.is_existing_client || false,
        problem_title: data.booking_data?.problem_title || '',
        problem_description: data.booking_data?.problem_description || '',
        problem_started: data.booking_data?.problem_started || '',
        is_emergency: data.booking_data?.is_emergency || false,
        is_damage_involved: data.booking_data?.is_damage_involved || false,
        category: data.booking_data?.category?.id || data.booking_data?.category || '',
        service: data.booking_data?.service?.id || data.booking_data?.service || '',
        region: data.booking_data?.region || '',
        district: data.booking_data?.district || '',
        town: data.booking_data?.town || '',
        street: data.booking_data?.street || '',
        house_number: data.booking_data?.house_number || '',
        gps_location: data.booking_data?.gps_location || '',
        landmark: data.booking_data?.landmark || '',
        address_full: data.booking_data?.address_full || '',
        preferred_date: data.booking_data?.preferred_date || new Date().toISOString().split('T')[0],
        preferred_time: data.booking_data?.preferred_time || new Date().toTimeString().slice(0, 5),
        alternative_date: data.booking_data?.alternative_date || '',
        alternative_time: data.booking_data?.alternative_time || '',
        flexible_appointment: data.booking_data?.flexible_appointment || false,
        urgency: data.booking_data?.urgency || 'FLEXIBLE',
        min_budget: data.booking_data?.min_budget || '',
        max_budget: data.booking_data?.max_budget || '',
        budget_unknown: data.booking_data?.budget_unknown || false,
        property_type: data.booking_data?.property_type || 'HOUSE',
        preferred_artisan: data.booking_data?.preferred_artisan || '',
        estimated_cost: data.booking_data?.estimated_cost || '',
        estimated_duration: data.booking_data?.estimated_duration || '',
        agent_notes: data.booking_data?.agent_notes || data.call_notes || '',
        follow_up_required: data.booking_data?.follow_up_required || false,
        follow_up_date: data.booking_data?.follow_up_date || '',
      });
    } else {
      // No initialData → reset only if not already reset
      if (!hasInitializedRef.current) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        resetForm();
      }
    }
  }, [initialData, resetForm]);

  // ─── Reset when modal closes ──────────────────────────────────
  useEffect(() => {
    if (!isOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      resetForm();
    }
  }, [isOpen, resetForm]);

  // ─── Fetch options when modal opens ─────────────────────────
  useEffect(() => {
    if (!isOpen) return;
    const fetchOptions = async () => {
      setLoadingOptions(true);
      try {
        const [catRes, servRes] = await Promise.all([getCategories(), getServices()]);
        if (mounted.current) {
          setCategories(catRes.data?.results || catRes.data || []);
          setServices(servRes.data?.results || servRes.data || []);
        }
      } catch (error) {
        console.error('Failed to load options:', error);
        toast.error('Could not load categories/services.');
      } finally {
        if (mounted.current) setLoadingOptions(false);
      }
    };
    fetchOptions();
  }, [isOpen]);

  // ─── Filter services based on selected category ─────────────
  const filteredServices = useMemo(() => {
    if (form.category) {
      const selectedCategory = categories.find(c => c.id === parseInt(form.category));
      if (selectedCategory) return services.filter(s => s.category === selectedCategory.name);
      return [];
    }
    return services;
  }, [form.category, services, categories]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleDateSelect = (date) => {
    setForm(prev => ({ ...prev, preferred_date: date }));
  };

  const artisanOptions = useMemo(() => {
    const suggestedIds = new Set(suggestedArtisans.map(a => a.id));
    return [...suggestedArtisans, ...allArtisans.filter(a => !suggestedIds.has(a.id))];
  }, [suggestedArtisans, allArtisans]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!form.caller_number || !form.client_name || !form.client_phone || !form.problem_title || !form.problem_description) {
      toast.error('Please fill in all required fields.');
      return;
    }
    if (!form.category || !form.service) {
      toast.error('Please select a Category and Service.');
      return;
    }
    if (!form.preferred_date || !form.preferred_time) {
      toast.error('Please select a preferred date and time.');
      return;
    }

    const payload = {
      call_type: form.call_type,
      caller_number: form.caller_number,
      caller_name: form.caller_name || form.client_name,
      alternative_phone: form.alternative_phone,
      email: form.email || form.client_email,
      call_notes: form.call_notes,

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

      category: form.category ? parseInt(form.category) : null,
      service: form.service ? parseInt(form.service) : null,

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
      preferred_artisan: form.preferred_artisan ? parseInt(form.preferred_artisan) : null,

      estimated_cost: form.estimated_cost ? parseFloat(form.estimated_cost) : null,
      estimated_duration: form.estimated_duration ? parseFloat(form.estimated_duration) : null,
      agent_notes: form.agent_notes || null,
      follow_up_required: form.follow_up_required,
      follow_up_date: form.follow_up_date || null,
    };

    onSubmit(payload);
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="modal-overlay"
          onMouseDown={handleOverlayClick}
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            className="modal-content"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>{initialData ? 'Edit Call Log' : 'New Call & Booking'}</h2>
              <button onClick={onClose} className="modal-close-btn">
                <FaTimes />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
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
                      ref={firstInputRef}
                      type="text"
                      name="caller_number"
                      value={form.caller_number}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Caller Name</label>
                    <input type="text" name="caller_name" value={form.caller_name} onChange={handleChange} />
                  </div>
                  <div className="form-group">
                    <label>Alternative Phone</label>
                    <input type="text" name="alternative_phone" value={form.alternative_phone} onChange={handleChange} />
                  </div>
                  <div className="form-group full-width">
                    <label>Email</label>
                    <input type="email" name="email" value={form.email} onChange={handleChange} />
                  </div>
                  <div className="form-group full-width">
                    <label>Call Notes</label>
                    <textarea name="call_notes" value={form.call_notes} onChange={handleChange} rows="3" />
                  </div>
                </div>
              </fieldset>

              {/* ─── Section 2: Client Information ─── */}
              <fieldset className="form-section">
                <legend>Client Information</legend>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Client Full Name *</label>
                    <input type="text" name="client_name" value={form.client_name} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label>Client Phone *</label>
                    <input type="text" name="client_phone" value={form.client_phone} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label>Alternative Phone</label>
                    <input type="text" name="client_alt_phone" value={form.client_alt_phone} onChange={handleChange} />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input type="email" name="client_email" value={form.client_email} onChange={handleChange} />
                  </div>
                  <div className="form-group checkbox">
                    <label>
                      <input type="checkbox" name="is_existing_client" checked={form.is_existing_client} onChange={handleChange} />
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
                    <input type="text" name="problem_title" value={form.problem_title} onChange={handleChange} required />
                  </div>
                  <div className="form-group full-width">
                    <label>Detailed Description *</label>
                    <textarea name="problem_description" value={form.problem_description} onChange={handleChange} rows="4" required />
                  </div>
                  <div className="form-group">
                    <label>Started On</label>
                    <input type="date" name="problem_started" value={form.problem_started} onChange={handleChange} />
                  </div>
                  <div className="form-group checkbox">
                    <label>
                      <input type="checkbox" name="is_emergency" checked={form.is_emergency} onChange={handleChange} />
                      Emergency
                    </label>
                  </div>
                  <div className="form-group checkbox">
                    <label>
                      <input type="checkbox" name="is_damage_involved" checked={form.is_damage_involved} onChange={handleChange} />
                      Damage Involved
                    </label>
                  </div>
                  <div className="form-group">
                    <label>Category *</label>
                    {loadingOptions ? (
                      <div style={{ padding: '0.6rem', color: '#64748b' }}>Loading…</div>
                    ) : (
                      <select name="category" value={form.category} onChange={handleChange} required>
                        <option value="">Select category</option>
                        {categories.map(c => (
                          <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                      </select>
                    )}
                  </div>
                  <div className="form-group">
                    <label>Service *</label>
                    {loadingOptions ? (
                      <div style={{ padding: '0.6rem', color: '#64748b' }}>Loading…</div>
                    ) : (
                      <select name="service" value={form.service} onChange={handleChange} required>
                        <option value="">Select service</option>
                        {filteredServices.map(s => (
                          <option key={s.id} value={s.id}>{s.name}</option>
                        ))}
                      </select>
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

              {/* ─── Section 5: Appointment & Artisan Assignment ─── */}
              <fieldset className="form-section">
                <legend>Appointment & Artisan Assignment</legend>
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

                  <div className="form-group full-width">
                    <label>Artisan Availability</label>
                    <ArtisanCalendar onDateSelect={handleDateSelect} />
                    <small className="hint">Click a date to auto‑fill the preferred date above.</small>
                  </div>

                  <div className="form-group full-width">
                    <label>Assign Artisan</label>
                    {loadingArtisans ? (
                      <div className="loading-indicator">Loading suggestions…</div>
                    ) : (
                      <select
                        name="preferred_artisan"
                        value={form.preferred_artisan}
                        onChange={handleChange}
                        className="artisan-select"
                      >
                        <option value="">– Auto‑assign / Select artisan –</option>
                        {suggestedArtisans.length > 0 && (
                          <optgroup label="⭐ Recommended">
                            {suggestedArtisans.map((a) => (
                              <option key={a.id} value={a.id}>
                                {a.name} (⭐ {a.rating || 0} · {a.experience_years || 0} yrs)
                              </option>
                            ))}
                          </optgroup>
                        )}
                        <optgroup label="All Artisans">
                          {artisanOptions.map((a) => (
                            <option key={a.id} value={a.id}>
                              {a.name} (⭐ {a.rating || 0} · {a.experience_years || 0} yrs)
                            </option>
                          ))}
                        </optgroup>
                      </select>
                    )}
                    {form.preferred_artisan && (
                      <small className="hint">Assigned artisan will be notified.</small>
                    )}
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

              {/* ─── Section 7: Estimates ─── */}
              <fieldset className="form-section">
                <legend>Estimates</legend>
                <div className="form-grid">
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
                <button type="button" onClick={onClose} className="btn-cancel">
                  <FaTimes /> Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn-submit">
                  {submitting ? <FaSpinner className="spin" /> : <FaSave />}
                  {submitting ? 'Submitting…' : initialData ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}