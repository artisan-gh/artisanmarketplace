// src/components/provider/TestCentre.jsx
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FaThLarge, FaRegEdit, FaRegClipboard, FaBookOpen, FaLock,
  FaBrain, FaBolt, FaClock,
  FaListOl, FaRedo, FaHeadset, FaCircleNotch, FaSignOutAlt,
} from 'react-icons/fa';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import './TestCentre.css';

const NAV_ITEMS = [
  { to: '/artisan/dashboard', label: 'Dashboard', icon: FaThLarge, end: true },
  { to: '/artisan/profile', label: 'My details', icon: FaRegEdit },
  { to: '/provider/test-centre', label: 'Test centre', icon: FaRegClipboard },
  { to: '/provider/training-centre', label: 'Training centre', icon: FaBookOpen, locked: true },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};
const itemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

const STATUS_LABEL = {
  PASSED: 'PASSED',
  READY: 'READY',
  LOCKED: 'LOCKED',
  IN_PROGRESS: 'IN PROGRESS',
  EXHAUSTED: 'NO ATTEMPTS',
};

const statusTone = (s) => {
  if (s === 'PASSED') return 'success';
  if (s === 'READY' || s === 'IN_PROGRESS') return 'ready';
  return 'locked';
};

/* ─── Fallback demo card (shown if the API returns nothing) ─── */
const DEMO_SKILL_TESTS = [
  {
    id: 'demo-electrical',
    slug: 'electrical-services',
    title: 'Electrical Services Skill Test',
    status: 'READY',
    description: 'Technical assessment for Electrical Services proficiency.',
    questions_count: 15,
    duration_minutes: 30,
    attempts_used: 0,
    max_attempts: 2,
    can_start: false,
    is_locked: false,
  },
];

const AssessmentCard = ({ assessment, onStart }) => {
  const tone = statusTone(assessment.status);
  const actionLabel =
    assessment.status === 'PASSED' ? 'VIEW RESULT'
    : assessment.status === 'IN_PROGRESS' ? 'RESUME'
    : assessment.status === 'LOCKED' ? 'LOCKED'
    : assessment.status === 'EXHAUSTED' ? 'CONTACT SUPPORT'
    : 'START';

  const disabled =
    !assessment.can_start &&
    assessment.status !== 'IN_PROGRESS' &&
    assessment.status !== 'PASSED';

  return (
    <motion.article className="tc-card" variants={itemVariants}>
      <div className="tc-card__head">
        <h3 className="tc-card__title">{assessment.title}</h3>
        <span className={`tc-status tc-status--${tone}`}>
          {STATUS_LABEL[assessment.status] || assessment.status}
        </span>
      </div>

      <p className="tc-card__desc">{assessment.description}</p>

      <div className="tc-card__meta">
        <div className="tc-meta">
          <span className="tc-meta__label"><FaListOl /> Questions</span>
          <span className="tc-meta__value">{assessment.questions_count}</span>
        </div>
        <div className="tc-meta">
          <span className="tc-meta__label"><FaClock /> Time</span>
          <span className="tc-meta__value">{assessment.duration_minutes} min</span>
        </div>
        <div className="tc-meta">
          <span className="tc-meta__label"><FaRedo /> Attempts</span>
          <span className="tc-meta__value">
            {assessment.attempts_used} / {assessment.max_attempts}
          </span>
        </div>
      </div>

      <button
        type="button"
        className={`tc-cta tc-cta--${tone}`}
        onClick={() => onStart(assessment)}
        disabled={disabled}
      >
        {actionLabel}
      </button>
    </motion.article>
  );
};

export const TestCentre = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const fullName = user?.full_name || user?.name || 'Artisan';
  const firstName = fullName.split(' ')[0] || 'Artisan';
  const avatarUrl = user?.profile_picture || null;

  const { data, isLoading, error } = useQuery({
    queryKey: ['testCentre'],
    queryFn: () => api.get('/provider/assessments/').then((r) => r.data),
  });

  const handleStart = async (assessment) => {
    if (!assessment.can_start) {
      // Locked or exhausted — don't try to start
      if (assessment.is_locked) {
        window.alert(
          'Pass the psychometric test first to unlock this skill test.'
        );
      } else if (assessment.status === 'EXHAUSTED') {
        window.alert(
          'No attempts remaining. Contact support to reset your attempts.'
        );
      }
      return;
    }

    if (assessment.status === 'PASSED' && assessment.last_attempt_id) {
      navigate(`/provider/test-centre/result/${assessment.last_attempt_id}`);
      return;
    }
    if (assessment.status === 'IN_PROGRESS' && assessment.active_attempt_id) {
      navigate(`/provider/test-centre/${assessment.slug}/run`);
      return;
    }
    try {
      await api.post(`/provider/assessments/${assessment.slug}/start/`);
      navigate(`/provider/test-centre/${assessment.slug}/run`);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Could not start the test.';
      window.alert(msg);
    }
  };

  const psychometric = data?.psychometric || [];

  // Use real skill tests if the API returned any; otherwise show the demo card
  const apiSkillTests = data?.skill_tests || [];
  const skillTests = apiSkillTests.length > 0 ? apiSkillTests : DEMO_SKILL_TESTS;

  const anySkillLocked = skillTests.some((s) => s.is_locked);

  return (
    <div className="tc-layout">
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

      <main className="tc-main">
        <motion.div
          className="tc-inner"
          variants={containerVariants}
          initial="hidden"
          animate="show"
        >
          <motion.header className="tc-hero" variants={itemVariants}>
            <div className="tc-hero__icon"><FaBrain /></div>
            <h1>tumakonect Test Centre</h1>
            <p>
              Prove your proficiency in your chosen fields. Complete psychometric
              and skill tests and get assigned high profile jobs.
            </p>
          </motion.header>

          {/* ─── Mandatory Assessments ──────────────────────── */}
          <motion.section className="tc-section" variants={itemVariants}>
            <div className="tc-section__head">
              <span className="tc-section__icon"><FaRegClipboard /></span>
              <h2>Mandatory Assessments</h2>
            </div>

            {isLoading ? (
              <div className="tc-loading">
                <FaCircleNotch className="tc-spin" /> Loading…
              </div>
            ) : error ? (
              <div className="tc-error">Failed to load assessments.</div>
            ) : psychometric.length === 0 ? (
              <div className="tc-empty">No mandatory assessments yet.</div>
            ) : (
              <div className="tc-skill-grid">
                {psychometric.map((a) => (
                  <AssessmentCard key={a.id} assessment={a} onStart={handleStart} />
                ))}
              </div>
            )}
          </motion.section>

          {/* ─── Skill Tests ────────────────────────────────── */}
          <motion.section className="tc-section" variants={itemVariants}>
            <div className="tc-section__head">
              <span className="tc-section__icon tc-section__icon--bolt">
                <FaBolt />
              </span>
              <div>
                <h2>Skill Tests</h2>
                {anySkillLocked && (
                  <p className="tc-section__sub">
                    Pass the psychometric test to unlock skill tests. You will not
                    be assigned jobs with skills you haven&apos;t passed.
                  </p>
                )}
              </div>
            </div>

            {/* Lock notice above the cards (doesn't replace them) */}
            {anySkillLocked && (
              <div className="tc-locked">
                <span className="tc-locked__icon"><FaLock /></span>
                <div>
                  <strong>Pass the psychometric test to unlock skill tests</strong>
                  <p>You will not be assigned jobs with skills you haven&apos;t passed.</p>
                </div>
              </div>
            )}

            {/* Always render the skill test cards */}
            {!isLoading && !error && skillTests.length > 0 && (
              <div className="tc-skill-grid">
                {skillTests.map((a) => (
                  <AssessmentCard key={a.id} assessment={a} onStart={handleStart} />
                ))}
              </div>
            )}
          </motion.section>

          {/* ─── Help Center ────────────────────────────────── */}
          <motion.section className="tc-help" variants={itemVariants}>
            <div className="tc-help__left">
              <span className="tc-help__icon"><FaHeadset /></span>
              <div>
                <strong>Help Center</strong>
                <p>
                  Need assistance or reached your maximum attempts? Contact
                  support for a reset and get back on track.
                </p>
              </div>
            </div>
            <a href="mailto:support@tumakonect.app" className="tc-help__btn">
              Contact Support
            </a>
          </motion.section>
        </motion.div>
      </main>
    </div>
  );
};

export default TestCentre;
