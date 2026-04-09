import { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import { AgentInfo, AgentSkill } from '../types';

interface SkillEntry {
  skill: AgentSkill;
  agentName: string;
  agentPort: number;
}

export default function SkillsBrowser() {
  const [skills, setSkills] = useState<SkillEntry[]>([]);
  const [selected, setSelected] = useState<SkillEntry | null>(null);
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/agents')
      .then(r => r.json())
      .then((agents: AgentInfo[]) => {
        const all: SkillEntry[] = [];
        for (const agent of agents) {
          if (agent.card?.skills) {
            for (const skill of agent.card.skills) {
              all.push({ skill, agentName: agent.card.name || agent.name, agentPort: agent.port });
            }
          }
        }
        setSkills(all);
      })
      .catch(() => setError('Backend not running'));
  }, []);

  const invoke = async () => {
    if (!selected || !input) return;
    setLoading(true);
    setResponse('');
    try {
      const r = await fetch(`/api/agents/${selected.agentPort}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await r.json();
      setResponse(JSON.stringify(data, null, 2));
    } catch {
      setResponse('Error: Agent not reachable');
    }
    setLoading(false);
  };

  return (
    <div>
      {error && <div className="demo-error">{error}</div>}

      <div className="skills-grid">
        {skills.map((entry, i) => (
          <div
            key={i}
            className="skill-card"
            onClick={() => {
              setSelected(entry);
              setInput(entry.skill.examples?.[0] || '');
              setResponse('');
            }}
            style={selected?.skill.id === entry.skill.id && selected?.agentPort === entry.agentPort
              ? { borderColor: '#6366f1' }
              : {}
            }
          >
            <div className="skill-card-name">{entry.skill.name}</div>
            <div className="skill-card-agent">{entry.agentName} (:{entry.agentPort})</div>
            <div className="skill-card-desc">{entry.skill.description}</div>
            <div className="skill-tags">
              {entry.skill.tags?.map(tag => (
                <span key={tag} className="skill-tag">{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {skills.length === 0 && !error && (
        <p style={{ color: '#94a3b8', fontSize: 14 }}>No agents running. Start the agents first.</p>
      )}

      {selected && (
        <div style={{ marginTop: 20 }}>
          <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>
            Invoke: {selected.skill.name} ({selected.agentName})
          </div>
          <input
            className="demo-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Enter query..."
            onKeyDown={e => e.key === 'Enter' && invoke()}
          />
          <button className="demo-button" onClick={invoke} disabled={loading || !input}>
            {loading ? <div className="loading-spinner" /> : <Send size={16} />}
            Invoke Skill
          </button>
          {response && <div className="demo-output" style={{ marginTop: 12 }}>{response}</div>}
        </div>
      )}
    </div>
  );
}
