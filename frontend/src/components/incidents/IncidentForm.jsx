// src/components/incidents/IncidentForm.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { FaSignOutAlt } from 'react-icons/fa';
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
  onLogout = null, // <-- new: optional logout handler
}) => {
  // ─── Lazy initializer ──────────────────────────────────────
  const getDefaultTargetResolution = () => {
    return new Date(Date.now() + 24 * 60 * 60 * 1000)
      .toISOString()
      .slice(0, 16);
  };

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
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
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
    if (errors.customer) {
      setErrors((prev) => ({ ...prev, customer: '' }));
    }
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
    <div className="incident-form-container">
      {/* ─── Header ────────────────────────────────────────── */}
      <div className="incident-form-header">
        <div className="incident-form-header__title-group">
          <span className="incident-form-header__icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </span>
          <h2>{isEditing ? 'Edit Incident' : 'New Incident'}</h2>
        </div>

        <div className="incident-form-header__actions">
          {headerActions}
          {onLogout && (
            <button
              type="button"
              onClick={onLogout}
              className="btn btn-logout"
              aria-label="Logout"
            >
              <FaSignOutAlt className="btn-icon" />
              <span>Logout</span>
            </button>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="incident-form">
        {/* ─── General Error ────────────────────────────────── */}
        {generalError && (
          <div className="error-banner">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{generalError}</span>
          </div>
        )}

        {/* ─── Customer Section ────────────────────────────── */}
        <div className="field-group">
          <label>
            Customer <span className="required-star">*</span>
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
              {selectedCustomer && (
                <div className="customer-selected">
                  <span className="customer-name">{selectedCustomer.name}</span>
                  <span className="customer-phone">{selectedCustomer.phone}</span>
                </div>
              )}
              <button
                type="button"
                onClick={toggleNewCustomer}
                className="new-customer-toggle"
              >
                + Create new customer
              </button>
            </>
          ) : (
            <div className="new-customer-form">
              <h4>New Customer Details</h4>
              <div className="grid-2">
                <div className="field-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={newCustomer.name}
                    onChange={handleNewCustomerChange}
                    className={newCustomerErrors.name ? 'input-error' : ''}
                  />
                  {newCustomerErrors.name && (
                    <span className="error-text">{newCustomerErrors.name}</span>
                  )}
                </div>
                <div className="field-group">
                  <label>Phone *</label>
                  <input
                    type="tel"
                    name="phone"
                    value={newCustomer.phone}
                    onChange={handleNewCustomerChange}
                    className={newCustomerErrors.phone ? 'input-error' : ''}
                  />
                  {newCustomerErrors.phone && (
                    <span className="error-text">{newCustomerErrors.phone}</span>
                  )}
                </div>
                <div className="field-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={newCustomer.email}
                    onChange={handleNewCustomerChange}
                    className={newCustomerErrors.email ? 'input-error' : ''}
                  />
                  {newCustomerErrors.email && (
                    <span className="error-text">{newCustomerErrors.email}</span>
                  )}
                </div>
                <div className="field-group">
                  <label>Address</label>
                  <input
                    type="text"
                    name="address"
                    value={newCustomer.address}
                    onChange={handleNewCustomerChange}
                    className={newCustomerErrors.address ? 'input-error' : ''}
                  />
                  {newCustomerErrors.address && (
                    <span className="error-text">{newCustomerErrors.address}</span>
                  )}
                </div>
              </div>
              <div className="btn-group" style={{ justifyContent: 'flex-end', borderTop: 'none', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={toggleNewCustomer}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={createAndSelectCustomer}
                  disabled={creatingCustomer}
                  className="btn btn-success"
                >
                  {creatingCustomer ? 'Creating...' : 'Create & Select'}
                </button>
              </div>
            </div>
          )}
          {errors.customer && (
            <span className="error-text">{errors.customer}</span>
          )}
        </div>

        {/* ─── Title ────────────────────────────────────────── */}
        <div className="field-group">
          <label>
            Title <span className="required-star">*</span>
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Brief summary of the issue"
            className={errors.title ? 'input-error' : ''}
          />
          {errors.title && <span className="error-text">{errors.title}</span>}
        </div>

        {/* ─── Description ──────────────────────────────────── */}
        <div className="field-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="3"
            placeholder="Detailed description of the issue..."
          />
        </div>

        {/* ─── Category & Subcategory ──────────────────────── */}
        <div className="grid-2">
          <div className="field-group">
            <label>Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
            >
              <option value="">Select category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div className="field-group">
            <label>Subcategory</label>
            <select
              name="subcategory"
              value={formData.subcategory}
              onChange={handleChange}
              disabled={!formData.category}
            >
              <option value="">Select subcategory</option>
              {subcategories.map((sub) => (
                <option key={sub.id} value={sub.id}>{sub.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* ─── Priority ─────────────────────────────────────── */}
        <div className="field-group">
          <label>Priority</label>
          <select
            name="priority"
            value={formData.priority}
            onChange={handleChange}
          >
            {priorities.map((pri) => (
              <option key={pri.id} value={pri.name}>{pri.name}</option>
            ))}
          </select>
        </div>

        {/* ─── Status (only when editing) ───────────────────── */}
        {isEditing && (
          <div className="field-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="">Select status</option>
              {statuses.map((stat) => (
                <option key={stat.id} value={stat.id}>{stat.name}</option>
              ))}
            </select>
          </div>
        )}

        {/* ─── Target Resolution ───────────────────────────── */}
        <div className="field-group">
          <label>
            Target Resolution <span className="required-star">*</span>
          </label>
          <input
            type="datetime-local"
            name="target_resolution"
            value={formData.target_resolution}
            onChange={handleChange}
            className={errors.target_resolution ? 'input-error' : ''}
          />
          {errors.target_resolution && (
            <span className="error-text">{errors.target_resolution}</span>
          )}
          <p className="text-xs text-gray-400 mt-1">
            Expected time by which this incident should be resolved.
          </p>
        </div>

        {/* ─── Location ─────────────────────────────────────── */}
        <div className="field-group">
          <label>Location</label>
          <input
            type="text"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="Address or GPS coordinates"
          />
        </div>

        {/* ─── Buttons ──────────────────────────────────────── */}
        <div className="btn-group">
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
          >
            Incident List
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || creatingCustomer}
            className="btn btn-primary"
          >
            {loading ? (
              <>
                <span className="spinner" />
                Saving...
              </>
            ) : (
              isEditing ? 'Update Incident' : 'Create Incident'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

IncidentForm.propTypes = {
  initialData: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isEditing: PropTypes.bool,
  headerActions: PropTypes.node,
  onLogout: PropTypes.func, // <-- new
};