import { useState } from 'react';
import { Play, ChevronRight } from 'lucide-react';

const STATES = ['submitted', 'working', 'completed'];

export default function TaskLifecycle() {
  const [currentState, setCurrentState] = useState<string | null>(null);
  const [events, setEvents] = useState<Array<{ state: string; timestamp: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runDemo = async () => {
    setLoading(true);
    setError('');
    setCurrentState(null);
    setEvents([]);

    try {
      const r = await fetch('/api/demo/task-lifecycle', { method: 'POST' });
      const reader = r.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error('No reader');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            setCurrentState(data.state);
            setEvents(prev => [...prev, { state: data.state, timestamp: data.timestamp }]);
          }
        }
      }
    } catch {
      setError('Backend not running. Start it with: cd backend && uv run uvicorn main:app --port 8000');
    }
    setLoading(false);
  };

  const getStateClass = (state: string) => {
    if (!currentState) return '';
    const currentIdx = STATES.indexOf(currentState);
    const stateIdx = STATES.indexOf(state);
    if (stateIdx < currentIdx) return 'done';
    if (state === currentState) return 'active';
    return '';
  };

  return (
    <div>
      <div className="task-lifecycle">
        {STATES.map((state, i) => (
          <div key={state} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div className={`task-state ${getStateClass(state)}`}>{state}</div>
            {i < STATES.length - 1 && <ChevronRight size={18} className="task-arrow" />}
          </div>
        ))}
      </div>

      <button className="demo-button" onClick={runDemo} disabled={loading}>
        {loading ? <div className="loading-spinner" /> : <Play size={16} />}
        Create Task
      </button>

      {error && <div className="demo-error">{error}</div>}

      {events.length > 0 && (
        <div className="event-log" style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 8, fontWeight: 600 }}>Event Log</div>
          {events.map((e, i) => (
            <div key={i} className={`event-log-item${i === events.length - 1 ? ' new' : ''}`}>
              [{e.timestamp}s] TaskStatusUpdateEvent: state={e.state}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
