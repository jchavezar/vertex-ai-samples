import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Upload, Database, Cpu, Zap, FileText, Table2, BarChart3,
  Image as ImageIcon, Activity, CheckCircle2, Loader2, RefreshCw,
  MessageSquare, Sparkles, Layers, Terminal, Play
} from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chunks?: any[];
}

interface PipelineEntity {
  chunk_id: string;
  document_name: string;
  page_number: number;
  entity_type: string;
  content: string;
  box_2d?: number[];
  frontend_id?: string;
}

interface IndexedDoc {
  document_name: string;
  chunk_count: number;
}

type AppView = 'upload' | 'dashboard';
type TabView = 'data' | 'images' | 'traces' | 'sql';

interface SqlResult {
  success: boolean;
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  error?: string;
}

const AuroraLogo = () => (
  <svg viewBox="0 0 32 32" fill="none">
    <defs>
      <linearGradient id="aurora-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#a855f7" />
        <stop offset="100%" stopColor="#14b8a6" />
      </linearGradient>
    </defs>
    <circle cx="16" cy="16" r="14" stroke="url(#aurora-grad)" strokeWidth="2" fill="none" />
    <path d="M16 6 L20 14 L28 16 L20 18 L16 26 L12 18 L4 16 L12 14 Z" fill="url(#aurora-grad)" />
  </svg>
);

function App() {
  const [view, setView] = useState<AppView>('upload');
  const [activeTab, setActiveTab] = useState<TabView>('data');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [indexedDocs, setIndexedDocs] = useState<IndexedDoc[]>([]);

  const [pipelineData, setPipelineData] = useState<PipelineEntity[]>([]);
  const [annotatedImages, setAnnotatedImages] = useState<string[]>([]);
  const [traces, setTraces] = useState<any[]>([]);

  // SQL Query state
  const [sqlQuery, setSqlQuery] = useState('SELECT * FROM document_chunks LIMIT 10;');
  const [sqlResult, setSqlResult] = useState<SqlResult | null>(null);
  const [sqlLoading, setSqlLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  const models = [
    { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
    { id: 'gemini-3-flash-preview', label: 'Gemini 3 Flash Preview' },
  ];

  useEffect(() => {
    fetchIndexedDocs();
  }, []);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const fetchIndexedDocs = async () => {
    try {
      const res = await fetch('/api/documents');
      if (res.ok) {
        const data = await res.json();
        setIndexedDocs(data.documents || []);
      }
    } catch (e) {
      console.error('Failed to fetch indexed docs:', e);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      await processFile(file);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const processFile = async (file: File) => {
    setIsProcessing(true);
    setProcessingStep(0);

    const stepInterval = setInterval(() => {
      setProcessingStep(prev => Math.min(prev + 1, 3));
    }, 3000);

    const formData = new FormData();
    formData.append('files', file);
    formData.append('selected_model', selectedModel);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Processing failed');

      const data = await res.json();
      if (data.session_id) setSessionId(data.session_id);

      setPipelineData(data.pipeline_data || []);
      setAnnotatedImages(data.annotated_images || []);
      setTraces(data.traces || []);

      setMessages([{
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || `Successfully processed **${file.name}**. The document has been indexed in pgvector. How can I help you analyze it?`,
        chunks: data.pipeline_data || [],
      }]);

      setView('dashboard');
      fetchIndexedDocs();
    } catch (err) {
      console.error(err);
      alert('Error processing file');
    } finally {
      clearInterval(stepInterval);
      setIsProcessing(false);
    }
  };

  const loadDocument = async (docName: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/documents/${encodeURIComponent(docName)}/data`);
      if (res.ok) {
        const data = await res.json();
        if (data.session_id) setSessionId(data.session_id);
        setPipelineData(data.pipeline_data || []);
        setAnnotatedImages(data.annotated_images || []);
        setTraces(data.traces || []);

        setMessages([{
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Loaded **${docName}** from pgvector index. Ask me anything about this document!`,
          chunks: data.pipeline_data || [],
        }]);

        setView('dashboard');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('message', userMsg.content);
    formData.append('selected_model', selectedModel);
    if (sessionId) formData.append('session_id', sessionId);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Chat failed');

      const data = await res.json();

      // Merge new chunks
      if (data.pipeline_data) {
        setPipelineData(prev => {
          const existing = new Set(prev.map(c => c.chunk_id));
          const newChunks = data.pipeline_data.filter((c: PipelineEntity) => !existing.has(c.chunk_id));
          return [...prev, ...newChunks];
        });
      }

      if (data.traces) {
        setTraces(prev => [...prev, ...data.traces]);
      }

      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || 'No response generated.',
        chunks: data.pipeline_data || [],
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Error: ${err}`,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetSession = () => {
    if (confirm('Start a new session? This will clear current chat.')) {
      setView('upload');
      setMessages([]);
      setPipelineData([]);
      setAnnotatedImages([]);
      setTraces([]);
      setSessionId('');
    }
  };

  const executeSql = async () => {
    if (!sqlQuery.trim() || sqlLoading) return;

    setSqlLoading(true);
    setSqlResult(null);

    const formData = new FormData();
    formData.append('query', sqlQuery);

    try {
      const res = await fetch('/api/sql', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setSqlResult(data);
    } catch (err) {
      setSqlResult({
        success: false,
        error: String(err),
        columns: [],
        rows: [],
        row_count: 0,
      });
    } finally {
      setSqlLoading(false);
    }
  };

  const renderMarkdown = (content: string, chunks?: any[]) => {
    const citationRegex = /\[([\d,\s]+)\]/g;
    const processed = content.replace(citationRegex, (_match, ids) => {
      return ids.split(',').map((id: string) => `[${id.trim()}](#cite-${id.trim()})`).join(' ');
    });

    return (
      <ReactMarkdown
        components={{
          a: ({ href, children }) => {
            if (href?.startsWith('#cite-')) {
              const id = href.replace('#cite-', '');
              return <span className="citation">{id}</span>;
            }
            return <a href={href}>{children}</a>;
          }
        }}
      >
        {processed}
      </ReactMarkdown>
    );
  };

  const getEntityBadgeClass = (type: string) => {
    const t = type.toLowerCase();
    if (t === 'table') return 'table';
    if (t === 'chart' || t === 'image') return 'chart';
    return 'text';
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-logo">
          <AuroraLogo />
          <div>
            <div className="app-title">PGVector Document Nexus</div>
            <div className="app-subtitle">Aurora Edition</div>
          </div>
        </div>
        <div className="header-controls">
          <select
            className="model-selector"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            {models.map(m => (
              <option key={m.id} value={m.id}>{m.label}</option>
            ))}
          </select>
          {view === 'dashboard' && (
            <button className="btn-reset" onClick={resetSession}>
              <RefreshCw size={16} />
              New Session
            </button>
          )}
        </div>
      </header>

      {/* Processing Overlay */}
      <AnimatePresence>
        {isProcessing && (
          <motion.div
            className="processing-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="processing-card"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
            >
              <div className="processing-spinner">
                <Loader2 size={36} color="white" />
              </div>
              <h2 className="processing-title">Processing Document</h2>
              <p style={{ color: 'var(--text-secondary)' }}>ADK pipeline is extracting and indexing...</p>

              <div className="processing-steps">
                {[
                  { label: 'Uploading Document', icon: Upload },
                  { label: 'ADK Parallel Extraction', icon: Cpu },
                  { label: 'Generating Embeddings', icon: Zap },
                  { label: 'Indexing to pgvector', icon: Database },
                ].map((step, i) => (
                  <div
                    key={i}
                    className={`processing-step ${i === processingStep ? 'active' : ''} ${i < processingStep ? 'done' : ''}`}
                  >
                    <div className="processing-step-icon">
                      {i < processingStep ? (
                        <CheckCircle2 size={18} color="var(--aurora-teal)" />
                      ) : i === processingStep ? (
                        <Loader2 size={18} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                      ) : (
                        <step.icon size={18} color="var(--text-muted)" />
                      )}
                    </div>
                    {step.label}
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="main-content">
        {view === 'upload' ? (
          <div className="panel panel-left">
            <div className="hero-section">
              <div className="hero-title">
                <h1>Document Intelligence</h1>
                <p>Upload documents to extract, embed, and search with Cloud SQL pgvector</p>
              </div>

              <div
                className="upload-zone"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="upload-icon">
                  <Upload size={28} />
                </div>
                <h3>Drop a document here</h3>
                <p>Supports PDF, PNG, JPEG</p>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileSelect}
                accept=".pdf,.png,.jpg,.jpeg"
              />

              <div className="features-grid">
                <div className="feature-card">
                  <div className="feature-card-icon"><Cpu size={20} /></div>
                  <h4>ADK Extraction</h4>
                  <p>Parallel agents extract text, tables, and charts with bounding boxes</p>
                </div>
                <div className="feature-card">
                  <div className="feature-card-icon"><Database size={20} /></div>
                  <h4>pgvector Storage</h4>
                  <p>HNSW-indexed embeddings for sub-50ms semantic search</p>
                </div>
                <div className="feature-card">
                  <div className="feature-card-icon"><Sparkles size={20} /></div>
                  <h4>Grounded RAG</h4>
                  <p>LLM responses with verifiable citations to source documents</p>
                </div>
              </div>

              {indexedDocs.length > 0 && (
                <div className="indexed-section">
                  <div className="indexed-header">
                    <Layers size={16} />
                    Previously Indexed Documents
                  </div>
                  <div className="indexed-list">
                    {indexedDocs.map(doc => (
                      <div
                        key={doc.document_name}
                        className="indexed-item"
                        onClick={() => loadDocument(doc.document_name)}
                      >
                        <FileText size={16} />
                        {doc.document_name}
                        <span className="chunk-count">{doc.chunk_count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="panel panel-left dashboard-view">
            <div className="results-panel">
              <div className="results-tabs">
                <button
                  className={`tab-btn ${activeTab === 'data' ? 'active' : ''}`}
                  onClick={() => setActiveTab('data')}
                >
                  <Table2 size={16} />
                  Data ({pipelineData.length})
                </button>
                <button
                  className={`tab-btn ${activeTab === 'images' ? 'active' : ''}`}
                  onClick={() => setActiveTab('images')}
                >
                  <ImageIcon size={16} />
                  Pages ({annotatedImages.length})
                </button>
                <button
                  className={`tab-btn ${activeTab === 'traces' ? 'active' : ''}`}
                  onClick={() => setActiveTab('traces')}
                >
                  <Activity size={16} />
                  Traces ({traces.length})
                </button>
                <button
                  className={`tab-btn ${activeTab === 'sql' ? 'active' : ''}`}
                  onClick={() => setActiveTab('sql')}
                >
                  <Terminal size={16} />
                  SQL
                </button>
              </div>

              <div className="results-content">
                {activeTab === 'data' && (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Type</th>
                        <th>Page</th>
                        <th>Content</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pipelineData.map((entity, idx) => (
                        <tr key={entity.chunk_id}>
                          <td>{idx + 1}</td>
                          <td>
                            <span className={`entity-badge ${getEntityBadgeClass(entity.entity_type)}`}>
                              {entity.entity_type}
                            </span>
                          </td>
                          <td>{entity.page_number}</td>
                          <td style={{ maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {entity.content.slice(0, 100)}...
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {activeTab === 'images' && (
                  <div className="images-grid">
                    {annotatedImages.map((img, idx) => (
                      <div key={idx} className="image-card">
                        <img src={img} alt={`Page ${idx + 1}`} />
                        <div className="image-card-label">Page {idx + 1}</div>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'traces' && (
                  <div className="traces-list">
                    {traces.map((trace, idx) => (
                      <div key={idx} className="trace-item">
                        <div className="trace-icon"><Cpu size={18} /></div>
                        <div className="trace-content">
                          <div className="trace-title">{trace.agent_name || trace.step || 'Agent'}</div>
                          <div className="trace-meta">
                            {trace.page_number && `Page ${trace.page_number}`}
                            {trace.entities_extracted && ` | ${trace.entities_extracted} entities`}
                            {trace.description && trace.description}
                          </div>
                        </div>
                        {trace.duration_seconds && (
                          <span className="trace-duration">{trace.duration_seconds}s</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'sql' && (
                  <div className="sql-query-panel">
                    <div className="sql-input-area">
                      <textarea
                        className="sql-textarea"
                        value={sqlQuery}
                        onChange={(e) => setSqlQuery(e.target.value)}
                        placeholder="Enter SQL query (SELECT only)..."
                        rows={4}
                      />
                      <button
                        className="sql-run-btn"
                        onClick={executeSql}
                        disabled={sqlLoading || !sqlQuery.trim()}
                      >
                        {sqlLoading ? <Loader2 size={16} className="spin" /> : <Play size={16} />}
                        {sqlLoading ? 'Running...' : 'Run Query'}
                      </button>
                    </div>

                    <div className="sql-examples">
                      <span>Examples:</span>
                      <button onClick={() => setSqlQuery('SELECT * FROM document_chunks LIMIT 10;')}>All chunks</button>
                      <button onClick={() => setSqlQuery('SELECT document_name, COUNT(*) as chunks FROM document_chunks GROUP BY document_name;')}>Doc summary</button>
                      <button onClick={() => setSqlQuery('SELECT chunk_id, entity_type, page_number, LEFT(content, 100) as preview FROM document_chunks ORDER BY created_at DESC LIMIT 20;')}>Recent chunks</button>
                      <button onClick={() => setSqlQuery("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'document_chunks';")}>Show indexes</button>
                    </div>

                    {sqlResult && (
                      <div className="sql-result">
                        {sqlResult.success ? (
                          <>
                            <div className="sql-result-meta">
                              {sqlResult.row_count} row{sqlResult.row_count !== 1 ? 's' : ''} returned
                            </div>
                            {sqlResult.rows.length > 0 ? (
                              <div className="sql-table-wrapper">
                                <table className="data-table sql-result-table">
                                  <thead>
                                    <tr>
                                      {sqlResult.columns.map((col) => (
                                        <th key={col}>{col}</th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {sqlResult.rows.map((row, idx) => (
                                      <tr key={idx}>
                                        {sqlResult.columns.map((col) => (
                                          <td key={col}>
                                            {typeof row[col] === 'object'
                                              ? JSON.stringify(row[col])
                                              : String(row[col] ?? '')}
                                          </td>
                                        ))}
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            ) : (
                              <div className="sql-empty">No rows returned</div>
                            )}
                          </>
                        ) : (
                          <div className="sql-error">
                            <strong>Error:</strong> {sqlResult.error}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Chat Panel */}
        <div className="panel panel-right">
          <div className="chat-panel">
            <div className="chat-header">
              <div className="chat-header-icon">
                <MessageSquare size={18} />
              </div>
              <h3>Document Chat</h3>
            </div>

            <div className="chat-messages" ref={chatScrollRef}>
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                  Upload a document or select one from the index to start chatting
                </div>
              )}
              {messages.map(msg => (
                <div key={msg.id} className={`chat-message ${msg.role}`}>
                  {msg.role === 'assistant' ? renderMarkdown(msg.content, msg.chunks) : msg.content}
                </div>
              ))}
              {isLoading && (
                <div className="chat-message assistant shimmer" style={{ height: '60px' }} />
              )}
            </div>

            <div className="chat-input-area">
              <textarea
                placeholder="Ask about the document..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                rows={1}
              />
              <button
                className="btn-send"
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
