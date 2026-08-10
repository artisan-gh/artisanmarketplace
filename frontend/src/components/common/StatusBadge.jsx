import PropTypes from 'prop-types';

const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  deleted: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  resolved: 'bg-blue-100 text-blue-800',
  closed: 'bg-gray-100 text-gray-800',
  assigned: 'bg-purple-100 text-purple-800',
  in_progress: 'bg-indigo-100 text-indigo-800',
  new: 'bg-green-100 text-green-800',
  open: 'bg-blue-100 text-blue-800',
  accepted: 'bg-purple-100 text-purple-800',
  en_route: 'bg-yellow-100 text-yellow-800',
  on_site: 'bg-orange-100 text-orange-800',
  work_in_progress: 'bg-indigo-100 text-indigo-800',
  pending_parts: 'bg-pink-100 text-pink-800',
  escalated: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

export const StatusBadge = ({ status, children }) => {
  const color = statusColors[status?.toLowerCase()] || 'bg-gray-100 text-gray-800';
  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${color}`}>
      {children || status}
    </span>
  );
};

StatusBadge.propTypes = {
  status: PropTypes.string,
  children: PropTypes.node,
};