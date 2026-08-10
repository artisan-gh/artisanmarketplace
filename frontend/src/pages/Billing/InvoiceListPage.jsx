import { InvoiceList } from '../../components/billing/InvoiceList';

export const InvoiceListPage = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-2xl font-bold mb-4">Invoices</h1>
    <InvoiceList />
  </div>
);