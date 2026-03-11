import React, { useState, useEffect } from 'react';

interface Classification {
  file_uid: string;
  filename: string;
  sensitivity_level: string;
  contains_pii: boolean;
  classification_tags: string[];
  summary: string;
  reasoning: string;
}

interface Status {
  is_running: boolean;
  last_run: string | null;
  error: string | null;
}

function App() {
  const [results, setResults] = useState<Classification[]>([]);
  const [status, setStatus] = useState<Status>({ is_running: false, last_run: null, error: null });
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [resResults, resStatus] = await Promise.all([
        fetch('/api/results'),
        fetch('/api/status')
      ]);
      const dataResults = await resResults.json();
      const dataStatus = await resStatus.json();
      setResults(dataResults);
      setStatus(dataStatus);
    } catch (err) {
      console.error("Failed to fetch data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const triggerSync = async () => {
    try {
      await fetch('/api/sync', { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error("Failed to trigger sync", err);
    }
  };

  return (
    <div className="container">
      <header>
        <div className="logo">SHAREPOINT SENTINEL</div>
        <div className="status-badge">
          <div className={`status-dot ${status.is_running ? 'active' : ''}`}></div>
          {status.is_running ? 'SYNCING...' : 'READY'}
        </div>
      </header>

      <div className="hero">
        <h1>Sovereign Data Forensics</h1>
        <p>
          Automated sensitivity classification and PII detection across your SharePoint environment using Google Gemini and sovereign local inference.
        </p>
        <button 
          className="btn-primary" 
          onClick={triggerSync} 
          disabled={status.is_running}
        >
          {status.is_running ? 'PROCESSING...' : 'START SCAN'}
        </button>
      </div>

      <div className="grid">
        {results.length === 0 && !loading && (
          <div style={{gridColumn: '1/-1', textAlign: 'center', color: '#718096'}}>
            No documents processed yet. Click 'Start Scan' to begin.
          </div>
        )}
        
        {results.map((res) => (
          <div key={res.file_uid} className="card">
            <div className="card-header">
              <div className="filename" title={res.filename}>{res.filename}</div>
              <div className={`level-tag ${res.sensitivity_level}`}>
                {res.sensitivity_level}
              </div>
            </div>
            <div className="summary">
              {res.summary}
            </div>
            <div className="tags">
              {res.classification_tags.map(tag => (
                <span key={tag} className="tag">{tag}</span>
              ))}
              {res.contains_pii && <span className="tag" style={{color: '#f56565', borderColor: '#f56565'}}>PII</span>}
            </div>
          </div>
        ))}
      </div>

      {loading && results.length === 0 && (
        <div className="loading" style={{textAlign: 'center', marginTop: '2rem'}}>
          Loading Sentinel Data...
        </div>
      )}
    </div>
  );
}

export default App;
