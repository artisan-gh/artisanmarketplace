
// src/components/provider/TestRunner.jsx
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { FaClock, FaCircleNotch, FaCheckCircle } from 'react-icons/fa';
import api from '../../api/client';
import './TestCentre.css';

const AUTOSAVE_KEY = (slug) => `ayuda.testcentre.draft.${slug}`;

export const TestRunner = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [index, setIndex] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirming, setConfirming] = useState(false);
  const tickRef = useRef(null);

  // Start (or resume) an attempt on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { data } = await api.post(`/provider/assessments/${slug}/start/`);
        if (cancelled) return;
        setAttempt(data);

        const cached = localStorage.getItem(AUTOSAVE_KEY(slug));
        if (cached) {
          try { setAnswers(JSON.parse(cached)); } catch {}
        }

        const expires = new Date(data.expires_at).getTime();
        const tick = () => {
          const left = Math.max(0, Math.floor((expires - Date.now()) / 1000));
          setSecondsLeft(left);
          if (left <= 0) {
            clearInterval(tickRef.current);
            submit(true);
          }
        };
        tick();
        tickRef.current = setInterval(tick, 1000);
      } catch (err) {
        if (!cancelled) {
          setError(err?.response?.data?.detail || 'Could not start the test.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
      if (tickRef.current) clearInterval(tickRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  const questions = attempt?.questions || [];
  const question = questions[index];
  const total = questions.length;

  // Autosave
  useEffect(() => {
    if (!slug) return;
    try { localStorage.setItem(AUTOSAVE_KEY(slug), JSON.stringify(answers)); } catch {}
  }, [answers, slug]);

  const progressPct = useMemo(
    () => (total ? ((index + 1) / total) * 100 : 0),
    [index, total]
  );

  const setAnswer = (qid, value) => {
    setAnswers((prev) => ({ ...prev, [qid]: value }));
  };

  const toggleMulti = (qid, optionId) => {
    setAnswers((prev) => {
      const current = Array.isArray(prev[qid]) ? prev[qid] : [];
      return {
        ...prev,
        [qid]: current.includes(optionId)
          ? current.filter((x) => x !== optionId)
          : [...current, optionId],
      };
    });
  };

  const submit = async (auto = false) => {
    if (!attempt) return;
    if (!auto && !window.confirm('Submit your answers now?')) return;
    try {
      const payload = {
        answers: Object.entries(answers).map(([question_id, answer]) => ({
          question_id, answer,
        })),
      };
      const { data } = await api.post(`/provider/attempts/${attempt.attempt_id}/submit/`, payload);
      localStorage.removeItem(AUTOSAVE_KEY(slug));
      navigate(`/provider/test-centre/result/${data.attempt_id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not submit the test.');
    }
  };

  const renderInput = () => {
    if (!question) return null;
    const value = answers[question.id];

    if (question.type === 'likert') {
      return (
        <div className="tr-likert">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              className={`tr-likert__opt ${value === n ? 'is-selected' : ''}`}
              onClick={() => setAnswer(question.id, n)}
            >
              {n}
            </button>
          ))}
        </div>
      );
    }

    if (question.type === 'boolean') {
      return (
        <div className="tr-options">
          {['true', 'false'].map((opt) => (
            <button
              key={opt}
              type="button"
              className={`tr-option ${String(value) === opt ? 'is-selected' : ''}`}
              onClick={() => setAnswer(question.id, opt === 'true')}
            >
              {opt === 'true' ? 'True' : 'False'}
            </button>
          ))}
        </div>
      );
    }

    if (question.type === 'multiple_choice') {
      const current = Array.isArray(value) ? value : [];
      return (
        <div className="tr-options">
          {question.options.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`tr-option ${current.includes(opt.id) ? 'is-selected' : ''}`}
              onClick={() => toggleMulti(question.id, opt.id)}
            >
              {opt.text}
            </button>
          ))}
        </div>
      );
    }

    // single_choice default
    return (
      <div className="tr-options">
        {question.options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            className={`tr-option ${value === opt.id ? 'is-selected' : ''}`}
            onClick={() => setAnswer(question.id, opt.id)}
          >
            {opt.text}
          </button>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="tr-page">
        <div className="tc-loading"><FaCircleNotch className="tc-spin" /> Preparing your test…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tr-page">
        <div className="tc-error">{error}</div>
      </div>
    );
  }

  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const ss = String(secondsLeft % 60).padStart(2, '0');
  const timerTone = secondsLeft <= 60 ? 'danger' : secondsLeft <= 300 ? 'warning' : '';

  return (
    <div className="tr-page">
      <header className="tr-header">
        <div className="tr-header__left">
          <span className="tr-dot" />
          <div>
            <span className="tr-header__label">In progress</span>
            <h1>{attempt?.assessment_title}</h1>
          </div>
        </div>
        <div className={`tr-timer ${timerTone}`}>
          <FaClock />
          <span>{mm}:{ss}</span>
        </div>
      </header>

      <div className="tr-progress">
        <div className="tr-progress__bar">
          <div className="tr-progress__fill" style={{ width: `${progressPct}%` }} />
        </div>
        <span className="tr-progress__text">
          Question {index + 1} of {total}
        </span>
      </div>

      <main className="tr-body">
        {question && (
          <div className="tr-question">
            <p className="tr-question__text">{question.text}</p>
            {renderInput()}
          </div>
        )}

        <div className="tr-nav">
          <button
            type="button"
            className="tr-btn tr-btn--ghost"
            disabled={index === 0}
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
          >
            Previous
          </button>

          {index < total - 1 ? (
            <button
              type="button"
              className="tr-btn tr-btn--primary"
              onClick={() => setIndex((i) => Math.min(total - 1, i + 1))}
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              className="tr-btn tr-btn--primary"
              onClick={() => setConfirming(true)}
            >
              <FaCheckCircle /> Submit
            </button>
          )}
        </div>
      </main>

      {confirming && (
        <div className="tr-modal" role="dialog" aria-modal="true">
          <div className="tr-modal__card">
            <h3>Submit your answers?</h3>
            <p>You won&apos;t be able to change them after submitting.</p>
            <div className="tr-modal__actions">
              <button
                type="button"
                className="tr-btn tr-btn--ghost"
                onClick={() => setConfirming(false)}
              >
                Keep going
              </button>
              <button
                type="button"
                className="tr-btn tr-btn--primary"
                onClick={() => submit(false)}
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestRunner;
