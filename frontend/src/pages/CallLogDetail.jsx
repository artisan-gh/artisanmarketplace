import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaPhone } from 'react-icons/fa';
import { getCallLog, endCall, addBookingToCall } from '../api/call_centerAPI';
import { getAvailableArtisans } from '../api/call_centerAPI';
import CallBookingForm from '../components/CallBookingForm';
import toast from 'react-hot-toast';
import './CallLogDetail.css';

export default function CallLogDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [log, setLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [availableArtisans, setAvailableArtisans] = useState([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getCallLog(id);
        setLog(res.data);
        // Pre-fetch artisans if service is known
        if (res.data.booking_data?.service) {
          const artisans = await getAvailableArtisans({ service_id: res.data.booking_data.service });
          setAvailableArtisans(artisans.data);
        }
      } catch (error) {
        console.error('Failed to fetch call log:', error);
        toast.error('Call not found');
        navigate('/call-center/logs');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [id, navigate]);

  const handleEndCall = async () => {
    try {
      await endCall(id);
      toast.success('Call ended');
      navigate('/call-center/logs');
    } catch (error) {
      console.error('Failed to end call:', error);  // ✅ error is now used
      toast.error(error.response?.data?.error || 'Failed to end call');
    }
  };

  const handleAddBooking = async (bookingData) => {
    setSubmitting(true);
    try {
      const res = await addBookingToCall(id, bookingData);
      toast.success('Booking created successfully!');
      setLog(res.data.call_log);
      setShowBookingForm(false);
      navigate(`/bookings/${res.data.booking.id}`);
    } catch (error) {
      console.error('Failed to create booking:', error);
      toast.error(error.response?.data?.error || 'Failed to create booking');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading…</div>;
  if (!log) return <div className="empty">Call not found</div>;

  return (
    <div className="call-detail-page">
      <div className="detail-container">
        <div className="detail-nav">
          <Link to="/call-center/logs"><FaArrowLeft /> Back</Link>
          <div>
            <button onClick={handleEndCall} className="btn-end">End Call</button>
            {!log.booking && (
              <button onClick={() => setShowBookingForm(true)} className="btn-book">+ Create Booking</button>
            )}
          </div>
        </div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="detail-card">
          <div className="detail-header">
            <div>
              <h2>{log.caller_name || 'Unknown Caller'}</h2>
              <p><FaPhone /> {log.caller_number}</p>
            </div>
            <div>
              <span className={`badge ${log.call_status}`}>{log.call_status}</span>
              <span className={`badge ${log.disposition || 'N/A'}`}>{log.disposition || 'N/A'}</span>
            </div>
          </div>

          <div className="detail-body">
            <div className="info-grid">
              <div><strong>Agent:</strong> {log.agent_name || 'N/A'}</div>
              <div><strong>Type:</strong> {log.call_type}</div>
              <div><strong>Duration:</strong> {log.call_duration ? `${log.call_duration}s` : 'Ongoing'}</div>
              <div><strong>Start:</strong> {new Date(log.start_time).toLocaleString()}</div>
              {log.alternative_phone && <div><strong>Alt Phone:</strong> {log.alternative_phone}</div>}
              {log.email && <div><strong>Email:</strong> {log.email}</div>}
            </div>
            {log.call_notes && (
              <div className="notes">
                <h4>Call Notes</h4>
                <p>{log.call_notes}</p>
              </div>
            )}
            {log.booking && (
              <div className="existing-booking">
                <h4>✅ Booking Created</h4>
                <Link to={`/bookings/${log.booking.id}`}>View Booking #{log.booking.id}</Link>
              </div>
            )}
          </div>
        </motion.div>

        {showBookingForm && (
          <div className="booking-form-wrapper">
            <CallBookingForm
              initialData={log.booking_data || { call_log: id }}
              onSubmit={handleAddBooking}
              onCancel={() => setShowBookingForm(false)}
              submitting={submitting}
              availableArtisans={availableArtisans}
            />
          </div>
        )}
      </div>
    </div>
  );
}