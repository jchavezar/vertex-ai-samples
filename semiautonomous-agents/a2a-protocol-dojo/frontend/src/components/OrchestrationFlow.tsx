import { useState } from 'react';
import { Play } from 'lucide-react';

interface OrcStep {
  step: string;
  message?: string;
  agent?: string;
  agents?: Array<{ port: number; name: string }>;
  response?: string;
  results?: Array<{ agent: string; response: string }>;
}

export default function OrchestrationFlow() {
  const [query, setQuery] = useState('What is A2A?');
  const [steps, setSteps] = useState<OrcStep[]>([]);
  const [activeStep, setActiveStep] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true);
    setError('');
    setSteps([]);
    setActiveStep('');

    try {
      const r = await fetch('/api/demo/orchestration', {
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
        const text = decoder.decode(value);
        for (const line of text.split('\n')) {
          if (line.startsWith('data: ')) {
            const data: OrcStep = JSON.parse(line.slice(6));
            setActiveStep(data.step);
            setSteps(prev => [...prev, data]);
          }
        }
      }
    } catch {
      setError('Backend not running');
    }
    setLoading(false);
  };

  const getNodeClass = (nodeStep: string) => {
    const stepOrder = ['discovery', 'agents_found', 'delegating', 'result', 'complete'];
    const activeIdx = stepOrder.indexOf(activeStep);
    const nodeIdx = stepOrder.indexOf(nodeStep);
    if (activeStep === 'complete') return 'done';
    if (nodeIdx <= activeIdx) return 'active';
    return '';
  };

  const agents = steps.find(s => s.step === 'agents_found')?.agents || [];

  return (
    <div>
      <input
        className="demo-input"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Query to send to all agents..."
        onKeyDown={e => e.key === 'Enter' && run()}
      />
      <button className="demo-button" onClick={run} disabled={loading || !query}>
        {loading ? <div className="loading-spinner" /> : <Play size={16} />}
        Run Orchestration
      </button>

      {error && <div className="demo-error">{error}</div>}

      {steps.length > 0 && (
        <div className="flow-diagram" style={{ marginTop: 20 }}>
          <div className={`flow-node ${getNodeClass('discovery')}`}>Client</div>
          <div className={`flow-connector ${activeStep !== '' ? 'active' : ''}`} />
          <div className={`flow-node ${getNodeClass('agents_found')}`}>Orchestrator</div>
          <div className={`flow-connector ${agents.length > 0 ? 'active' : ''}`} />
          <div className="flow-agents">
            {agents.map(a => (
              <div key={a.port} className={`flow-node ${getNodeClass('result')}`}>
                {a.name} (:{a.port})
              </div>
            ))}
          </div>
        </div>
      )}

      {steps.length > 0 && (
        <div className="event-log" style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, color: '#94a3b8', fontWeight: 600, marginBottom: 8 }}>Orchestration Log</div>
          {steps.map((s, i) => (
            <div key={i} className={`event-log-item${i === steps.length - 1 ? ' new' : ''}`}>
              {s.step === 'discovery' && `Discovering available agents...`}
              {s.step === 'agents_found' && `Found ${s.agents?.length} agent(s): ${s.agents?.map(a => a.name).join(', ')}`}
              {s.step === 'delegating' && `Delegating to ${s.agent} (port ${(s as OrcStep & { port?: number }).port || '?'})...`}
              {s.step === 'result' && `${s.agent} responded: ${s.response?.slice(0, 80)}${(s.response?.length || 0) > 80 ? '...' : ''}`}
              {s.step === 'complete' && `Orchestration complete! ${s.results?.length} responses collected.`}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
