import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getArtisan, getArtisanAvailability, setArtisanAvailability } from '../../api/artisansAPI';
import { StatusBadge } from '../common/StatusBadge';

export const ArtisanProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // ─── Fetch artisan profile ──────────────────────────────
  const {
    data: artisan,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['artisan', id],
    queryFn: () => getArtisan(id).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });

  // ─── Fetch availability ──────────────────────────────────
  const {
    data: availability = [],
    isLoading: loadingAvailability,
  } = useQuery({
    queryKey: ['artisanAvailability', id],
    queryFn: () => getArtisanAvailability(id).then((res) => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  // ─── Update availability ─────────────────────────────────
  const mutation = useMutation({
    mutationFn: (data) => setArtisanAvailability(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['artisanAvailability', id] });
    },
    onError: () => {
      alert('Failed to update availability.');
    },
  });

  const handleAvailabilityChange = (day, field, value) => {
    const existing = availability.find((a) => a.day_of_week === day);
    const data = {
      day_of_week: day,
      start_time: existing?.start_time || '09:00',
      end_time: existing?.end_time || '17:00',
      is_working: existing?.is_working !== undefined ? existing.is_working : true,
      ...(field === 'is_working' ? { is_working: value } : {}),
      ...(field === 'start_time' ? { start_time: value } : {}),
      ...(field === 'end_time' ? { end_time: value } : {}),
    };
    mutation.mutate(data);
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-red-500">Failed to load artisan.</div>;
  if (!artisan) return <div className="text-center py-8">Artisan not found.</div>;

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold">{artisan.user_detail?.full_name}</h1>
          <p className="text-gray-600">{artisan.user_detail?.email}</p>
          <div className="flex space-x-2 mt-2">
            <StatusBadge status={artisan.is_available ? 'active' : 'inactive'}>
              {artisan.is_available ? 'Available' : 'Busy'}
            </StatusBadge>
            <span className="text-sm text-gray-500">
              Rating: {artisan.average_rating > 0 ? `${artisan.average_rating.toFixed(1)} ★` : 'No ratings'}
            </span>
          </div>
        </div>
        <button
          onClick={() => navigate('/artisans')}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-700">Skills</h3>
          <div className="flex flex-wrap gap-2 mt-2">
            {artisan.skills_list?.length > 0 ? (
              artisan.skills_list.map((skill) => (
                <span
                  key={skill.id}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                >
                  {skill.name}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-500">No skills listed</span>
            )}
          </div>
          <div className="mt-4">
            <p className="text-sm"><strong>Max Concurrent Jobs:</strong> {artisan.max_concurrent_jobs}</p>
            <p className="text-sm"><strong>Current Workload:</strong> {artisan.current_workload || 0}</p>
            <p className="text-sm"><strong>Hire Date:</strong> {artisan.hire_date ? new Date(artisan.hire_date).toLocaleDateString() : '—'}</p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-700">Availability Schedule</h3>
          {loadingAvailability ? (
            <p className="text-sm text-gray-500">Loading...</p>
          ) : (
            <div className="mt-2 space-y-3">
              {days.map((day, idx) => {
                const entry = availability.find((a) => a.day_of_week === idx);
                const isWorking = entry?.is_working !== undefined ? entry.is_working : true;
                const start = entry?.start_time || '09:00';
                const end = entry?.end_time || '17:00';

                return (
                  <div key={day} className="flex items-center gap-2">
                    <span className="w-24 text-sm font-medium text-gray-700">{day}</span>
                    <label className="flex items-center gap-1 text-sm">
                      <input
                        type="checkbox"
                        checked={isWorking}
                        onChange={(e) =>
                          handleAvailabilityChange(idx, 'is_working', e.target.checked)
                        }
                        className="rounded"
                      />
                      Working
                    </label>
                    <input
                      type="time"
                      value={start}
                      onChange={(e) =>
                        handleAvailabilityChange(idx, 'start_time', e.target.value)
                      }
                      disabled={!isWorking}
                      className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50"
                    />
                    <span className="text-sm">to</span>
                    <input
                      type="time"
                      value={end}
                      onChange={(e) =>
                        handleAvailabilityChange(idx, 'end_time', e.target.value)
                      }
                      disabled={!isWorking}
                      className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50"
                    />
                    {mutation.isPending && <span className="text-xs text-blue-500">Saving...</span>}
                  </div>
                );
              })}
            </div>
          )}
          <p className="text-xs text-gray-500 mt-2">Toggle "Working" to set availability. Times are in your local timezone.</p>
        </div>
      </div>
    </div>
  );
};