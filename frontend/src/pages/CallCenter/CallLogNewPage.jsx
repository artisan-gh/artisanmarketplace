import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createCallLog } from '../../api/call_centerAPI';
import { CallLogForm } from '../../components/callcenter/CallLogForm';

export const CallLogNewPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createCallLog,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['callLogs'] });
      navigate('/call-center/logs');
    },
  });

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">New Call Log</h1>
      <CallLogForm
        onSubmit={mutation.mutate}
        onCancel={() => navigate('/call-center/logs')}
      />
    </div>
  );
};