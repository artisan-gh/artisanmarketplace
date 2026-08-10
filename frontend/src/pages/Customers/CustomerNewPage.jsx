import { useNavigate } from 'react-router-dom';
import { CustomerForm } from '../../components/customers/CustomerForm';
import { createCustomer } from '../../api/customersAPI';

export const CustomerNewPage = () => {
  const navigate = useNavigate();

  const handleSubmit = async (data) => {
    const res = await createCustomer(data);
    navigate(`/customers/${res.data.id}`);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">New Customer</h1>
      <CustomerForm onSubmit={handleSubmit} onCancel={() => navigate('/customers')} />
    </div>
  );
};