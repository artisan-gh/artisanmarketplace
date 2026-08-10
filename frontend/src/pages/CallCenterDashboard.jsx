import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaPhone, FaCalendarDay, FaUser, FaCheckCircle, FaClock, FaArrowRight, FaPen } from 'react-icons/fa';
import { getCallLogs, getTodayCalls, getMyCalls } from '../api/call_centerAPI';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './CallCenter.css';

export default function CallCenterDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ total: 0, today: 0, myCalls: 0, bookings: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [totalRes, todayRes, myRes] = await Promise.all([
          getCallLogs(),
          getTodayCalls(),
          getMyCalls(),
        ]);
        setStats({
          total: totalRes.data.count || totalRes.data.length || 0,
          today: todayRes.data.length || 0,
          myCalls: myRes.data.length || 0,
          bookings: totalRes.data.results?.filter(c => c.booking_id).length || 0,
        });
      } catch (error) {
        console.error(error);
        toast.error('Failed to load stats');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const isAgent = user?.is_staff || user?.has_perm?.('call_center.is_call_agent');

  if (!isAgent) {
    return (
      <div className="call-center-page">
        <div className="access-denied">
          <h2>Access Denied</h2>
          <p>You don't have permission to view this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="call-center-page">
      <div className="call-center-container">
        <div className="call-center-header">
          <h1>📞 Call Center</h1>
          <p>Manage incoming calls, log issues, and create bookings.</p>
        </div>

        {loading ? (
          <div className="loading-spinner">Loading stats…</div>
        ) : (
          <>
            <div className="stats-grid">
              <StatCard
                icon={<FaPhone />}
                label="Total Calls"
                value={stats.total}
                color="#2563eb"
              />
              <StatCard
                icon={<FaCalendarDay />}
                label="Today's Calls"
                value={stats.today}
                color="#7c3aed"
              />
              <StatCard
                icon={<FaUser />}
                label="My Calls"
                value={stats.myCalls}
                color="#059669"
              />
              <StatCard
                icon={<FaCheckCircle />}
                label="Bookings Created"
                value={stats.bookings}
                color="#d97706"
              />
            </div>

            <div className="quick-actions">
              <Link to="/call-center/logs" className="quick-action-card">
                <FaPhone /> View All Calls
                <FaArrowRight />
              </Link>
              <Link to="/call-center/logs/new" className="quick-action-card">
                <FaPhone /> New Call
                <FaArrowRight />
              </Link>
              <Link to="/report-issue" className="quick-action-card">
                <FaPen /> Report Issue & Book
                <FaArrowRight />
              </Link>
              <Link to="/call-center/performance" className="quick-action-card">
                <FaClock /> My Performance
                <FaArrowRight />
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="stat-card"
      style={{ borderLeftColor: color }}
    >
      <div className="stat-icon" style={{ color }}>{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </motion.div>
  );
}