import { useState } from 'react';
import PropTypes from 'prop-types';
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from '../../hooks/useDebounce';
import { searchCustomers } from '../../api/customersAPI';
import { SearchBar } from '../common/SearchBar';

export const CustomerSearch = ({ onSelect, onNewCustomer }) => {
  const [query, setQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const debouncedQuery = useDebounce(query, 400);

  // ─── Handle input change: update query & show results ──
  const handleInputChange = (value) => {
    setQuery(value);
    setShowResults(value.length >= 2);
  };

  // ─── Fetch search results with React Query ───────────────
  const {
    data: results = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['customerSearch', debouncedQuery],
    queryFn: () =>
      searchCustomers(debouncedQuery).then((res) => res.data.results || []),
    enabled: debouncedQuery.length >= 2,
    staleTime: 2 * 60 * 1000,
  });

  const showResultsDropdown = showResults && debouncedQuery.length >= 2;

  const handleSelect = (customer) => {
    setQuery(customer.name);
    setShowResults(false);
    if (onSelect) onSelect(customer);
  };

  const handleNewCustomer = () => {
    setShowResults(false);
    if (onNewCustomer) onNewCustomer(query);
  };

  const handleBlur = () => {
    setTimeout(() => setShowResults(false), 200);
  };

  const handleFocus = () => {
    if (debouncedQuery.length >= 2) {
      setShowResults(true);
    }
  };

  return (
    <div className="relative w-full">
      <SearchBar
        value={query}
        onChange={handleInputChange}
        placeholder="Search customer by name or phone..."
        className="w-full"
        onFocus={handleFocus}
        onBlur={handleBlur}
      />

      {isLoading && (
        <div className="absolute right-3 top-3 text-sm text-gray-500">Loading...</div>
      )}

      {isError && (
        <div className="absolute right-3 top-3 text-sm text-red-500">Error searching</div>
      )}

      {showResultsDropdown && results.length > 0 && (
        <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {results.map((cust) => (
            <li
              key={cust.id}
              className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex justify-between"
              onClick={() => handleSelect(cust)}
            >
              <span>{cust.name}</span>
              <span className="text-sm text-gray-500">{cust.phone}</span>
            </li>
          ))}
        </ul>
      )}

      {showResultsDropdown && results.length === 0 && !isLoading && !isError && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-2 text-center text-gray-500">
          No customers found.{' '}
          <button
            type="button"
            className="text-blue-600 hover:underline"
            onClick={handleNewCustomer}
          >
            Create new customer "{query}"
          </button>
        </div>
      )}
    </div>
  );
};

CustomerSearch.propTypes = {
  onSelect: PropTypes.func,
  onNewCustomer: PropTypes.func,
};