import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaSearch, FaPlus, FaSpinner, FaSignOutAlt, FaUser } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import { getBookings, createCallLog, addBookingToCall } from '../api/call_centerAPI';
import toast from 'react-hot-toast';
import CallLogFormModal from '../components/CallLogFormModal';
import './CallLogList.css';

// ─── Custom hook for fetching bookings ──────────────────────
function useBookings(filters, search, key) {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = { ...filters, search };
        Object.keys(params).forEach(key => {
          if (!params[key]) delete params[key];
        });
        const data = await getBookings(params);
        if (mounted.current) {
          setBookings(Array.isArray(data) ? data : []);
          setLoading(false);
        }
      } catch (err) {
        if (mounted.current) {
          console.error('Fetch error:', err);
          setError('Failed to load bookings');
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      abortController.abort();
    };
  }, [filters, search, key]);

  return { bookings, loading, error };
}

// ─── Component ──────────────────────────────────────────────
export default function CallLogList() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [filters, setFilters] = useState({
    status: '',
    scheduled_date_range: '',
    created_at_range: '',
  });
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const { bookings, loading, error } = useBookings(filters, search, refreshKey);

  // Force refetch by incrementing key
  const refetch = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, [setRefreshKey]);

  // ─── Handlers ──────────────────────────────────────────────
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleNew = () => {
    setModalOpen(true);
  };

  const handleModalSubmit = async (payload) => {
    setSubmitting(true);
    try {
      // Create call log
      const callRes = await createCallLog({
        call_type: payload.call_type,
        caller_number: payload.caller_number,
        caller_name: payload.caller_name,
        alternative_phone: payload.alternative_phone,
        email: payload.email,
        call_notes: payload.call_notes,
      });
      const callId = callRes.data.id;
      // Add booking to call
      await addBookingToCall(callId, payload);
      toast.success('Call logged and booking created');
      setModalOpen(false);
      // Refetch bookings after a short delay
      setTimeout(() => refetch(), 300);
    } catch (error) {
      console.error('❌ Full error:', error);
      console.error('❌ Response data:', error.response?.data);
      
      // Parse the error response
      const responseData = error.response?.data;
      
      // If the backend returned validation details, show them
      if (responseData?.details) {
        // Flatten all error messages into a single string
        const messages = Object.values(responseData.details)
          .flat()
          .join(', ');
        toast.error(`Validation failed: ${messages}`);
      } else if (responseData?.error) {
        toast.error(responseData.error);
      } else if (responseData?.message) {
        toast.error(responseData.message);
      } else if (typeof responseData === 'string') {
        // If the response is a string (HTML error page), show generic message
        toast.error('Operation failed. Please check the console for details.');
      } else {
        toast.error('Operation failed. Please try again.');
      }
      
      // Log the full response for debugging
      if (responseData) {
        console.log('📋 Full response:', JSON.stringify(responseData, null, 2));
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const displayName = user?.full_name || user?.email || 'User';

  return (
    <div className="call-log-list-page">
      <div className="top-bar">
        <div className="user-info">
          <FaUser className="user-icon" />
          <span className="user-name">Welcome, {displayName}</span>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          <FaSignOutAlt /> Logout
        </button>
      </div>

      <div className="list-container">
        <div className="list-header">
          <h1>Bookings</h1>
          <button onClick={handleNew} className="btn-primary">
            <FaPlus /> New Call
          </button>
        </div>

        <div className="filters-bar">
          <div className="search-box">
            <FaSearch />
            <input
              type="text"
              placeholder="Search by title or reference…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label>By status</label>
            <select name="status" value={filters.status} onChange={handleFilterChange}>
              <option value="">All</option>
              <option value="PENDING">Pending</option>
              <option value="ACCEPTED">Accepted</option>
              <option value="REJECTED">Rejected</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div className="filter-group">
            <label>By scheduled date</label>
            <select name="scheduled_date_range" value={filters.scheduled_date_range} onChange={handleFilterChange}>
              <option value="">Any date</option>
              <option value="today">Today</option>
              <option value="past_7_days">Past 7 days</option>
              <option value="this_month">This month</option>
              <option value="this_year">This year</option>
            </select>
          </div>
          <div className="filter-group">
            <label>By created at</label>
            <select name="created_at_range" value={filters.created_at_range} onChange={handleFilterChange}>
              <option value="">Any date</option>
              <option value="today">Today</option>
              <option value="past_7_days">Past 7 days</option>
              <option value="this_month">This month</option>
              <option value="this_year">This year</option>
            </select>
          </div>
        </div>

        <div className="count-badge">
          {Array.isArray(bookings) ? bookings.length : 0} {bookings.length === 1 ? 'Booking' : 'Bookings'}
        </div>

        {loading ? (
          <div className="loading"><FaSpinner className="spin" /> Loading…</div>
        ) : error ? (
          <div className="empty-state">{error}</div>
        ) : !Array.isArray(bookings) || bookings.length === 0 ? (
          <div className="empty-state">No bookings found.</div>
        ) : (
          <div className="table-wrapper">
            <table className="booking-table">
              <thead>
                <tr>
                  <th>Reference</th>
                  <th>Title</th>
                  <th>Client</th>
                  <th>Artisan</th>
                  <th>Service</th>
                  <th>Scheduled date</th>
                  <th>Scheduled time</th>
                  <th>Status</th>
                  <th>Estimated cost</th>
                  <th>Created at</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking) => (
                  <motion.tr
                    key={booking.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="booking-row"
                  >
                    <td className="ref-cell">
                      <span className="ref-badge">{booking.reference || `#${booking.id}`}</span>
                    </td>
                    <td>{booking.title || '—'}</td>
                    <td>{booking.client_email || '—'}</td>
                    <td>{booking.artisan_email || '—'}</td>
                    <td>{booking.service_name || '—'}</td>
                    <td>
                      {booking.scheduled_date
                        ? new Date(booking.scheduled_date).toLocaleDateString()
                        : '—'}
                    </td>
                    <td>{booking.scheduled_time || '—'}</td>
                    <td>
                      <span className={`status-badge ${booking.status?.toLowerCase()}`}>
                        {booking.status}
                      </span>
                    </td>
                    <td>
                      {booking.estimated_cost !== null && booking.estimated_cost !== undefined
                        ? `GHS ${Number(booking.estimated_cost).toFixed(2)}`
                        : '—'}
                    </td>
                    <td>
                      {booking.created_at
                        ? new Date(booking.created_at).toLocaleString()
                        : '—'}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <CallLogFormModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        initialData={null}
        onSubmit={handleModalSubmit}
        submitting={submitting}
      />
    </div>
  );
}