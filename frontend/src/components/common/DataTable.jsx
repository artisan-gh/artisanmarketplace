import PropTypes from 'prop-types';

export const DataTable = ({
  columns,
  data,
  loading = false,
  pagination,
  onRowClick,
}) => {
  return (
    <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="px-3 py-4 text-center text-sm text-gray-500">
                Loading...
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-3 py-4 text-center text-sm text-gray-500">
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={row.id || idx}
                onClick={() => onRowClick && onRowClick(row)}
                className={onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-3 py-4 text-sm text-gray-900">
                    {col.render ? col.render(row[col.key], row) : row[col.key] || '—'}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
      {pagination && (
        <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center text-sm text-gray-700">
            Showing {pagination.total === 0 ? 0 : (pagination.current - 1) * pagination.pageSize + 1} to{' '}
            {Math.min(pagination.current * pagination.pageSize, pagination.total)} of {pagination.total} results
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => pagination.onPageChange(pagination.current - 1)}
              disabled={pagination.current <= 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => pagination.onPageChange(pagination.current + 1)}
              disabled={pagination.current * pagination.pageSize >= pagination.total}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

DataTable.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      render: PropTypes.func,
    })
  ).isRequired,
  data: PropTypes.array.isRequired,
  loading: PropTypes.bool,
  pagination: PropTypes.shape({
    current: PropTypes.number,
    pageSize: PropTypes.number,
    total: PropTypes.number,
    onPageChange: PropTypes.func,
    onPageSizeChange: PropTypes.func,
  }),
  onRowClick: PropTypes.func,
};