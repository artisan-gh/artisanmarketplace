import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PrivateRoute } from './components/PrivateRoute';

// ─── Authentication ──────────────────────────────────────────
import Login from './pages/Login';
import Register from './pages/Register';

// ─── Dashboard Pages ─────────────────────────────────────────
import { AdminDashboardPage } from './pages/Dashboard/AdminDashboardPage';
import { AgentDashboardPage } from './pages/Dashboard/AgentDashboardPage';
import { ArtisanDashboardPage } from './pages/Dashboard/ArtisanDashboardPage';
import DispatchPage from './pages/Dashboard/DispatchPage';

// ─── Phase 1: Customers & Incidents ─────────────────────────
import { CustomersPage } from './pages/Customers/CustomersPage';
import { CustomerNewPage } from './pages/Customers/CustomerNewPage';
import { CustomerDetailPage } from './pages/Customers/CustomerDetailPage';
import { IncidentsPage } from './pages/Incidents/IncidentsPage';
import { IncidentNewPage } from './pages/Incidents/IncidentNewPage';
import { IncidentDetailPage } from './pages/Incidents/IncidentDetailPage';

// ─── Phase 2: Artisans & Assignments ────────────────────────
import { ArtisansPage } from './pages/Artisans/ArtisansPage';
import { ArtisanProfilePage } from './pages/Artisans/ArtisanProfilePage';
import { AssignmentsPage } from './pages/Assignments/AssignmentsPage';
import { AssignmentNewPage } from './pages/Assignments/AssignmentNewPage';
import { MyJobsPage } from './pages/Artisans/MyJobsPage';
import { JobDetailPage } from './pages/Artisans/JobDetailPage';

// ─── Phase 3: Call Center & Reports ─────────────────────────
import { CallLogsPage } from './pages/CallCenter/CallLogsPage';
import { CallLogNewPage } from './pages/CallCenter/CallLogNewPage';
import { CallLogDetailPage } from './pages/CallCenter/CallLogDetailPage';
import { IncidentReportPage } from './pages/Reports/IncidentReportPage';

// ─── Phase 4a: SLA ───────────────────────────────────────────
import { SLAPolicyListPage } from './pages/SLA/SLAPolicyListPage';
import { SLAPolicyFormPage } from './pages/SLA/SLAPolicyFormPage';
import { SLATrackerListPage } from './pages/SLA/SLATrackerListPage';

// ─── Phase 4b: Audit ─────────────────────────────────────────
import { AuditLogListPage } from './pages/Audit/AuditLogListPage';
import { AuditLogDetailPage } from './pages/Audit/AuditLogDetailPage';

// ─── Phase 4c: Billing ──────────────────────────────────────
import { InvoiceListPage } from './pages/Billing/InvoiceListPage';
import { InvoiceFormPage } from './pages/Billing/InvoiceFormPage';
import { InvoiceDetailPage } from './pages/Billing/InvoiceDetailPage';
import { PaymentListPage } from './pages/Billing/PaymentListPage';
import { PaymentDetailPage } from './pages/Billing/PaymentDetailPage';

// ─── Phase 4d: Notifications ────────────────────────────────
import { NotificationsPage } from './pages/Notifications/NotificationsPage';
import { NotificationDetailPage } from './pages/Notifications/NotificationDetailPage';


import { PaymentSuccess } from './pages/PaymentSuccess';
import { PaymentFailed } from './pages/PaymentFailed';

import { UserSettings } from './pages/UserSettings';

import { LandingPage } from './pages/LandingPage';

import { PublicInvoicePage } from './pages/PublicInvoicePage';

import { MyAssignments } from './components/assignments/MyAssignments';

import { ArtisanAgreementPage } from './pages/ArtisanAgreementPage';

import { About } from './pages/About';
import { Careers } from './pages/Careers';
import { Blog } from './pages/Blog';
import { Contact } from './pages/Contact';
import { HelpCenter } from './pages/HelpCenter';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TermsOfService } from './pages/TermsOfService';
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* ─── Public Routes ────────────────────────────────── */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/careers" element={<Careers />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/help" element={<HelpCenter />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/terms/artisan-agreement" element={<ArtisanAgreementPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* ─── Root ────────────────────────────────────────── */}
          {/* Remove or comment out the redirect line: */}
          {/* <Route path="/" element={<Navigate to="/dashboard" replace />} /> */}

          {/* ─── Dashboards ───────────────────────────────────── */}
          <Route path="/dashboard" element={<PrivateRoute><AdminDashboardPage /></PrivateRoute>} />
          <Route path="/admin/dashboard" element={<PrivateRoute><AdminDashboardPage /></PrivateRoute>} />
          <Route path="/agent/dashboard" element={<PrivateRoute><AgentDashboardPage /></PrivateRoute>} />
          <Route path="/artisan/dashboard" element={<PrivateRoute><ArtisanDashboardPage /></PrivateRoute>} />
          <Route path="/dispatch" element={<PrivateRoute><DispatchPage /></PrivateRoute>} />

          {/* ─── Customers ────────────────────────────────────── */}
          <Route path="/customers" element={<PrivateRoute><CustomersPage /></PrivateRoute>} />
          <Route path="/customers/new" element={<PrivateRoute><CustomerNewPage /></PrivateRoute>} />
          <Route path="/customers/:id" element={<PrivateRoute><CustomerDetailPage /></PrivateRoute>} />
          <Route path="/customers/:id/edit" element={<PrivateRoute><CustomerNewPage /></PrivateRoute>} />

          {/* ─── Incidents ────────────────────────────────────── */}
          <Route path="/incidents" element={<PrivateRoute><IncidentsPage /></PrivateRoute>} />
          <Route path="/incidents/new" element={<PrivateRoute><IncidentNewPage /></PrivateRoute>} />
          <Route path="/incidents/:id" element={<PrivateRoute><IncidentDetailPage /></PrivateRoute>} />
          <Route path="/incidents/:id/edit" element={<PrivateRoute><IncidentNewPage /></PrivateRoute>} />

          {/* ─── Artisans ─────────────────────────────────────── */}
          <Route path="/artisans" element={<PrivateRoute><ArtisansPage /></PrivateRoute>} />
          <Route path="/artisans/:id" element={<PrivateRoute><ArtisanProfilePage /></PrivateRoute>} />

          {/* ─── Assignments ──────────────────────────────────── */}
          <Route path="/assignments" element={<PrivateRoute><AssignmentsPage /></PrivateRoute>} />
          <Route path="/assignments/new/:incidentId" element={<PrivateRoute><AssignmentNewPage /></PrivateRoute>} />
          <Route path="/assignments/my" element={<MyAssignments />} />

          {/* ─── Artisan Jobs ─────────────────────────────────── */}
          <Route path="/my-jobs" element={<PrivateRoute><MyJobsPage /></PrivateRoute>} />
          <Route path="/jobs/:id" element={<PrivateRoute><JobDetailPage /></PrivateRoute>} />

          {/* ─── Call Center ──────────────────────────────────── */}
          <Route path="/call-center/logs" element={<PrivateRoute><CallLogsPage /></PrivateRoute>} />
          <Route path="/call-center/logs/new" element={<PrivateRoute><CallLogNewPage /></PrivateRoute>} />
          <Route path="/call-center/logs/:id" element={<PrivateRoute><CallLogDetailPage /></PrivateRoute>} />

          {/* ─── Reports ──────────────────────────────────────── */}
          <Route path="/reports/incidents" element={<PrivateRoute><IncidentReportPage /></PrivateRoute>} />

          {/* ─── SLA ──────────────────────────────────────────── */}
          <Route path="/sla/policies" element={<PrivateRoute><SLAPolicyListPage /></PrivateRoute>} />
          <Route path="/sla/policies/new" element={<PrivateRoute><SLAPolicyFormPage /></PrivateRoute>} />
          <Route path="/sla/policies/:id" element={<PrivateRoute><SLAPolicyFormPage /></PrivateRoute>} />
          <Route path="/sla/tracker" element={<PrivateRoute><SLATrackerListPage /></PrivateRoute>} />

          {/* ─── Audit ────────────────────────────────────────── */}
          <Route path="/audit/logs" element={<PrivateRoute><AuditLogListPage /></PrivateRoute>} />
          <Route path="/audit/logs/:id" element={<PrivateRoute><AuditLogDetailPage /></PrivateRoute>} />

          {/* ─── Billing ──────────────────────────────────────── */}
          <Route path="/billing/invoices" element={<PrivateRoute><InvoiceListPage /></PrivateRoute>} />
          <Route path="/billing/invoices/new" element={<PrivateRoute><InvoiceFormPage /></PrivateRoute>} />
          <Route path="/billing/invoices/:id" element={<PrivateRoute><InvoiceDetailPage /></PrivateRoute>} />
          <Route path="/billing/invoices/:id/edit" element={<PrivateRoute><InvoiceFormPage /></PrivateRoute>} />
          <Route path="/billing/payments" element={<PrivateRoute><PaymentListPage /></PrivateRoute>} />
          <Route path="/billing/payments/:id" element={<PrivateRoute><PaymentDetailPage /></PrivateRoute>} />

          {/* ─── Notifications ────────────────────────────────── */}
          <Route path="/notifications" element={<PrivateRoute><NotificationsPage /></PrivateRoute>} />
          <Route path="/notifications/:id" element={<PrivateRoute><NotificationDetailPage /></PrivateRoute>} />

          <Route path="/payment-success" element={<PaymentSuccess />} />
          <Route path="/payment-failed" element={<PaymentFailed />} />
          // Inside your route configuration:
          <Route path="/billing/invoices/public/:token" element={<PublicInvoicePage />} />


          {/* ─── Catch-all ────────────────────────────────────── */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />

          <Route path="/settings" element={<UserSettings />} />

          
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
