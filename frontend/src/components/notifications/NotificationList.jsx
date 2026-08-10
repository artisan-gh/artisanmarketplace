// src/components/notifications/NotificationList.jsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  getUnreadCount,
} from '../../api/notificationsAPI';
import { StatusBadge } from '../common/StatusBadge';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';

export const NotificationList = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // ─── Fetch notifications ────────────────────────────────────
  const { data, isLoading } = useQuery({
    queryKey: ['notifications', { page, pageSize }],
    queryFn: () =>
      getNotifications({ page, page_size: pageSize }).then((res) => res.data),
    staleTime: 2 * 60 * 1000,
  });

  // ─── Fetch unread count ─────────────────────────────────────
  const { data: unreadData, refetch: refetchUnread } = useQuery({
    queryKey: ['unreadCount'],
    queryFn: () => getUnreadCount().then((res) => res.data),
    staleTime: 30 * 1000,
  });

  // ─── Mark as read mutation ──────────────────────────────────
  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      refetchUnread();
    },
  });

  // ─── Mark all read mutation ─────────────────────────────────
  const markAllReadMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      refetchUnread();
    },
  });

  const notifications = data?.results || [];
  const total = data?.count || 0;
  const unreadCount = unreadData?.unread_count || 0;

  const getTypeColor = (type) => {
    const map = {
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
    return map[type] || 'default';
  };

  // ─── Reset to page 1 when page size changes ────────────────
  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setPage(1);
  };

  if (isLoading) return <div className="text-center py-8">Loading notifications...</div>;

  return (
    <div>
      {/* ─── Header ────────────────────────────────────────────── */}
      <div className="flex flex-wrap justify-between items-center gap-3 mb-4">
        <div>
          <h1 className="text-2xl font-bold">Notifications</h1>
          {unreadCount > 0 && (
            <span className="text-sm text-gray-500">{unreadCount} unread</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Show:</label>
            <select
              value={pageSize}
              onChange={handlePageSizeChange}
              className="px-2 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <button
            onClick={() => markAllReadMutation.mutate()}
            disabled={unreadCount === 0 || markAllReadMutation.isPending}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {markAllReadMutation.isPending ? 'Marking...' : 'Mark All as Read'}
          </button>
        </div>
      </div>

      {/* ─── List ──────────────────────────────────────────────── */}
      {notifications.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No notifications.</div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {notifications.map((notification) => (
            <li
              key={notification.id}
              className={`py-4 ${!notification.is_read ? 'bg-blue-50' : ''}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <StatusBadge status={getTypeColor(notification.notification_type)}>
                      {notification.notification_type}
                    </StatusBadge>
                    {!notification.is_read && (
                      <span className="text-xs text-blue-600 font-medium">● New</span>
                    )}
                  </div>
                  <p className="font-medium text-gray-900">{notification.subject}</p>
                  <p className="text-sm text-gray-600">{notification.message}</p>
                  {notification.incident_number && (
                    <Link
                      to={`/incidents/${notification.incident}`}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      View Incident #{notification.incident_number}
                    </Link>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDistanceToNow(new Date(notification.sent_at), { addSuffix: true })}
                  </p>
                </div>
                <div className="flex gap-2 ml-4">
                  {!notification.is_read && (
                    <button
                      onClick={() => markReadMutation.mutate(notification.id)}
                      disabled={markReadMutation.isPending}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Mark read
                    </button>
                  )}
                  <Link
                    to={`/notifications/${notification.id}`}
                    className="text-xs text-gray-500 hover:underline"
                  >
                    Details
                  </Link>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* ─── Pagination ────────────────────────────────────────── */}
      {total > pageSize && (
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 border rounded-md disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {page} of {Math.ceil(total / pageSize)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * pageSize >= total}
            className="px-3 py-1 border rounded-md disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};