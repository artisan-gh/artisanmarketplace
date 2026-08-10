// src/components/sla/SLAPolicyForm.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSLAPolicy, createSLAPolicy, updateSLAPolicy } from '../../api/slaAPI';

export const SLAPolicyForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = Boolean(id);

  const { data: policy, isLoading } = useQuery({
    queryKey: ['slaPolicy', id],
    queryFn: () => getSLAPolicy(id).then(res => res.data),
    enabled: isEditing,
    staleTime: 5 * 60 * 1000,
  });

  const [formData, setFormData] = useState({
    name: '',
    priority: 'MEDIUM',
    resolution_hours: 24,
    escalation_hours: null,
    is_active: true,
  });

  useEffect(() => {
    if (policy) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFormData((prev) => {
        const current = { ...prev, escalation_hours: prev.escalation_hours ?? null };
        const incoming = { ...policy, escalation_hours: policy.escalation_hours ?? null };
        return JSON.stringify(current) !== JSON.stringify(incoming) ? policy : prev;
      });
    }
  }, [policy]);

  const mutation = useMutation({
    mutationFn: (data) =>
      isEditing ? updateSLAPolicy(id, data) : createSLAPolicy(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['slaPolicies'] });
      navigate('/sla/policies');
    },
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  if (isLoading) return <div className="text-center py-8">Loading policy...</div>;

  return (
    <form onSubmit={handleSubmit} className="max-w-lg mx-auto space-y-4">
      <h2 className="text-xl font-bold">{isEditing ? 'Edit SLA Policy' : 'New SLA Policy'}</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Priority</label>
        <select
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Resolution Hours</label>
        <input
          type="number"
          name="resolution_hours"
          value={formData.resolution_hours}
          onChange={handleChange}
          min="1"
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Escalation Hours (optional)</label>
        <input
          type="number"
          name="escalation_hours"
          value={formData.escalation_hours || ''}
          onChange={handleChange}
          min="1"
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
        <p className="text-xs text-gray-500 mt-1">
          If set, incidents will be escalated after this many hours.
        </p>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          name="is_active"
          checked={formData.is_active}
          onChange={handleChange}
          className="h-4 w-4 text-blue-600"
        />
        <label className="text-sm font-medium text-gray-700">Active</label>
      </div>

      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="btn btn-primary disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving...' : isEditing ? 'Update' : 'Create'}
        </button>
        <button
          type="button"
          onClick={() => navigate('/sla/policies')}
          className="btn btn-secondary"
        >
          Cancel
        </button>
      </div>

      {mutation.error && (
        <div className="text-red-600 text-sm mt-2">
          Error: {mutation.error.message}
        </div>
      )}
    </form>
  );
};