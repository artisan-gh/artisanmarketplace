import { useState, useRef, useId } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaUser, FaPhone, FaCalendarAlt, FaIdCard, FaCamera, FaImage,
  FaCheckCircle, FaExclamationCircle, FaArrowLeft, FaUserEdit,
} from 'react-icons/fa';
import './Profile.css';

export default function Profile() {
  const { user, updateProfile } = useAuth();

  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone_number: user?.phone_number || '',
    date_of_birth: user?.date_of_birth || '',
    gender: user?.gender || '',
    national_id: user?.national_id || '',
  });

  const [profilePicture, setProfilePicture] = useState(user?.profile_picture || '');
  const [previewUrl, setPreviewUrl] = useState(user?.profile_picture || '');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fileInputRef = useRef(null);
  const idPrefix = useId();
  const id = (name) => `${idPrefix}-${name}`;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file.');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size must be less than 5MB.');
        return;
      }
      setProfilePicture(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      Object.keys(form).forEach((key) => {
        if (form[key]) {
          formData.append(key, form[key]);
        }
      });
      if (profilePicture instanceof File) {
        formData.append('profile_picture', profilePicture);
      }

      await updateProfile(formData);
      setMessage('Profile updated successfully');
    } catch (err) {
      setError(err?.detail || err?.message || 'Profile update failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="profile-loading">
        <div>
          <div className="profile-loading-spinner" aria-hidden="true" />
          <p>Loading profile…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="glow-field" aria-hidden="true">
        <div className="glow glow-blue" />
        <div className="glow glow-purple" />
        <div className="glow glow-indigo" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 28, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        className="profile-card-wrap"
      >
        <Link to="/dashboard" className="back-link">
          <FaArrowLeft aria-hidden="true" />
          Back to dashboard
        </Link>

        <div className="profile-card">
          <div className="profile-header">
            <h1>Profile</h1>
            <p>Update your personal information</p>
          </div>

          <AnimatePresence>
            {message && (
              <motion.div
                role="status"
                aria-live="polite"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="status-banner is-success"
              >
                <FaCheckCircle aria-hidden="true" />
                <span>{message}</span>
              </motion.div>
            )}
            {error && (
              <motion.div
                role="alert"
                aria-live="assertive"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="status-banner is-error"
              >
                <FaExclamationCircle aria-hidden="true" />
                <span>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} encType="multipart/form-data" className="profile-form" noValidate>
            {/* Email (read-only) */}
            <div className="field-group">
              <label htmlFor={id('email')} className="field-label">Email</label>
              <div className="input-wrap">
                <FaUser className="input-icon" aria-hidden="true" />
                <input
                  id={id('email')}
                  type="email"
                  value={user.email}
                  disabled
                  className="text-input"
                />
              </div>
            </div>

            {/* Profile picture */}
            <div className="field-group">
              <span className="field-label">Profile picture</span>
              <div className="avatar-row">
                <div className="avatar-preview">
                  {previewUrl ? (
                    <img src={previewUrl} alt="Profile" />
                  ) : (
                    <FaImage className="avatar-preview-empty" aria-hidden="true" />
                  )}
                </div>
                <div className="avatar-actions">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="avatar-choose-btn"
                  >
                    <FaCamera aria-hidden="true" />
                    Choose image
                  </button>
                  <p className="avatar-hint">JPG, PNG, GIF up to 5MB</p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="visually-hidden"
                  aria-label="Upload profile picture"
                />
              </div>
            </div>

            {/* Name */}
            <div className="field-grid-2">
              <div className="field-group">
                <label htmlFor={id('first_name')} className="field-label">First name</label>
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
                  />
                </div>
              </div>
              <div className="field-group">
                <label htmlFor={id('last_name')} className="field-label">Last name</label>
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
                  />
                </div>
              </div>
            </div>

            {/* Phone */}
            <div className="field-group">
              <label htmlFor={id('phone_number')} className="field-label">Phone number</label>
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
                />
              </div>
            </div>

            {/* DOB + Gender */}
            <div className="field-grid-2">
              <div className="field-group">
                <label htmlFor={id('date_of_birth')} className="field-label">Date of birth</label>
                <div className="input-wrap">
                  <FaCalendarAlt className="input-icon" aria-hidden="true" />
                  <input
                    id={id('date_of_birth')}
                    name="date_of_birth"
                    type="date"
                    className="text-input"
                    value={form.date_of_birth}
                    onChange={handleChange}
                  />
                </div>
              </div>
              <div className="field-group">
                <label htmlFor={id('gender')} className="field-label">Gender</label>
                <div className="input-wrap">
                  <FaUser className="input-icon" aria-hidden="true" />
                  <select
                    id={id('gender')}
                    name="gender"
                    className="text-input select-input"
                    value={form.gender}
                    onChange={handleChange}
                  >
                    <option value="">Select</option>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="O">Other</option>
                  </select>
                </div>
              </div>
            </div>

            {/* National ID */}
            <div className="field-group">
              <label htmlFor={id('national_id')} className="field-label">National ID</label>
              <div className="input-wrap">
                <FaIdCard className="input-icon" aria-hidden="true" />
                <input
                  id={id('national_id')}
                  name="national_id"
                  placeholder="e.g., GHA-123456"
                  className="text-input"
                  value={form.national_id}
                  onChange={handleChange}
                />
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
                  <span className="visually-hidden">Updating…</span>
                </>
              ) : (
                <>
                  <FaUserEdit aria-hidden="true" />
                  Update profile
                </>
              )}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}