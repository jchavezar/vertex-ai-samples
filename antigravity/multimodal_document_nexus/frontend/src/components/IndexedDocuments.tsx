import React, { useState, useEffect } from 'react';
import { Trash2, RefreshCw, FileText, MousePointerClick } from 'lucide-react';

interface IndexedDoc {
  document_name: string;
  chunk_count: number;
}

export const IndexedDocuments: React.FC<{ onSelectDocument?: (docName: string) => void }> = ({ onSelectDocument }) => {
  const [documents, setDocuments] = useState<IndexedDoc[]>([]);
  const [loading, setLoading] = useState(false);
  const [docToDelete, setDocToDelete] = useState<string | null>(null);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/documents');
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

  const executeDelete = async () => {
    if (!docToDelete) return;
    
    setLoading(true);
    try {
      const res = await fetch(`/api/documents/${encodeURIComponent(docToDelete)}`, {
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
      setDocToDelete(null);
    }
  };

  return (
    <div style={{ background: 'var(--bg-slate)', border: '1px solid var(--border-subtle)', borderRadius: '16px', padding: '2rem', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
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
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onSelectDocument) onSelectDocument(doc.document_name);
                    }}
                    title="Select to view document with bounding boxes & chat"
                    disabled={loading}
                    style={{ color: '#4a90e2', background: 'rgba(74, 144, 226, 0.1)', border: 'none', marginRight: '8px', padding: '6px 12px', borderRadius: '4px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                  >
                    <MousePointerClick size={16} />
                    <span style={{ fontSize: '12px', fontWeight: '500' }}>Select</span>
                  </button>
                  <button
                    className="icon-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDocToDelete(doc.document_name);
                    }}
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

      {/* Custom Confirmation Modal */}
      {docToDelete && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', 
          alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{
            background: '#1e1e2d', padding: '2rem', borderRadius: '12px', 
            maxWidth: '400px', width: '100%', border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <h3 style={{ color: '#fff', marginTop: 0, marginBottom: '1rem' }}>Confirm Deletion</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              Are you sure you want to delete <strong>{docToDelete}</strong> from the vector database? This action cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button 
                className="btn secondary" 
                onClick={() => setDocToDelete(null)}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                className="btn primary" 
                onClick={executeDelete}
                disabled={loading}
                style={{ background: '#f36c5b', color: '#fff' }}
              >
                {loading ? 'Deleting...' : 'Delete Index'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
