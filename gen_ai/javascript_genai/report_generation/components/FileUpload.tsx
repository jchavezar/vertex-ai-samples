
import React, { useRef, useState, useCallback } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, disabled }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const handleDrag = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled) return;
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, [disabled]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled) return;
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect, disabled]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`w-full p-6 py-8 border-2 border-dashed rounded-lg transition-colors duration-200 cursor-pointer
                  ${disabled ? 'border-dj-light-gray bg-dj-light-gray/30 cursor-not-allowed' : 
                               dragActive ? 'border-dj-blue bg-dj-blue/10' : 'border-dj-blue hover:bg-dj-blue/5'}`}
      onClick={!disabled ? openFileDialog : undefined}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={!disabled ? handleDrop : undefined}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="File upload area"
      aria-disabled={disabled}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
        className="hidden"
        disabled={disabled}
      />
      <div className="flex flex-col items-center justify-center text-center pointer-events-none">
        <span className="material-symbols-outlined text-4xl text-dj-blue mb-2">cloud_upload</span>
        <p className="text-sm font-medium text-dj-text-primary">Click to upload or drag & drop</p>
        <p className="text-xs text-dj-text-secondary/80">CSV, XLSX, or XLS files</p>
      </div>
    </div>
  );
};