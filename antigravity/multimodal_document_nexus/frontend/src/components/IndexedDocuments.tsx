import React, { useState, useEffect } from 'react';
import { Trash2, RefreshCw, FileText, DownloadCloud } from 'lucide-react';

interface IndexedDoc {
  document_name: string;
  chunk_count: number;
}

export const IndexedDocuments: React.FC<{ onSelectDocument?: (docName: string) => void }> = ({ onSelectDocument }) => {
  const [documents, setDocuments] = useState<IndexedDoc[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8001/api/documents');
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleDelete = async (docName: string) => {
    if (!confirm(`Are you sure you want to delete ${docName} from the database? This action cannot be undone.`)) return;
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8001/api/documents/${encodeURIComponent(docName)}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        await fetchDocs();
      } else {
        alert('Failed to delete document');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="results-viewer" style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', color: 'var(--text-primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} className="accent-color" />
            BigQuery Index Manager
          </h2>
          <p style={{ color: 'var(--text-secondary)' }}>Manage documents currently embedded and searchable via Vector Search.</p>
        </div>
        <button className="btn secondary" onClick={fetchDocs} disabled={loading} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <RefreshCw size={16} className={loading ? 'spinning' : ''} /> Refresh
        </button>
      </div>

      <div className="bq-table-container">
        <table className="bq-table">
          <thead>
            <tr>
              <th>Document Name</th>
              <th>Chunks Indexed</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.document_name}>
                <td style={{ fontWeight: '500' }}>{doc.document_name}</td>
                <td><span className="entity-badge">{doc.chunk_count}</span></td>
                <td>
                  <button
                    className="icon-btn"
                    onClick={() => onSelectDocument && onSelectDocument(doc.document_name)}
                    title="Load Document Data"
                    disabled={loading}
                    style={{ color: '#4a90e2', background: 'rgba(74, 144, 226, 0.1)', border: 'none', marginRight: '8px' }}
                  >
                    <DownloadCloud size={16} />
                  </button>
                  <button
                    className="icon-btn"
                    onClick={() => handleDelete(doc.document_name)}
                    title="Delete Document"
                    disabled={loading}
                    style={{ color: '#f36c5b', background: 'rgba(243, 108, 91, 0.1)', border: 'none' }}
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {documents.length === 0 && !loading && (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                  No documents found in the Vector Search index.
                </td>
              </tr>
            )}
            {loading && documents.length === 0 && (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                  Loading indexed documents...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
