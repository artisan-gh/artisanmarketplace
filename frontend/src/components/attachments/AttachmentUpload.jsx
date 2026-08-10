import { useMutation, useQueryClient } from '@tanstack/react-query';
import PropTypes from 'prop-types';
import { createAttachment } from '../../api/attachmentsAPI';
import { FileUpload } from '../common/FileUpload';

export const AttachmentUpload = ({ incidentId, onUploadComplete }) => {
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (files) => {
      const formData = new FormData();
      formData.append('incident', incidentId);
      for (const file of files) {
        formData.append('file', file);
        formData.append('filename', file.name);
      }
      return createAttachment(formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attachments', incidentId] });
      if (onUploadComplete) onUploadComplete();
    },
    onError: () => {
      alert('Failed to upload file.');
    },
  });

  return (
    <div>
      <FileUpload onUpload={uploadMutation.mutate} multiple accept="*/*" />
      {uploadMutation.isPending && <p className="text-sm text-blue-600 mt-2">Uploading...</p>}
    </div>
  );
};

AttachmentUpload.propTypes = {
  incidentId: PropTypes.string.isRequired,
  onUploadComplete: PropTypes.func,
};