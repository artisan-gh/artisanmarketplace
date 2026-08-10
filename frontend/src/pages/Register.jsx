import { useState, useId } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import {
  FaUserPlus, FaEnvelope, FaUser, FaPhone, FaCalendarAlt, FaLock,
  FaEye, FaEyeSlash, FaExclamationCircle, FaIdCard, FaGlobe,
  FaPhoneAlt, FaFileUpload, FaCamera, FaTags,
} from 'react-icons/fa';
import './Login.css';
import './Register.css';

// ─── Configuration ──────────────────────────────────────────
const DAYS_OF_WEEK = [
  { value: 'MONDAY', label: 'Monday' },
  { value: 'TUESDAY', label: 'Tuesday' },
  { value: 'WEDNESDAY', label: 'Wednesday' },
  { value: 'THURSDAY', label: 'Thursday' },
  { value: 'FRIDAY', label: 'Friday' },
  { value: 'SATURDAY', label: 'Saturday' },
  { value: 'SUNDAY', label: 'Sunday' },
];

const GENDER_OPTIONS = [
  { value: 'MALE',   label: 'Male' },
  { value: 'FEMALE', label: 'Female' },
  { value: 'OTHER',  label: 'Other' },
];

const DOCUMENT_TYPES = [
  { value: 'National ID', label: 'National ID' },
  { value: 'Passport', label: 'Passport' },
  { value: "Driver's License", label: "Driver's License" },
  { value: 'Work Permit', label: 'Work Permit' },
  { value: 'Other', label: 'Other' },
];

const TIMEZONES = [
  'UTC', 'Africa/Accra', 'Africa/Lagos', 'Africa/Nairobi',
  'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
  'Europe/London', 'Europe/Paris', 'Europe/Berlin',
  'Asia/Dubai', 'Asia/Kolkata', 'Asia/Singapore', 'Asia/Tokyo',
  'Australia/Sydney',
];

// ─── Axios instance ──────────────────────────────────────────
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const api = axios.create({ baseURL: API_BASE_URL });

export default function Register() {
  const [form, setForm] = useState({
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    user_type: 'ARTISAN',
    date_of_birth: '',
    gender: '',
    identification_document_type: '',
    identification_number: '',
    timezone: 'UTC',
    emergency_contact_name: '',
    emergency_contact_phone: '',
  });

  const [availabilityDays, setAvailabilityDays] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSkills, setSelectedSkills] = useState([]);

  const [profilePicture, setProfilePicture] = useState(null);
  const [proofOfAddress, setProofOfAddress] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();
  const idPrefix = useId();

  // ─── Fetch categories ──────────────────────────────────────
  const { data: categories = [], isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      try {
        const res = await api.get('/public/categories/');
        return res.data.results || res.data || [];
      } catch (err) {
        console.error('Failed to fetch categories:', err);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  // ─── Fetch subcategories ───────────────────────────────────
  const { data: subcategories = [], isLoading: subcategoriesLoading } = useQuery({
    queryKey: ['subcategories', selectedCategory],
    queryFn: async () => {
      if (!selectedCategory) return [];
      try {
        const res = await api.get(`/public/subcategories/?category=${selectedCategory}`);
        return res.data.results || res.data || [];
      } catch (err) {
        console.error('Failed to fetch subcategories:', err);
        return [];
      }
    },
    enabled: !!selectedCategory,
    staleTime: 5 * 60 * 1000,
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (name === 'profile_picture') {
      setProfilePicture(files[0]);
    } else if (name === 'proof_of_address') {
      setProofOfAddress(files[0]);
    }
  };

  const handleDayToggle = (day) => {
    setAvailabilityDays((prev) =>
      prev.includes(day)
        ? prev.filter((d) => d !== day)
        : [...prev, day]
    );
  };

  const handleSkillToggle = (skillId) => {
    setSelectedSkills((prev) =>
      prev.includes(skillId)
        ? prev.filter((id) => id !== skillId)
        : [...prev, skillId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (form.password !== form.password2) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    if (!selectedCategory) {
      setError('Please select a category/trade area.');
      setLoading(false);
      return;
    }

    if (!profilePicture) {
      setError('Please upload a profile picture.');
      setLoading(false);
      return;
    }

    if (!proofOfAddress) {
      setError('Please upload an ID document.');
      setLoading(false);
      return;
    }

    if (availabilityDays.length === 0) {
      setError('Please select at least one availability day.');
      setLoading(false);
      return;
    }

    if (selectedSkills.length === 0) {
      setError('Please select at least one skill.');
      setLoading(false);
      return;
    }

    const formData = new FormData();

    formData.append('email', form.email);
    formData.append('password', form.password);
    formData.append('confirm_password', form.password2);
    formData.append('first_name', form.first_name);
    formData.append('last_name', form.last_name);
    formData.append('phone_number', form.phone_number);
    formData.append('user_type', form.user_type);

    formData.append('date_of_birth', form.date_of_birth);
    formData.append('gender', form.gender);
    formData.append('identification_document_type', form.identification_document_type);
    formData.append('identification_number', form.identification_number);
    formData.append('timezone', form.timezone);
    formData.append('emergency_contact_name', form.emergency_contact_name);
    formData.append('emergency_contact_phone', form.emergency_contact_phone);

    formData.append('profile_picture', profilePicture);
    formData.append('proof_of_address', proofOfAddress);

    formData.append('category', String(selectedCategory));
    formData.append('availability_days', JSON.stringify(availabilityDays));
    formData.append('skills', JSON.stringify(selectedSkills));

    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      console.error('Registration error:', err);
      let errorMessage = '';

      if (typeof err === 'object' && err !== null) {
        if (err.detail) {
          errorMessage = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
        } else if (typeof err === 'object') {
          const messages = [];
          for (const [key, value] of Object.entries(err)) {
            if (key !== 'non_field_errors') {
              const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
              if (Array.isArray(value)) {
                messages.push(`${label}: ${value.join(' ')}`);
              } else if (typeof value === 'string') {
                messages.push(`${label}: ${value}`);
              }
            }
          }
          if (err.non_field_errors) {
            const nonField = Array.isArray(err.non_field_errors)
              ? err.non_field_errors.join(' ')
              : err.non_field_errors;
            messages.push(nonField);
          }
          errorMessage = messages.length > 0 ? messages.join(' | ') : 'Registration failed. Please check your details.';
        } else if (typeof err === 'string') {
          errorMessage = err;
        }
      } else {
        errorMessage = 'An unexpected error occurred. Please try again.';
      }

      setError(errorMessage || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const id = (name) => `${idPrefix}-${name}`;

  return (
    <div className="login-page register-page">
      <div className="glow-field" aria-hidden="true">
        <div className="glow glow-blue" />
        <div className="glow glow-purple" />
        <div className="glow glow-indigo" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 28, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        className="login-card-wrap"
      >
        <div className="login-card">
          <div className="brand">
            <div className="brand-badge">
              <FaUserPlus aria-hidden="true" />
            </div>
            <h1>
              Artisan <span className="brand-gradient-text">Marketplace</span>
            </h1>
            <p>Create your Artisan account</p>
          </div>

          <h2 className="form-heading">Get started</h2>

          <AnimatePresence>
            {error && (
              <motion.div
                role="alert"
                aria-live="assertive"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="error-banner"
              >
                <FaExclamationCircle aria-hidden="true" />
                <span>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="login-form" encType="multipart/form-data" noValidate>
            <div className="field-group">
              <label htmlFor={id('email')} className="field-label">Email *</label>
              <div className="input-wrap">
                <FaEnvelope className="input-icon" aria-hidden="true" />
                <input
                  id={id('email')}
                  name="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  className="text-input"
                  value={form.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="field-grid-2">
              <div className="field-group">
                <label htmlFor={id('first_name')} className="field-label">First name *</label>
                <div className="input-wrap">
                  <FaUser className="input-icon" aria-hidden="true" />
                  <input
                    id={id('first_name')}
                    name="first_name"
                    autoComplete="given-name"
                    placeholder="Jane"
                    className="text-input"
                    value={form.first_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div className="field-group">
                <label htmlFor={id('last_name')} className="field-label">Last name *</label>
                <div className="input-wrap">
                  <FaUser className="input-icon" aria-hidden="true" />
                  <input
                    id={id('last_name')}
                    name="last_name"
                    autoComplete="family-name"
                    placeholder="Doe"
                    className="text-input"
                    value={form.last_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="field-grid-3">
              <div className="field-group">
                <label htmlFor={id('phone_number')} className="field-label">Phone *</label>
                <div className="input-wrap">
                  <FaPhone className="input-icon" aria-hidden="true" />
                  <input
                    id={id('phone_number')}
                    name="phone_number"
                    type="tel"
                    autoComplete="tel"
                    placeholder="+233 000 000 000"
                    className="text-input"
                    value={form.phone_number}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div className="field-group">
                <label htmlFor={id('date_of_birth')} className="field-label">Birth date *</label>
                <div className="input-wrap">
                  <FaCalendarAlt className="input-icon" aria-hidden="true" />
                  <input
                    id={id('date_of_birth')}
                    name="date_of_birth"
                    type="date"
                    className="text-input"
                    value={form.date_of_birth}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div className="field-group">
                <label htmlFor={id('gender')} className="field-label">Gender *</label>
                <select
                  id={id('gender')}
                  name="gender"
                  className="text-input select-input"
                  value={form.gender}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select</option>
                  {GENDER_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="section-divider">
              <span className="section-label">KYC Information</span>
            </div>

            <div className="field-grid-2">
              <div className="field-group">
                <label htmlFor={id('identification_document_type')} className="field-label">ID Document Type *</label>
                <select
                  id={id('identification_document_type')}
                  name="identification_document_type"
                  className="text-input select-input"
                  value={form.identification_document_type}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select</option>
                  {DOCUMENT_TYPES.map((doc) => (
                    <option key={doc.value} value={doc.value}>
                      {doc.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-group">
                <label htmlFor={id('identification_number')} className="field-label">ID Number *</label>
                <div className="input-wrap">
                  <FaIdCard className="input-icon" aria-hidden="true" />
                  <input
                    id={id('identification_number')}
                    name="identification_number"
                    type="text"
                    placeholder="e.g., GHA-123456"
                    className="text-input"
                    value={form.identification_number}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </div>

            {/* ─── Upload ID Document ──────────────────────────── */}
            <div className="field-group">
              <label htmlFor={id('proof_of_address')} className="field-label">
                Upload ID Document (PDF/Image) *
              </label>
              <div className="input-wrap file-wrap">
                <FaFileUpload className="input-icon" aria-hidden="true" />
                <input
                  id={id('proof_of_address')}
                  name="proof_of_address"
                  type="file"
                  accept=".pdf,application/pdf,.jpg,.jpeg,.png,image/*" // ✅ enhanced
                  onChange={handleFileChange}
                  className="file-input"
                  required
                />
                {proofOfAddress && (
                  <span className="file-name">{proofOfAddress.name}</span>
                )}
              </div>
            </div>

            <div className="field-group">
              <label htmlFor={id('profile_picture')} className="field-label">Profile Picture *</label>
              <div className="input-wrap file-wrap">
                <FaCamera className="input-icon" aria-hidden="true" />
                <input
                  id={id('profile_picture')}
                  name="profile_picture"
                  type="file"
                  accept=".jpg,.jpeg,.png,image/*"
                  onChange={handleFileChange}
                  className="file-input"
                  required
                />
                {profilePicture && (
                  <span className="file-name">{profilePicture.name}</span>
                )}
              </div>
            </div>

            <div className="section-divider">
              <span className="section-label">Emergency & Preferences</span>
            </div>

            <div className="field-grid-2">
              <div className="field-group">
                <label htmlFor={id('emergency_contact_name')} className="field-label">Emergency Contact Name *</label>
                <div className="input-wrap">
                  <FaUser className="input-icon" aria-hidden="true" />
                  <input
                    id={id('emergency_contact_name')}
                    name="emergency_contact_name"
                    type="text"
                    placeholder="Next of kin"
                    className="text-input"
                    value={form.emergency_contact_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div className="field-group">
                <label htmlFor={id('emergency_contact_phone')} className="field-label">Emergency Contact Phone *</label>
                <div className="input-wrap">
                  <FaPhoneAlt className="input-icon" aria-hidden="true" />
                  <input
                    id={id('emergency_contact_phone')}
                    name="emergency_contact_phone"
                    type="tel"
                    placeholder="+233 000 000 000"
                    className="text-input"
                    value={form.emergency_contact_phone}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="field-group">
              <label htmlFor={id('timezone')} className="field-label">Timezone *</label>
              <div className="input-wrap">
                <FaGlobe className="input-icon" aria-hidden="true" />
                <select
                  id={id('timezone')}
                  name="timezone"
                  className="text-input select-input"
                  value={form.timezone}
                  onChange={handleChange}
                  required
                >
                  {TIMEZONES.map((tz) => (
                    <option key={tz} value={tz}>{tz}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="section-divider">
              <span className="section-label">Artisan Details</span>
            </div>

            <div className="field-group">
              <label className="field-label">Availability Days</label>
              <div className="availability-grid">
                {DAYS_OF_WEEK.map((day) => (
                  <label key={day.value} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={availabilityDays.includes(day.value)}
                      onChange={() => handleDayToggle(day.value)}
                    />
                    <span className="checkbox-text">{day.label}</span>
                  </label>
                ))}
              </div>
              <small className="helper-text">Select the days you are available to work.</small>
            </div>

            <div className="field-group">
              <label htmlFor={id('category')} className="field-label">Category / Trade Area *</label>
              <div className="input-wrap">
                <FaTags className="input-icon" aria-hidden="true" />
                <select
                  id={id('category')}
                  name="category"
                  className="text-input select-input"
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    setSelectedSkills([]);
                  }}
                  disabled={categoriesLoading}
                  required
                >
                  <option value="">{categoriesLoading ? 'Loading categories...' : 'Select a category'}</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              {categories.length === 0 && !categoriesLoading && (
                <p className="helper-text helper-text--error">
                  No categories loaded. Please refresh or try again shortly.
                </p>
              )}
            </div>

            <div className="field-group">
              <label className="field-label">Skills *</label>
              <div className="skills-grid">
                {subcategoriesLoading && <p className="helper-text">Loading skills...</p>}
                {!selectedCategory && !subcategoriesLoading && (
                  <p className="helper-text">Please select a category first.</p>
                )}
                {selectedCategory && !subcategoriesLoading && subcategories.length === 0 && (
                  <p className="helper-text">No skills available for this category.</p>
                )}
                {selectedCategory &&
                  subcategories.map((skill) => (
                    <label key={skill.id} className={`checkbox-label ${selectedSkills.includes(skill.id) ? 'active' : ''}`}>
                      <input
                        type="checkbox"
                        checked={selectedSkills.includes(skill.id)}
                        onChange={() => handleSkillToggle(skill.id)}
                      />
                      <span className="checkbox-text">{skill.name}</span>
                    </label>
                  ))}
              </div>
              <small className="helper-text">Select all skills that apply to you.</small>
            </div>

            <div className="section-divider">
              <span className="section-label">Security</span>
            </div>

            <div className="field-grid-2">
              <div className="field-group">
                <label htmlFor={id('password')} className="field-label">Password *</label>
                <div className="input-wrap">
                  <FaLock className="input-icon" aria-hidden="true" />
                  <input
                    id={id('password')}
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    placeholder="Min 8 characters"
                    className="text-input has-toggle"
                    value={form.password}
                    onChange={handleChange}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    aria-pressed={showPassword}
                    className="password-toggle"
                  >
                    <AnimatePresence mode="wait" initial={false}>
                      {showPassword ? (
                        <motion.span key="hide" initial={{ opacity: 0, rotate: -45, scale: 0.7 }} animate={{ opacity: 1, rotate: 0, scale: 1 }} exit={{ opacity: 0, rotate: 45, scale: 0.7 }} transition={{ duration: 0.15 }} style={{ display: 'flex' }}>
                          <FaEyeSlash aria-hidden="true" />
                        </motion.span>
                      ) : (
                        <motion.span key="show" initial={{ opacity: 0, rotate: 45, scale: 0.7 }} animate={{ opacity: 1, rotate: 0, scale: 1 }} exit={{ opacity: 0, rotate: -45, scale: 0.7 }} transition={{ duration: 0.15 }} style={{ display: 'flex' }}>
                          <FaEye aria-hidden="true" />
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </button>
                </div>
              </div>

              <div className="field-group">
                <label htmlFor={id('password2')} className="field-label">Confirm password *</label>
                <div className="input-wrap">
                  <FaLock className="input-icon" aria-hidden="true" />
                  <input
                    id={id('password2')}
                    name="password2"
                    type={showPassword2 ? 'text' : 'password'}
                    autoComplete="new-password"
                    placeholder="Re-enter password"
                    className="text-input has-toggle"
                    value={form.password2}
                    onChange={handleChange}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword2((v) => !v)}
                    aria-label={showPassword2 ? 'Hide password' : 'Show password'}
                    aria-pressed={showPassword2}
                    className="password-toggle"
                  >
                    <AnimatePresence mode="wait" initial={false}>
                      {showPassword2 ? (
                        <motion.span key="hide" initial={{ opacity: 0, rotate: -45, scale: 0.7 }} animate={{ opacity: 1, rotate: 0, scale: 1 }} exit={{ opacity: 0, rotate: 45, scale: 0.7 }} transition={{ duration: 0.15 }} style={{ display: 'flex' }}>
                          <FaEyeSlash aria-hidden="true" />
                        </motion.span>
                      ) : (
                        <motion.span key="show" initial={{ opacity: 0, rotate: 45, scale: 0.7 }} animate={{ opacity: 1, rotate: 0, scale: 1 }} exit={{ opacity: 0, rotate: -45, scale: 0.7 }} transition={{ duration: 0.15 }} style={{ display: 'flex' }}>
                          <FaEye aria-hidden="true" />
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </button>
                </div>
              </div>
            </div>

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              aria-busy={loading}
              className="submit-btn"
            >
              {loading ? (
                <>
                  <span className="spinner" aria-hidden="true" />
                  <span className="sr-only">Creating account…</span>
                </>
              ) : (
                <>
                  <FaUserPlus aria-hidden="true" />
                  Create Artisan Account
                </>
              )}
            </motion.button>
          </form>

          <div className="divider-row">
            <span className="divider-label">Or</span>
          </div>
          <div className="social-grid">
            <button type="button" className="social-btn">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path fill="#EA4335" d="M12.545 10.239v3.821h5.445c-.712 2.315-2.647 3.972-5.445 3.972a6.033 6.033 0 110-12.064c1.498 0 2.866.549 3.921 1.453l2.814-2.814A9.969 9.969 0 0012.545 2C7.021 2 2.543 6.478 2.543 12s4.478 10 10.002 10c8.396 0 10.249-7.85 9.426-11.748l-9.426-.013z" />
              </svg>
              Google
            </button>
            <button type="button" className="social-btn">
              <svg fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.03-2.682-.103-.253-.447-1.27.098-2.646 0 0 .84-.269 2.75 1.025.8-.223 1.65-.334 2.5-.334.85 0 1.7.111 2.5.334 1.91-1.294 2.75-1.025 2.75-1.025.545 1.376.201 2.393.099 2.646.64.698 1.03 1.591 1.03 2.682 0 3.841-2.337 4.687-4.565 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.161 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
              </svg>
              GitHub
            </button>
          </div>

          <div className="login-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="signup-link">Sign in</Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}