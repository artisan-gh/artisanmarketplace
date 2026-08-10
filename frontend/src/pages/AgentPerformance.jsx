import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaUser, FaPhone, FaCheckCircle, FaClock, FaChartLine } from 'react-icons/fa';
import { getAgentPerformance } from '../api/call_centerAPI';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './AgentPerformance.css';

export default function AgentPerformance() {
  const { user } = useAuth();
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getAgentPerformance();
        const data = res.data.results || res.data || [];
        setPerformance(data.length > 0 ? data[0] : null);
      } catch (error) {
        console.error(error);
        toast.error('Failed to load performance');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  if (loading) return <div className="loading">Loading performance…</div>;
  if (!performance) return <div className="empty">No performance data yet.</div>;

  // Display agent's name in the header
  const agentName = user?.full_name || user?.email || 'Agent';

  return (
    <div className="performance-page">
      <div className="performance-container">
        <h1>📊 {agentName}'s Performance</h1>
        <div className="performance-grid">
          <PerfCard icon={<FaPhone />} label="Total Calls" value={performance.total_calls || 0} color="#2563eb" />
          <PerfCard icon={<FaCheckCircle />} label="Answered" value={performance.answered_calls || 0} color="#059669" />
          <PerfCard icon={<FaClock />} label="Avg Duration" value={`${performance.avg_call_duration || 0}s`} color="#d97706" />
          <PerfCard icon={<FaChartLine />} label="Conversion Rate" value={`${performance.conversion_rate || 0}%`} color="#7c3aed" />
          <PerfCard icon={<FaUser />} label="Bookings Created" value={performance.bookings_created || 0} color="#dc2626" />
          <PerfCard icon={<FaCheckCircle />} label="Satisfaction" value={`${performance.client_satisfaction || 0}★`} color="#059669" />
        </div>
      </div>
    </div>
  );
}

function PerfCard({ icon, label, value, color }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="perf-card">
      <div className="perf-icon" style={{ color }}>{icon}</div>
      <div className="perf-value">{value}</div>
      <div className="perf-label">{label}</div>
    </motion.div>
  );
}