import { useState } from 'react';
import { Search } from 'lucide-react';
import { AgentCard } from '../types';

export default function AgentCardViewer() {
  const [card, setCard] = useState<AgentCard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [rawJson, setRawJson] = useState('');

  const fetchCard = async () => {
    setLoading(true);
    setError('');
    try {
      const r = await fetch('/api/agents/8001/card');
      const data = await r.json();
      if (r.ok) {
        setCard(data);
        setRawJson(JSON.stringify(data, null, 2));
      } else {
        setError(data.detail || 'Failed to fetch');
      }
    } catch {
      setError('Echo Agent not running. Start it with: uv run python agents/echo_agent.py');
    }
    setLoading(false);
  };

  return (
    <div>
      <p style={{ marginBottom: 12, color: '#94a3b8', fontSize: 14 }}>
        Fetch the Agent Card from the Echo Agent on port 8001:
      </p>
      <div style={{ marginBottom: 8, fontFamily: 'var(--font-code)', fontSize: 12, color: '#94a3b8' }}>
        GET http://localhost:8001/.well-known/agent-card.json
      </div>
      <button className="demo-button" onClick={fetchCard} disabled={loading}>
        {loading ? <div className="loading-spinner" /> : <Search size={16} />}
        Fetch Agent Card
      </button>

      {error && <div className="demo-error">{error}</div>}

      {card && (
        <div style={{ marginTop: 16 }}>
          <div className="agent-card-display">
            <div className="agent-card-field">
              <span className="agent-card-key">name</span>
              <span className="agent-card-value">{card.name}</span>
            </div>
            <div className="agent-card-field">
              <span className="agent-card-key">description</span>
              <span className="agent-card-value">{card.description}</span>
            </div>
            <div className="agent-card-field">
              <span className="agent-card-key">url</span>
              <span className="agent-card-value">{card.url}</span>
            </div>
            <div className="agent-card-field">
              <span className="agent-card-key">version</span>
              <span className="agent-card-value">{card.version}</span>
            </div>
            <div className="agent-card-field">
              <span className="agent-card-key">capabilities</span>
              <span className="agent-card-value">{JSON.stringify(card.capabilities)}</span>
            </div>
            <div className="agent-card-field">
              <span className="agent-card-key">skills</span>
              <span className="agent-card-value">
                {card.skills?.map(s => `${s.name} (${s.id})`).join(', ')}
              </span>
            </div>
          </div>

          <details style={{ marginTop: 12 }}>
            <summary className="json-toggle">Show raw JSON</summary>
            <div className="demo-output">{rawJson}</div>
          </details>
        </div>
      )}
    </div>
  );
}
