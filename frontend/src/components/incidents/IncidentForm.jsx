// src/components/incidents/IncidentForm.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaSignOutAlt,
  FaExclamationTriangle,
  FaUserPlus,
  FaUserCheck,
  FaTimes,
  FaSave,
  FaArrowLeft,
  FaMapMarkerAlt,
  FaClock,
} from 'react-icons/fa';
import {
  getIncidentCategories,
  getSubcategoriesByCategory,
} from '../../api/incident_categoryAPI';
import { getIncidentPriorities } from '../../api/incident_priorityAPI';
import { getIncidentStatuses } from '../../api/incident_statusesAPI';
import { createCustomer } from '../../api/customersAPI';
import { CustomerSearch } from '../customers/CustomerSearch';
import './IncidentForm.css';

export const IncidentForm = ({
  initialData = {},
  onSubmit,
  onCancel,
  isEditing = false,
  headerActions = null,
  onLogout = null,
}) => {
  // ─── Lazy initializer ──────────────────────────────────────
  const getDefaultTargetResolution = () =>
    new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16);

  const [formData, setFormData] = useState(() => ({
    customer: '',
    title: '',
    description: '',
    category: '',
    subcategory: '',
    priority: 'MEDIUM',
    status: '',
    address: '',
    target_resolution: getDefaultTargetResolution(),
    ...initialData,
  }));
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [generalError, setGeneralError] = useState('');

  const [showNewCustomer, setShowNewCustomer] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    name: '',
    phone: '',
    email: '',
    address: '',
  });
  const [newCustomerErrors, setNewCustomerErrors] = useState({});
  const [creatingCustomer, setCreatingCustomer] = useState(false);

  // ─── Queries ──────────────────────────────────────────────
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const res = await getIncidentCategories();
      return res.data.results || res.data || [];
    },
    staleTime: 5 * 60 * 1000,
  });

  const { data: priorities = [] } = useQuery({
    queryKey: ['priorities'],
    queryFn: async () => {
      try {
        const res = await getIncidentPriorities();
        return res.data.results || res.data || [];
      } catch (err) {
        console.error('Priority fetch error:', err);
        return [
          { id: 1, name: 'LOW' },
          { id: 2, name: 'MEDIUM' },
          { id: 3, name: 'HIGH' },
          { id: 4, name: 'CRITICAL' },
        ];
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  const { data: statuses = [] } = useQuery({
    queryKey: ['statuses'],
    queryFn: async () => {
      const res = await getIncidentStatuses();
      return res.data.results || res.data || [];
    },
    staleTime: 5 * 60 * 1000,
    enabled: isEditing,
  });

  const { data: subcategories = [] } = useQuery({
    queryKey: ['subcategories', formData.category],
    queryFn: async () => {
      if (!formData.category) return [];
      const res = await getSubcategoriesByCategory(formData.category);
      return res.data.results || res.data || [];
    },
    enabled: !!formData.category,
    staleTime: 5 * 60 * 1000,
  });

  // ─── Handlers ──────────────────────────────────────────────
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
    if (generalError) setGeneralError('');
  };

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer);
    setFormData((prev) => ({
      ...prev,
      customer: customer.id,
      address: customer.address || '',
    }));
    setShowNewCustomer(false);
    if (errors.customer) setErrors((prev) => ({ ...prev, customer: '' }));
  };

  const handleNewCustomerChange = (e) => {
    const { name, value } = e.target;
    setNewCustomer((prev) => ({ ...prev, [name]: value }));
    if (newCustomerErrors[name]) {
      setNewCustomerErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const toggleNewCustomer = () => {
    setShowNewCustomer((prev) => !prev);
    if (!showNewCustomer) {
      setSelectedCustomer(null);
      setFormData((prev) => ({ ...prev, customer: '', address: '' }));
    } else {
      setNewCustomer({ name: '', phone: '', email: '', address: '' });
      setNewCustomerErrors({});
    }
  };

  const validateNewCustomer = () => {
    const errs = {};
    if (!newCustomer.name.trim()) errs.name = 'Name is required';
    if (!newCustomer.phone.trim()) errs.phone = 'Phone is required';
    setNewCustomerErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const createAndSelectCustomer = async () => {
    if (!validateNewCustomer()) return;
    setCreatingCustomer(true);
    try {
      const response = await createCustomer(newCustomer);
      const customer = response.data;
      handleCustomerSelect(customer);
      setShowNewCustomer(false);
      setNewCustomer({ name: '', phone: '', email: '', address: '' });
    } catch (err) {
      console.error('Error creating customer:', err);
      if (err.response?.data) {
        const apiErrors = err.response.data;
        const fieldErrors = {};
        Object.keys(apiErrors).forEach((key) => {
          fieldErrors[key] = Array.isArray(apiErrors[key]) ? apiErrors[key][0] : apiErrors[key];
        });
        setNewCustomerErrors(fieldErrors);
      } else {
        setGeneralError('Failed to create customer. Please try again.');
      }
    } finally {
      setCreatingCustomer(false);
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.customer) newErrors.customer = 'Please select or create a customer';
    if (!formData.title?.trim()) newErrors.title = 'Title is required';
    if (!formData.target_resolution) newErrors.target_resolution = 'Target resolution is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ─── Submit ──────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (typeof onSubmit !== 'function') {
      console.error('onSubmit prop is not a function!', onSubmit);
      setGeneralError('Form configuration error. Please contact support.');
      return;
    }

    if (!validate()) {
      setGeneralError('Please fix the highlighted fields.');
      return;
    }

    setLoading(true);
    setGeneralError('');

    try {
      const payload = { ...formData };
      if (!payload.subcategory) delete payload.subcategory;
      if (!isEditing) delete payload.status;

      await onSubmit(payload);
    } catch (err) {
      console.error('Submission error:', err);
      if (err.response?.data) {
        const apiErrors = err.response.data;
        const fieldErrors = {};
        let generalMsg = '';

        Object.keys(apiErrors).forEach((key) => {
          if (key === 'non_field_errors' || key === 'detail') {
            generalMsg = Array.isArray(apiErrors[key]) ? apiErrors[key][0] : apiErrors[key];
          } else {
            fieldErrors[key] = Array.isArray(apiErrors[key]) ? apiErrors[key][0] : apiErrors[key];
          }
        });
        setErrors(fieldErrors);
        if (generalMsg) setGeneralError(generalMsg);
      } else {
        setGeneralError(err.message || 'An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // ─── Render ──────────────────────────────────────────────
  return (
    <div className="am-incident">
      <motion.div
        className="am-incident__card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      >
        {/* ─── Header ─────────────────────────────────────── */}
        <header className="am-incident__header">
          <div className="am-incident__title-group">
            <div className="am-incident__icon">
              <FaExclamationTriangle />
            </div>
            <div>
              <span className="am-eyebrow">{isEditing ? 'Update' : 'Create'}</span>
              <h2>{isEditing ? 'Edit Incident' : 'New Incident'}</h2>
              <p>
                {isEditing
                  ? 'Update the details of this incident and save your changes.'
                  : 'Log a new incident and assign a target resolution time.'}
              </p>
            </div>
          </div>

          <div className="am-incident__header-actions">
            {headerActions}
            {onLogout && (
              <button
                type="button"
                onClick={onLogout}
                className="am-btn am-btn--danger"
                aria-label="Logout"
              >
                <FaSignOutAlt />
                <span>Logout</span>
              </button>
            )}
          </div>
        </header>

        <form onSubmit={handleSubmit} className="am-incident__body" noValidate>
          {/* ─── General Error ─────────────────────────── */}
          <AnimatePresence>
            {generalError && (
              <motion.div
                className="am-alert"
                role="alert"
                initial={{ opacity: 0, y: -8, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, y: -8, height: 0 }}
              >
                <FaExclamationTriangle />
                <span>{generalError}</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ─── Customer Section ──────────────────────── */}
          <section className="am-section">
            <div className="am-section__head">
              <span className="am-section__step">1</span>
              <div>
                <h3>Customer</h3>
                <p>Select an existing customer or create a new one.</p>
              </div>
            </div>

            <div className="am-field">
              <label>
                Customer <span className="am-required">*</span>
              </label>

              {!showNewCustomer ? (
                <>
                  <CustomerSearch
                    onSelect={handleCustomerSelect}
                    onNewCustomer={() => {
                      setShowNewCustomer(true);
                      setSelectedCustomer(null);
                      setFormData((prev) => ({ ...prev, customer: '', address: '' }));
                    }}
                  />

                  <AnimatePresence>
                    {selectedCustomer && (
                      <motion.div
                        className="am-customer-selected"
                        initial={{ opacity: 0, y: -6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -6 }}
                      >
                        <div className="am-customer-selected__icon">
                          <FaUserCheck />
                        </div>
                        <div>
                          <strong>{selectedCustomer.name}</strong>
                          <span>{selectedCustomer.phone}</span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <button
                    type="button"
                    onClick={toggleNewCustomer}
                    className="am-btn am-btn--ghost am-btn--sm"
                  >
                    <FaUserPlus />
                    Create new customer
                  </button>
                </>
              ) : (
                <motion.div
                  className="am-new-customer"
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="am-new-customer__head">
                    <h4>New customer details</h4>
                    <button
                      type="button"
                      onClick={toggleNewCustomer}
                      className="am-icon-btn"
                      aria-label="Close"
                    >
                      <FaTimes />
                    </button>
                  </div>

                  <div className="am-grid am-grid--2">
                    <div className="am-field">
                      <label>
                        Full name <span className="am-required">*</span>
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={newCustomer.name}
                        onChange={handleNewCustomerChange}
                        placeholder="e.g. Kwame Mensah"
                        className={newCustomerErrors.name ? 'has-error' : ''}
                      />
                      {newCustomerErrors.name && (
                        <span className="am-error-text">{newCustomerErrors.name}</span>
                      )}
                    </div>

                    <div className="am-field">
                      <label>
                        Phone <span className="am-required">*</span>
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={newCustomer.phone}
                        onChange={handleNewCustomerChange}
                        placeholder="+233 000 000 000"
                        className={newCustomerErrors.phone ? 'has-error' : ''}
                      />
                      {newCustomerErrors.phone && (
                        <span className="am-error-text">{newCustomerErrors.phone}</span>
                      )}
                    </div>

                    <div className="am-field">
                      <label>Email</label>
                      <input
                        type="email"
                        name="email"
                        value={newCustomer.email}
                        onChange={handleNewCustomerChange}
                        placeholder="customer@example.com"
                        className={newCustomerErrors.email ? 'has-error' : ''}
                      />
                      {newCustomerErrors.email && (
                        <span className="am-error-text">{newCustomerErrors.email}</span>
                      )}
                    </div>

                    <div className="am-field">
                      <label>Address</label>
                      <input
                        type="text"
                        name="address"
                        value={newCustomer.address}
                        onChange={handleNewCustomerChange}
                        placeholder="Street, city, region"
                        className={newCustomerErrors.address ? 'has-error' : ''}
                      />
                      {newCustomerErrors.address && (
                        <span className="am-error-text">{newCustomerErrors.address}</span>
                      )}
                    </div>
                  </div>

                  <div className="am-new-customer__actions">
                    <button
                      type="button"
                      onClick={toggleNewCustomer}
                      className="am-btn am-btn--ghost am-btn--sm"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={createAndSelectCustomer}
                      disabled={creatingCustomer}
                      className="am-btn am-btn--success am-btn--sm"
                    >
                      {creatingCustomer ? (
                        <>
                          <span className="am-spinner am-spinner--sm am-spinner--dark" />
                          Creating…
                        </>
                      ) : (
                        <>
                          <FaUserPlus />
                          Create &amp; select
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              )}

              {errors.customer && (
                <span className="am-error-text">{errors.customer}</span>
              )}
            </div>
          </section>

          {/* ─── Incident Details ─────────────────────── */}
          <section className="am-section">
            <div className="am-section__head">
              <span className="am-section__step">2</span>
              <div>
                <h3>Incident details</h3>
                <p>Describe what happened and how urgent it is.</p>
              </div>
            </div>

            <div className="am-field">
              <label>
                Title <span className="am-required">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Brief summary of the issue"
                className={errors.title ? 'has-error' : ''}
              />
              {errors.title && <span className="am-error-text">{errors.title}</span>}
            </div>

            <div className="am-field">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                placeholder="Detailed description of the issue…"
              />
            </div>

            <div className="am-grid am-grid--2">
              <div className="am-field">
                <label>Category</label>
                <select name="category" value={formData.category} onChange={handleChange}>
                  <option value="">Select category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="am-field">
                <label>Subcategory</label>
                <select
                  name="subcategory"
                  value={formData.subcategory}
                  onChange={handleChange}
                  disabled={!formData.category}
                >
                  <option value="">Select subcategory</option>
                  {subcategories.map((sub) => (
                    <option key={sub.id} value={sub.id}>
                      {sub.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className={`am-grid ${isEditing ? 'am-grid--2' : ''}`}>
              <div className="am-field">
                <label>Priority</label>
                <select name="priority" value={formData.priority} onChange={handleChange}>
                  {priorities.map((pri) => (
                    <option key={pri.id} value={pri.name}>
                      {pri.name}
                    </option>
                  ))}
                </select>
              </div>

              {isEditing && (
                <div className="am-field">
                  <label>Status</label>
                  <select name="status" value={formData.status} onChange={handleChange}>
                    <option value="">Select status</option>
                    {statuses.map((stat) => (
                      <option key={stat.id} value={stat.id}>
                        {stat.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </section>

          {/* ─── Scheduling & Location ─────────────────── */}
          <section className="am-section">
            <div className="am-section__head">
              <span className="am-section__step">3</span>
              <div>
                <h3>Target &amp; location</h3>
                <p>When should this be resolved, and where is it happening?</p>
              </div>
            </div>

            <div className="am-field">
              <label>
                Target resolution <span className="am-required">*</span>
              </label>
              <div className={`am-input has-icon ${errors.target_resolution ? 'has-error' : ''}`}>
                <span className="am-input__icon">
                  <FaClock />
                </span>
                <input
                  type="datetime-local"
                  name="target_resolution"
                  value={formData.target_resolution}
                  onChange={handleChange}
                />
              </div>
              {errors.target_resolution && (
                <span className="am-error-text">{errors.target_resolution}</span>
              )}
              <p className="am-help">Expected time by which this incident should be resolved.</p>
            </div>

            <div className="am-field">
              <label>Location</label>
              <div className="am-input has-icon">
                <span className="am-input__icon">
                  <FaMapMarkerAlt />
                </span>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  placeholder="Address or GPS coordinates"
                />
              </div>
            </div>
          </section>

          {/* ─── Actions ──────────────────────────────── */}
          <div className="am-incident__actions">
            <button type="button" onClick={onCancel} className="am-btn am-btn--ghost">
              <FaArrowLeft />
              Back to list
            </button>

            <div className="am-incident__actions-right">
              <button type="button" onClick={onCancel} className="am-btn am-btn--ghost">
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || creatingCustomer}
                className="am-btn am-btn--primary am-btn--cta"
              >
                {loading ? (
                  <>
                    <span className="am-spinner am-spinner--sm" />
                    Saving…
                  </>
                ) : (
                  <>
                    <FaSave />
                    {isEditing ? 'Update incident' : 'Create incident'}
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

IncidentForm.propTypes = {
  initialData: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isEditing: PropTypes.bool,
  headerActions: PropTypes.node,
  onLogout: PropTypes.func,
};