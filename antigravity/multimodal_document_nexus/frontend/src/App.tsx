import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, PlusCircle, FileSearch, MousePointerClick, LayoutDashboard, BrainCircuit, Database, User } from 'lucide-react';
import { UploadOverlay } from './components/UploadOverlay';
import { ResultsViewer, type PipelineEntity } from './components/ResultsViewer';
import { IndexedDocuments } from './components/IndexedDocuments';
import { Citation } from './components/Citation';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chunks?: any[];
}

type AppState = 'processing' | 'dashboard';

const GeminiSparkleIcon = ({ className = "" }: { className?: string }) => (
  <svg
    className={`gemini-sparkle-icon ${className}`}
    width="22"
    height="22"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="gemini-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#5eaefd" />
        <stop offset="50%" stopColor="#b47dff" />
        <stop offset="100%" stopColor="#f36c5b" />
      </linearGradient>
    </defs>
    <path
      d="M12 0C12 6.627 6.627 12 0 12C6.627 12 12 17.373 12 24C12 17.373 17.373 12 24 12C17.373 12 12 6.627 12 0Z"
      fill="url(#gemini-gradient)"
    />
  </svg>
);

function App() {
  const [appState, setAppState] = useState<AppState>('dashboard');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [session, setSession] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isIndexedLoading, setIsIndexedLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [pipelineResult, setPipelineResult] = useState<{
    pipeline_data?: PipelineEntity[],
    annotated_images?: string[],
    traces?: any[],
    evaluator_logs?: string,
    latest_query?: string,
    latest_answer?: string,
    latest_retrieval?: any[],
    llm_prompt?: string
  } | null>(null);

  const [activeHighlight, setActiveHighlight] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('bigquery');
  const [selectedModel, setSelectedModel] = useState<string>('gemini-3.1-flash-lite-preview');

  const availableModels = [
    { id: 'gemini-3.1-flash-lite-preview', label: 'Gemini 3.1 Flash Lite Preview (Fast)' },
    { id: 'gemini-3-flash-preview', label: 'Gemini 3 Flash Preview (Balanced)' },
    { id: 'gemini-2.5-flash-lite', label: 'Gemini 2.5 Flash Lite (Fast)' },
    { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (Balanced)' }
  ];

  const resetSession = () => {
    if (confirm('Are you sure you want to start a new session? This will clear the current chat and document.')) {
      setSession('');
      setMessages([]);
      setPipelineResult(null);
      setAppState('dashboard');
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading, appState]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      startPipeline(newFiles);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };



  const startGcsPipeline = async () => {
    setAppState('processing');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('gcs_uri', 'gs://vtxdemos-datasets-private/deloitte/multimodal_document_project/Sample-ISS-Ch10-Sample-Industry 1.pdf');
    formData.append('selected_model', selectedModel);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'GCS Pipeline failed');
      }

      const data = await response.json();
      if (data.session_id) setSession(data.session_id);

      setPipelineResult({
        pipeline_data: data.pipeline_data,
        annotated_images: data.annotated_images,
        traces: data.traces,
        evaluator_logs: data.evaluator_logs,
        latest_query: "Document Uploaded / Parsed",
        latest_answer: data.response || "GCS Pipeline process complete.",
        latest_retrieval: []
      });

      setMessages([{
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || "GCS Pipeline process complete. How can I help you analyze this document?",
        chunks: data.pipeline_data || []
      }]);

      setAppState('dashboard');
    } catch (err) {
      console.error(err);
      setAppState('dashboard');
      alert(`Error processing GCS document: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };


  const startPipeline = async (files: File[]) => {
    setAppState('processing');
    setIsLoading(true);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('selected_model', selectedModel);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Pipeline failed');
      }

      const data = await response.json();
      if (data.session_id) setSession(data.session_id);

      setPipelineResult({
        pipeline_data: data.pipeline_data,
        annotated_images: data.annotated_images,
        traces: data.traces,
        evaluator_logs: data.evaluator_logs,
        latest_query: "Document Uploaded",
        latest_answer: data.response || "Pipeline process complete.",
        latest_retrieval: []
      });

      setMessages([{
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || "Pipeline process complete. How can I help you analyze this document?",
        chunks: data.pipeline_data || []
      }]);

      setAppState('dashboard');
    } catch (err) {
      console.error(err);
      setAppState('dashboard');
      alert('Error processing document. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDocument = async (docName: string) => {
    setIsIndexedLoading(true);
    try {
      const res = await fetch(`/api/documents/${encodeURIComponent(docName)}/data`);
      if (res.ok) {
        const data = await res.json();
        if (data.session_id) setSession(data.session_id);
        setPipelineResult(data);
        setMessages([{
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Successfully loaded document **${docName}** from the index. How can I help you analyze it?`,
          chunks: data.pipeline_data || []
        }]);
        setAppState('dashboard');
      } else {
        alert('Failed to load document data');
      }
    } catch (e) {
      console.error(e);
      alert('Error loading document data');
    } finally {
      setIsIndexedLoading(false);
    }
  };

  const handleExploreAllDocuments = async () => {
    setIsIndexedLoading(true);
    try {
      const res = await fetch('/api/documents/all/data');
      if (res.ok) {
        const data = await res.json();
        setPipelineResult(data);
        setSession('');
        setMessages([{
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Successfully loaded **Global Index Preview**. This mode shows data across all indexed documents. Click on any row in the BigQuery Preview to open that specific document.`,
          chunks: []
        }]);
        setAppState('dashboard');
      } else {
        alert('Failed to load global document data');
      }
    } catch (e) {
      console.error(e);
      alert('Error loading global document data');
    } finally {
      setIsIndexedLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('message', userMessage.content);
    formData.append('selected_model', selectedModel);
    if (session) formData.append('session_id', session);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      // Accumulate new RAG chunks into the pipeline data for citation tooltips
      setPipelineResult(prev => {
        const existingData = prev?.pipeline_data || [];
        // Simple deduplication by chunk_id
        let newChunks: any[] = [];
        if (data.pipeline_data && data.pipeline_data.length > 0) {
            newChunks = data.pipeline_data.filter((newChunk: any) =>
                !existingData.some((existingChunk: any) => existingChunk.chunk_id === newChunk.chunk_id)
            );
        }
        const existingTraces = prev?.traces || [];
        const newTraces = data.traces || [];
        
        return {
          ...prev,
          pipeline_data: [...existingData, ...newChunks],
          annotated_images: prev?.annotated_images || [],
          traces: [...existingTraces, ...newTraces],
          evaluator_logs: data.evaluator_logs || prev?.evaluator_logs,
          llm_prompt: data.llm_prompt,
          latest_query: userMessage.content,
          latest_answer: data.response || "No text generated.",
          latest_retrieval: data.pipeline_data || []
        };
      });

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || "No text generated.",
        chunks: data.pipeline_data || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      const errMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `**Error**: ${err}`,
      };
      setMessages(prev => [...prev, errMsg]);
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

  const handleHighlightClick = async (chunkId: string) => {
    const chunk = pipelineResult?.pipeline_data?.find((c: any) => c.chunk_id === chunkId);
    if (!chunk) return;

    // If we are in the Global view (identified by lack of annotated_images), we need to load the specific document first
    if (!pipelineResult?.annotated_images || pipelineResult.annotated_images.length === 0) {
      await handleSelectDocument(chunk.document_name);
    }
    
    // Set highlight and tab after document is loaded or if already loaded
    setTimeout(() => {
      setActiveHighlight(chunkId);
      setActiveTab('bounding-boxes');
    }, 100); // Small delay to allow the new document state to render if it was just loaded
  };

  // Custom markdown component to parse citation tags like [Doc: filename, Page: X, Chunk: id]
  const renderMarkdown = (content: string, messageChunks?: any[]) => {
    // Replace citations like [1] or [1, 2] with standard markdown links using a custom protocol
    // E.g., parse [1], [2], [1, 2]
    const citationRegex = /\[([\d,\s]+)\]/g;
    const processedContent = content.replace(citationRegex, (_match, idsString) => {
      const ids = idsString.split(',').map((s: string) => s.trim()).filter(Boolean);
      return ids.map((id: string) => `[${id}](#citation-${id})`).join(' ');
    });

    return (
      <ReactMarkdown
        components={{
          a: ({ node, href, title, children, ...props }) => {
            const isCitation = href && href.startsWith('#citation-');
            if (isCitation) {
              const id = href.replace('#citation-', '');
              const index = parseInt(id) - 1;
              const chunkData = messageChunks && messageChunks.length > index
                ? messageChunks[index]
                : pipelineResult?.pipeline_data?.[index];
              const chunkId = chunkData?.chunk_id || `chunk_${id}`;

              const isActive = activeHighlight === chunkId;

              return (
                <Citation
                  id={id}
                  chunkData={chunkData}
                  isActive={isActive}
                  onClick={() => handleHighlightClick(chunkId)}
                >
                  {id}
                </Citation>
              );
            }
            return <a href={href} title={title} {...props}>{children}</a>;
          }
        }}
      >
        {processedContent}
      </ReactMarkdown>
    );
  };

  return (
    <>
      <header className="app-header">
        <div className="app-title">Nexus Multi-Doc Analyst</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {session && (
            <div 
              title="Current Active Session ID"
              style={{
                background: 'rgba(34, 211, 238, 0.1)',
                border: '1px solid rgba(34, 211, 238, 0.3)',
                color: 'var(--accent-cyan)',
                padding: '0.3rem 0.6rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                fontFamily: 'monospace',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                userSelect: 'all'
              }}
            >
              <Database size={12} />
              Session: {session.length > 8 ? `${session.substring(0, 8)}...` : session}
            </div>
          )}
          <select 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            style={{ 
              background: 'rgba(255,255,255,0.05)', 
              color: 'var(--text-primary)', 
              border: '1px solid rgba(255,255,255,0.1)', 
              padding: '0.4rem 0.8rem', 
              borderRadius: '0.5rem',
              fontSize: '0.85rem',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {availableModels.map(model => (
              <option key={model.id} value={model.id} style={{ background: '#0f172a' }}>{model.label}</option>
            ))}
          </select>
          {pipelineResult && (
            <button 
              className="btn outline" 
              onClick={resetSession}
              title="Start New Session"
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <PlusCircle size={16} />
              New Session
            </button>
          )}
        </div>
      </header>



      {appState === 'processing' && (
        <UploadOverlay isProcessing={true} />
      )}

      {appState === 'dashboard' && (
        <main className="dashboard-layout">
          <div className="dashboard-main">
            {pipelineResult && pipelineResult.pipeline_data ? (
              <ResultsViewer
                data={pipelineResult.pipeline_data}
                annotatedImages={pipelineResult.annotated_images}
                traces={pipelineResult.traces}
                evaluatorLogs={pipelineResult.evaluator_logs}
                latestQuery={pipelineResult.latest_query}
                latestAnswer={pipelineResult.latest_answer}
                latestRetrieval={pipelineResult.latest_retrieval}
                llmPrompt={pipelineResult.llm_prompt}
                activeHighlight={activeHighlight}
                onHighlightClick={handleHighlightClick}
                activeTab={activeTab}
                onTabChange={setActiveTab}
                onSelectDocument={handleSelectDocument}
                isIndexedLoading={isIndexedLoading}
              />
            ) : (
              <div style={{ flex: 1, padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem', overflowY: 'auto' }}>
                <div className="upload-view-title" style={{ textAlign: 'center', marginBottom: 0 }}>
                  <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--text-primary), var(--accent-cyan))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontWeight: 800, letterSpacing: '-0.02em' }}>Multi-Modal Document Intelligence</h1>
                  <p style={{ maxWidth: '600px', margin: '0 auto', color: 'var(--text-secondary)', fontSize: '1.1rem', lineHeight: 1.6 }}>Upload a new document or select an existing one below to activate the Multimodal ADK pipeline and start interacting.</p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', width: '100%', maxWidth: '850px', margin: '0 auto' }}>
                  {/* Card 1: Processing */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem', transition: 'all 0.3s ease' }} className="feature-card">
                    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(34, 211, 238, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
                      <BrainCircuit size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Vision & Parsing</h3>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>Automatically extract text alongside visual bounding box coordinates using Gemini Vision.</p>
                    <div className="feature-card-overlay">
                      <h4>Method</h4>
                      <p>Spatial understanding &amp; structured data extraction from images.</p>
                      <span className="tech-tag">Model: Gemini 3 Flash Preview</span>
                    </div>
                  </div>
                  
                  {/* Card 2: Interactive */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem', transition: 'all 0.3s ease' }} className="feature-card">
                    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(139, 92, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-purple)' }}>
                      <MousePointerClick size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Visual Citations</h3>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>Click on highlighted entities in the BigQuery preview to jump directly to the original page.</p>
                    <div className="feature-card-overlay" style={{ borderColor: 'rgba(139, 92, 246, 0.2)' }}>
                      <h4 style={{ color: 'var(--accent-purple)' }}>Method</h4>
                      <p>Cross-referencing indexed chunks with BigQuery spatial data.</p>
                      <span className="tech-tag" style={{ color: 'var(--accent-purple)', borderColor: 'rgba(139, 92, 246, 0.2)', background: 'rgba(139, 92, 246, 0.1)' }}>DB: BigQuery Vector</span>
                    </div>
                  </div>

                  {/* Card 3: Indexing */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem', transition: 'all 0.3s ease' }} className="feature-card">
                    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-blue)' }}>
                      <LayoutDashboard size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>ADK Workflow</h3>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>Uses intelligent agents to evaluate answers against document context for Hallucination checks.</p>
                    <div className="feature-card-overlay" style={{ borderColor: 'rgba(59, 130, 246, 0.2)' }}>
                      <h4 style={{ color: 'var(--accent-blue)' }}>Method</h4>
                      <p>Orchestrated evaluation pipeline for fact-checking and grounding.</p>
                      <span className="tech-tag" style={{ color: 'var(--accent-blue)', borderColor: 'rgba(59, 130, 246, 0.2)', background: 'rgba(59, 130, 246, 0.1)' }}>Framework: Google ADK</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%', maxWidth: '600px', margin: '0 auto', alignItems: 'center' }}>
                  <div 
                    className="hero-dropzone" 
                    onClick={() => fileInputRef.current?.click()} 
                    style={{ padding: '2.5rem', width: '100%', display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: '1.5rem', textAlign: 'left', background: 'linear-gradient(180deg, rgba(34, 211, 238, 0.05) 0%, transparent 100%)', border: '1px solid var(--accent-cyan)', boxShadow: '0 0 30px rgba(34, 211, 238, 0.1)' }}
                  >
                    <div className="upload-icon-container" style={{ width: '56px', height: '56px', marginBottom: 0, flexShrink: 0, background: 'rgba(34, 211, 238, 0.15)' }}>
                      <FileSearch size={28} />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem', color: 'var(--text-primary)', fontWeight: 600 }}>Select a file from your computer</h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Supports PDFs, PNGs, and JPEG images</p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '1rem', margin: '0.5rem 0' }}>
                    <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>OR</span>
                    <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
                  </div>

                  <div className="gcs-button-wrapper" style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="btn-global-explore-wrapper">
                      <button
                        className="btn-global-explore"
                        onClick={handleExploreAllDocuments}
                        title="View All Indexed Documents"
                      >
                        <Database size={24} />
                        <span style={{ letterSpacing: '0.02em', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>Explore Global BigQuery Index Preview</span>
                      </button>
                    </div>

                    <div className="btn-gcs-test-wrapper">
                      <button
                        className="btn-gcs-test"
                        onClick={startGcsPipeline}
                        title="Test with GCS File"
                      >
                        <FileSearch size={18} />
                        <span style={{ fontSize: '0.95rem' }}>Run test with Sample Industry File (GCS)</span>
                      </button>
                    </div>
                  </div>
                </div>

                  <input
                    type="file"
                    multiple
                    ref={fileInputRef}
                    style={{ width: 0, height: 0, position: 'absolute', opacity: 0 }}
                    onChange={handleFileSelect}
                  />

                  <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)', margin: '1rem 0' }}></div>

                  {isIndexedLoading && (
                    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(5, 5, 10, 0.8)', backdropFilter: 'blur(8px)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <div style={{ padding: '2rem 3rem', background: 'var(--bg-slate)', border: '1px solid var(--accent-cyan)', borderRadius: '16px', textAlign: 'center', boxShadow: '0 0 40px rgba(34, 211, 238, 0.2)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
                        <div className="pulse-ring" style={{ position: 'absolute', opacity: 0.5 }}></div>
                        <GeminiSparkleIcon className="animate-spin" />
                        <span style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.1em' }} className="pulsing-text">Loading Indexed File...</span>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Retrieving document data and bounding boxes from BigQuery</p>
                      </div>
                    </div>
                  )}

                  <IndexedDocuments onSelectDocument={handleSelectDocument} />
                </div>
            )}
          </div>

          <div className="dashboard-sidebar">
            <div className="chat-container" ref={scrollRef}>
              {messages.map((msg) => (
                <div key={msg.id} className={`chat-bubble-wrapper ${msg.role}`}>
                  <div className="chat-avatar">
                    {msg.role === 'user' ? (
                      <User size={20} />
                    ) : (
                      <div className="bot-avatar-glow"><GeminiSparkleIcon /></div>
                    )}
                  </div>
                  <div className={`chat-bubble ${msg.role}`}>
                    {renderMarkdown(msg.content, msg.chunks)}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="gemini-loading-wrapper">
                  <div className="gemini-search-pill">
                    <GeminiSparkleIcon />
                    <div className="gemini-loading-text">
                      <div className="gemini-loading-title">Google ADK</div>
                      <div className="gemini-loading-subtitle pulsing-text">Synthesizing...</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="input-area">
              <div className="input-wrapper">
                <textarea
                  placeholder="Ask a question about the document..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isLoading}
                  rows={1}
                />
              </div>

              <button
                className="btn primary"
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </main>
      )}
    </>
  );
}

export default App;
