// src/components/audit/AuditLogDetail.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAuditLog } from '../../api/auditAPI';
import { format } from 'date-fns';

export const AuditLogDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: log, isLoading, error } = useQuery({
    queryKey: ['auditLog', id],
    queryFn: () => getAuditLog(id).then((res) => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error || !log) return <div className="text-center py-8 text-red-500">Log not found.</div>;

  const formatDate = (date) => (date ? format(new Date(date), 'PPpp') : '—');

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex justify-between items-start mb-6">
        <h1 className="text-2xl font-bold">Audit Log</h1>
        <button
          onClick={() => navigate('/audit/logs')}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Back
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p><strong>ID:</strong> {log.id}</p>
            <p><strong>Timestamp:</strong> {formatDate(log.timestamp)}</p>
            <p><strong>User:</strong> {log.user_email || log.user || 'System'}</p>
            <p><strong>Action:</strong> {log.action}</p>
          </div>
          <div>
            <p><strong>Object Type:</strong> {log.object_type}</p>
            <p><strong>Object:</strong> {log.object_repr || '—'}</p>
            <p><strong>Object ID:</strong> {log.object_id || '—'}</p>
          </div>
        </div>

        {log.changes && (
          <div>
            <p><strong>Changes:</strong></p>
            <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-auto">
              {typeof log.changes === 'string'
                ? JSON.stringify(JSON.parse(log.changes), null, 2)
                : JSON.stringify(log.changes, null, 2)}
            </pre>
          </div>
        )}

        {log.ip_address && (
          <div>
            <p><strong>IP Address:</strong> {log.ip_address}</p>
          </div>
        )}
      </div>
    </div>
  );
};