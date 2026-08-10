import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { getComments, deleteComment } from '../../api/commentsAPI';

export const CommentList = ({ incidentId }) => {
  const queryClient = useQueryClient();

  // ─── Fetch comments ──────────────────────────────────────
  const {
    data: comments = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['comments', incidentId],
    queryFn: () =>
      getComments({ incident: incidentId }).then((res) => res.data.results || []),
    enabled: !!incidentId,
    staleTime: 5 * 60 * 1000,
  });

  // ─── Delete mutation ────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: deleteComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', incidentId] });
    },
    onError: () => {
      alert('Failed to delete comment.');
    },
  });

  const handleDelete = (id) => {
    if (!window.confirm('Delete this comment?')) return;
    deleteMutation.mutate(id);
  };

  if (isLoading) return <div className="text-sm text-gray-500">Loading comments...</div>;
  if (error) return <div className="text-sm text-red-500">Failed to load comments.</div>;
  if (comments.length === 0) return <div className="text-sm text-gray-500">No comments yet.</div>;

  return (
    <div className="space-y-3">
      {comments.map((comment) => (
        <div key={comment.id} className="bg-gray-50 p-3 rounded-lg">
          <div className="flex justify-between">
            <div className="flex items-center space-x-2">
              <span className="font-medium">{comment.user_name || 'Unknown'}</span>
              {comment.is_internal && (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">
                  Internal
                </span>
              )}
              <span className="text-sm text-gray-500">
                {new Date(comment.created_at).toLocaleString()}
              </span>
            </div>
            <button
              onClick={() => handleDelete(comment.id)}
              disabled={deleteMutation.isPending}
              className="text-red-600 hover:text-red-800 text-sm disabled:opacity-50"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </button>
          </div>
          <p className="mt-1 text-gray-800">{comment.text}</p>
        </div>
      ))}
    </div>
  );
};

CommentList.propTypes = {
  incidentId: PropTypes.string.isRequired,
};