import { useAuth } from '../../context/AuthContext';
import { AdminDashboard } from '../../components/dashboard/AdminDashboard';
import { AgentDashboard } from '../../components/dashboard/AgentDashboard';
import { ArtisanDashboard } from '../../components/dashboard/ArtisanDashboard';

export const DashboardPage = () => {
  const { user } = useAuth();

  if (user?.user_type === 'ADMIN' || user?.user_type === 'SUPERVISOR' || user?.user_type === 'MANAGER') {
    return <AdminDashboard />;
  }
  if (user?.user_type === 'AGENT') {
    return <AgentDashboard />;
  }
  if (user?.user_type === 'ARTISAN') {
    return <ArtisanDashboard />;
  }
  return (
    <div className="text-center py-8">
      <p>Welcome, {user?.full_name || 'User'}!</p>
      <p className="text-gray-500">Your dashboard will appear here.</p>
    </div>
  );
};