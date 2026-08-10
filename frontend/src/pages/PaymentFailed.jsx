// src/pages/PaymentFailed.jsx
import { useSearchParams, Link } from 'react-router-dom';

export const PaymentFailed = () => {
  const [searchParams] = useSearchParams();
  const error = searchParams.get('error') || 'Something went wrong. Please try again.';
  const status = searchParams.get('status') || '';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-rose-100 px-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center">
        {/* Error Icon */}
        <div className="mb-4 flex justify-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        </div>

        <h1 className="text-2xl font-bold text-gray-800 mb-2">Payment Failed</h1>
        <p className="text-gray-600 mb-4">{error}</p>

        {status && (
          <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-500">
            <span>Status: </span>
            <span className="capitalize font-medium text-red-600">{status}</span>
          </div>
        )}

        <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/billing/invoices"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Try Again
          </Link>
          <Link
            to="/support"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
          >
            Contact Support
          </Link>
        </div>
      </div>
    </div>
  );
};