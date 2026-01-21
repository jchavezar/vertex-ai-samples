import React, { useRef, useEffect } from 'react';
import { Terminal, Upload, Download, AlertCircle, Clock, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const TraceLog = ({ logs = [], isMaximized = false }) => {
  const endRef = useRef(null);

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  if (!logs || logs.length === 0) {
    return (
      <div className="trace-empty-state">
        <Terminal size={48} color="#e6ebf1" />
        <p>No activity recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="trace-log-container">
      {logs.map((log, idx) => (
        <div key={idx} className={`trace-entry ${log.type}`}>
          <div className="trace-meta">
            <span className="trace-time">{log.timestamp}</span>
            <span className={`trace-type-badge ${log.type}`}>{log.type}</span>
          </div>
          <div className="trace-content">
            {renderContent(log, isMaximized)}
          </div>
        </div>
      ))}
      <div ref={endRef} />

      <style jsx="true">{`
        .trace-log-container {
            padding: 24px;
            font-family: var(--font-mono);
            font-size: 11px;
            background: transparent;
            min-height: 100%;
        }
        .trace-empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-muted);
            gap: 16px;
            opacity: 0.5;
        }
        .trace-entry {
            margin-bottom: 24px;
            border-left: 2px solid var(--border);
            padding-left: 20px;
            padding-bottom: 8px;
            transition: border-color 0.3s;
        }
        .trace-entry.user { border-left-color: var(--brand); }
        .trace-entry.assistant { border-left-color: var(--text-muted); }
        .trace-entry.tool_call { border-left-color: #bb86fc; }
        .trace-entry.tool_result { border-left-color: var(--green); }
        .trace-entry.error { border-left-color: var(--red); }

        .trace-meta {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 8px;
        }
        .trace-time { 
            color: var(--text-muted); 
            font-size: 10px; 
            font-weight: 600;
        }
        .trace-type-badge {
            text-transform: uppercase;
            font-weight: 800;
            font-size: 9px;
            padding: 2px 8px;
            border-radius: 999px;
            color: #fff;
            letter-spacing: 0.5px;
        }
        .trace-type-badge.user { background: var(--brand); }
        .trace-type-badge.assistant { background: var(--text-muted); }
        .trace-type-badge.tool_call { background: #bb86fc; }
        .trace-type-badge.tool_result { background: var(--green); }
        .trace-type-badge.error { background: var(--red); }
        .trace-type-badge.debug { background: #3ea6ff; }
        .trace-type-badge.system { background: rgba(255,255,255,0.1); color: var(--text-secondary); }

        .trace-content {
            color: var(--text-primary);
            line-height: 1.6;
            word-wrap: break-word;
        }
        .code-snippet {
            background: rgba(255, 255, 255, 0.03);
            padding: 12px;
            border-radius: 12px;
            overflow-x: auto;
            border: 1px solid var(--border);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            margin-top: 8px;
        }
      `}</style>
    </div>
  );
};

const deepParseJSON = (obj) => {
  if (typeof obj === 'string') {
    const trimmed = obj.trim();
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
      try {
        return deepParseJSON(JSON.parse(trimmed));
      } catch (e) { return obj; }
    }
  }
  if (Array.isArray(obj)) {
    return obj.map(deepParseJSON);
  }
  if (obj !== null && typeof obj === 'object') {
    const newObj = {};
    for (const key in obj) {
      newObj[key] = deepParseJSON(obj[key]);
    }
    return newObj;
  }
  return obj;
};

const renderContent = (log, isMaximized) => {
  switch (log.type) {
    case 'user':
      return <div style={{ fontWeight: 600 }}>{log.content}</div>;
    case 'assistant':
      return <ReactMarkdown remarkPlugins={[remarkGfm]}>{log.content}</ReactMarkdown>;
    case 'tool_call':
      let argsDisplay = '';
      try {
        argsDisplay = JSON.stringify(deepParseJSON(log.args), null, 2);
      } catch (e) {
        argsDisplay = String(log.args);
      }
      return (
        <div>
          <div><strong>Executing:</strong> {log.tool}</div>
          <div className="code-snippet">
            <pre>{argsDisplay}</pre>
          </div>
        </div>
      );
    case 'tool_result':
      let resultDisplay = '';
      try {
        resultDisplay = JSON.stringify(deepParseJSON(log.result), null, 2);
      } catch (e) {
        resultDisplay = String(log.result);
      }
      return (
        <div>
          <div><strong>Result from:</strong> {log.tool} {log.duration ? <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginLeft: '8px', fontWeight: 'normal' }}>({typeof log.duration === 'number' ? log.duration.toFixed(3) + 's' : log.duration})</span> : null}</div>
          <div className="code-snippet">
            <pre style={{ maxHeight: isMaximized ? '600px' : '300px', overflowY: 'auto', fontSize: '10px' }}>{resultDisplay}</pre>
          </div>
        </div>
      );
    case 'usage':
      return <div style={{ color: '#10b981', fontWeight: 800, background: 'rgba(16, 185, 129, 0.1)', padding: '6px 12px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>{log.content}</div>;
    case 'system':
      return <div style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>{log.content}</div>;
    case 'error':
      return <div style={{ color: 'var(--red)', fontWeight: 800 }}>{log.content}</div>;
    case 'text':
      return <div className="markdown-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{String(log.content)}</ReactMarkdown></div>;
    default:
      return <div>{String(log.content || '')}</div>;
  }
};

export default TraceLog;
