import { IncidentReport } from '../../components/reports/IncidentReport';

export const IncidentReportPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Incident Report</h1>
      <IncidentReport />
    </div>
  );
};