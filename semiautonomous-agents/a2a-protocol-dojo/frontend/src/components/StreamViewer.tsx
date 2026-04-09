import { useState, useRef } from 'react';
import { Zap } from 'lucide-react';

export default function StreamViewer() {
  const [query, setQuery] = useState('Explain the A2A protocol');
  const [streamText, setStreamText] = useState('');
  const [events, setEvents] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const textRef = useRef<HTMLDivElement>(null);

  const stream = async () => {
    setLoading(true);
    setError('');
    setStreamText('');
    setEvents([]);

    try {
      const r = await fetch('/api/agents/8002/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query }),
      });

      const reader = r.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error('No reader');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const raw = line.slice(6);
            setEvents(prev => [...prev, raw]);
            try {
              const data = JSON.parse(raw);
              if (data.artifact?.parts) {
                const text = data.artifact.parts
                  .map((p: Record<string, string>) => p.text || '')
                  .join('');
                if (text) setStreamText(text);
              }
              if (data.result?.artifacts) {
                for (const art of data.result.artifacts) {
                  const text = art.parts?.map((p: Record<string, string>) => p.text || '').join('');
                  if (text) setStreamText(text);
                }
              }
            } catch {
              // non-JSON event
            }
          }
        }
        if (textRef.current) textRef.current.scrollTop = textRef.current.scrollHeight;
      }
    } catch {
      setError('Gemini Agent not running. Start it with: uv run python agents/gemini_agent.py');
    }
    setLoading(false);
  };

  return (
    <div>
      <input
        className="demo-input"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Type your query..."
        onKeyDown={e => e.key === 'Enter' && stream()}
      />
      <button className="demo-button" onClick={stream} disabled={loading || !query}>
        {loading ? <div className="loading-spinner" /> : <Zap size={16} />}
        Stream Response
      </button>

      {error && <div className="demo-error">{error}</div>}

      {(streamText || events.length > 0) && (
        <div className="stream-viewer">
          <div className="stream-panel">
            <div className="stream-panel-header">Response Text</div>
            <div className="stream-panel-body" ref={textRef}>
              {streamText || <span style={{ color: '#64748b' }}>Waiting for response...</span>}
            </div>
          </div>
          <div className="stream-panel">
            <div className="stream-panel-header">SSE Events ({events.length})</div>
            <div className="stream-panel-body">
              {events.map((e, i) => (
                <div key={i} style={{ marginBottom: 8, color: i === events.length - 1 ? '#e2e8f0' : '#64748b', fontSize: 11 }}>
                  <span style={{ color: '#6366f1' }}>event {i + 1}:</span> {e.length > 120 ? e.slice(0, 120) + '...' : e}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
