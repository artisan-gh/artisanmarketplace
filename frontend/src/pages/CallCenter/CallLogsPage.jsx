import { useNavigate } from 'react-router-dom';
import { CallLogList } from '../../components/callcenter/CallLogList';

export const CallLogsPage = () => {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Call Logs</h1>
        <button
          onClick={() => navigate('/call-center/logs/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          New Call Log
        </button>
      </div>
      <CallLogList />
    </div>
  );
};