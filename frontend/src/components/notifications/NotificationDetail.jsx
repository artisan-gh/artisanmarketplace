// src/components/notifications/NotificationDetail.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getNotification, markNotificationRead } from '../../api/notificationsAPI';
import { StatusBadge } from '../common/StatusBadge';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';

export const NotificationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: notification, isLoading } = useQuery({
    queryKey: ['notification', id],
    queryFn: () => getNotification(id).then((res) => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  const markReadMutation = useMutation({
    mutationFn: () => markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification', id] });
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['unreadCount'] });
    },
  });

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (!notification) return <div className="text-center py-8 text-red-500">Notification not found.</div>;

  const typeColorMap = {
    ASSIGNMENT: 'info',
    STATUS_UPDATE: 'warning',
    ESCALATION: 'error',
    REMINDER: 'default',
    INCIDENT_CREATED: 'success',
    SLA_BREACHED: 'error',
    PAYMENT_RECEIVED: 'success',
    INVOICE_SENT: 'info',
    GENERAL: 'default',
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold">Notification</h1>
          <div className="flex items-center gap-2 mt-1">
            <StatusBadge status={typeColorMap[notification.notification_type] || 'default'}>
              {notification.notification_type}
            </StatusBadge>
            {!notification.is_read && (
              <span className="text-xs text-blue-600 font-medium">● Unread</span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {!notification.is_read && (
            <button
              onClick={() => markReadMutation.mutate()}
              disabled={markReadMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {markReadMutation.isPending ? 'Marking...' : 'Mark as Read'}
            </button>
          )}
          <button
            onClick={() => navigate('/notifications')}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Back
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <div>
          <p><strong>Subject:</strong> {notification.subject}</p>
          <p><strong>Message:</strong> {notification.message}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p><strong>Channel:</strong> {notification.channel}</p>
            <p><strong>Sent:</strong> {format(new Date(notification.sent_at), 'PPpp')}</p>
            {notification.read_at && (
              <p><strong>Read:</strong> {format(new Date(notification.read_at), 'PPpp')}</p>
            )}
          </div>
          <div>
            {notification.incident && (
              <p>
                <strong>Incident:</strong>{' '}
                <Link to={`/incidents/${notification.incident}`} className="text-blue-600 hover:underline">
                  {notification.incident_number || notification.incident}
                </Link>
              </p>
            )}
            {notification.assignment && (
              <p>
                <strong>Assignment:</strong>{' '}
                <Link to={`/assignments/${notification.assignment}`} className="text-blue-600 hover:underline">
                  {notification.assignment_id || notification.assignment}
                </Link>
              </p>
            )}
          </div>
        </div>

        {notification.data && Object.keys(notification.data).length > 0 && (
          <div>
            <p><strong>Metadata:</strong></p>
            <pre className="bg-gray-100 p-3 rounded-md text-sm overflow-auto">
              {JSON.stringify(notification.data, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};