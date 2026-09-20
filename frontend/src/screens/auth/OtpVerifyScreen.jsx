
import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { FaCircleNotch, FaArrowLeft } from 'react-icons/fa';
import { verifyOtp, resendOtp } from '../../api/authClient';
import { useAuth } from '../../context/AuthContext';
import './auth.css';

export default function OtpVerifyScreen() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithToken } = useAuth() || {};
  const phone = location.state?.phone || '';
  const debugCode = location.state?.debugCode || '';

  const [code, setCode] = useState(debugCode || '');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [seconds, setSeconds] = useState(60);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => { if (!phone) navigate('/login-phone', { replace: true }); }, [phone, navigate]);
  useEffect(() => { inputRef.current?.focus(); }, []);
  useEffect(() => {
    if (seconds <= 0) return;
    const t = setInterval(() => setSeconds(s => s - 1), 1000);
    return () => clearInterval(t);
  }, [seconds]);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (!/^[0-9]{6}$/.test(code)) { setError('Enter the 6-digit code.'); return; }
    setLoading(true);
    try {
      const res = await verifyOtp(phone, code);
      if (loginWithToken) await loginWithToken(res);
      else {
        localStorage.setItem('accessToken', res.access);
        localStorage.setItem('refreshToken', res.refresh);
        localStorage.setItem('user_type', res.user.user_type);
      }
      navigate('/client/invoices', { replace: true });
    } catch (e) {
      setError(e?.response?.data?.detail || 'Verification failed.');
    } finally { setLoading(false); }
  };

  const resend = async () => {
    setResending(true); setError('');
    try {
      const res = await resendOtp(phone);
      setSeconds(60);
      if (res?.debug_code) setCode(res.debug_code);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Could not resend.');
    } finally { setResending(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/login-phone" className="auth-back"><FaArrowLeft /> Change number</Link>
        <div className="auth-hero">
          <h1>Enter the code</h1>
          <p>We sent a 6-digit code to <strong>{phone}</strong>.</p>
        </div>

        <form onSubmit={submit} className="auth-form">
          <div className="auth-field">
            <label htmlFor="code">Verification code</label>
            <input
              id="code" ref={inputRef} type="text" inputMode="numeric"
              pattern="[0-9]*" maxLength={6}
              value={code}
              onChange={(e) => { setCode(e.target.value.replace(/[^0-9]/g, '')); setError(''); }}
              className="auth-code"
              placeholder="000000"
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-btn" disabled={loading || code.length !== 6}>
            {loading ? <><FaCircleNotch className="auth-spin" /> Verifying…</> : 'Verify & sign in'}
          </button>

          <div className="auth-resend">
            {seconds > 0 ? (
              <span>Resend in <strong>{seconds}s</strong></span>
            ) : (
              <button type="button" onClick={resend} disabled={resending}>
                {resending ? 'Sending…' : 'Resend code'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
