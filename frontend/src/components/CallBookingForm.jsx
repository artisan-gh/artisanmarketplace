import { useState, useEffect } from 'react';
import { FaSpinner, FaCheck } from 'react-icons/fa'; // ✅ added imports
import { getServices } from '../api/servicesAPI';
import { getCategories } from '../api/categoriesAPI';
import { getAvailableArtisans } from '../api/call_centerAPI';
import toast from 'react-hot-toast';
import './CallBookingForm.css';

export default function CallBookingForm({ initialData, onSubmit, onCancel, submitting, availableArtisans }) {
  const [form, setForm] = useState({
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
    subcategory: '',
    service: '',
    region: '',
    district: '',
    town: '',
    street: '',
    house_number: '',
    gps_location: '',
    landmark: '',
    address_full: '',
    preferred_date: '',
    preferred_time: '',
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
    ...initialData,
  });

  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [artisans, setArtisans] = useState(availableArtisans || []);
  const [setLoadingOptions] = useState(false); // ✅ fixed state declaration

  useEffect(() => {
    const fetchOptions = async () => {
      setLoadingOptions(true);
      try {
        const catRes = await getCategories();
        setCategories(catRes.data.results || catRes.data || []);
        const servRes = await getServices();
        setServices(servRes.data.results || servRes.data || []);
        if (form.service) {
          const artRes = await getAvailableArtisans({ service_id: form.service });
          setArtisans(artRes.data);
        }
      } catch (error) {
        console.error(error);
        toast.error('Failed to load options');
      } finally {
        setLoadingOptions(false);
      }
    };
    fetchOptions();
  }, [form.service, setLoadingOptions]); // ✅ added setLoadingOptions to deps

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.client_phone || !form.problem_title || !form.problem_description || !form.preferred_date || !form.preferred_time) {
      toast.error('Please fill all required fields');
      return;
    }
    onSubmit(form);
  };

  return (
    <div className="booking-form-container">
      <h3>📋 Create Booking from Call</h3>
      <form onSubmit={handleSubmit} className="booking-form">
        <div className="form-grid">
          {/* Client */}
          <div className="form-group">
            <label>Full Name *</label>
            <input name="client_name" value={form.client_name} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Phone *</label>
            <input name="client_phone" value={form.client_phone} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Alternative Phone</label>
            <input name="client_alt_phone" value={form.client_alt_phone} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input name="client_email" value={form.client_email} onChange={handleChange} type="email" />
          </div>
          <div className="form-group checkbox">
            <label>
              <input type="checkbox" name="is_existing_client" checked={form.is_existing_client} onChange={handleChange} />
              Existing Client
            </label>
          </div>

          {/* Problem */}
          <div className="form-group full-width">
            <label>Problem Title *</label>
            <input name="problem_title" value={form.problem_title} onChange={handleChange} required />
          </div>
          <div className="form-group full-width">
            <label>Description *</label>
            <textarea name="problem_description" value={form.problem_description} onChange={handleChange} rows="3" required />
          </div>
          <div className="form-group">
            <label>Started On</label>
            <input name="problem_started" value={form.problem_started} onChange={handleChange} type="date" />
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

          {/* Service */}
          <div className="form-group">
            <label>Category</label>
            <select name="category" value={form.category} onChange={handleChange}>
              <option value="">Select</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Service</label>
            <select name="service" value={form.service} onChange={handleChange}>
              <option value="">Select</option>
              {services.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>

          {/* Location */}
          <div className="form-group">
            <label>Region</label>
            <input name="region" value={form.region} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>District</label>
            <input name="district" value={form.district} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Town</label>
            <input name="town" value={form.town} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Street</label>
            <input name="street" value={form.street} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>House Number</label>
            <input name="house_number" value={form.house_number} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>GPS Location</label>
            <input name="gps_location" value={form.gps_location} onChange={handleChange} placeholder="e.g., GA-123-4567" />
          </div>
          <div className="form-group full-width">
            <label>Full Address</label>
            <textarea name="address_full" value={form.address_full} onChange={handleChange} rows="2" />
          </div>

          {/* Appointment */}
          <div className="form-group">
            <label>Preferred Date *</label>
            <input name="preferred_date" value={form.preferred_date} onChange={handleChange} type="date" required />
          </div>
          <div className="form-group">
            <label>Preferred Time *</label>
            <input name="preferred_time" value={form.preferred_time} onChange={handleChange} type="time" required />
          </div>
          <div className="form-group">
            <label>Alternative Date</label>
            <input name="alternative_date" value={form.alternative_date} onChange={handleChange} type="date" />
          </div>
          <div className="form-group">
            <label>Alternative Time</label>
            <input name="alternative_time" value={form.alternative_time} onChange={handleChange} type="time" />
          </div>
          <div className="form-group checkbox">
            <label>
              <input type="checkbox" name="flexible_appointment" checked={form.flexible_appointment} onChange={handleChange} />
              Flexible
            </label>
          </div>

          {/* Urgency & Budget */}
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
          <div className="form-group">
            <label>Min Budget (GHS)</label>
            <input name="min_budget" value={form.min_budget} onChange={handleChange} type="number" step="0.01" />
          </div>
          <div className="form-group">
            <label>Max Budget (GHS)</label>
            <input name="max_budget" value={form.max_budget} onChange={handleChange} type="number" step="0.01" />
          </div>
          <div className="form-group checkbox">
            <label>
              <input type="checkbox" name="budget_unknown" checked={form.budget_unknown} onChange={handleChange} />
              Budget Unknown
            </label>
          </div>

          {/* Property */}
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

          {/* Artisan */}
          <div className="form-group">
            <label>Preferred Artisan</label>
            <select name="preferred_artisan" value={form.preferred_artisan} onChange={handleChange}>
              <option value="">Auto-assign</option>
              {artisans.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>

          {/* Estimate */}
          <div className="form-group">
            <label>Estimated Cost (GHS)</label>
            <input name="estimated_cost" value={form.estimated_cost} onChange={handleChange} type="number" step="0.01" />
          </div>
          <div className="form-group">
            <label>Estimated Duration (hours)</label>
            <input name="estimated_duration" value={form.estimated_duration} onChange={handleChange} type="number" step="0.5" />
          </div>

          {/* Notes */}
          <div className="form-group full-width">
            <label>Agent Notes</label>
            <textarea name="agent_notes" value={form.agent_notes} onChange={handleChange} rows="2" />
          </div>
          <div className="form-group checkbox">
            <label>
              <input type="checkbox" name="follow_up_required" checked={form.follow_up_required} onChange={handleChange} />
              Follow-up Required
            </label>
          </div>
          <div className="form-group">
            <label>Follow-up Date</label>
            <input name="follow_up_date" value={form.follow_up_date} onChange={handleChange} type="date" />
          </div>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} className="btn-cancel">Cancel</button>
          <button type="submit" disabled={submitting} className="btn-submit">
            {submitting ? <FaSpinner className="spin" /> : <FaCheck />}
            {submitting ? 'Creating…' : 'Create Booking'}
          </button>
        </div>
      </form>
    </div>
  );
}