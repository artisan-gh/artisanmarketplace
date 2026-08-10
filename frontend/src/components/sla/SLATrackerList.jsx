// src/components/sla/SLATrackerList.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSLATrackers } from '../../api/slaAPI';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { Link } from 'react-router-dom';

export const SLATrackerList = () => {
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [slaStatusFilter, setSlaStatusFilter] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: [
      'slaTrackers',
      { status: statusFilter, priority: priorityFilter, sla_status: slaStatusFilter },
    ],
    queryFn: () =>
      getSLATrackers({
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        sla_status: slaStatusFilter || undefined,
      }).then(res => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const columns = [
    {
      key: 'incident_number',
      label: 'Incident',
      render: (val, row) => (
        <Link to={`/incidents/${row.incident}`} className="text-blue-600 hover:underline">
          {val}
        </Link>
      ),
    },
    { key: 'customer_name', label: 'Customer' },
    { key: 'priority', label: 'Priority' },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <StatusBadge status={val?.toLowerCase()}>{val}</StatusBadge>,
    },
    {
      key: 'target_resolution',
      label: 'Target Resolution',
      render: (val) => new Date(val).toLocaleString(),
    },
    {
      key: 'sla_status',
      label: 'SLA Status',
      render: (val) => {
        const statusMap = {
          ON_TRACK: { label: 'On Track', color: 'success' },
          AT_RISK: { label: 'At Risk', color: 'warning' },
          BREACHED: { label: 'Breached', color: 'error' },
        };
        const info = statusMap[val] || { label: val || 'Unknown', color: 'default' };
        return <StatusBadge status={info.color}>{info.label}</StatusBadge>;
      },
    },
    {
      key: 'remaining_time',
      label: 'Remaining Time',
      render: (val) => val || '—',
    },
  ];

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All Incident Statuses</option>
          <option value="NEW">New</option>
          <option value="OPEN">Open</option>
          <option value="ASSIGNED">Assigned</option>
          <option value="RESOLVED">Resolved</option>
          <option value="CLOSED">Closed</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All Priorities</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
        </select>

        <select
          value={slaStatusFilter}
          onChange={(e) => setSlaStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All SLA Status</option>
          <option value="ON_TRACK">On Track</option>
          <option value="AT_RISK">At Risk</option>
          <option value="BREACHED">Breached</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
      />
    </div>
  );
};