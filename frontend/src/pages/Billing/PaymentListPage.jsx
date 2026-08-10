import { PaymentList } from '../../components/billing/PaymentList';

export const PaymentListPage = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-2xl font-bold mb-4">Payments</h1>
    <PaymentList />
  </div>
);