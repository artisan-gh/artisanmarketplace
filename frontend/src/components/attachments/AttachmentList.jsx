import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { getAttachments, deleteAttachment } from '../../api/attachmentsAPI';

export const AttachmentList = ({ incidentId }) => {
  const queryClient = useQueryClient();

  // ─── Fetch attachments ──────────────────────────────────────
  const {
    data: attachments = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['attachments', incidentId],
    queryFn: () =>
      getAttachments({ incident: incidentId }).then((res) => res.data.results || []),
    enabled: !!incidentId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // ─── Delete mutation ────────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: deleteAttachment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attachments', incidentId] });
    },
    onError: () => {
      alert('Failed to delete attachment.');
    },
  });

  const handleDelete = (id) => {
    if (!window.confirm('Delete this attachment?')) return;
    deleteMutation.mutate(id);
  };

  // ─── Render states ─────────────────────────────────────────
  if (isLoading) return <div className="text-sm text-gray-500">Loading attachments...</div>;
  if (error) return <div className="text-sm text-red-500">Failed to load attachments.</div>;
  if (attachments.length === 0) return <div className="text-sm text-gray-500">No attachments.</div>;

  return (
    <ul className="divide-y divide-gray-200">
      {attachments.map((att) => (
        <li key={att.id} className="py-2 flex justify-between items-center">
          <div>
            <a
              href={att.file}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {att.filename || 'Download'}
            </a>
            <span className="text-sm text-gray-500 ml-2">
              Uploaded {new Date(att.created_at).toLocaleDateString()}
            </span>
          </div>
          <button
            onClick={() => handleDelete(att.id)}
            disabled={deleteMutation.isPending}
            className="text-red-600 hover:text-red-800 text-sm disabled:opacity-50"
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </button>
        </li>
      ))}
    </ul>
  );
};

AttachmentList.propTypes = {
  incidentId: PropTypes.string.isRequired,
};