import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAssignment, acceptAssignment, rejectAssignment, startAssignment, completeAssignment } from '../../api/assignmentsAPI';
import { getIncident } from '../../api/incidentsAPI';
import { StatusBadge } from '../common/StatusBadge';
import { useAuth } from '../../context/AuthContext';

export const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // ─── Fetch assignment details ─────────────────────────────
  const {
    data: assignment,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['assignment', id],
    queryFn: () => getAssignment(id).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  // ─── Fetch incident details ──────────────────────────────
  const { data: incident } = useQuery({
    queryKey: ['incident', assignment?.incident],
    queryFn: () => getIncident(assignment.incident).then((res) => res.data),
    enabled: !!assignment?.incident,
    staleTime: 5 * 60 * 1000,
  });

  // ─── Mutations ─────────────────────────────────────────────
  const acceptMut = useMutation({
    mutationFn: () => acceptAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment', id] });
      queryClient.invalidateQueries({ queryKey: ['myAssignments'] });
    },
  });

  const rejectMut = useMutation({
    mutationFn: () => rejectAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment', id] });
      queryClient.invalidateQueries({ queryKey: ['myAssignments'] });
    },
  });

  const startMut = useMutation({
    mutationFn: () => startAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment', id] });
      queryClient.invalidateQueries({ queryKey: ['myAssignments'] });
    },
  });

  const completeMut = useMutation({
    mutationFn: () => completeAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment', id] });
      queryClient.invalidateQueries({ queryKey: ['myAssignments'] });
    },
  });

  const handleAction = (action) => {
    if (action === 'accept') acceptMut.mutate();
    else if (action === 'reject') rejectMut.mutate();
    else if (action === 'start') startMut.mutate();
    else if (action === 'complete') completeMut.mutate();
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error || !assignment) return <div className="text-red-500">Assignment not found.</div>;

  const isArtisan = user?.user_type === 'ARTISAN';
  const canAccept = assignment.status === 'PENDING' && isArtisan;
  const canReject = assignment.status === 'PENDING' && isArtisan;
  const canStart = assignment.status === 'ACCEPTED' && isArtisan;
  const canComplete = assignment.status === 'IN_PROGRESS' && isArtisan;

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold">Job Details</h1>
          <p className="text-gray-600">Assignment #{id}</p>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <div className="flex justify-between">
          <div>
            <p><strong>Incident:</strong> {incident?.incident_number || assignment.incident}</p>
            <p><strong>Title:</strong> {incident?.title || '—'}</p>
            <p><strong>Customer:</strong> {incident?.customer_name || '—'}</p>
          </div>
          <div className="text-right">
            <p><strong>Status:</strong> <StatusBadge status={assignment.status?.toLowerCase()}>{assignment.status}</StatusBadge></p>
            <p><strong>Assigned At:</strong> {new Date(assignment.assigned_at).toLocaleString()}</p>
          </div>
        </div>

        {incident?.description && (
          <div>
            <p><strong>Description:</strong></p>
            <p className="text-gray-700">{incident.description}</p>
          </div>
        )}

        {assignment.notes && (
          <div>
            <p><strong>Notes:</strong></p>
            <p className="text-gray-700">{assignment.notes}</p>
          </div>
        )}

        <div className="border-t pt-4 flex flex-wrap gap-2">
          {canAccept && (
            <button
              onClick={() => handleAction('accept')}
              disabled={acceptMut.isPending}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {acceptMut.isPending ? 'Accepting...' : 'Accept Job'}
            </button>
          )}
          {canReject && (
            <button
              onClick={() => handleAction('reject')}
              disabled={rejectMut.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {rejectMut.isPending ? 'Rejecting...' : 'Reject Job'}
            </button>
          )}
          {canStart && (
            <button
              onClick={() => handleAction('start')}
              disabled={startMut.isPending}
              className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50"
            >
              {startMut.isPending ? 'Starting...' : 'Start Work'}
            </button>
          )}
          {canComplete && (
            <button
              onClick={() => handleAction('complete')}
              disabled={completeMut.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {completeMut.isPending ? 'Completing...' : 'Complete Job'}
            </button>
          )}
          {!isArtisan && (
            <span className="text-sm text-gray-500">You are not an artisan.</span>
          )}
          {isArtisan && !canAccept && !canReject && !canStart && !canComplete && (
            <span className="text-sm text-gray-500">No actions available.</span>
          )}
        </div>
      </div>
    </div>
  );
};