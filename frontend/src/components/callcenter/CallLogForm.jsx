import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getIncidents } from '../../api/incidentsAPI';
import { CustomerSearch } from '../customers/CustomerSearch';

export const CallLogForm = ({ onSubmit, onCancel, initialData = {} }) => {
  const [formData, setFormData] = useState({
    customer: '',
    incident: '',
    call_type: 'INBOUND',
    phone_number: '',
    notes: '',
    disposition: 'PENDING',
    is_resolved: false,
    follow_up_required: false,
    follow_up_date: '',
    ...initialData,
  });
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  // ─── Fetch incidents for dropdown ──────────────────────────
  const { data: incidents = [] } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => getIncidents({ page_size: 100 }).then(res => res.data.results || []),
    staleTime: 5 * 60 * 1000,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer);
    setFormData(prev => ({ ...prev, customer: customer.id, phone_number: customer.phone }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Customer</label>
        <CustomerSearch onSelect={handleCustomerSelect} />
        {selectedCustomer && (
          <p className="text-sm text-green-600 mt-1">Selected: {selectedCustomer.name}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Phone Number</label>
        <input
          type="text"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Incident (optional)</label>
        <select
          name="incident"
          value={formData.incident}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">None</option>
          {incidents.map(inc => (
            <option key={inc.id} value={inc.id}>{inc.incident_number} – {inc.title}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Call Type</label>
          <select
            name="call_type"
            value={formData.call_type}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="INBOUND">Inbound</option>
            <option value="OUTBOUND">Outbound</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Disposition</label>
          <select
            name="disposition"
            value={formData.disposition}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="PENDING">Pending</option>
            <option value="RESOLVED">Resolved</option>
            <option value="ESCALATED">Escalated</option>
            <option value="CALLBACK">Callback</option>
            <option value="NO_ANSWER">No Answer</option>
            <option value="VOICEMAIL">Voicemail</option>
            <option value="OTHER">Other</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Notes</label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows="3"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div className="flex items-center space-x-4">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            name="is_resolved"
            checked={formData.is_resolved}
            onChange={(e) => setFormData(prev => ({ ...prev, is_resolved: e.target.checked }))}
          />
          <span>Resolved</span>
        </label>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            name="follow_up_required"
            checked={formData.follow_up_required}
            onChange={(e) => setFormData(prev => ({ ...prev, follow_up_required: e.target.checked }))}
          />
          <span>Follow-up Required</span>
        </label>
      </div>

      {formData.follow_up_required && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Follow-up Date</label>
          <input
            type="datetime-local"
            name="follow_up_date"
            value={formData.follow_up_date}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      )}

      <div className="flex justify-end space-x-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 border rounded-md">Cancel</button>
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Save Call Log
        </button>
      </div>
    </form>
  );
};