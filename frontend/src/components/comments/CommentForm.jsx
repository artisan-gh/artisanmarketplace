import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { createComment } from '../../api/commentsAPI';

export const CommentForm = ({ incidentId, onCommentAdded }) => {
  const queryClient = useQueryClient();
  const [text, setText] = useState('');
  const [isInternal, setIsInternal] = useState(false);

  // ─── Create comment mutation ─────────────────────────────
  const mutation = useMutation({
    mutationFn: () =>
      createComment({
        incident: incidentId,
        text: text.trim(),
        is_internal: isInternal,
      }),
    onSuccess: () => {
      setText('');
      queryClient.invalidateQueries({ queryKey: ['comments', incidentId] });
      if (onCommentAdded) onCommentAdded();
    },
    onError: () => {
      alert('Failed to add comment.');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || mutation.isPending) return;
    mutation.mutate();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a comment..."
          rows="2"
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div className="flex items-center space-x-4">
        <label className="flex items-center space-x-1 text-sm">
          <input
            type="checkbox"
            checked={isInternal}
            onChange={(e) => setIsInternal(e.target.checked)}
          />
          <span>Internal note</span>
        </label>
        <button
          type="submit"
          disabled={mutation.isPending || !text.trim()}
          className="px-4 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Posting...' : 'Post Comment'}
        </button>
      </div>
    </form>
  );
};

CommentForm.propTypes = {
  incidentId: PropTypes.string.isRequired,
  onCommentAdded: PropTypes.func,
};