import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, UploadCloud, FileText } from 'lucide-react';
import { UploadOverlay } from './components/UploadOverlay';
import { ResultsViewer, type PipelineEntity } from './components/ResultsViewer';
import { IndexedDocuments } from './components/IndexedDocuments';
import { Citation } from './components/Citation';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
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
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [pipelineResult, setPipelineResult] = useState<{
    pipeline_data?: PipelineEntity[],
    annotated_images?: string[],
    traces?: any[]
  } | null>(null);

  const [activeHighlight, setActiveHighlight] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('bigquery');

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

  const loadTestPDF = async () => {
    try {
      const response = await fetch('/sample_fictional.pdf');
      const blob = await response.blob();
      const file = new File([blob], 'sample_fictional.pdf', { type: 'application/pdf' });
      startPipeline([file]);
    } catch (e) {
      console.error('Failed to load test PDF', e);
    }
  };

  const startPipeline = async (files: File[]) => {
    setAppState('processing');
    setIsLoading(true);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

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
        traces: data.traces
      });

      setMessages([{
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || "Pipeline process complete. How can I help you analyze this document?",
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
      if (data.pipeline_data && data.pipeline_data.length > 0) {
        setPipelineResult(prev => {
          const existingData = prev?.pipeline_data || [];
          // Simple deduplication by chunk_id
          const newChunks = data.pipeline_data.filter((newChunk: any) =>
            !existingData.some((existingChunk: any) => existingChunk.chunk_id === newChunk.chunk_id)
          );
          return {
            ...prev,
            pipeline_data: [...existingData, ...newChunks],
            annotated_images: prev?.annotated_images || [],
            traces: prev?.traces || []
          };
        });
      }

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || "No text generated.",
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

  const handleHighlightClick = (chunkId: string) => {
    setActiveHighlight(chunkId);
    setActiveTab('bounding-boxes');
  };

  // Custom markdown component to parse citation tags like [Doc: filename, Page: X, Chunk: id]
  const renderMarkdown = (content: string) => {
    // Replace citations with standard markdown links using a custom protocol
    // E.g., parse [1], [2]
    const citationRegex = /\[(\d+)\]/g;
    const processedContent = content.replace(citationRegex, (_match, id) => {
      return `[${id}](#citation-${id})`;
    });

    return (
      <ReactMarkdown
        components={{
          a: ({ node, href, title, children, ...props }) => {
            const isCitation = href && href.startsWith('#citation-');
            if (isCitation) {
              const id = href.replace('#citation-', '');
              const index = parseInt(id) - 1;
              const chunkData = pipelineResult?.pipeline_data?.[index];
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
                activeHighlight={activeHighlight}
                onHighlightClick={handleHighlightClick}
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
            ) : (
              <div style={{ flex: 1, padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem', overflowY: 'auto' }}>
                <div className="upload-view-title" style={{ textAlign: 'left', marginBottom: 0 }}>
                  <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--text-primary), var(--accent-cyan))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Multi-Modal Document Intelligence</h1>
                  <p style={{ maxWidth: '100%', color: 'var(--text-secondary)' }}>Upload a new document or select an indexed document below to start chatting.</p>
                </div>

                  <div className="hero-dropzone" onClick={() => fileInputRef.current?.click()} style={{ padding: '2rem', maxWidth: '100%', width: '100%', display: 'flex', flexDirection: 'row', justifyContent: 'center', textAlign: 'left' }}>
                    <div className="upload-icon-container" style={{ width: '60px', height: '60px', marginBottom: 0, marginRight: '1.5rem' }}>
                      <UploadCloud size={32} />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                      <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem', color: 'var(--text-primary)' }}>Click to upload a new document</h3>
                      <p style={{ color: 'var(--text-secondary)' }}>PDF, PNG, or images</p>
                    </div>
                  </div>

                  <button
                    className="btn outline"
                    onClick={loadTestPDF}
                    title="Load Test PDF"
                    style={{ width: 'FIT-CONTENT', margin: '0 auto', padding: '0.5rem 1rem' }}
                  >
                    <FileText size={16} />
                    Quick Run with Test PDF
                  </button>

                  <input
                    type="file"
                    multiple
                    ref={fileInputRef}
                    style={{ width: 0, height: 0, position: 'absolute', opacity: 0 }}
                    onChange={handleFileSelect}
                  />

                  <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)', margin: '1rem 0' }}></div>

                  <IndexedDocuments
                    onSelectDocument={async (docName) => {
                      try {
                        const res = await fetch(`http://localhost:8001/api/documents/${encodeURIComponent(docName)}/data`);
                        if (res.ok) {
                          const data = await res.json();
                          if (data.session_id) setSession(data.session_id);
                          setPipelineResult(data);
                          setMessages([{
                            id: crypto.randomUUID(),
                            role: 'assistant',
                            content: `Successfully loaded document **${docName}** from the index. How can I help you analyze it?`,
                          }]);
                          setAppState('dashboard');
                        } else {
                          alert('Failed to load document data');
                        }
                      } catch (e) {
                        console.error(e);
                        alert('Error loading document data');
                      }
                    }}
                  />
                </div>
            )}
          </div>

          <div className="dashboard-sidebar">
            <div className="chat-container" ref={scrollRef}>
              {messages.map((msg) => (
                <div key={msg.id} className={`chat-bubble ${msg.role}`}>
                  {renderMarkdown(msg.content)}
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
