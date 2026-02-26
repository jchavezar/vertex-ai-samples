'use client';

import { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [events, setEvents] = useState<{ role: string, text: string }[]>([]);

  const handleRun = () => {
    if (!query) return;
    setEvents([...events, { role: 'user', text: query }]);
    // Mocking agent response
    setTimeout(() => {
      setEvents(prev => [...prev, { role: 'agent', text: "Processing forensic data... Orchestrating Audit and Tax agents." }]);
    }, 1000);
    setQuery('');
  };

  return (
    <div>
      <div className="card">
        <h2>Multi-Agent Orchestrator</h2>
        <div className="flow-graph">
          [ Generative Flow Graph: Audit -> Tax -> Synthesis ]
        </div>
        <div style={{ marginTop: '20px' }}>
          {events.map((e, i) => (
            <div key={i} style={{ marginBottom: '10px', padding: '10px', background: e.role === 'user' ? '#f0f0f0' : '#e3f2fd', borderLeft: `4px solid ${e.role === 'user' ? '#999' : '#00338D'}` }}>
              <strong>{e.role.toUpperCase()}:</strong> {e.text}
            </div>
          ))}
        </div>
        <input 
          type="text" 
          className="chat-input" 
          placeholder="Ask Verity to analyze a transaction or check compliance..." 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleRun()}
        />
        <button className="btn-primary" onClick={handleRun} style={{ marginTop: '10px' }}>Execute AI Flow</button>
      </div>

      <div className="card">
        <h3>Evidence Dashboard</h3>
        <p>Upload CSV or JSON evidence for forensic analysis.</p>
        <button className="btn-primary">Upload Evidence</button>
      </div>
    </div>
  );
}
