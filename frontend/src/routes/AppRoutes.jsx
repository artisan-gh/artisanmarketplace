import { Routes, Route } from 'react-router-dom';

// ─── Pages ────────────────────────────────────────────────
import { CustomersPage } from '../pages/Customers/CustomersPage';
import { CustomerNewPage } from '../pages/Customers/CustomerNewPage';
import { CustomerDetailPage } from '../pages/Customers/CustomerDetailPage';
import { IncidentsPage } from '../pages/Incidents/IncidentsPage';
import { IncidentNewPage } from '../pages/Incidents/IncidentNewPage';
import { IncidentDetailPage } from '../pages/Incidents/IncidentDetailPage';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* ─── Customers ──────────────────────────────────────── */}
      <Route path="/customers" element={<CustomersPage />} />
      <Route path="/customers/new" element={<CustomerNewPage />} />
      <Route path="/customers/:id" element={<CustomerDetailPage />} />
      <Route path="/customers/:id/edit" element={<CustomerNewPage />} /> {/* TODO: add edit mode */}

      {/* ─── Incidents ──────────────────────────────────────── */}
      <Route path="/incidents" element={<IncidentsPage />} />
      <Route path="/incidents/new" element={<IncidentNewPage />} />
      <Route path="/incidents/:id" element={<IncidentDetailPage />} />
      <Route path="/incidents/:id/edit" element={<IncidentNewPage />} /> {/* TODO: add edit mode */}

      {/* Additional routes for other phases will go here */}
    </Routes>
  );
};