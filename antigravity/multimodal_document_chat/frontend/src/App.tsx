import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, UploadCloud, FileText } from 'lucide-react';
import { UploadOverlay } from './components/UploadOverlay';
import { ResultsViewer, type PipelineEntity } from './components/ResultsViewer';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

type AppState = 'upload' | 'processing' | 'dashboard';

function App() {
  const [appState, setAppState] = useState<AppState>('upload');
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
      const response = await fetch('/test.pdf');
      const blob = await response.blob();
      const file = new File([blob], 'test.pdf', { type: 'application/pdf' });
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
      setAppState('upload');
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
    // We pre-process the content to wrap citations in a specific span for ReactMarkdown to handle as text nodes,
    // or we can use a simpler approach: regex replace with a custom token and let React handle it.
    // For simplicity with react-markdown, we can parse it dynamically or just use a custom renderer for `text`.
    // Actually, writing a custom text renderer is best.

    // Simpler approach: split by regex and map to React nodes
    const citationRegex = /\[Doc:\s*(.*?),?\s*Page:\s*(\d+|unknown),?\s*Chunk:\s*([^\]]+)\]/g;

    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = citationRegex.exec(content)) !== null) {
      // Push preceding text 
      if (match.index > lastIndex) {
        parts.push(<ReactMarkdown key={`text-${lastIndex}`}>{content.slice(lastIndex, match.index)}</ReactMarkdown>);
      }

      // Push the citation pill
      const [fullMatch, doc, page, chunk] = match;
      const isActive = activeHighlight === chunk;

      parts.push(
        <span
          key={`cite-${match.index}`}
          onClick={() => handleHighlightClick(chunk)}
          className={`citation-pill ${isActive ? 'active' : ''}`}
          title={`View ${doc} - Page ${page}`}
        >
          <FileText size={12} style={{ display: 'inline', marginRight: '4px' }} />
          P{page}
        </span>
      );

      lastIndex = match.index + fullMatch.length;
    }

    // Push remaining text
    if (lastIndex < content.length) {
      parts.push(<ReactMarkdown key={`text-${lastIndex}`}>{content.slice(lastIndex)}</ReactMarkdown>);
    }

    // If no citations found, just render standard markdown
    if (parts.length === 0) {
      return <ReactMarkdown>{content}</ReactMarkdown>;
    }

    return <>{parts}</>;
  };

  return (
    <>
      <header className="app-header">
        <div className="app-title">Nexus Multi-Doc Analyst</div>
      </header>

      {appState === 'upload' && (
        <main className="upload-view">
          <div className="upload-view-title">
            <h1>Document Intelligence</h1>
            <p>Upload a complex PDF document to automatically extract tabular data, detect bounding boxes, and chat securely with the contents.</p>
          </div>

          <div className="hero-dropzone" onClick={() => fileInputRef.current?.click()}>
            <div className="upload-icon-container">
              <UploadCloud size={48} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Click to upload a document</h3>
              <p style={{ color: 'var(--text-secondary)' }}>PDF, PNG, or images</p>
            </div>

            <div className="startup-actions" onClick={e => e.stopPropagation()}>
              <button
                className="btn primary"
                onClick={loadTestPDF}
                title="Load Test PDF"
                style={{ padding: '0.75rem 1.5rem', marginTop: '1rem', width: '100%' }}
              >
                <FileText size={20} />
                Run with Test PDF
              </button>
            </div>
          </div>

          <input
            type="file"
            multiple
            ref={fileInputRef}
            style={{ width: 0, height: 0, position: 'absolute', opacity: 0 }}
            onChange={handleFileSelect}
          />
        </main>
      )}

      {appState === 'processing' && (
        <UploadOverlay isProcessing={true} />
      )}

      {appState === 'dashboard' && (
        <main className="dashboard-layout">
          <div className="dashboard-main">
            {pipelineResult && pipelineResult.pipeline_data && (
              <ResultsViewer
                data={pipelineResult.pipeline_data}
                annotatedImages={pipelineResult.annotated_images}
                traces={pipelineResult.traces}
                activeHighlight={activeHighlight}
                onHighlightClick={handleHighlightClick}
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
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
                <div className="chat-bubble assistant pending">
                  <div className="thinking-dots">
                    <span></span><span></span><span></span>
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
