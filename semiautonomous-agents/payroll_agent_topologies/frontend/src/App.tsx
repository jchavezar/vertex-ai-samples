import React, { useState } from 'react'
import { Play, Layers, ShieldAlert, Cpu, Database, HelpCircle, Activity } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant';
  content: string;
  latency?: number;
  routerDecision?: string;
  timestamp: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'playground' | 'docs'>('playground');
  const [topology, setTopology] = useState<'t1' | 't2'>('t1');
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingTime, setThinkingTime] = useState(0.0);
  const [currentLatency, setCurrentLatency] = useState<number | null>(null);
  const [currentDecision, setCurrentDecision] = useState<string | null>(null);

  // Predefined shortcut questions
  const SHORTCUTS = [
    {
      label: '1. Cross-Domain (PTO & Expense)',
      query: 'Hi, I am employee EMP101. What is my current accrued PTO balance, and do I have any pending reimbursement claims?',
      badge: 'CROSS-DOMAIN'
    },
    {
      label: '2. PTO Balance (Attendance)',
      query: 'Check my accrued PTO balance, I am employee EMP102.',
      badge: 'ATTENDANCE'
    },
    {
      label: '3. Get W-2 Statement (Tax)',
      query: 'I am employee EMP101. Please retrieve my W-2 statement for the tax year 2025.',
      badge: 'EARNINGS'
    },
    {
      label: '4. Direct Deposit (Expenses)',
      query: 'I am employee EMP102. Submit a reimbursement claim for $120.00 for category "Meals" with description "Team dinner".',
      badge: 'EXPENSES'
    }
  ];

  const handleShortcutClick = (q: string) => {
    setQuery(q);
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isThinking) return;

    const userMsg = query;
    setQuery('');
    setChatHistory(prev => [...prev, {
      role: 'user',
      content: userMsg,
      timestamp: new Date().toLocaleTimeString()
    }]);

    setIsThinking(true);
    setThinkingTime(0.0);

    // Start a timer for thinking UI
    const timerInterval = setInterval(() => {
      setThinkingTime(t => parseFloat((t + 0.1).toFixed(1)));
    }, 100);

    try {
      const response = await fetch('http://localhost:8099/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: userMsg, topology })
      });

      const data = await response.json();
      clearInterval(timerInterval);

      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        latency: data.latency,
        routerDecision: data.router_decision,
        timestamp: new Date().toLocaleTimeString()
      }]);

      setCurrentLatency(data.latency);
      setCurrentDecision(data.router_decision);
    } catch (err) {
      clearInterval(timerInterval);
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: `Error connecting to backend: ${err}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#faf9f6] text-[#1a1a19] font-sans antialiased">
      
      {/* Yazdani Architectural Linear Header */}
      <header className="border-b border-[#d8d6d0] bg-[#faf9f6] px-10 py-5 flex-shrink-0">
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-4">
            <span className="font-bold text-xl tracking-[0.08em] uppercase text-[#1a1a19]">
              SYSTEM: PAYROLL TOPOLOGIES
            </span>
            <span className="text-xs text-[#7c7a75] tracking-widest uppercase">
              / EVALUATION PROVING GROUNDS
            </span>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-[10px] font-mono text-[#7c7a75] uppercase">
              <span className="h-2 w-2 bg-emerald-500 inline-block animate-pulse"></span>
              GCP: us-central1 (vtxdemos)
            </div>
            <span className="text-[10px] border border-[#d8d6d0] px-2 py-0.5 font-mono text-[#1a1a19]">
              ADK v2.3.0
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        
        {/* Left Side: Evaluation Dashboard */}
        <div className="flex-1 overflow-y-auto p-10 border-r border-[#d8d6d0]">
          
          <div className="max-w-4xl space-y-10">
            
            {/* Project Overview Card */}
            <div className="border border-[#d8d6d0] p-6 bg-[#faf9f6] rounded-none">
              <div className="flex items-center gap-3 mb-3">
                <Activity className="h-5 w-5 text-[#1a1a19]" />
                <h3 className="font-bold text-sm tracking-wider uppercase">THE CONCURRENCY CHALLENGE</h3>
              </div>
              <p className="text-sm text-[#7c7a75] leading-relaxed">
                Evaluating a payroll application with <strong>24 REST endpoints / tools</strong> under a simulated load of 
                <strong> 148,000 concurrent executions</strong>. This proving grounds compares a single, fully-equipped agent (Topology 1) 
                against an LLM-routed sub-agent pipeline (Topology 2).
              </p>
            </div>

            {/* Matrix comparison */}
            <div className="space-y-4">
              <div className="flex justify-between items-baseline border-b border-[#d8d6d0] pb-2">
                <h3 className="font-bold text-xs tracking-widest uppercase text-[#7c7a75]">
                  01 // EVALUATION BENCHMARKS MATRIX
                </h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#d8d6d0] uppercase text-[#7c7a75]">
                      <th className="py-3 font-semibold">METRIC / ATTRIBUTE</th>
                      <th className="py-3 font-semibold bg-[#f4f3ef] px-3">T1: SINGLE MONOLITH</th>
                      <th className="py-3 font-semibold">T2: LLM ROUTER WORKFLOW</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#d8d6d0]">
                    <tr>
                      <td className="py-3 font-medium uppercase">Avg. Latency</td>
                      <td className="py-3 bg-[#f4f3ef] px-3 font-mono font-semibold text-emerald-700">~4.9s - 5.9s 🟢</td>
                      <td className="py-3 font-mono text-red-700">~8.1s - 14.5s 🔴</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-medium uppercase">Cross-Domain Queries</td>
                      <td className="py-3 bg-[#f4f3ef] px-3 text-emerald-700 font-semibold">Supported (100%) 🟢</td>
                      <td className="py-3 text-red-700">Fails (routes to 1 subagent) 🔴</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-medium uppercase">Tool Confusion Risks</td>
                      <td className="py-3 bg-[#f4f3ef] px-3 text-[#7c7a75]">Medium (24 tools in context)</td>
                      <td className="py-3 text-[#1a1a19] font-medium">None (4-6 tools per agent)</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-medium uppercase">Token Cost (Input Size)</td>
                      <td className="py-3 bg-[#f4f3ef] px-3 text-red-700">High (~4k tool tokens)</td>
                      <td className="py-3 text-emerald-700 font-semibold">Low (~1k per agent) 🟢</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-medium uppercase">LLM Calls at Peak</td>
                      <td className="py-3 bg-[#f4f3ef] px-3 text-emerald-700 font-semibold">148,000 (1x) 🟢</td>
                      <td className="py-3 text-red-700">296,000 (2x turns) 🔴</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Architecture Section */}
            <div className="space-y-4">
              <h3 className="font-bold text-xs tracking-widest uppercase text-[#7c7a75]">
                02 // DATAFLOW ARCHITECTURES
              </h3>
              
              <div className="grid grid-cols-2 gap-6">
                {/* T1 */}
                <div className="border border-[#d8d6d0] p-6 bg-[#f4f3ef] rounded-none">
                  <h4 className="font-bold text-xs uppercase mb-4 text-[#1a1a19]">Topology 1: Monolithic Agent</h4>
                  <div className="font-mono text-[10px] text-[#7c7a75] leading-normal bg-white p-3 border border-[#d8d6d0]">
                    [User Query]  <br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;│<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;▼<br/>
                    ┌─────────────────────────┐<br/>
                    │ &nbsp;&nbsp;&nbsp;&nbsp;LlmAgent (Root) &nbsp;&nbsp;&nbsp;&nbsp;│ &lt;─ Access to 24 Tools<br/>
                    └────────────┬────────────┘<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Final Answer]<br/>
                  </div>
                </div>

                {/* T2 */}
                <div className="border border-[#d8d6d0] p-6 bg-[#f4f3ef] rounded-none">
                  <h4 className="font-bold text-xs uppercase mb-4 text-[#1a1a19]">Topology 2: LLM Router Workflow</h4>
                  <div className="font-mono text-[10px] text-[#7c7a75] leading-normal bg-white p-3 border border-[#d8d6d0]">
                    [User Query] ➔ [Router Agent] ➔ [Route Evaluator]<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┌───────────────┼───────────────┐<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Attendance) &nbsp;&nbsp;&nbsp;(Expenses) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Profile)<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┌──────────┐ &nbsp;&nbsp;&nbsp;┌──────────┐ &nbsp;&nbsp;&nbsp;┌──────────┐<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│Attendance│ &nbsp;&nbsp;&nbsp;│ Expenses │ &nbsp;&nbsp;&nbsp;│ Profile  │<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──────────┘ &nbsp;&nbsp;&nbsp;└──────────┘ &nbsp;&nbsp;&nbsp;└──────────┘<br/>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="border-t border-[#d8d6d0] pt-6">
              <h3 className="font-bold text-xs tracking-widest uppercase text-[#7c7a75] mb-4">
                03 // PRODUCTION RECOMMENDATIONS FOR 148K CONCURRENCY
              </h3>
              <ul className="text-xs text-[#7c7a75] space-y-3 list-disc pl-5">
                <li>
                  <strong className="text-[#1a1a19]">Never Spawn Stdio Subprocesses at Scale:</strong> The server will crash. The MCP server must be deployed to Google Cloud Run utilizing Server-Sent Events (SSE).
                </li>
                <li>
                  <strong className="text-[#1a1a19]">Enable Vertex AI Context Caching:</strong> Cache the 24 static tool definitions to reduce input token billing and cut Time to First Token (TTFT) by over 80%.
                </li>
                <li>
                  <strong className="text-[#1a1a19]">Implement a Deterministic Router:</strong> Bypass the LLM for routing (Topology 3). Use lightweight regex or local embeddings to map tools, and trigger sub-agents in parallel when compound questions are identified.
                </li>
              </ul>
            </div>

          </div>

        </div>

        {/* Right Side: Flat Technical Chat Console */}
        <div className="w-[450px] flex flex-col bg-[#f4f3ef] border-l border-[#d8d6d0]">
          
          {/* Console Header */}
          <div className="px-6 py-5 border-b border-[#d8d6d0] flex flex-col gap-3">
            <div className="flex items-baseline justify-between">
              <h3 className="font-bold text-[#1a1a19] text-sm tracking-widest uppercase">CONVERSATIONAL TRIAL</h3>
              <span className="text-[9px] text-[#7c7a75] uppercase font-mono">STANDALONE APP</span>
            </div>
            
            {/* Topology Select Toggle */}
            <div className="flex border border-[#d8d6d0]">
              <button 
                onClick={() => setTopology('t1')}
                className={`flex-1 py-1.5 text-[10px] font-mono font-bold tracking-wider uppercase border-none rounded-none transition-all ${
                  topology === 't1' 
                    ? 'bg-[#1a1a19] text-[#faf9f6]' 
                    : 'bg-[#faf9f6] text-[#7c7a75] hover:bg-[#f4f3ef]'
                }`}
              >
                T1: Monolith
              </button>
              <button 
                onClick={() => setTopology('t2')}
                className={`flex-1 py-1.5 text-[10px] font-mono font-bold tracking-wider uppercase border-none rounded-none transition-all ${
                  topology === 't2' 
                    ? 'bg-[#1a1a19] text-[#faf9f6]' 
                    : 'bg-[#faf9f6] text-[#7c7a75] hover:bg-[#f4f3ef]'
                }`}
              >
                T2: Router Workflow
              </button>
            </div>
          </div>

          {/* Shortcuts Panel */}
          <div className="p-6 border-b border-[#d8d6d0] bg-[#faf9f6] space-y-3">
            <span className="text-[10px] font-bold text-[#7c7a75] tracking-widest uppercase block">
              SHORTCUT QUESTIONS (TEST CASES)
            </span>
            <div className="grid grid-cols-1 gap-2">
              {SHORTCUTS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleShortcutClick(s.query)}
                  className="w-full text-left p-3 border border-[#d8d6d0] bg-[#faf9f6] hover:bg-[#f4f3ef] transition-colors rounded-none flex flex-col gap-1"
                >
                  <div className="flex justify-between items-center w-full">
                    <span className="font-bold text-[10px] text-[#1a1a19] tracking-wide uppercase">
                      {s.label.split('(')[0]}
                    </span>
                    <span className="text-[8px] bg-[#1a1a19] text-[#faf9f6] px-1 font-mono uppercase">
                      {s.badge}
                    </span>
                  </div>
                  <span className="text-[11px] text-[#7c7a75] truncate w-full">
                    {s.query}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Chat Messages Log */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {chatHistory.length === 0 && (
              <div className="h-full flex items-center justify-center text-center p-6">
                <p className="text-xs text-[#7c7a75] uppercase tracking-wide">
                  Console idle. Select a shortcut question above or write your own to begin testing.
                </p>
              </div>
            )}

            {chatHistory.map((msg, idx) => (
              <div key={idx} className="flex flex-col w-full">
                <span className="text-[9px] font-bold text-[#7c7a75] tracking-wider uppercase mb-1">
                  {msg.role === 'user' ? 'USER' : `AGENT [${topology.toUpperCase()}]`} • {msg.timestamp}
                </span>
                <div className={`text-xs pl-3 border-l-2 leading-relaxed font-sans ${
                  msg.role === 'user' 
                    ? 'border-[#7c7a75] text-[#7c7a75]' 
                    : 'border-[#1a1a19] text-[#1a1a19]'
                }`}>
                  {msg.content}
                  
                  {msg.role === 'assistant' && msg.latency && (
                    <div className="mt-2 pt-1.5 border-t border-dotted border-[#d8d6d0] flex justify-between font-mono text-[9px] text-[#7c7a75]">
                      <span>[LATENCY: {msg.latency.toFixed(2)}s]</span>
                      {msg.routerDecision && (
                        <span className="truncate max-w-[200px]" title={msg.routerDecision}>
                          [ROUTE: {msg.routerDecision.split(' - ')[0]}]
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Thinking indicator */}
            {isThinking && (
              <div className="flex flex-col w-full">
                <span className="text-[9px] font-bold text-[#7c7a75] tracking-wider uppercase mb-1">
                  AGENT [{topology.toUpperCase()}]
                </span>
                <div className="text-xs pl-3 border-l-2 border-[#1a1a19] text-[#7c7a75] font-mono flex items-center gap-2">
                  <span className="yazdani-spinner" /> 
                  <span className="sweep-text">Thinking... {thinkingTime.toFixed(1)}s</span>
                </div>
              </div>
            )}
          </div>

          {/* Console Text Input */}
          <div className="p-6 border-t border-[#d8d6d0] bg-[#faf9f6]">
            <form onSubmit={handleSend} className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Write custom question here..."
                disabled={isThinking}
                className="flex-1 text-xs bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-3 text-[#1a1a19] focus:outline-none focus:border-[#1a1a19] rounded-none disabled:opacity-50"
              />
              <button 
                type="submit"
                disabled={isThinking || !query.trim()}
                className="bg-[#1a1a19] text-[#faf9f6] hover:bg-[#333333] active:bg-black px-6 py-3 text-[10px] font-bold tracking-widest uppercase rounded-none transition-colors disabled:opacity-50"
              >
                Send
              </button>
            </form>
          </div>

        </div>

      </div>

    </div>
  )
}
