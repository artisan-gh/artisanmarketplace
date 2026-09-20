
// src/components/provider/TestResult.jsx
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FaCheckCircle, FaTimesCircle, FaCircleNotch } from 'react-icons/fa';
import api from '../../api/client';
import './TestCentre.css';

export const TestResult = () => {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get(`/provider/attempts/${id}/result/`)
      .then((r) => setResult(r.data))
      .catch((err) =>
        setError(err?.response?.data?.detail || 'Could not load the result.')
      );
  }, [id]);

  if (error) {
    return (
      <div className="tr-page">
        <div className="tc-error">{error}</div>
        <Link to="/provider/test-centre" className="tc-back">Back to Test Centre</Link>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="tr-page">
        <div className="tc-loading">
          <FaCircleNotch className="tc-spin" /> Loading your result…
        </div>
      </div>
    );
  }

  const passed = result.passed;
  const tone = passed ? 'success' : 'fail';

  return (
    <div className="tr-page tr-page--result">
      <div className={`tr-result tr-result--${tone}`}>
        <div className="tr-result__icon">
          {passed ? <FaCheckCircle /> : <FaTimesCircle />}
        </div>
        <h1>{passed ? 'You passed!' : 'Not quite there yet'}</h1>
        <p className="tr-result__sub">
          {result.assessment_title}
        </p>

        <div className="tr-result__score">
          <span className="tr-result__score-value">{result.score}%</span>
          <span className="tr-result__score-label">
            Pass threshold: {result.pass_threshold}%
          </span>
        </div>

        <div className="tr-result__stats">
          <div>
            <span className="tr-result__stat-label">Duration</span>
            <span className="tr-result__stat-value">
              {Math.round(result.duration_seconds / 60)} min
            </span>
          </div>
          <div>
            <span className="tr-result__stat-label">Kind</span>
            <span className="tr-result__stat-value">{result.kind}</span>
          </div>
          {result.timed_out && (
            <div>
              <span className="tr-result__stat-label">Status</span>
              <span className="tr-result__stat-value">Timed out</span>
            </div>
          )}
        </div>

        {result.skill_unlocked && (
          <div className="tr-result__unlock">
            <FaCheckCircle />
            <div>
              <strong>Skill unlocked: {result.skill_unlocked.name}</strong>
              <span>You can now be assigned jobs in this category.</span>
            </div>
          </div>
        )}

        <div className="tr-result__actions">
          <Link to="/provider/test-centre" className="tr-btn tr-btn--ghost">
            Back to Test Centre
          </Link>
          {!passed && (
            <Link
              to={`/provider/test-centre/${result.assessment_slug}/run`}
              className="tr-btn tr-btn--primary"
            >
              Try again
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestResult;
