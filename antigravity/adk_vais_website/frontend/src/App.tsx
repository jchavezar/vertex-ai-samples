import { useState } from 'react'
import { Search, Terminal, Database, Sparkles, AlertCircle, Copy, Check, ChevronDown, ChevronUp, Maximize2, Minimize2 } from 'lucide-react'
import './index.css'

interface AgentResult {
  response: string;
  logs: string;
}

interface CompareResponse {
  adk: AgentResult;
  custom: AgentResult;
}

const DebugTerminal = ({ logs, title }: { logs: string; title: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(logs);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toggleMaximize = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMaximized(!isMaximized);
    if (!isMaximized) setIsOpen(true); // Ensure open when maximizing
  };

  // Simple syntax highlighting for JSON-like logs
  const highlightLogs = (text: string) => {
    if (!text) return "No logs available.";
    return text.split('\n').map((line, i) => {
      // split by keys including quotes
      const parts = line.split(/("[^"]+":)/g);
      return (
        <div key={i}>
          {parts.map((part, j) => {
            // Is it a Key?
            if (part.match(/"[^"]+":/)) {
              const isImportant = /"(grounding_metadata|search_data_store|tool_name|function_call|repo_id|model_version)":/.test(part);
              return <span key={j} className={isImportant ? "json-key-important" : "json-key"}>{part}</span>;
            }
            // It's a Value or structural chars. Detect types.
            // Strings (not keys): "[^"]+"
            // Numbers: \b-?\d+(?:\.\d+)?\b
            // Booleans/Null: true|false|null
            const valueParts = part.split(/("[^"]*")|(\b-?\d+(?:\.\d+)?\b)|(\b(?:true|false|null)\b)/g).filter(p => p !== undefined);

            return (
              <span key={j}>
                {valueParts.map((subPart, k) => {
                  if (!subPart) return null;
                  if (subPart.startsWith('"')) return <span key={k} className="json-string">{subPart}</span>;
                  if (/^-?\d+(\.\d+)?$/.test(subPart)) return <span key={k} className="json-number">{subPart}</span>;
                  if (/^(true|false|null)$/.test(subPart)) return <span key={k} className="json-boolean">{subPart}</span>;
                  return <span key={k}>{subPart}</span>;
                })}
              </span>
            );
          })}
        </div>
      );
    });
  };

  return (
    <>
      {/* Backdrop for maximized state */}
      {isMaximized && <div className="terminal-backdrop" onClick={() => setIsMaximized(false)} />}

      <div className={`terminal-wrapper ${isMaximized ? 'maximized' : ''}`}>
        {!isMaximized && (
          <button
            className="toggle-logs-btn"
            onClick={() => setIsOpen(!isOpen)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Terminal size={16} style={{ color: isOpen ? '#8b5cf6' : 'currentColor' }} />
              {isOpen ? 'Hide Debug Logs' : 'View Debug Logs'}
            </div>
            {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        )}

        {(isOpen || isMaximized) && (
          <div className="animate-slide-down" style={{ height: isMaximized ? '100%' : 'auto', display: 'flex', flexDirection: 'column' }}>
            <div className="terminal-header">
              <div className="terminal-controls">
                <div className="control-dot dot-red" onClick={() => setIsMaximized(false)} />
                <div className="control-dot dot-yellow" onClick={() => setIsMaximized(false)} />
                <div className="control-dot dot-green" onClick={toggleMaximize} />
              </div>
              <div className="terminal-title">
                <Terminal size={12} /> {title}
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="copy-btn" onClick={toggleMaximize} title={isMaximized ? "Minimize" : "Maximize"}>
                  {isMaximized ? <Minimize2 size={12} /> : <Maximize2 size={12} />}
                </button>
                <button className="copy-btn" onClick={handleCopy} title="Copy to clipboard">
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <div className="terminal-body" style={{ flexGrow: 1, maxHeight: isMaximized ? 'none' : '400px' }}>
              {highlightLogs(logs)}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<CompareResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8001/api/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="title">
        <Sparkles style={{ display: 'inline', marginRight: '0.5rem', color: '#a855f7' }} />
        Agent Comparison
      </h1>
      <p className="subtitle">Vertex AI Search: Standard ADK vs Custom Client</p>

      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Ask a question (e.g., 'revenue for factset')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          className="search-button"
          onClick={handleSearch}
          disabled={loading || !query.trim()}
        >
          {loading ? (
            <>
              <span className="animate-spin" style={{ marginRight: '0.5rem' }}>⟳</span>
              Searching...
            </>
          ) : (
            <><Search size={20} /> Search</>
          )}
        </button>
      </div>

      {error && (
        <div style={{ color: '#f87171', marginBottom: '2rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '1rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          <AlertCircle style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
          {error}
        </div>
      )}

      {results && (
        <div className="results-grid">
          {/* ADK Agent Card */}
          <div className="result-card">
            <div className="card-header">
              <div className="icon-box adk">
                <Database size={24} />
              </div>
              <div>
                <h2 className="card-title">Standard ADK Tool</h2>
                <p className="card-subtitle">VertexAiSearchTool (High Level)</p>
              </div>
            </div>
            <div className="response-area">
              {results.adk.response}
            </div>
            <DebugTerminal logs={results.adk.logs} title="adk_agent_trace.log" />
          </div>

          {/* Custom Client Agent Card */}
          <div className="result-card">
            <div className="card-header">
              <div className="icon-box custom">
                <Sparkles size={24} />
              </div>
              <div>
                <h2 className="card-title">Custom Discovery Client</h2>
                <p className="card-subtitle">Direct API Control (Low Level)</p>
              </div>
            </div>
            <div className="response-area">
              {results.custom.response}
            </div>
            <DebugTerminal logs={results.custom.logs} title="custom_client_trace.log" />
          </div>
        </div>
      )}
    </div>
  )
}

export default App
