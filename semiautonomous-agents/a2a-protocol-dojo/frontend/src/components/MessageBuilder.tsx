import { useState } from 'react';
import { Send } from 'lucide-react';

export default function MessageBuilder() {
  const [message, setMessage] = useState('Hello, echo agent!');
  const [showJson, setShowJson] = useState(false);
  const [response, setResponse] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const jsonPayload = {
    jsonrpc: '2.0',
    id: 'msg-001',
    method: 'message/send',
    params: {
      message: {
        role: 'user',
        parts: [{ kind: 'text', text: message }],
        messageId: 'msg-001',
      },
    },
  };

  const sendMessage = async () => {
    setLoading(true);
    setError('');
    setResponse(null);
    try {
      const r = await fetch('/api/agents/8001/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await r.json();
      if (r.ok) setResponse(data);
      else setError(data.detail || 'Request failed');
    } catch {
      setError('Echo Agent not running. Start it with: uv run python agents/echo_agent.py');
    }
    setLoading(false);
  };

  return (
    <div>
      <input
        className="demo-input"
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="Type your message..."
        onKeyDown={e => e.key === 'Enter' && sendMessage()}
      />

      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <button className="demo-button" onClick={sendMessage} disabled={loading || !message}>
          {loading ? <div className="loading-spinner" /> : <Send size={16} />}
          Send Message
        </button>
        <button className="json-toggle" onClick={() => setShowJson(!showJson)}>
          {showJson ? 'Hide' : 'Show'} JSON-RPC payload
        </button>
      </div>

      {showJson && (
        <div className="demo-output" style={{ marginTop: 12 }}>
          {JSON.stringify(jsonPayload, null, 2)}
        </div>
      )}

      {error && <div className="demo-error">{error}</div>}

      {response && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, color: '#94a3b8', fontWeight: 600, marginBottom: 8 }}>Response</div>
          <div className="demo-output">
            {JSON.stringify(response, null, 2)}
          </div>
        </div>
      )}
    </div>
  );
}
