
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaPhoneAlt, FaArrowRight, FaCircleNotch } from 'react-icons/fa';
import { sendOtp } from '../../api/authClient';
import './auth.css';

const PHONE_RE = /^\+?[0-9]{9,15}$/;

export default function PhoneEntryScreen() {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    const cleaned = phone.replace(/[\s-]/g, '');
    if (!PHONE_RE.test(cleaned)) { setError('Enter a valid phone number.'); return; }
    setLoading(true);
    try {
      const res = await sendOtp(cleaned);
      navigate('/login-otp', { state: { phone: cleaned, debugCode: res?.debug_code } });
    } catch (e) {
      setError(e?.response?.data?.detail || 'Could not send code.');
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-hero">
          <div className="auth-hero__icon"><FaPhoneAlt /></div>
          <h1>Sign in</h1>
          <p>Enter your phone number. We'll text you a 6-digit code.</p>
        </div>

        <form onSubmit={submit} className="auth-form">
          <div className="auth-field">
            <label htmlFor="phone">Phone number</label>
            <input
              id="phone" type="tel" inputMode="tel"
              value={phone} onChange={(e) => { setPhone(e.target.value); setError(''); }}
              placeholder="+233 24 000 0000" autoFocus autoComplete="tel"
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-btn" disabled={loading || !phone}>
            {loading ? <><FaCircleNotch className="auth-spin" /> Sending…</> : <>Continue <FaArrowRight /></>}
          </button>
        </form>
      </div>
    </div>
  );
}
