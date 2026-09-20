import { useState, useId } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import {
  FaUserPlus,
  FaEnvelope,
  FaUser,
  FaPhone,
  FaCalendarAlt,
  FaLock,
  FaEye,
  FaEyeSlash,
  FaExclamationCircle,
  FaIdCard,
  FaGlobe,
  FaPhoneAlt,
  FaCamera,
  FaTags,
  FaArrowLeft,
  FaArrowRight,
  FaCheck,
  FaShieldAlt,
  FaBriefcase,
  FaClock,
  FaCloudUploadAlt,
  FaCheckCircle,
} from 'react-icons/fa';

import './Register.css';

const DAYS_OF_WEEK = [
  { value: 'MONDAY', label: 'Monday', short: 'Mon' },
  { value: 'TUESDAY', label: 'Tuesday', short: 'Tue' },
  { value: 'WEDNESDAY', label: 'Wednesday', short: 'Wed' },
  { value: 'THURSDAY', label: 'Thursday', short: 'Thu' },
  { value: 'FRIDAY', label: 'Friday', short: 'Fri' },
  { value: 'SATURDAY', label: 'Saturday', short: 'Sat' },
  { value: 'SUNDAY', label: 'Sunday', short: 'Sun' },
];

const GENDER_OPTIONS = [
  { value: 'MALE', label: 'Male' },
  { value: 'FEMALE', label: 'Female' },
  { value: 'OTHER', label: 'Other' },
];

const DOCUMENT_TYPES = [
  { value: 'National ID', label: 'National ID' },
  { value: 'Passport', label: 'Passport' },
  { value: "Driver's License", label: "Driver's License" },
  { value: 'Work Permit', label: 'Work Permit' },
  { value: 'Other', label: 'Other' },
];

const TIMEZONES = [
  'UTC',
  'Africa/Accra',
  'Africa/Lagos',
  'Africa/Nairobi',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Asia/Dubai',
  'Asia/Kolkata',
  'Asia/Singapore',
  'Asia/Tokyo',
  'Australia/Sydney',
];

const STEPS = [
  { number: 1, title: 'Account', description: 'Create your secure account', icon: FaUser },
  { number: 2, title: 'About You', description: 'Tell us about yourself', icon: FaUserPlus },
  { number: 3, title: 'Profession', description: 'Choose your trade', icon: FaBriefcase },
  { number: 4, title: 'Skills', description: 'Select your expertise', icon: FaTags },
  { number: 5, title: 'Availability', description: 'Set your schedule', icon: FaClock },
  { number: 6, title: 'Verification', description: 'Verify your identity', icon: FaShieldAlt },
  { number: 7, title: 'Emergency', description: 'Emergency contact', icon: FaPhoneAlt },
];

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://backendapi-tv2v.onrender.com';

const api = axios.create({ baseURL: API_BASE_URL });

const stepTransition = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, y: -12, transition: { duration: 0.2 } },
};

export default function Register() {
  const [currentStep, setCurrentStep] = useState(1);

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
    timezone: 'Africa/Accra',
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

  const id = (name) => `${idPrefix}-${name}`;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (!files || !files[0]) return;
    if (name === 'profile_picture') setProfilePicture(files[0]);
    if (name === 'proof_of_address') setProofOfAddress(files[0]);
    setError('');
  };

  const handleDayToggle = (day) => {
    setAvailabilityDays((prev) =>
      prev.includes(day) ? prev.filter((item) => item !== day) : [...prev, day]
    );
    setError('');
  };

  const handleSkillToggle = (skillId) => {
    setSelectedSkills((prev) =>
      prev.includes(skillId) ? prev.filter((i) => i !== skillId) : [...prev, skillId]
    );
    setError('');
  };

  const validateStep = (step) => {
    setError('');

    if (step === 1) {
      if (!form.first_name.trim() || !form.last_name.trim() || !form.phone_number.trim() || !form.email.trim()) {
        setError('Please complete all required account details.');
        return false;
      }
      if (!form.password || !form.password2) {
        setError('Please create and confirm your password.');
        return false;
      }
      if (form.password !== form.password2) {
        setError('Passwords do not match.');
        return false;
      }
      if (form.password.length < 8) {
        setError('Password must contain at least 8 characters.');
        return false;
      }
    }

    if (step === 2) {
      if (!form.date_of_birth || !form.gender) {
        setError('Please provide your date of birth and gender.');
        return false;
      }
      if (!profilePicture) {
        setError('Please upload a profile picture.');
        return false;
      }
    }

    if (step === 3 && !selectedCategory) {
      setError('Please select your main profession or trade.');
      return false;
    }

    if (step === 4 && selectedSkills.length === 0) {
      setError('Please select at least one skill.');
      return false;
    }

    if (step === 5 && availabilityDays.length === 0) {
      setError('Please select at least one day you are available.');
      return false;
    }

    if (step === 6) {
      if (!form.identification_document_type || !form.identification_number.trim()) {
        setError('Please provide your identification details.');
        return false;
      }
      if (!proofOfAddress) {
        setError('Please upload your identification document.');
        return false;
      }
    }

    if (step === 7) {
      if (!form.emergency_contact_name.trim() || !form.emergency_contact_phone.trim()) {
        setError('Please provide your emergency contact details.');
        return false;
      }
    }

    return true;
  };

  const nextStep = () => {
    if (!validateStep(currentStep)) return;
    if (currentStep < STEPS.length) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const previousStep = () => {
    setError('');
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep(7)) return;

    setLoading(true);
    setError('');

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
        } else {
          const messages = [];
          for (const [key, value] of Object.entries(err)) {
            if (key !== 'non_field_errors') {
              const label = key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
              if (Array.isArray(value)) messages.push(`${label}: ${value.join(' ')}`);
              else if (typeof value === 'string') messages.push(`${label}: ${value}`);
            }
          }
          if (err.non_field_errors) {
            const nonField = Array.isArray(err.non_field_errors)
              ? err.non_field_errors.join(' ')
              : err.non_field_errors;
            messages.push(nonField);
          }
          errorMessage = messages.length > 0 ? messages.join(' | ') : 'Registration failed. Please check your details.';
        }
      } else if (typeof err === 'string') {
        errorMessage = err;
      }

      setError(errorMessage || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const selectedCategoryObject = categories.find(
    (category) => String(category.id) === String(selectedCategory)
  );

  const getFilePreview = (file) => (file ? URL.createObjectURL(file) : null);
  
  const progressPct = ((currentStep - 1) / (STEPS.length - 1)) * 100;

  return (
    <div className="am-register">
      <div className="am-register__glow am-register__glow--a" />
      <div className="am-register__glow am-register__glow--b" />

      <motion.div
        className="am-shell"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        {/* SIDEBAR */}
        <aside className="am-sidebar">
          <Link to="/" className="am-brand">
            <div className="am-brand__mark">
              <FaUserPlus />
            </div>
            <div className="am-brand__text">
              <strong>Artisan</strong>
              <span>Marketplace</span>
            </div>
          </Link>

          <div className="am-sidebar__intro">
            <h2>Become a verified artisan</h2>
            <p>Complete these seven steps to start receiving job requests in your area.</p>
          </div>

          <nav className="am-steps" aria-label="Registration steps">
            {STEPS.map((step) => {
              const completed = currentStep > step.number;
              const active = currentStep === step.number;
              const Icon = step.icon;

              return (
                <div
                  key={step.number}
                  className={[
                    'am-step',
                    active ? 'is-active' : '',
                    completed ? 'is-complete' : '',
                  ].join(' ')}
                >
                  <div className="am-step__marker">
                    {completed ? <FaCheck /> : <Icon />}
                  </div>
                  <div className="am-step__content">
                    <span className="am-step__label">{step.title}</span>
                    <span className="am-step__hint">{step.description}</span>
                  </div>
                </div>
              );
            })}
          </nav>

          <div className="am-sidebar__footer">
            <FaShieldAlt />
            <span>256-bit encrypted</span>
          </div>
        </aside>

        {/* MAIN */}
        <main className="am-main">
          <header className="am-main__header">
            <div className="am-main__heading">
              <span className="am-eyebrow">
                Step {currentStep} of {STEPS.length}
              </span>
              <h1>{STEPS[currentStep - 1].title}</h1>
              <p>{STEPS[currentStep - 1].description}</p>
            </div>

            <Link to="/login" className="am-signin-link">
              Sign in
            </Link>
          </header>

          {/* Mobile progress */}
          <div className="am-progress-mobile">
            <div className="am-progress-mobile__track">
              <motion.div
                className="am-progress-mobile__fill"
                initial={false}
                animate={{ width: `${progressPct}%` }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
              />
            </div>
            <div className="am-progress-mobile__meta">
              <span>{STEPS[currentStep - 1].title}</span>
              <span>
                {currentStep}/{STEPS.length}
              </span>
            </div>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                className="am-alert"
                role="alert"
                initial={{ opacity: 0, y: -8, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, y: -8, height: 0 }}
              >
                <FaExclamationCircle />
                <span>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} encType="multipart/form-data" noValidate>
            <div className="am-body">
              <AnimatePresence mode="wait">
                {/* STEP 1 */}
                {currentStep === 1 && (
                  <motion.section key="step-1" className="am-section" {...stepTransition}>
                    <div className="am-grid am-grid--2">
                      <Field label="First name" htmlFor={id('first_name')} icon={<FaUser />}>
                        <input
                          id={id('first_name')}
                          name="first_name"
                          value={form.first_name}
                          onChange={handleChange}
                          placeholder="Kofi"
                          autoComplete="given-name"
                        />
                      </Field>
                      <Field label="Last name" htmlFor={id('last_name')} icon={<FaUser />}>
                        <input
                          id={id('last_name')}
                          name="last_name"
                          value={form.last_name}
                          onChange={handleChange}
                          placeholder="Mensah"
                          autoComplete="family-name"
                        />
                      </Field>
                    </div>

                    <Field label="Phone number" htmlFor={id('phone_number')} icon={<FaPhone />}>
                      <input
                        id={id('phone_number')}
                        name="phone_number"
                        type="tel"
                        value={form.phone_number}
                        onChange={handleChange}
                        placeholder="+233 000 000 000"
                        autoComplete="tel"
                      />
                    </Field>

                    <Field label="Email address" htmlFor={id('email')} icon={<FaEnvelope />}>
                      <input
                        id={id('email')}
                        name="email"
                        type="email"
                        value={form.email}
                        onChange={handleChange}
                        placeholder="you@example.com"
                        autoComplete="email"
                      />
                    </Field>

                    <div className="am-grid am-grid--2">
                      <Field
                        label="Password"
                        htmlFor={id('password')}
                        icon={<FaLock />}
                        trailing={
                          <button
                            type="button"
                            className="am-input__action"
                            onClick={() => setShowPassword((v) => !v)}
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                          >
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                          </button>
                        }
                      >
                        <input
                          id={id('password')}
                          name="password"
                          type={showPassword ? 'text' : 'password'}
                          value={form.password}
                          onChange={handleChange}
                          placeholder="At least 8 characters"
                          autoComplete="new-password"
                        />
                      </Field>

                      <Field
                        label="Confirm password"
                        htmlFor={id('password2')}
                        icon={<FaLock />}
                        trailing={
                          <button
                            type="button"
                            className="am-input__action"
                            onClick={() => setShowPassword2((v) => !v)}
                            aria-label={showPassword2 ? 'Hide password' : 'Show password'}
                          >
                            {showPassword2 ? <FaEyeSlash /> : <FaEye />}
                          </button>
                        }
                      >
                        <input
                          id={id('password2')}
                          name="password2"
                          type={showPassword2 ? 'text' : 'password'}
                          value={form.password2}
                          onChange={handleChange}
                          placeholder="Repeat password"
                          autoComplete="new-password"
                        />
                      </Field>
                    </div>

                    <div className="am-hint">
                      <FaShieldAlt />
                      <span>Use at least 8 characters. Mix letters, numbers and symbols for a strong password.</span>
                    </div>
                  </motion.section>
                )}

                {/* STEP 2 */}
                {currentStep === 2 && (
                  <motion.section key="step-2" className="am-section" {...stepTransition}>
                    <div className="am-photo">
                      <div className="am-photo__preview">
                        {profilePicture ? (
                          <img src={getFilePreview(profilePicture)} alt="Profile preview" />
                        ) : (
                          <div className="am-photo__placeholder">
                            <FaCamera />
                          </div>
                        )}
                      </div>

                      <div className="am-photo__content">
                        <h3>Profile photo</h3>
                        <p>A clear face photo helps clients trust and recognise you.</p>

                        <label htmlFor={id('profile_picture')} className="am-btn am-btn--ghost am-btn--sm">
                          <FaCamera />
                          {profilePicture ? 'Change photo' : 'Choose photo'}
                        </label>

                        <input
                          id={id('profile_picture')}
                          name="profile_picture"
                          type="file"
                          accept=".jpg,.jpeg,.png,image/*"
                          onChange={handleFileChange}
                          hidden
                        />

                        {profilePicture && (
                          <span className="am-photo__filename">
                            <FaCheckCircle /> {profilePicture.name}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="am-grid am-grid--2">
                      <Field label="Date of birth" htmlFor={id('date_of_birth')} icon={<FaCalendarAlt />}>
                        <input
                          id={id('date_of_birth')}
                          name="date_of_birth"
                          type="date"
                          value={form.date_of_birth}
                          onChange={handleChange}
                        />
                      </Field>

                      <Field label="Gender" htmlFor={id('gender')}>
                        <select
                          id={id('gender')}
                          name="gender"
                          value={form.gender}
                          onChange={handleChange}
                        >
                          <option value="">Select gender</option>
                          {GENDER_OPTIONS.map((o) => (
                            <option key={o.value} value={o.value}>
                              {o.label}
                            </option>
                          ))}
                        </select>
                      </Field>
                    </div>
                  </motion.section>
                )}

                {/* STEP 3 */}
                {currentStep === 3 && (
                  <motion.section key="step-3" className="am-section" {...stepTransition}>
                    {categoriesLoading ? (
                      <Loading text="Loading categories…" />
                    ) : categories.length === 0 ? (
                      <Empty icon={<FaTags />} text="No categories are currently available." />
                    ) : (
                      <div className="am-cards am-cards--categories">
                        {categories.map((category) => {
                          const selected = String(selectedCategory) === String(category.id);
                          return (
                            <button
                              type="button"
                              key={category.id}
                              className={`am-card ${selected ? 'is-selected' : ''}`}
                              onClick={() => {
                                setSelectedCategory(String(category.id));
                                setSelectedSkills([]);
                                setError('');
                              }}
                            >
                              <span className="am-card__icon">
                                <FaBriefcase />
                              </span>
                              <span className="am-card__label">{category.name}</span>
                              <span className="am-card__check">
                                {selected && <FaCheck />}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {selectedCategoryObject && (
                      <motion.div
                        className="am-confirm"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                      >
                        <FaCheckCircle />
                        <span>
                          Selected: <strong>{selectedCategoryObject.name}</strong>
                        </span>
                      </motion.div>
                    )}
                  </motion.section>
                )}

                {/* STEP 4 */}
                {currentStep === 4 && (
                  <motion.section key="step-4" className="am-section" {...stepTransition}>
                    <div className="am-banner">
                      <FaBriefcase />
                      <div>
                        <small>YOUR PROFESSION</small>
                        <strong>{selectedCategoryObject?.name || 'Selected category'}</strong>
                      </div>
                    </div>

                    {subcategoriesLoading ? (
                      <Loading text="Loading skills…" />
                    ) : !selectedCategory ? (
                      <Empty icon={<FaTags />} text="Please go back and select a category first." />
                    ) : subcategories.length === 0 ? (
                      <Empty icon={<FaTags />} text="No skills are currently available for this category." />
                    ) : (
                      <div className="am-chips">
                        {subcategories.map((skill) => {
                          const selected = selectedSkills.includes(skill.id);
                          return (
                            <button
                              type="button"
                              key={skill.id}
                              className={`am-chip ${selected ? 'is-selected' : ''}`}
                              onClick={() => handleSkillToggle(skill.id)}
                            >
                              {selected && <FaCheck />}
                              {skill.name}
                            </button>
                          );
                        })}
                      </div>
                    )}

                    <div className="am-counter">
                      {selectedSkills.length} skill{selectedSkills.length === 1 ? '' : 's'} selected
                    </div>
                  </motion.section>
                )}

                {/* STEP 5 */}
                {currentStep === 5 && (
                  <motion.section key="step-5" className="am-section" {...stepTransition}>
                    <div className="am-days">
                      {DAYS_OF_WEEK.map((day) => {
                        const selected = availabilityDays.includes(day.value);
                        return (
                          <button
                            type="button"
                            key={day.value}
                            className={`am-day ${selected ? 'is-selected' : ''}`}
                            onClick={() => handleDayToggle(day.value)}
                          >
                            <span className="am-day__short">{day.short}</span>
                            <span className="am-day__full">{day.label}</span>
                            <span className="am-day__check">{selected && <FaCheck />}</span>
                          </button>
                        );
                      })}
                    </div>

                    <div className="am-summary-inline">
                      <FaClock />
                      <div>
                        <strong>
                          {availabilityDays.length} {availabilityDays.length === 1 ? 'day' : 'days'} selected
                        </strong>
                        <span>You can update this later from your profile.</span>
                      </div>
                    </div>

                    <Field label="Timezone" htmlFor={id('timezone')} icon={<FaGlobe />}>
                      <select
                        id={id('timezone')}
                        name="timezone"
                        value={form.timezone}
                        onChange={handleChange}
                      >
                        {TIMEZONES.map((tz) => (
                          <option key={tz} value={tz}>
                            {tz}
                          </option>
                        ))}
                      </select>
                    </Field>
                  </motion.section>
                )}

                {/* STEP 6 */}
                {currentStep === 6 && (
                  <motion.section key="step-6" className="am-section" {...stepTransition}>
                    <div className="am-banner am-banner--info">
                      <div className="am-banner__icon">
                        <FaShieldAlt />
                      </div>
                      <div>
                        <strong>Your information is protected</strong>
                        <span>Verification data is used strictly to confirm your identity.</span>
                      </div>
                    </div>

                    <Field label="Identification document" htmlFor={id('identification_document_type')}>
                      <select
                        id={id('identification_document_type')}
                        name="identification_document_type"
                        value={form.identification_document_type}
                        onChange={handleChange}
                      >
                        <option value="">Select document type</option>
                        {DOCUMENT_TYPES.map((d) => (
                          <option key={d.value} value={d.value}>
                            {d.label}
                          </option>
                        ))}
                      </select>
                    </Field>

                    <Field label="Identification number" htmlFor={id('identification_number')} icon={<FaIdCard />}>
                      <input
                        id={id('identification_number')}
                        name="identification_number"
                        value={form.identification_number}
                        onChange={handleChange}
                        placeholder="Enter identification number"
                      />
                    </Field>

                    <div className="am-drop">
                      <input
                        id={id('proof_of_address')}
                        name="proof_of_address"
                        type="file"
                        accept=".pdf,application/pdf,.jpg,.jpeg,.png,image/*"
                        onChange={handleFileChange}
                        hidden
                      />
                      <label htmlFor={id('proof_of_address')} className="am-drop__label">
                        <div className={`am-drop__icon ${proofOfAddress ? 'is-done' : ''}`}>
                          {proofOfAddress ? <FaCheckCircle /> : <FaCloudUploadAlt />}
                        </div>
                        <strong>
                          {proofOfAddress ? 'Document selected' : 'Upload your ID document'}
                        </strong>
                        <span>{proofOfAddress ? proofOfAddress.name : 'PDF, JPG, JPEG or PNG · Max 5MB'}</span>
                        <em>{proofOfAddress ? 'Click to change document' : 'Click to choose a file'}</em>
                      </label>
                    </div>
                  </motion.section>
                )}

                {/* STEP 7 */}
                {currentStep === 7 && (
                  <motion.section key="step-7" className="am-section" {...stepTransition}>
                    <div className="am-banner am-banner--warn">
                      <div className="am-banner__icon">
                        <FaPhoneAlt />
                      </div>
                      <div>
                        <strong>Emergency contact</strong>
                        <span>Someone we can reach in case of an emergency.</span>
                      </div>
                    </div>

                    <Field label="Contact name" htmlFor={id('emergency_contact_name')} icon={<FaUser />}>
                      <input
                        id={id('emergency_contact_name')}
                        name="emergency_contact_name"
                        value={form.emergency_contact_name}
                        onChange={handleChange}
                        placeholder="Full name"
                      />
                    </Field>

                    <Field label="Contact phone" htmlFor={id('emergency_contact_phone')} icon={<FaPhoneAlt />}>
                      <input
                        id={id('emergency_contact_phone')}
                        name="emergency_contact_phone"
                        type="tel"
                        value={form.emergency_contact_phone}
                        onChange={handleChange}
                        placeholder="+233 000 000 000"
                      />
                    </Field>

                    <div className="am-review">
                      <div className="am-review__head">
                        <FaCheckCircle />
                        <div>
                          <h3>Almost done</h3>
                          <p>Review your details and create your account.</p>
                        </div>
                      </div>
                      <dl className="am-review__list">
                        <div>
                          <dt>Name</dt>
                          <dd>{form.first_name} {form.last_name}</dd>
                        </div>
                        <div>
                          <dt>Email</dt>
                          <dd>{form.email}</dd>
                        </div>
                        <div>
                          <dt>Profession</dt>
                          <dd>{selectedCategoryObject?.name || 'Not selected'}</dd>
                        </div>
                        <div>
                          <dt>Skills</dt>
                          <dd>{selectedSkills.length} selected</dd>
                        </div>
                        <div>
                          <dt>Availability</dt>
                          <dd>{availabilityDays.length} days</dd>
                        </div>
                      </dl>
                    </div>
                  </motion.section>
                )}
              </AnimatePresence>
            </div>

            {/* NAV */}
            <div className="am-nav">
              {currentStep > 1 ? (
                <button type="button" className="am-btn am-btn--ghost" onClick={previousStep} disabled={loading}>
                  <FaArrowLeft />
                  Back
                </button>
              ) : (
                <Link to="/login" className="am-btn am-btn--ghost">
                  <FaArrowLeft />
                  Sign in
                </Link>
              )}

              {currentStep < STEPS.length ? (
                <motion.button
                  type="button"
                  className="am-btn am-btn--primary"
                  onClick={nextStep}
                  whileTap={{ scale: 0.98 }}
                >
                  Continue
                  <FaArrowRight />
                </motion.button>
              ) : (
                <motion.button
                  type="submit"
                  className="am-btn am-btn--primary am-btn--cta"
                  disabled={loading}
                  whileTap={{ scale: 0.98 }}
                >
                  {loading ? (
                    <>
                      <span className="am-spinner am-spinner--sm" />
                      Creating account…
                    </>
                  ) : (
                    <>
                      Create account
                      <FaCheck />
                    </>
                  )}
                </motion.button>
              )}
            </div>
          </form>

          <div className="am-footnote">
            <FaShieldAlt />
            <span>Your information is securely handled and used only for registration and verification.</span>
          </div>
        </main>
      </motion.div>

      <footer className="am-page-footer">
        <span>© {new Date().getFullYear()} Artisan Marketplace</span>
        <span>Professional services made simple.</span>
      </footer>
    </div>
  );
}

/* ---------- Small reusable pieces ---------- */

function Field({ label, htmlFor, icon, trailing, children }) {
  return (
    <div className="am-field">
      <label htmlFor={htmlFor}>{label}</label>
      <div className={`am-input ${icon ? 'has-icon' : ''} ${trailing ? 'has-trailing' : ''}`}>
        {icon && <span className="am-input__icon">{icon}</span>}
        {children}
        {trailing}
      </div>
    </div>
  );
}

function Loading({ text }) {
  return (
    <div className="am-state">
      <span className="am-spinner" />
      <span>{text}</span>
    </div>
  );
}

function Empty({ icon, text }) {
  return (
    <div className="am-state am-state--empty">
      {icon}
      <p>{text}</p>
    </div>
  );
}