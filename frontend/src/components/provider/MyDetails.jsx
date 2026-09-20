// src/components/provider/MyDetails.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaThLarge, FaRegEdit, FaRegClipboard, FaBookOpen, FaLock,
  FaLock as FaLockSolid, FaSignOutAlt, FaCamera, FaCheck,
  FaInfoCircle, FaSave, FaUser, FaUserFriends, FaPhone,
  FaBriefcase, FaGraduationCap, FaUniversity, FaMapMarkerAlt,
  FaIdCard, FaVenusMars, FaBirthdayCake, FaFlag, FaHeart,
  FaFileInvoiceDollar, FaBell,
} from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';
import './MyDetails.css';

/* ─── Flat nav ─────────────────────────────────────────────── */
const NAV_ITEMS = [
  { to: '/artisan/dashboard', label: 'Dashboard', icon: FaThLarge, end: true },
  { to: '/artisan/profile', label: 'My details', icon: FaRegEdit, end: true },
  { to: '/provider/test-centre', label: 'Test centre', icon: FaRegClipboard },
  { to: '/provider/training-centre', label: 'Training centre', icon: FaBookOpen, locked: true },
];

/* ─── 8 wizard steps ───────────────────────────────────────── */
const STEPS = [
  { id: 1, key: 'personal',       label: 'Personal',       icon: FaUser },
  { id: 2, key: 'next_of_kin',    label: 'Next of Kin',    icon: FaUserFriends },
  { id: 3, key: 'contact',        label: 'Contact',        icon: FaPhone },
  { id: 4, key: 'professional',   label: 'Professional',   icon: FaBriefcase },
  { id: 5, key: 'education',      label: 'Education',      icon: FaGraduationCap },
  { id: 6, key: 'account',        label: 'Account',        icon: FaUniversity },
  { id: 7, key: 'address',        label: 'Address',        icon: FaMapMarkerAlt },
  { id: 8, key: 'identification', label: 'Identification', icon: FaIdCard },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};
const itemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

/* ─── Fields per step ──────────────────────────────────────── */
const PERSONAL_FIELDS = [
  { label: 'Title',            value: 'Mr',             icon: FaUser },
  { label: 'First name',       value: 'Moro',           icon: FaUser },
  { label: 'Last name',        value: 'Zakari',         icon: FaUser },
  { label: 'Middle name(s)',   value: '',               icon: FaUser },
  { label: 'Date of birth',    value: '05 / 07 / 1984', icon: FaBirthdayCake },
  { label: 'Gender',           value: 'Male',           icon: FaVenusMars },
  { label: 'Marital status',   value: '',               icon: FaHeart },
  { label: 'Nationality',      value: 'Ghanaian',       icon: FaFlag },
  { label: 'Taxpayer ID (TIN)', value: '',              icon: FaFileInvoiceDollar },
  { label: 'GRA Number',       value: '',               icon: FaFileInvoiceDollar },
];

export const MyDetails = () => {
  const { logout, user } = useAuth();
  const [activeStep, setActiveStep] = useState(1);
  const [profileLocked] = useState(true);

  const fullName = user?.full_name || user?.name || 'Artisan';
  const firstName = fullName.split(' ')[0] || 'Artisan';
  const avatarUrl = user?.profile_picture || null;

  const active = STEPS.find((s) => s.id === activeStep);
  const totalSteps = STEPS.length;
  const progressPct = (activeStep / totalSteps) * 100;

  return (
    <div className="md-layout">
      {/* ─── Sidebar ─────────────────────────────────────── */}
      <aside className="ay-sidebar">
        <div className="ay-sidebar__brand">
          <div className="ay-sidebar__logo">
            <span className="ay-sidebar__logo-mark" />
            <span className="ay-sidebar__logo-text">tumakonect</span>
          </div>
          <p className="ay-sidebar__brand-sub">…here to help</p>
          <p className="ay-sidebar__brand-title">Service provider portal</p>
        </div>

        <nav className="ay-nav" aria-label="Primary">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end, locked }) => (
            <Link
              key={to}
              to={locked ? '#' : to}
              end={end}
              className={({ isActive }) =>
                `ay-nav__item ${isActive && !locked ? 'is-active' : ''} ${locked ? 'is-locked' : ''}`
              }
              onClick={(e) => locked && e.preventDefault()}
            >
              <span className="ay-nav__icon"><Icon /></span>
              <span className="ay-nav__label">{label}</span>
              {locked && <FaLock className="ay-nav__lock" />}
            </Link>
          ))}
        </nav>

        <div className="ay-sidebar__footer">
          <div className="ay-sidebar__avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt={fullName} />
            ) : (
              <span>{firstName.charAt(0).toUpperCase()}</span>
            )}
            <span className="ay-sidebar__avatar-dot" />
          </div>
          <div className="ay-sidebar__profile">
            <strong>{fullName}</strong>
            <span>Artisan</span>
          </div>
          <button
            type="button"
            onClick={logout}
            className="ay-sidebar__chev"
            aria-label="Sign out"
          >
            <FaSignOutAlt />
          </button>
        </div>
      </aside>

      {/* ─── Main ────────────────────────────────────────── */}
      <main className="md-main">
        <motion.div
          className="md-inner"
          variants={containerVariants}
          initial="hidden"
          animate="show"
        >
          {/* Hero */}
          <motion.header className="md-hero" variants={itemVariants}>
            <div className="md-hero__left">
              <div className="md-hero__icon"><FaRegEdit /></div>
              <div>
                <span className="md-eyebrow">Profile</span>
                <h1>My details</h1>
                <p>Review and manage the information on your Ayuda profile.</p>
              </div>
            </div>

            <div className="md-hero__progress">
              <div className="md-hero__progress-head">
                <span>Profile completion</span>
                <strong>{Math.round(progressPct)}%</strong>
              </div>
              <div className="md-hero__progress-track">
                <motion.div
                  className="md-hero__progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPct}%` }}
                  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                />
              </div>
            </div>
          </motion.header>

          {/* Card */}
          <motion.section className="md-card" variants={itemVariants}>
            <div className="md-card__grid">
              {/* Step rail */}
              <aside className="md-rail">
                <div className="md-rail__line" aria-hidden="true" />
                {STEPS.map((step) => {
                  const isActive = step.id === activeStep;
                  const isComplete = step.id < activeStep;
                  const StepIcon = step.icon;
                  return (
                    <button
                      key={step.id}
                      type="button"
                      className={`md-rail__item ${isActive ? 'is-active' : ''} ${isComplete ? 'is-complete' : ''}`}
                      onClick={() => setActiveStep(step.id)}
                    >
                      <span className="md-rail__num">
                        {isComplete ? <FaCheck /> : <StepIcon />}
                      </span>
                      <span className="md-rail__text">
                        <span className="md-rail__index">Step {step.id}</span>
                        <span className="md-rail__label">{step.label}</span>
                      </span>
                    </button>
                  );
                })}
              </aside>

              {/* Content */}
              <div className="md-content">
                <header className="md-content__head">
                  <div className="md-content__head-left">
                    <span className="md-content__step">
                      Step {activeStep} of {totalSteps}
                    </span>
                    <h2>{active.label} Information</h2>
                  </div>
                  <span className="md-content__icon">
                    <active.icon />
                  </span>
                </header>

                {/* Locked banner */}
                {profileLocked && (
                  <motion.div
                    className="md-locked"
                    initial={{ opacity: 0, y: -6 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <span className="md-locked__icon">
                      <FaLockSolid />
                    </span>
                    <div className="md-locked__body">
                      <strong>Profile Locked</strong>
                      <p>
                        Profile details cannot be changed after verification.
                        Contact <a href="mailto:support@ayuda.app">Ayuda Support</a> if
                        you need your details updated.
                      </p>
                    </div>
                  </motion.div>
                )}

                {/* Step body */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={active.key}
                    className="md-body"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.25 }}
                  >
                    {active.key === 'personal' && (
                      <PersonalStep fields={PERSONAL_FIELDS} />
                    )}
                    {active.key === 'next_of_kin' && <PlaceholderStep title="Next of Kin" />}
                    {active.key === 'contact' && <PlaceholderStep title="Contact" />}
                    {active.key === 'professional' && <PlaceholderStep title="Professional" />}
                    {active.key === 'education' && <PlaceholderStep title="Education" />}
                    {active.key === 'account' && <PlaceholderStep title="Account" />}
                    {active.key === 'address' && <PlaceholderStep title="Address" />}
                    {active.key === 'identification' && <PlaceholderStep title="Identification" />}
                  </motion.div>
                </AnimatePresence>

                {/* Actions */}
                <footer className="md-actions">
                  <div className="md-actions__left">
                    {activeStep > 1 && (
                      <button
                        type="button"
                        className="md-btn md-btn--ghost"
                        onClick={() => setActiveStep((s) => Math.max(1, s - 1))}
                      >
                        Previous
                      </button>
                    )}
                  </div>
                  <div className="md-actions__right">
                    {activeStep < totalSteps && (
                      <button
                        type="button"
                        className="md-btn md-btn--ghost"
                        onClick={() => setActiveStep((s) => Math.min(totalSteps, s + 1))}
                      >
                        Next
                      </button>
                    )}
                    <button
                      type="button"
                      className="md-btn md-btn--primary"
                      disabled={profileLocked}
                    >
                      <FaSave /> Save changes
                    </button>
                  </div>
                </footer>
              </div>
            </div>
          </motion.section>
        </motion.div>
      </main>
    </div>
  );
};

/* ─── Personal step ─────────────────────────────────────────── */
const PersonalStep = ({ fields }) => (
  <div className="md-form">
    {/* Profile photo */}
    <div className="md-photo">
      <div className="md-photo__preview">
        <div className="md-photo__placeholder">
          <FaCamera />
        </div>
      </div>
      <div className="md-photo__content">
        <h3>Profile photo</h3>
        <p>A clear face photo helps clients recognise and trust you.</p>
        <button type="button" className="md-btn md-btn--ghost md-btn--sm" disabled>
          <FaCamera /> Change photo
        </button>
      </div>
    </div>

    {/* Fields */}
    <div className="md-field-grid">
      {fields.map((f) => (
        <Field key={f.label} {...f} />
      ))}
    </div>
  </div>
);

const Field = ({ label, value, icon: Icon }) => (
  <div className="md-field">
    <span className="md-field__icon">
      {Icon ? <Icon /> : <FaInfoCircle />}
    </span>
    <div className="md-field__body">
      <span className="md-field__label">{label}</span>
      <span className={`md-field__value ${value ? '' : 'is-empty'}`}>
        {value || 'Not provided'}
      </span>
    </div>
  </div>
);

const PlaceholderStep = ({ title }) => (
  <div className="md-placeholder">
    <div className="md-placeholder__icon">
      <FaBell />
    </div>
    <div>
      <strong>{title}</strong>
      <p>This section is coming soon. You&apos;ll be able to complete it here.</p>
    </div>
  </div>
);

export default MyDetails;