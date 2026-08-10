import { useState, useRef } from 'react';
import PropTypes from 'prop-types';

export const FileUpload = ({ onUpload, accept = '*/*', multiple = false, maxSize = 5 * 1024 * 1024 }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleFiles = (selectedFiles) => {
    const validFiles = Array.from(selectedFiles).filter(
      (file) => file.size <= maxSize
    );
    if (validFiles.length < selectedFiles.length) {
      alert(`Some files exceed the ${maxSize / 1024 / 1024}MB limit and were skipped.`);
    }
    setFiles(validFiles);
    if (onUpload) onUpload(validFiles);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 text-center ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleChange}
        className="hidden"
      />
      <div className="space-y-2">
        <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p className="text-sm text-gray-600">
          Drag and drop files here, or{' '}
          <button
            type="button"
            className="text-blue-600 hover:underline"
            onClick={() => fileInputRef.current?.click()}
          >
            browse
          </button>
        </p>
        <p className="text-xs text-gray-500">
          Max file size: {maxSize / 1024 / 1024}MB
        </p>
        {files.length > 0 && (
          <div className="mt-2 text-left">
            {files.map((file) => (
              <div key={file.name} className="text-sm text-gray-700">
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

FileUpload.propTypes = {
  onUpload: PropTypes.func,
  accept: PropTypes.string,
  multiple: PropTypes.bool,
  maxSize: PropTypes.number,
};