// src/pages/Audit/AuditLogListPage.jsx
import { AuditLogList } from '../../components/audit/AuditLogList';

export const AuditLogListPage = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-2xl font-bold mb-4">Audit Logs</h1>
    <AuditLogList />
  </div>
);