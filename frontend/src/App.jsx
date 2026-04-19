import { useState } from 'react';
import Upload from './components/Upload';
import Result from './components/Result';
import Header from './components/Header';
import './index.css';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const API_BASE_URL = 'http://127.0.0.1:8000';

  const handleUpload = async (formData) => {
    try {
      setIsLoading(true);
      setError('');
      setAnalysisResult(null);

      const response = await fetch(`${API_BASE_URL}/api/upload-resume`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      const errorMessage =
        err instanceof TypeError
          ? 'Unable to connect to the server. Make sure backend is running.'
          : err.message;
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setError('');
    setIsLoading(false);
  };

  return (
    <div className="app-shell">

      {/* HEADER */}
      <Header />

      {/* MAIN */}
      <main className="container main-section">
        {analysisResult ? (
          <Result data={analysisResult} onReset={handleReset} />
        ) : (
          <>
            <div className="card glass">
              <Upload onUpload={handleUpload} isLoading={isLoading} />
            </div>

            {error && (
              <div className="error-message slide-up">
                <strong>⚠️ Error:</strong> {error}
              </div>
            )}
          </>
        )}
      </main>

      {/* FOOTER */}
      <footer className="app-footer">
        <p>AI Career Mentor • Built with AI + NLP</p>
      </footer>
    </div>
  );
}

export default App;