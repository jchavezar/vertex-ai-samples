import React, { useState, useEffect } from 'react';
import { Folder, File, ArrowLeft, CheckCircle, ShieldAlert, Activity, PlayCircle, Loader2, Network, X, RotateCcw } from 'lucide-react';
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

interface PipelineEvent {
  stage: string;
  status: 'running' | 'completed' | 'failed' | 'success';
  elapsed_ms: number;
  result?: any;
  error?: string;
}

export const DocumentWorkspaceV2: React.FC<{ token?: string }> = ({ token }) => {
  const [currentPath, setCurrentPath] = useState<PathNode[]>([{ id: 'root', name: 'root' }]);
  const [items, setItems] = useState<SharePointItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<SharePointItem | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ text: string; type: 'info' | 'success' | 'error' } | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Pipeline Tracking State
  const [pipelineEvents, setPipelineEvents] = useState<PipelineEvent[]>([]);
  const [modifiedContent, setModifiedContent] = useState<any>(null); // from final result
  
  const [showArchitecture, setShowArchitecture] = useState(false);

  // Restore Modal State
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [availableBackups, setAvailableBackups] = useState<SharePointItem[]>([]);
  const [loadingBackups, setLoadingBackups] = useState(false);

  const fetchFolder = async (folderId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/sharepoint/list?folder_id=${folderId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.items) {
        setItems(data.items);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (file: SharePointItem) => {
    setLoading(true);
    setPreviewUrl(null);
    setSelectedFile(file);
    setPipelineEvents([]);
    setModifiedContent(null);

    const isPDF = file.name.toLowerCase().endsWith('.pdf');

    try {
      if (isPDF) {
        try {
          const previewRes = await fetch(`/api/sharepoint/preview_url?item_id=${file.id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const previewData = await previewRes.json();
          if (previewData.preview_url) {
            // Append view=fitH to the URL to force "Window Width" zoom natively if supported
            const urlWithZoom = previewData.preview_url.includes('?') 
              ? `${previewData.preview_url}&view=fitH` 
              : `${previewData.preview_url}?view=fitH`;
            setPreviewUrl(urlWithZoom);
          }
        } catch (e) {
          console.warn("Native preview failed", e);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchFolder(currentPath[currentPath.length - 1].id);
  }, [currentPath, token]);

  const handleItemClick = (item: SharePointItem) => {
    if (item.type === 'folder') {
      setCurrentPath([...currentPath, { id: item.id, name: item.name }]);
    } else {
      fetchFileContent(item);
    }
  };

  const startRegenerativePipeline = async () => {
    if (!selectedFile || !aiPrompt) return;

    setPipelineEvents([]);
    setModifiedContent(null);
    setIsProcessing(true);
    setStatusMsg(null);

    // Using POST with fetch for SSE requires a workaround or custom reader since EventSource only supports GET.
    // We'll use the ReadableStream API to process the SSE stream manually.
    try {
      const response = await fetch('/api/sharepoint/regenerative_stream', {
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

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let buffer = "";
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process SSE lines
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ""; // Keep the last incomplete block
        
        for (const block of lines) {
          if (block.startsWith('data: ')) {
            const jsonStr = block.replace('data: ', '');
            try {
              const event: PipelineEvent = JSON.parse(jsonStr);
              setPipelineEvents(prev => {
                // Update or append
                const existing = prev.findIndex(e => e.stage === event.stage);
                if (existing >= 0) {
                  const newEvents = [...prev];
                  newEvents[existing] = event;
                  return newEvents;
                }
                return [...prev, event];
              });

              if (event.result && event.result.modified_content) {
                 setModifiedContent(event.result.modified_content);
              }

              if (event.status === 'failed') {
                 setIsProcessing(false);
                 setStatusMsg({ text: "Pipeline Failed", type: 'error' });
                 return;
              }

              if (event.status === 'success') {
                 setIsProcessing(false);
                 setStatusMsg({ text: "Pipeline Complete", type: 'success' });
                 return;
              }
            } catch (e) {
              console.error("Error parsing SSE JSON", e);
            }
          }
        }
      }
    } catch (e) {
      console.error("Stream connection error", e);
      setIsProcessing(false);
      setStatusMsg({ text: "Connection failed", type: 'error' });
    }
  };

  const commitChanges = async () => {
     if (!selectedFile || !modifiedContent) return;
 
     setIsProcessing(true);
     setStatusMsg({ text: "Committing high-fidelity PDF...", type: 'info' });
 
     try {
       const response = await fetch('/api/sharepoint/commit_modification', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${token}`
         },
         body: JSON.stringify({
           item_id: selectedFile.id,
           content: `PDF_REGEN:${JSON.stringify(modifiedContent)}`
         })
       });
 
       const data = await response.json();
       if (data.status === 'success') {
         setStatusMsg({ text: "Synthetic Backup & Commit Successful", type: 'success' });
         setRefreshKey(prev => prev + 1);
         setPipelineEvents([]);
         setModifiedContent(null);
       } else {
         setStatusMsg({ text: `Commit Error: ${data.error}`, type: 'error' });
       }
     } catch (e) {
       setStatusMsg({ text: "Failed to save changes", type: 'error' });
     } finally {
       setIsProcessing(false);
     }
  };

  return (
    <div className="dw-container" style={{ height: 'calc(100vh - 60px)' }}> {/* Maximize space hook */}
      <div className="dw-header">
        <div className="dw-header-top">
          <h2 className="dw-title">Document Workspace (V2: Regenerative Pipeline)</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {selectedFile && selectedFile.type === 'file' && (
              <button 
                className="pwc-btn secondary" 
                style={{ padding: '4px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
                onClick={async () => {
                  if (selectedFile.name.includes('_BAK_')) {
                    // Direct restore if we are looking at a backup file
                    try {
                      setStatusMsg({ text: `Restoring ${selectedFile.name}...`, type: 'info' });
                      setIsProcessing(true);
                      const res = await fetch('/api/sharepoint/restore_backup', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                        body: JSON.stringify({ item_id: selectedFile.id }) // Backend handles _BAK_ logic
                      });
                      const data = await res.json();
                      if (data.status === 'success') {
                        setStatusMsg({ text: "Restored successfully", type: 'success' });
                        // Optionally refresh the current view
                        setRefreshKey(prev => prev + 1);
                      } else {
                        setStatusMsg({ text: `Restore failed: ${data.error}`, type: 'error' });
                      }
                    } catch (e) {
                      setStatusMsg({ text: "Restore error", type: 'error' });
                    } finally {
                      setIsProcessing(false);
                    }
                  } else {
                    // Normal flow: Open modal to pick a backup for this original file
                    setShowRestoreModal(true);
                    setLoadingBackups(true);
                    try {
                      const res = await fetch(`/api/sharepoint/backups?item_id=${selectedFile.id}`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                      });
                      const data = await res.json();
                      if (data.backups) {
                        setAvailableBackups(data.backups);
                      }
                    } catch (e) {
                      console.error("Failed to load backups", e);
                    } finally {
                      setLoadingBackups(false);
                    }
                  }
                }}
                disabled={isProcessing}
                title={selectedFile.name.includes('_BAK_') ? "Restore this backup to the root folder" : "View automated backups to restore"}
              >
                <RotateCcw size={14} /> {selectedFile.name.includes('_BAK_') ? "Restore this Backup" : "Restore Original"}
              </button>
            )}
            {statusMsg && (
              <div className={`dw-status-badge ${statusMsg.type === 'success' ? 'dw-status-success' : statusMsg.type === 'error' ? 'dw-status-error' : ''}`}>
                {statusMsg.type === 'success' ? <CheckCircle size={14} /> : <Activity size={14} />} 
                {statusMsg.text}
              </div>
            )}
          </div>
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
        <div className="dw-panel" style={{ flex: '0 0 250px' }}>
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
          <div className="dw-panel-content preview" style={{ padding: 0 }}>
            {selectedFile ? (
              loading && !previewUrl ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '15px' }}>
                  <div className="dw-spinner"></div>
                  <p style={{ color: '#888', fontSize: '12px' }}>Loading native preview...</p>
                </div>
              ) : previewUrl ? (
                <iframe
                  key={refreshKey}
                  src={previewUrl}
                  className="dw-iframe-preview dw-fade-in"
                  title="PDF Preview"
                  style={{ width: '100%', height: '100%', border: 'none' }}
                />
              ) : (
                <div className="dw-preview-area dw-fade-in">
                  Preview not available.
                </div>
              )
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#888', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <File size={48} style={{ marginBottom: '15px', opacity: 0.3 }} />
                <p>Select a file to preview</p>
              </div>
            )}
          </div>
        </div>

        {/* Panel 3: Action & Pipeline Tracking */}
        <div className="dw-panel" style={{ flex: '0 0 350px' }}>
          <div className="dw-panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Transformation Pipeline</h3>
            <button 
              onClick={() => setShowArchitecture(true)} 
              style={{ background: 'rgba(255, 182, 0, 0.1)', border: '1px solid rgba(255, 182, 0, 0.3)', color: '#d04a02', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', padding: '4px 8px', borderRadius: '4px' }}
              title="View Pipeline Architecture"
            >
              <Network size={14} /> <span style={{ fontSize: '11px', fontWeight: 600 }}>Architecture</span>
            </button>
          </div>
          <div className="dw-panel-content" style={{ display: 'flex', flexDirection: 'column' }}>
            {selectedFile ? (
              <>
                <div className="dw-ai-input-group" style={{ marginBottom: '20px' }}>
                  <label className="dw-label">PIPELINE DIRECTIVE</label>
                  <textarea
                    className="dw-textarea"
                    value={aiPrompt}
                    onChange={(e) => setAiPrompt(e.target.value)}
                    placeholder="e.g. 'in the 1.2 column change the column names as follows...'"
                    style={{ minHeight: '80px', marginBottom: '10px' }}
                  />
                  <button
                    className="pwc-btn"
                    style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}
                    onClick={startRegenerativePipeline}
                    disabled={isProcessing || !aiPrompt}
                  >
                    {isProcessing ? <><Loader2 size={16} className="spin" /> Pipeline Running</> : <><PlayCircle size={16} /> Execute Pipeline</>}
                  </button>
                </div>

                {/* Live Pipeline Visualizer */}
                {pipelineEvents.length > 0 && (
                   <div style={{ flex: 1, overflowY: 'auto' }}>
                     <label className="dw-label" style={{ color: '#888', marginBottom: '12px', display: 'block' }}>PIPELINE TELEMETRY</label>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                       {pipelineEvents.map((evt, idx) => {
                          if (evt.stage === 'Pipeline Complete') return null;
                          return (
                            <div key={idx} style={{ 
                              background: '#f8f9fa', 
                              border: '1px solid #e2e8f0', 
                              borderRadius: '6px', 
                              padding: '12px',
                              display: 'flex',
                              flexDirection: 'column',
                              borderLeft: evt.status === 'running' ? '4px solid var(--pwc-orange)' : 
                                          evt.status === 'failed' ? '4px solid #ef4444' : '4px solid #22c55e'
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                                <span style={{ fontWeight: 600, fontSize: '13px', color: '#1e293b' }}>{evt.stage}</span>
                                <span style={{ fontFamily: 'monospace', fontSize: '11px', color: evt.status === 'running' ? 'var(--pwc-orange)' : '#64748b' }}>
                                  {evt.elapsed_ms}ms
                                </span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#64748b' }}>
                                {evt.status === 'running' && <Loader2 size={12} className="spin" color="var(--pwc-orange)" />}
                                {evt.status === 'completed' && <CheckCircle size={12} color="#22c55e" />}
                                {evt.status === 'failed' && <ShieldAlert size={12} color="#ef4444" />}
                                <span style={{ textTransform: 'capitalize' }}>{evt.status}</span>
                              </div>
                              {evt.error && <div style={{ marginTop: '8px', fontSize: '11px', color: '#ef4444', fontFamily: 'monospace' }}>{evt.error}</div>}
                            </div>
                          );
                       })}
                     </div>
                   </div>
                )}

                {/* Commit Action */}
                {modifiedContent && (
                  <div className="dw-fade-in" style={{ marginTop: '20px', padding: '15px', background: 'rgba(34, 197, 94, 0.05)', borderRadius: '8px', border: '1px dashed #22c55e' }}>
                    <p style={{ fontSize: '12px', marginBottom: '10px', color: '#166534', fontWeight: 600 }}>Aesthetics Evaluated & Synthesis Complete.</p>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button className="pwc-btn" style={{ flex: 1, backgroundColor: '#22c55e' }} onClick={commitChanges}>Accept & Commit</button>
                      <button className="pwc-btn secondary" style={{ flex: 0.5 }} onClick={() => { setModifiedContent(null); setPipelineEvents([]); }}>Discard</button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#888', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Activity size={48} style={{ marginBottom: '15px', opacity: 0.3 }} />
                <p>Pipeline Engine Ready</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {showArchitecture && (
        <div className="dw-fade-in" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 9999, 
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          backdropFilter: 'blur(3px)'
        }}>
          <div style={{
            background: 'white', padding: '30px', borderRadius: '12px', 
            width: '650px', maxWidth: '90%', maxHeight: '85vh', overflowY: 'auto',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px', borderBottom: '1px solid #e2e8f0', paddingBottom: '15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ background: '#fffbeb', padding: '8px', borderRadius: '8px', color: '#d04a02' }}>
                  <Network size={24} />
                </div>
                <div>
                  <h2 style={{ margin: 0, color: '#0f172a', fontSize: '20px', fontWeight: 600 }}>Pipeline Architecture</h2>
                  <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#64748b' }}>End-to-end components and models powering the regenerative engine.</p>
                </div>
              </div>
              <button 
                onClick={() => setShowArchitecture(false)} 
                style={{ background: '#f1f5f9', border: 'none', cursor: 'pointer', color: '#64748b', padding: '8px', borderRadius: '50%', display: 'flex' }}
                title="Close"
              >
                <X size={18} />
              </button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ borderLeft: '4px solid #3b82f6', background: '#f8fafc', padding: '15px', borderRadius: '0 8px 8px 0' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ background: '#3b82f6', color: 'white', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0 }}>1</span>
                  Snapshot De-synthesis
                </h4>
                <p style={{ margin: 0, fontSize: '13px', color: '#475569', display: 'grid', gridTemplateColumns: '80px 1fr', gap: '8px', marginBottom: '8px' }}>
                  <strong>Type:</strong> <div>Parser Subsystem</div>
                  <strong>Tools:</strong> <div><code>PDFDeSynthesizer</code> (PyMuPDF, pdfplumber)</div>
                </p>
                <p style={{ margin: 0, fontSize: '13px', color: '#64748b', lineHeight: '1.5' }}>Extracts tabular data, textual content, and infers the implicit stylistic templates (fonts, colors, spatial alignment) forming a baseline Component Feed JSON blueprint.</p>
              </div>

              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1, borderLeft: '4px solid #eab308', background: '#f8fafc', padding: '15px', borderRadius: '0 8px 8px 0' }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ background: '#eab308', color: 'white', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0 }}>2A</span>
                    Content Expert
                  </h4>
                  <p style={{ margin: 0, fontSize: '13px', color: '#475569', display: 'grid', gridTemplateColumns: '70px 1fr', gap: '8px', marginBottom: '8px' }}>
                    <strong>Type:</strong> <div>LlmAgent</div>
                    <strong>Model:</strong> <div><code>gemini-2.5-flash</code></div>
                  </p>
                  <p style={{ margin: 0, fontSize: '13px', color: '#64748b', lineHeight: '1.5' }}>Updates metrics, labels, and text based strictly on the user directive. Expressly forbidden from altering style rule definitions.</p>
                </div>

                <div style={{ flex: 1, borderLeft: '4px solid #a855f7', background: '#f8fafc', padding: '15px', borderRadius: '0 8px 8px 0' }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ background: '#a855f7', color: 'white', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0 }}>2B</span>
                    Style Expert
                  </h4>
                  <p style={{ margin: 0, fontSize: '13px', color: '#475569', display: 'grid', gridTemplateColumns: '70px 1fr', gap: '8px', marginBottom: '8px' }}>
                    <strong>Type:</strong> <div>LlmAgent</div>
                    <strong>Model:</strong> <div><code>gemini-2.5-flash</code></div>
                  </p>
                  <p style={{ margin: 0, fontSize: '13px', color: '#64748b', lineHeight: '1.5' }}>Re-affirms the structural layout constraints necessary to support the modified content while preserving the original design DNA.</p>
                </div>
              </div>

              <div style={{ borderLeft: '4px solid #22c55e', background: '#f8fafc', padding: '15px', borderRadius: '0 8px 8px 0' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ background: '#22c55e', color: 'white', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0 }}>3</span>
                  Aesthetic Evaluator 
                </h4>
                <p style={{ margin: 0, fontSize: '13px', color: '#475569', display: 'grid', gridTemplateColumns: '80px 1fr', gap: '8px', marginBottom: '8px' }}>
                  <strong>Type:</strong> <div>LlmAgent (Gatekeeper)</div>
                  <strong>Model:</strong> <div><code>gemini-2.5-flash</code></div>
                </p>
                <p style={{ margin: 0, fontSize: '13px', color: '#64748b', lineHeight: '1.5' }}>Cross-evaluates the output of both Parallel Experts. Intercepts any formatting regressions or unprompted aesthetic damage and enforces the master JSON Component structure.</p>
              </div>

              <div style={{ borderLeft: '4px solid #f97316', background: '#f8fafc', padding: '15px', borderRadius: '0 8px 8px 0' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ background: '#f97316', color: 'white', width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0 }}>4</span>
                  Server-Side Synthesis
                </h4>
                <p style={{ margin: 0, fontSize: '13px', color: '#475569', display: 'grid', gridTemplateColumns: '80px 1fr', gap: '8px', marginBottom: '8px' }}>
                  <strong>Type:</strong> <div>Rendering Engine</div>
                  <strong>Tools:</strong> <div><code>pwc_renderer</code> (Jinja2, WeasyPrint)</div>
                </p>
                <p style={{ margin: 0, fontSize: '13px', color: '#64748b', lineHeight: '1.5' }}>Executes a pixel-perfect HTML-to-PDF conversion utilizing the sanitized data payload and static asset bindings to generate the final modified document.</p>
              </div>
            </div>
            
          </div>
        </div>
      )}

      {/* Restore Modal */}
      {showRestoreModal && (
        <div className="dw-fade-in" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 10000, 
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          backdropFilter: 'blur(3px)'
        }}>
          <div style={{
            background: 'white', padding: '30px', borderRadius: '12px', 
            width: '500px', maxWidth: '90%', maxHeight: '85vh', overflowY: 'auto',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #e2e8f0', paddingBottom: '15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ background: '#f1f5f9', padding: '8px', borderRadius: '8px', color: '#334155' }}>
                  <RotateCcw size={20} />
                </div>
                <div>
                  <h2 style={{ margin: 0, color: '#0f172a', fontSize: '18px', fontWeight: 600 }}>Restore Document</h2>
                  <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#64748b' }}>Select a backup to revert this document to a previous state.</p>
                </div>
              </div>
              <button 
                onClick={() => setShowRestoreModal(false)} 
                style={{ background: '#f1f5f9', border: 'none', cursor: 'pointer', color: '#64748b', padding: '8px', borderRadius: '50%', display: 'flex' }}
              >
                <X size={16} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {loadingBackups ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '20px', color: '#888' }}>
                  <Loader2 size={24} className="spin" />
                </div>
              ) : availableBackups.length > 0 ? (
                availableBackups.map(backup => {
                  // Extract timestamp from backup name e.g., "Report_BAK_1680000000.pdf"
                  const match = backup.name.match(/_BAK_(\d+)/);
                  let dateStr = "Unknown Date";
                  if (match && match[1]) {
                    dateStr = new Date(parseInt(match[1]) * 1000).toLocaleString();
                  }

                  return (
                    <div key={backup.id} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '12px 16px', border: '1px solid #e2e8f0', borderRadius: '8px',
                      background: '#f8fafc'
                    }}>
                      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', paddingRight: '15px' }}>
                        <span style={{ fontWeight: 500, color: '#1e293b', fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {backup.name}
                        </span>
                        <span style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                          {dateStr}
                        </span>
                      </div>
                      <button 
                        className="pwc-btn secondary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={async () => {
                          setShowRestoreModal(false);
                          if (!selectedFile) return;
                          try {
                            setStatusMsg({ text: `Restoring ${backup.name}...`, type: 'info' });
                            setIsProcessing(true);
                            const res = await fetch('/api/sharepoint/restore_backup', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                              body: JSON.stringify({ item_id: selectedFile.id, backup_id: backup.id })
                            });
                            const data = await res.json();
                            if (data.status === 'success') {
                              setStatusMsg({ text: "Restored successfully", type: 'success' });
                              setRefreshKey(prev => prev + 1);
                            } else {
                              setStatusMsg({ text: `Restore failed: ${data.error}`, type: 'error' });
                            }
                          } catch (e) {
                            setStatusMsg({ text: "Restore error", type: 'error' });
                          } finally {
                            setIsProcessing(false);
                          }
                        }}
                      >
                        Restore
                      </button>
                    </div>
                  );
                })
              ) : (
                <div style={{ textAlign: 'center', padding: '30px', color: '#64748b', fontSize: '13px' }}>
                  No automated synthetic backups found.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
