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
            padding: 16px;
            font-family: 'Consolas', 'Monaco', monospace; /* Monospace for tech feel */
            font-size: 11px;
            background: #fafafa;
            min-height: 100%;
        }
        .trace-empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-muted);
            gap: 12px;
        }
        .trace-entry {
            margin-bottom: 16px;
            border-left: 2px solid #ccc;
            padding-left: 12px;
            padding-bottom: 8px;
        }
        .trace-entry.user { border-left-color: #004b87; }
        .trace-entry.assistant { border-left-color: #6c757d; }
        .trace-entry.tool_call { border-left-color: #6f42c1; }
        .trace-entry.tool_result { border-left-color: #28a745; }
        .trace-entry.error { border-left-color: #dc3545; }

        .trace-meta {
            display: flex;
            gap: 8px;
            align-items: center;
            margin-bottom: 4px;
            opacity: 0.8;
        }
        .trace-time { color: #888; font-size: 10px; }
        .trace-type-badge {
            text-transform: uppercase;
            font-weight: 700;
            font-size: 9px;
            padding: 1px 4px;
            border-radius: 3px;
            color: #fff;
        }
        .trace-type-badge.user { background: #004b87; }
        .trace-type-badge.assistant { background: #6c757d; }
        .trace-type-badge.tool_call { background: #6f42c1; }
        .trace-type-badge.tool_result { background: #28a745; }
        .trace-type-badge.error { background: #dc3545; }

        .trace-content {
            color: #333;
            line-height: 1.5;
            word-wrap: break-word; /* Ensure long JSON doesn't overflow */
        }
        .code-snippet {
            background: #f1f3f5;
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
            border: 1px solid #e9ecef;
            margin-top: 4px;
        }
      `}</style>
    </div>
  );
};

const renderContent = (log, isMaximized) => {
  switch (log.type) {
    case 'user':
      return <div style={{ fontWeight: 600 }}>{log.content}</div>;
    case 'assistant':
      // Assuming assistant logs might be markdown chunks
      return <ReactMarkdown remarkPlugins={[remarkGfm]}>{log.content}</ReactMarkdown>;
    case 'tool_call':
      return (
        <div>
          <div><strong>Executing:</strong> {log.tool}</div>
          <div className="code-snippet">
            <pre>{typeof log.args === 'string' ? log.args : JSON.stringify(log.args, null, 2)}</pre>
          </div>
        </div>
      );
    case 'tool_result':
      // Intelligent Formatting for MCP Results
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

      let resultDisplay = '';
      try {
        resultDisplay = JSON.stringify(deepParseJSON(log.result), null, 2);
      } catch (e) {
        resultDisplay = String(log.result);
      }

      return (
        <div>
          <div><strong>Result from:</strong> {log.tool}</div>
          <div className="code-snippet">
            <pre style={{ maxHeight: isMaximized ? '600px' : '300px', overflowY: 'auto', fontSize: '10px' }}>{resultDisplay}</pre>
          </div>
        </div>
      );
    case 'usage':
      return <div style={{ color: '#05603A', fontWeight: 600, background: '#e6fffa', padding: '4px 8px', borderRadius: '4px', border: '1px solid #b2f5ea' }}>{log.content}</div>;
    case 'system':
      return <div style={{ fontStyle: 'italic', color: '#666' }}>{log.content}</div>;
    case 'error':
      return <div style={{ color: '#dc3545', fontWeight: 600 }}>{log.content}</div>;
    case 'text':
      return <div className="markdown-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{String(log.content)}</ReactMarkdown></div>;
    default:
      return <div>{String(log.content || '')}</div>;
  }
};

export default TraceLog;
