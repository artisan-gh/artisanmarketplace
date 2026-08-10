import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaSpinner, FaArrowLeft, FaSave, FaTimes } from 'react-icons/fa';
import { getService, createService, updateService } from '../api/servicesAPI';
import toast from 'react-hot-toast';
import './ServiceForm.css';

// API functions – you'll need to create these or replace with actual calls
import { getCategories, getSubCategories } from '../api/categoriesAPI';

export default function ServiceForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [loading, setLoading] = useState(isEditing);
  const [submitting, setSubmitting] = useState(false);
  const [categories, setCategories] = useState([]);
  const [subcategories, setSubcategories] = useState([]);

  const [form, setForm] = useState({
    category: '',
    subcategory: '',
    name: '',
    description: '',
    image: '',
    minimum_price: '',
    maximum_price: '',
    estimated_duration: 1,
    is_featured: false,
    is_active: true,
  });

  // ─── Fetch categories and subcategories ────────────────────
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const catRes = await getCategories();
        setCategories(catRes.data.results || catRes.data || []);
        const subRes = await getSubCategories();
        setSubcategories(subRes.data.results || subRes.data || []);
      } catch (error) {
        console.error('Failed to load options:', error);
      }
    };
    fetchOptions();
  }, []);

  // ─── Fetch service data if editing ─────────────────────────
  useEffect(() => {
    // If we're creating a new service, do nothing – loading is already false
    if (!isEditing) return;

    const fetchService = async () => {
      try {
        const response = await getService(id);
        const data = response.data;
        setForm({
          category: data.category?.id || data.category || '',
          subcategory: data.subcategory?.id || data.subcategory || '',
          name: data.name || '',
          description: data.description || '',
          image: data.image || '',
          minimum_price: data.minimum_price || '',
          maximum_price: data.maximum_price || '',
          estimated_duration: data.estimated_duration || 1,
          is_featured: data.is_featured || false,
          is_active: data.is_active !== undefined ? data.is_active : true,
        });
      } catch (error) {
        console.error('Failed to fetch service:', error);
        toast.error('Could not load service.');
        navigate('/services');
      } finally {
        setLoading(false);
      }
    };

    fetchService();
  }, [id, isEditing, navigate]);

  // ─── Handle change ──────────────────────────────────────────
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // ─── Handle submit ──────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    if (!form.category || !form.name || !form.description || !form.minimum_price) {
      toast.error('Please fill in all required fields.');
      setSubmitting(false);
      return;
    }

    const payload = {
      ...form,
      minimum_price: parseFloat(form.minimum_price),
      maximum_price: parseFloat(form.maximum_price) || 0,
      estimated_duration: parseInt(form.estimated_duration, 10),
    };

    try {
      if (isEditing) {
        await updateService(id, payload);
        toast.success('Service updated successfully.');
      } else {
        await createService(payload);
        toast.success('Service created successfully.');
      }
      navigate('/services');
    } catch (error) {
      console.error('Save failed:', error);
      toast.error(error.response?.data?.error || 'Failed to save service.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="service-form-page">
        <div className="service-form-loading">
          <FaSpinner className="animate-spin" />
          <p>Loading form…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="service-form-page">
      <div className="service-form-container">
        <div className="service-form-header">
          <Link to="/services" className="service-form-back">
            <FaArrowLeft /> Back
          </Link>
          <h1>{isEditing ? 'Edit Service' : 'Create Service'}</h1>
        </div>

        <motion.form
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="service-form-card"
          onSubmit={handleSubmit}
        >
          <div className="form-grid">
            <div className="form-group">
              <label>Category *</label>
              <select
                name="category"
                value={form.category}
                onChange={handleChange}
                required
              >
                <option value="">Select category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Subcategory (optional)</label>
              <select
                name="subcategory"
                value={form.subcategory}
                onChange={handleChange}
              >
                <option value="">None</option>
                {subcategories
                  .filter(sub => !form.category || sub.category === form.category)
                  .map(sub => (
                    <option key={sub.id} value={sub.id}>{sub.name}</option>
                  ))}
              </select>
            </div>

            <div className="form-group full-width">
              <label>Service Name *</label>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g., House Wiring"
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Description *</label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                rows="4"
                placeholder="Detailed description of the service"
                required
              />
            </div>

            <div className="form-group">
              <label>Image URL</label>
              <input
                type="url"
                name="image"
                value={form.image}
                onChange={handleChange}
                placeholder="https://example.com/image.jpg"
              />
            </div>

            <div className="form-group">
              <label>Estimated Duration (hours)</label>
              <input
                type="number"
                name="estimated_duration"
                value={form.estimated_duration}
                onChange={handleChange}
                min="1"
                step="1"
              />
            </div>

            <div className="form-group">
              <label>Minimum Price (GHS) *</label>
              <input
                type="number"
                name="minimum_price"
                value={form.minimum_price}
                onChange={handleChange}
                placeholder="0.00"
                min="0"
                step="0.01"
                required
              />
            </div>

            <div className="form-group">
              <label>Maximum Price (GHS)</label>
              <input
                type="number"
                name="maximum_price"
                value={form.maximum_price}
                onChange={handleChange}
                placeholder="0.00"
                min="0"
                step="0.01"
              />
            </div>

            <div className="form-group full-width checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_featured"
                  checked={form.is_featured}
                  onChange={handleChange}
                />
                Featured
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={form.is_active}
                  onChange={handleChange}
                />
                Active
              </label>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/services')}
              className="btn btn-cancel"
            >
              <FaTimes /> Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn btn-submit"
            >
              {submitting ? <FaSpinner className="animate-spin" /> : <FaSave />}
              {submitting ? 'Saving…' : isEditing ? 'Update' : 'Create'}
            </button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}