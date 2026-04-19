import { useState } from 'react';

export default function Upload({ onUpload, isLoading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (file) => {
    setError('');
    
    if (!file.name.endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setError('Please select a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setError('');
      onUpload(formData);
    } catch (err) {
      setError(err.message || 'Failed to upload resume');
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

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileChange(files[0]);
    }
  };

  return (
    <div className="card fade-in upload-card">
      <form onSubmit={handleSubmit}>
        {/* Upload Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        >
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
            id="file-input"
            disabled={isLoading}
          />

          <label htmlFor="file-input">
            <div className="upload-icon">📄</div>
            <div className="upload-text">
              <strong>
                {selectedFile ? `Selected: ${selectedFile.name}` : 'Drag and drop your PDF resume here'}
              </strong>
              <span>or click to select a file</span>
            </div>
          </label>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        {/* File Info */}
        {selectedFile && !error && (
          <div className="success-message">
            <strong>✓ Ready to upload</strong>
            {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !selectedFile}
          className="btn-primary upload-btn"
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Analyzing Resume...
            </>
          ) : (
            ' Analyze Resume'
          )}
        </button>

        {/* Info Box */}
        <div className="info-message">
          <strong>💡 Tip:</strong> Upload a PDF resume to get AI-powered career recommendations, skill analysis, and personalized role suggestions.
        </div>
      </form>
    </div>
  );
}
