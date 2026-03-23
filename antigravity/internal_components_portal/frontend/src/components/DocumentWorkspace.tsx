import React, { useState, useEffect } from 'react';
import { Folder, File, ArrowLeft, CheckCircle, ShieldAlert } from 'lucide-react';
import './DocumentWorkspace.css';

interface SharePointItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  webUrl: string;
  size?: number;
}

interface PathNode {
  id: string;
  name: string;
}

const SimpleDiff: React.FC<{ original: string; modified: string }> = ({ original, modified }) => {
  if (!modified) return <div style={{ color: '#888', fontStyle: 'italic', padding: '20px' }}>No modifications proposed yet...</div>;

  if (modified.startsWith("PDF_PATCH:")) {
    let patches: Record<string, string>[] = [];
    try {
      const patchStr = modified.replace("PDF_PATCH:", "").trim().replace(/^```json/, "").replace(/```$/, "").trim();
      patches = JSON.parse(patchStr);
    } catch (e) {
      return <div>Error parsing PDF patch data: {String(e)}</div>;
    }

    return (
      <div className="dw-diff-viewer">
        {patches.map((p: Record<string, string>, idx: number) => (
          <div key={idx} style={{ marginBottom: '15px', padding: '10px', background: '#f9f9f9', borderRadius: '4px', borderLeft: '3px solid var(--internal-green)' }}>
            <div style={{ color: '#ff4d4d', textDecoration: 'line-through', fontSize: '12px', marginBottom: '4px' }}>- {p.find}</div>
            <div style={{ color: '#2e7d32', fontWeight: 'bold' }}>+ {p.replace}</div>
          </div>
        ))}
        <div style={{ marginTop: '10px', fontSize: '11px', color: '#888', fontStyle: 'italic' }}>* Visual patching will be applied to the PDF while preserving layout.</div>
      </div>
    );
  }

  return (
    <div className="dw-diff-viewer">
      <div style={{ color: '#ff4d4d', textDecoration: 'line-through', marginBottom: '10px', whiteSpace: 'pre-wrap' }}>
        - {original.slice(0, 500)}{original.length > 500 ? '...' : ''}
      </div>
      <div style={{ color: '#2e7d32', whiteSpace: 'pre-wrap' }}>
        + {modified.slice(0, 500)}{modified.length > 500 ? '...' : ''}
      </div>
    </div>
  );
};

export const DocumentWorkspace: React.FC<{ token?: string }> = ({ token }) => {
  const [currentPath, setCurrentPath] = useState<PathNode[]>([{ id: 'root', name: 'root' }]);
  const [items, setItems] = useState<SharePointItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<SharePointItem | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [modifiedContent, setModifiedContent] = useState<string>("");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ text: string; type: 'info' | 'success' | 'error' } | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchFolder = async (folderId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/sharepoint/list?folder_id=${folderId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.items) {
        setItems(data.items);
      } else {
        console.error("Failed to fetch folder items:", data.error);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (file: SharePointItem) => {
    setLoading(true);
    setFileContent("");
    setModifiedContent("");
    setPreviewUrl(null);
    setSelectedFile(file);

    const isPDF = file.name.toLowerCase().endsWith('.pdf');

    try {
      if (isPDF) {
        try {
          const previewRes = await fetch(`/api/sharepoint/preview_url?item_id=${file.id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const previewData = await previewRes.json();
          if (previewData.preview_url) {
            setPreviewUrl(previewData.preview_url);
            // Background fetch text for AI
            fetch(`/api/sharepoint/content?item_id=${file.id}`, {
              headers: { 'Authorization': `Bearer ${token}` }
            }).then(r => r.json()).then(d => {
              if (d.content) setFileContent(d.content);
            });
            setLoading(false);
            return;
          }
        } catch (e) {
          console.warn("Native preview failed", e);
        }
      }

      const response = await fetch(`/api/sharepoint/content?item_id=${file.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.content) {
        setFileContent(data.content);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchFolder(currentPath[currentPath.length - 1].id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPath, token]);

  const handleItemClick = (item: SharePointItem) => {
    if (item.type === 'folder') {
      setCurrentPath([...currentPath, { id: item.id, name: item.name }]);
    } else {
      fetchFileContent(item);
    }
  };

  const handleAction = async () => {
    if (!selectedFile || !aiPrompt) return;

    setIsProcessing(true);
    setStatusMsg(null);

    try {
      const response = await fetch('/api/sharepoint/propose_modification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          item_id: selectedFile.id,
          prompt: aiPrompt
        })
      });

      const data = await response.json();
      if (data.modified_content) {
        setModifiedContent(data.modified_content);
        setStatusMsg({ text: "AI Proposal Generated", type: 'success' });
      } else if (data.error) {
        setStatusMsg({ text: `Error: ${data.error}`, type: 'error' });
      }
    } catch (e) {
      console.error(e);
      setStatusMsg({ text: "Failed to connect to AI engine", type: 'error' });
    } finally {
      setIsProcessing(false);
    }
  };

  const commitChanges = async () => {
    if (!selectedFile || !modifiedContent) return;

    setIsProcessing(true);
    setStatusMsg(null);

    try {
      const response = await fetch('/api/sharepoint/commit_modification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          item_id: selectedFile.id,
          content: modifiedContent
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setStatusMsg({ text: "Changes committed to SharePoint successfully", type: 'success' });
        // Force refresh of preview and content
        setRefreshKey(prev => prev + 1);
        fetchFileContent(selectedFile);
      } else {
        setStatusMsg({ text: `Commit Error: ${data.error}`, type: 'error' });
      }
    } catch (e) {
      console.error(e);
      setStatusMsg({ text: "Failed to save changes to SharePoint", type: 'error' });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="dw-container">
      <div className="dw-header">
        <div className="dw-header-top">
          <h2 className="dw-title">Document Workspace (Action Center)</h2>
          {statusMsg && (
            <div className={`dw-status-badge ${statusMsg.type === 'success' ? 'dw-status-success' : 'dw-status-error'}`}>
              <CheckCircle size={14} /> {statusMsg.text}
            </div>
          )}
        </div>
        <div className="dw-breadcrumbs">
          {currentPath.map((p, i) => (
            <span key={i} className="dw-breadcrumb-item" onClick={() => setCurrentPath(currentPath.slice(0, i + 1))}>
              / {p.name}
            </span>
          ))}
        </div>
      </div>

      <div className="dw-grid">
        {/* Panel 1: Explorer */}
        <div className="dw-panel">
          <div className="dw-panel-header"><h3>Explorer</h3></div>
          <div className="dw-panel-content">
            {loading && items.length === 0 ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                <div className="dw-spinner"></div>
              </div>
            ) : (
              <ul className="dw-explorer-list">
                {currentPath.length > 1 && (
                  <li onClick={() => setCurrentPath(currentPath.slice(0, -1))} style={{ cursor: 'pointer', padding: '8px', display: 'flex', alignItems: 'center', gap: '8px', color: '#888' }}>
                    <ArrowLeft size={14} /> ..
                  </li>
                )}
                {items.map(item => (
                  <li
                    key={item.id}
                    onClick={() => handleItemClick(item)}
                    className={`dw-explorer-item ${selectedFile?.id === item.id ? 'active' : ''}`}
                  >
                    {item.type === 'folder' ? <Folder size={16} color="#FFB600" /> : <File size={16} color="#888" />}
                    <span style={{ fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Panel 2: Preview */}
        <div className="dw-panel">
          <div className="dw-panel-header"><h3>Document Preview</h3></div>
          <div className="dw-panel-content preview">
            {selectedFile ? (
              loading && !fileContent && !previewUrl ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '15px' }}>
                  <div className="dw-spinner"></div>
                  <p style={{ color: '#888', fontSize: '12px' }}>Reading document content...</p>
                </div>
              ) : previewUrl ? (
                <iframe
                  key={refreshKey}
                  src={previewUrl}
                  className="dw-iframe-preview dw-fade-in"
                  title="PDF Preview"
                />
              ) : (
                <div className="dw-preview-area dw-fade-in">
                  {fileContent || "No content available for this document."}
                </div>
              )
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                <File size={48} style={{ marginBottom: '15px', opacity: 0.3 }} />
                <p>Select a file to preview</p>
              </div>
            )}
          </div>
        </div>

        {/* Panel 3: Action & Diff */}
        <div className="dw-panel">
          <div className="dw-panel-header"><h3>AI Action Center</h3></div>
          <div className="dw-panel-content">
            {selectedFile ? (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '20px' }}>
                <div className="dw-ai-input-group">
                  <label className="dw-label">PROMPT AI MODIFICATION</label>
                  <textarea
                    className="dw-textarea"
                    value={aiPrompt}
                    onChange={(e) => setAiPrompt(e.target.value)}
                    placeholder="e.g. 'Summarize the risks section', 'Redact all PII'..."
                  />
                  <button
                    className="internal-btn"
                    style={{ width: '100%', marginTop: '5px' }}
                    onClick={() => handleAction()}
                    disabled={isProcessing || !aiPrompt}
                  >
                    {isProcessing ? 'Thinking...' : 'Generate Proposal'}
                  </button>
                </div>

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                  <label className="dw-label" style={{ color: '#888', marginBottom: '8px' }}>PROPOSED CHANGES (DIFF)</label>
                  <SimpleDiff original={fileContent} modified={modifiedContent} />
                </div>

                {modifiedContent && (
                  <div className="dw-fade-in" style={{ padding: '15px', background: 'rgba(208, 74, 2, 0.05)', borderRadius: '8px', border: '1px dashed var(--internal-green)' }}>
                    <p style={{ fontSize: '12px', marginBottom: '10px', color: '#555' }}>Ready to push these changes to SharePoint?</p>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button className="internal-btn" style={{ flex: 1 }} onClick={commitChanges}>Accept & Commit</button>
                      <button className="internal-btn secondary" style={{ flex: 0.5 }} onClick={() => setModifiedContent("")}>Discard</button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                <ShieldAlert size={48} style={{ marginBottom: '15px', opacity: 0.3 }} />
                <p>Governance engine ready</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

