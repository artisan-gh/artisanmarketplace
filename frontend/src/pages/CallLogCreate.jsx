import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaSave, FaTimes, FaSpinner } from 'react-icons/fa';
import { createCallLog } from '../api/call_centerAPI';
import toast from 'react-hot-toast';
import './CallLogCreate.css';

export default function CallLogCreate() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    call_type: 'INCOMING',
    caller_number: '',
    caller_name: '',
    alternative_phone: '',
    email: '',
    call_notes: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.caller_number) {
      toast.error('Caller number is required.');
      return;
    }
    setSubmitting(true);
    try {
      const res = await createCallLog(form);
      toast.success('Call logged successfully.');
      navigate(`/call-center/logs/${res.data.id}`);
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.error || 'Failed to log call.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="call-log-create-page">
      <div className="create-container">
        <div className="create-header">
          <Link to="/call-center/logs" className="back-link">
            <FaArrowLeft /> Back to logs
          </Link>
          <h1>📞 New Call</h1>
        </div>

        <motion.form
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="create-form"
          onSubmit={handleSubmit}
        >
          <div className="form-grid">
            <div className="form-group">
              <label>Call Type</label>
              <select name="call_type" value={form.call_type} onChange={handleChange}>
                <option value="INCOMING">Incoming</option>
                <option value="OUTGOING">Outgoing</option>
              </select>
            </div>

            <div className="form-group">
              <label>Caller Number *</label>
              <input
                type="text"
                name="caller_number"
                value={form.caller_number}
                onChange={handleChange}
                placeholder="e.g., 0244123456"
                required
              />
            </div>

            <div className="form-group">
              <label>Caller Name</label>
              <input
                type="text"
                name="caller_name"
                value={form.caller_name}
                onChange={handleChange}
                placeholder="John Doe"
              />
            </div>

            <div className="form-group">
              <label>Alternative Phone</label>
              <input
                type="text"
                name="alternative_phone"
                value={form.alternative_phone}
                onChange={handleChange}
                placeholder="0201234567"
              />
            </div>

            <div className="form-group full-width">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="client@example.com"
              />
            </div>

            <div className="form-group full-width">
              <label>Call Notes</label>
              <textarea
                name="call_notes"
                value={form.call_notes}
                onChange={handleChange}
                rows="4"
                placeholder="Notes about the call (issue summary, client mood, etc.)"
              />
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/call-center/logs')}
              className="btn-cancel"
            >
              <FaTimes /> Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-submit"
            >
              {submitting ? <FaSpinner className="spin" /> : <FaSave />}
              {submitting ? 'Saving…' : 'Log Call'}
            </button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}