// src/components/billing/InvoiceForm.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getInvoice, createInvoice, updateInvoice } from '../../api/billingAPI';
import { getCustomers } from '../../api/customersAPI';
import './InvoiceForm.css';

export const InvoiceForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = Boolean(id);

  const { data: invoice, isLoading: invoiceLoading } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => getInvoice(id).then((res) => res.data),
    enabled: isEditing,
    staleTime: 5 * 60 * 1000,
  });

  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => getCustomers({ page_size: 100 }).then((res) => res.data.results || []),
    staleTime: 5 * 60 * 1000,
  });

  // ─── Form state ──────────────────────────────────────────────
  const [formData, setFormData] = useState(() => {
    const today = new Date();
    const due = new Date(today.getTime() + 14 * 24 * 60 * 60 * 1000);
    return {
      customer: '',
      invoice_date: today.toISOString().split('T')[0],
      due_date: due.toISOString().split('T')[0],
      status: 'draft',
      items: [{ description: '', quantity: 1, unit_price: 0, tax_rate: 0 }],
      discount: 0,
      notes: '',
      purchased_items: [],
      transport_cost: 0, // <-- NEW
    };
  });

  // ─── Populate form when editing ──────────────────────────────
  useEffect(() => {
    if (invoice) {
      /* eslint-disable-next-line react-hooks/set-state-in-effect */
      setFormData({
        customer: invoice.customer?.id || '',
        invoice_date: invoice.invoice_date?.split('T')[0] || '',
        due_date: invoice.due_date?.split('T')[0] || '',
        status: invoice.status || 'draft',
        items: invoice.items || [{ description: '', quantity: 1, unit_price: 0, tax_rate: 0 }],
        discount: invoice.discount || 0,
        notes: invoice.notes || '',
        purchased_items: invoice.purchased_items || [],
        transport_cost: invoice.transport_cost || 0, // <-- load
      });
    }
  }, [invoice]);

  const mutation = useMutation({
    mutationFn: (data) => (isEditing ? updateInvoice(id, data) : createInvoice(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      navigate('/billing/invoices');
    },
  });

  // ─── Handlers ──────────────────────────────────────────────────
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // ─── Line items ────────────────────────────────────────────────
  const handleItemChange = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      items: prev.items.map((item, i) => (i === index ? { ...item, [field]: value } : item)),
    }));
  };

  const addItem = () => {
    setFormData((prev) => ({
      ...prev,
      items: [...prev.items, { description: '', quantity: 1, unit_price: 0, tax_rate: 0 }],
    }));
  };

  const removeItem = (index) => {
    setFormData((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }));
  };

  // ─── Materials (purchased_items) ──────────────────────────────
  const handleMaterialChange = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      purchased_items: prev.purchased_items.map((mat, i) =>
        i === index ? { ...mat, [field]: value } : mat
      ),
    }));
  };

  const addMaterial = () => {
    setFormData((prev) => ({
      ...prev,
      purchased_items: [...prev.purchased_items, { description: '', quantity: 1, unit_cost: 0 }],
    }));
  };

  const removeMaterial = (index) => {
    setFormData((prev) => ({
      ...prev,
      purchased_items: prev.purchased_items.filter((_, i) => i !== index),
    }));
  };

  // ─── Calculations ──────────────────────────────────────────────
  const calculateSubtotal = () =>
    formData.items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);

  const calculateTax = () =>
    formData.items.reduce((sum, item) => sum + item.quantity * item.unit_price * (item.tax_rate / 100), 0);

  const calculateMaterialsTotal = () =>
    formData.purchased_items.reduce((sum, mat) => sum + mat.quantity * mat.unit_cost, 0);

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const tax = calculateTax();
    const discount = parseFloat(formData.discount) || 0;
    const materials = calculateMaterialsTotal();
    const transport = parseFloat(formData.transport_cost) || 0;
    return subtotal + tax - discount + materials + transport;
  };

  // ─── Submit ────────────────────────────────────────────────────
  const handleSubmit = (e) => {
    e.preventDefault();
    const subtotal = calculateSubtotal();
    const tax = calculateTax();
    const discount = parseFloat(formData.discount) || 0;
    const materialsTotal = calculateMaterialsTotal();
    const transportCost = parseFloat(formData.transport_cost) || 0;
    const grandTotal = subtotal + tax - discount + materialsTotal + transportCost;

    const payload = {
      ...formData,
      subtotal,
      tax_amount: tax,
      discount_amount: discount,
      grand_total: grandTotal,
      transport_cost: transportCost, // <-- include
    };
    mutation.mutate(payload);
  };

  if (invoiceLoading) return <div className="invoice-form__loading">Loading invoice…</div>;

  return (
    <form onSubmit={handleSubmit} className="invoice-form">
      <div className="invoice-form__header">
        <div>
          <h2 className="invoice-form__title">{isEditing ? 'Edit Invoice' : 'New Invoice'}</h2>
          <p className="invoice-form__subtitle">
            {isEditing ? 'Update the details below and save your changes.' : 'Fill in the details to create a new invoice.'}
          </p>
        </div>
      </div>

      {/* ─── Customer & Dates ────────────────────────────────── */}
      <div className="form-section">
        <h3 className="form-section__title">Details</h3>
        <div className="form-grid">
          <div className="field">
            <label htmlFor="customer">
              Customer<span className="required">*</span>
            </label>
            <select id="customer" name="customer" value={formData.customer} onChange={handleChange} required>
              <option value="">Select customer</option>
              {customers?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="status">Status</label>
            <select id="status" name="status" value={formData.status} onChange={handleChange}>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="paid">Paid</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="invoice_date">Invoice Date</label>
            <input
              id="invoice_date"
              type="date"
              name="invoice_date"
              value={formData.invoice_date}
              onChange={handleChange}
            />
          </div>
          <div className="field">
            <label htmlFor="due_date">Due Date</label>
            <input id="due_date" type="date" name="due_date" value={formData.due_date} onChange={handleChange} />
          </div>
        </div>
      </div>

      {/* ─── Line Items ──────────────────────────────────────── */}
      <div className="form-section">
        <h3 className="form-section__title">Labour Charges</h3>
        <div className="line-items">
          <div className="line-items__head">
            <span>Description</span>
            <span>Qty</span>
            <span>Unit price</span>
            <span>Tax %</span>
            <span />
          </div>
          {formData.items.map((item, index) => (
            <div key={index} className="line-item-row">
              <input
                type="text"
                placeholder="Description"
                value={item.description}
                onChange={(e) => handleItemChange(index, 'description', e.target.value)}
              />
              <input
                type="number"
                placeholder="Qty"
                value={item.quantity}
                onChange={(e) => handleItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                min="1"
              />
              <input
                type="number"
                placeholder="0.00"
                value={item.unit_price}
                onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                min="0"
                step="0.01"
              />
              <input
                type="number"
                placeholder="0.00"
                value={item.tax_rate}
                onChange={(e) => handleItemChange(index, 'tax_rate', parseFloat(e.target.value) || 0)}
                min="0"
                step="0.01"
              />
              {formData.items.length > 1 ? (
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="line-item-row__remove"
                  aria-label="Remove line item"
                >
                  ×
                </button>
              ) : (
                <span />
              )}
            </div>
          ))}
        </div>
        <button type="button" onClick={addItem} className="add-item-btn">
          + Add line item
        </button>
      </div>

      {/* ─── Materials & Supplies (purchased on behalf) ────── */}
      <div className="form-section">
        <h3 className="form-section__title">Materials &amp; supplies purchased</h3>
        <p className="form-section__subtitle">
          Items bought on the customer’s behalf, added to the invoice total.
        </p>
        <div className="materials-list">
          <div className="materials-head">
            <span>Description</span>
            <span>Qty</span>
            <span>Unit cost</span>
            <span>Total cost</span>
            <span />
          </div>
          {formData.purchased_items.map((mat, index) => {
            const total = mat.quantity * mat.unit_cost;
            return (
              <div key={index} className="material-row">
                <input
                  type="text"
                  placeholder="Material description"
                  value={mat.description}
                  onChange={(e) => handleMaterialChange(index, 'description', e.target.value)}
                />
                <input
                  type="number"
                  placeholder="Qty"
                  value={mat.quantity}
                  onChange={(e) => handleMaterialChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                  min="1"
                />
                <input
                  type="number"
                  placeholder="0.00"
                  value={mat.unit_cost}
                  onChange={(e) => handleMaterialChange(index, 'unit_cost', parseFloat(e.target.value) || 0)}
                  min="0"
                  step="0.01"
                />
                <span className="material-total">{isNaN(total) ? '₵0.00' : `₵${total.toFixed(2)}`}</span>
                <button
                  type="button"
                  onClick={() => removeMaterial(index)}
                  className="material-remove"
                  aria-label="Remove material"
                >
                  ×
                </button>
              </div>
            );
          })}
        </div>
        <button type="button" onClick={addMaterial} className="add-item-btn">
          + Add material
        </button>
      </div>

      {/* ─── Totals ───────────────────────────────────────────── */}
      <div className="form-section">
        <div className="form-grid">
          <div className="field">
            <label htmlFor="discount">Discount</label>
            <input
              id="discount"
              type="number"
              name="discount"
              value={formData.discount}
              onChange={handleChange}
              min="0"
              step="0.01"
            />
          </div>
          <div className="field">
            <label htmlFor="transport_cost">Transport / Delivery cost</label>
            <input
              id="transport_cost"
              type="number"
              name="transport_cost"
              value={formData.transport_cost}
              onChange={handleChange}
              min="0"
              step="0.01"
            />
          </div>
          <div className="totals-panel">
            <div className="totals-row">
              <span>Subtotal</span>
              <span>₵{calculateSubtotal().toFixed(2)}</span>
            </div>
            <div className="totals-row">
              <span>Tax</span>
              <span>₵{calculateTax().toFixed(2)}</span>
            </div>
            {parseFloat(formData.discount) > 0 && (
              <div className="totals-row totals-row--discount">
                <span>Discount</span>
                <span>- ₵{parseFloat(formData.discount).toFixed(2)}</span>
              </div>
            )}
            {formData.purchased_items.length > 0 && calculateMaterialsTotal() > 0 && (
              <div className="totals-row totals-row--materials">
                <span>Materials &amp; supplies</span>
                <span>₵{calculateMaterialsTotal().toFixed(2)}</span>
              </div>
            )}
            {parseFloat(formData.transport_cost) > 0 && (
              <div className="totals-row totals-row--transport">
                <span>Transport</span>
                <span>₵{parseFloat(formData.transport_cost).toFixed(2)}</span>
              </div>
            )}
            <div className="totals-row totals-row--total">
              <span>Total</span>
              <span>₵{calculateTotal().toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ─── Notes ────────────────────────────────────────────── */}
      <div className="form-section">
        <div className="field">
          <label htmlFor="notes">Notes</label>
          <textarea id="notes" name="notes" value={formData.notes} onChange={handleChange} rows="3" />
        </div>
      </div>

      {/* ─── Buttons ──────────────────────────────────────────── */}
      <div className="invoice-form__actions">
        <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
          {mutation.isPending ? 'Saving…' : isEditing ? 'Update' : 'Create'}
        </button>
        <button type="button" onClick={() => navigate('/billing/invoices')} className="btn btn-secondary">
          Cancel
        </button>
      </div>
    </form>
  );
};