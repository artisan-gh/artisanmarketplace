import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCallLog, endCall } from '../../api/call_centerAPI';
import { StatusBadge } from '../common/StatusBadge';

export const CallLogDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: log, isLoading, error } = useQuery({
    queryKey: ['callLog', id],
    queryFn: () => getCallLog(id).then(res => res.data),
    staleTime: 5 * 60 * 1000,
  });

  const endCallMutation = useMutation({
    mutationFn: () => endCall(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['callLog', id] });
    },
  });

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error || !log) return <div className="text-center py-8 text-red-500">Call log not found.</div>;

  const formatDate = (date) => date ? new Date(date).toLocaleString() : '—';

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex justify-between items-start mb-6">
        <h1 className="text-2xl font-bold">{log.reference}</h1>
        <div className="flex gap-2">
          {log.status === 'ACTIVE' && (
            <button
              onClick={() => endCallMutation.mutate()}
              disabled={endCallMutation.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {endCallMutation.isPending ? 'Ending...' : 'End Call'}
            </button>
          )}
          <button
            onClick={() => navigate('/call-center/logs')}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Back
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p><strong>Customer:</strong> {log.customer_name || '—'}</p>
            <p><strong>Phone:</strong> {log.phone_number || '—'}</p>
            <p><strong>Direction:</strong> {log.call_type}</p>
            <p><strong>Status:</strong> <StatusBadge status={log.status?.toLowerCase()}>{log.status}</StatusBadge></p>
          </div>
          <div>
            <p><strong>Started:</strong> {formatDate(log.started_at)}</p>
            <p><strong>Ended:</strong> {formatDate(log.ended_at)}</p>
            <p><strong>Duration:</strong> {log.duration_seconds ? `${Math.floor(log.duration_seconds / 60)}m ${log.duration_seconds % 60}s` : '—'}</p>
            <p><strong>Resolved:</strong> {log.is_resolved ? '✅ Yes' : '❌ No'}</p>
          </div>
        </div>
        <div>
          <p><strong>Disposition:</strong> <StatusBadge status={log.disposition?.toLowerCase()}>{log.disposition}</StatusBadge></p>
        </div>
        {log.notes && (
          <div>
            <p><strong>Notes:</strong></p>
            <p className="text-gray-700">{log.notes}</p>
          </div>
        )}
        {log.follow_up_required && (
          <div>
            <p><strong>Follow-up Date:</strong> {formatDate(log.follow_up_date)}</p>
          </div>
        )}
        {log.incident && (
          <div>
            <p><strong>Incident:</strong> <span className="text-blue-600 hover:underline cursor-pointer" onClick={() => navigate(`/incidents/${log.incident}`)}>{log.incident_number || log.incident}</span></p>
          </div>
        )}
        {log.agent && (
          <div>
            <p><strong>Agent:</strong> {log.agent_name || log.agent}</p>
          </div>
        )}
      </div>
    </div>
  );
};