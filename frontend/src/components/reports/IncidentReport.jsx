// src/components/reports/IncidentReport.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getIncidentReport, exportReport } from '../../api/reportsAPI';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

const COLORS = ['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#8b5cf6'];

export const IncidentReport = () => {
  const [days, setDays] = useState(30);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['incidentReport', { days, status: statusFilter, priority: priorityFilter }],
    queryFn: () =>
      getIncidentReport({
        days,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
      }).then(res => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const handleExport = async () => {
    try {
      const blob = await exportReport({
        type: 'incidents',
        days,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'incident_report.csv';
      link.click();
    } catch {
      alert('Export failed.');
    }
  };

  if (isLoading) return <div className="text-center py-8">Loading report...</div>;
  if (error) return <div className="text-red-500">Failed to load report.</div>;

  const trends = data?.trends?.daily || [];
  const distribution = data?.distribution || {};

  // ─── Format data for charts ──────────────────────────────
  const trendData = trends.map(item => ({
    day: item.day,
    incidents: item.count,
  }));

  const statusData = distribution?.by_status?.map(s => ({
    name: s.status__name || 'Unknown',
    value: s.count,
  })) || [];

  const priorityData = distribution?.by_priority?.map(p => ({
    name: p.priority,
    value: p.count,
  })) || [];

  return (
    <div className="space-y-8">
      {/* ─── Header ────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Incident Report</h1>
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>

      {/* ─── Filters ────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div>
          <label className="block text-sm font-medium text-gray-700">Period</label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="mt-1 block px-3 py-2 border border-gray-300 rounded-md bg-white shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="mt-1 block px-3 py-2 border border-gray-300 rounded-md bg-white shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All</option>
            <option value="OPEN">Open</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Priority</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="mt-1 block px-3 py-2 border border-gray-300 rounded-md bg-white shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {/* ─── Summary Cards ────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
          <p className="text-sm text-gray-500">Total Incidents</p>
          <p className="text-2xl font-bold">{data?.summary?.total_incidents || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <p className="text-sm text-gray-500">Avg Resolution Time</p>
          <p className="text-2xl font-bold">{data?.summary?.avg_resolution_hours || 0}h</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-yellow-500">
          <p className="text-sm text-gray-500">SLA Compliance</p>
          <p className="text-2xl font-bold">{data?.sla?.met_percent || 0}%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
          <p className="text-sm text-gray-500">Open Incidents</p>
          <p className="text-2xl font-bold">{data?.summary?.open_incidents || 0}</p>
        </div>
      </div>

      {/* ─── Charts Row 1 – Trend ────────────────────────────── */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Daily Incident Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="incidents" stroke="#3b82f6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ─── Charts Row 2 – Distribution ────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">By Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">By Priority</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={priorityData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {priorityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── Detailed Table ────────────────────────────────────── */}
      <div className="bg-white p-4 rounded-lg shadow overflow-x-auto">
        <h3 className="text-lg font-semibold mb-4">Detailed Breakdown</h3>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Day</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Incidents</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {trendData.map((item) => (
              <tr key={item.day}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.day}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.incidents}</td>
              </tr>
            ))}
            {trendData.length === 0 && (
              <tr>
                <td colSpan="2" className="px-6 py-4 text-center text-sm text-gray-500">No data available</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};