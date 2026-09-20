
import api from './client';

export const listMyInvoices = () => api.get('/client/invoices/').then(r => r.data);
export const getMyInvoice = (id) => api.get(`/client/invoices/${id}/`).then(r => r.data);
export const payMyInvoice = (id, payload = {}) =>
  api.post(`/client/invoices/${id}/pay/`, payload).then(r => r.data);
export const getPublicInvoice = (token) =>
  api.get(`/client/invoices/public/${token}/`).then(r => r.data);
export const payPublicInvoice = (token, payload = {}) =>
  api.post(`/client/invoices/public/${token}/pay/`, payload).then(r => r.data);
