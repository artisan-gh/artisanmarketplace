import { AssignmentList } from '../../components/assignments/AssignmentList';

export const AssignmentsPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Assignments</h1>
      </div>
      <AssignmentList />
    </div>
  );
};