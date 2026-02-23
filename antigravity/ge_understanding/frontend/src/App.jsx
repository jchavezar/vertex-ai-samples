import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Terminal,
  Send,
  Cpu,
  Activity,
  Fingerprint,
  Database,
  ChevronRight,
  Shield,
  Zap,
  Box,
  Layout,
  Trash2,
  RefreshCcw,
  Search,
  Command,
  ArrowRight,
  ShieldCheck,
  ShieldX,
  Play
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const cn = (...inputs) => twMerge(clsx(inputs));

const BACKEND_URL = "http://127.0.0.1:8001";

// --- Components ---

const Header = () => (
  <header className="h-20 border-b border-slate-200 bg-white/80 backdrop-blur-xl flex items-center justify-between px-8 sticky top-0 z-50">
    <div className="flex items-center gap-4">
      <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center shadow-lg shadow-slate-200">
        <Cpu size={22} className="text-white" />
      </div>
      <div className="flex flex-col">
        <h1 className="text-sm font-black tracking-tight text-slate-900 mono">
          GE_INTERCEPTOR_V2
        </h1>
        <div className="text-[9px] text-slate-400 mono font-bold tracking-widest uppercase">
          Payload Security Layer
        </div>
      </div>
    </div>
    <div className="flex items-center gap-6 text-[10px] mono text-slate-500 font-bold uppercase tracking-wider hidden md:flex">
      <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-full border border-green-100">
        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
        SYSTEM_STABLE
      </div>
      <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full border border-blue-100">
        NODE: US-CENTRAL1
      </div>
    </div>
  </header>
);

const ChatInput = ({ onSend, disabled }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput("");
    }
  };

  return (
    <div className="px-8 pb-8 pt-4 bg-gradient-to-t from-white via-white/90 to-transparent">
      <form onSubmit={handleSubmit} className="relative group">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="ENTER_COMMAND_OR_QUERY..."
          className="w-full bg-slate-50 border border-slate-200 rounded-2xl h-14 pl-14 pr-14 focus:outline-none focus:border-slate-900 focus:ring-4 focus:ring-slate-900/5 mono text-slate-900 transition-all text-sm placeholder:text-slate-400 font-bold shadow-sm"
          disabled={disabled}
        />
        <div className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-slate-900 transition-colors">
          <Terminal size={20} />
        </div>
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:bg-slate-200 disabled:text-slate-400 transition-all shadow-md active:scale-95"
        >
          <ArrowRight size={20} />
        </button>
      </form>
    </div>
  );
};

const PayloadPane = ({ payload }) => {
  return (
    <div className="flex flex-col h-full bg-slate-50 border-x border-slate-200 overflow-hidden">
      <div className="h-12 border-b border-slate-200 bg-white flex items-center px-6 justify-between shrink-0">
        <div className="text-[10px] mono text-slate-900 font-black tracking-widest uppercase flex items-center gap-2">
          <Fingerprint size={12} className="text-blue-600" />
          INTERCEPTION_HUD
        </div>
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />
          <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />
          <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        {payload ? (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="text-[10px] mono font-bold text-slate-400 uppercase tracking-tighter">RESOURCE_TARGET</div>
                <div className="px-2 py-0.5 bg-slate-900 text-white text-[8px] mono rounded font-bold uppercase tracking-widest">
                  Verified
                </div>
              </div>
              <div className="text-slate-900 mono text-[11px] break-all leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100 italic">
                {payload.resource_name || 'UNDEFINED_RESOURCE'}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <div className="text-[8px] text-slate-400 mono font-bold uppercase tracking-tighter mb-1">METHOD</div>
                <div className="text-slate-900 font-black mono text-[11px] truncate">
                  {payload.method || 'UNSET'}
                </div>
              </div>
              <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <div className="text-[8px] text-slate-400 mono font-bold uppercase tracking-tighter mb-1">STREAMEABLE</div>
                <div className="text-blue-600 font-black mono text-[11px]">
                  TRUE
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-[9px] mono font-bold text-slate-400 uppercase pl-1">
                <Activity size={10} />
                RAW_ENVELOPE_DATA
              </div>
              <pre className="text-slate-700 leading-relaxed whitespace-pre-wrap break-all text-[11px] bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mono">
                {JSON.stringify(payload.parsed_payload || payload, null, 2)}
              </pre>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-300">
            <div className="w-16 h-16 bg-slate-100 rounded-3xl flex items-center justify-center mb-4">
              <Database size={32} />
            </div>
            <p className="tracking-[0.2em] text-[9px] font-black uppercase text-slate-400">Listening for activity...</p>
          </div>
        )}
      </div>
    </div>
  );
};

const AgentManager = ({ agents, geAgents, selectedId, onSelect, onRefresh, onDelete, onRegisterGE, onDeregisterGE, onTestSearch, onDeploy, isGeLoading, geMode, setGeMode, geQuery, setGeQuery }) => {
  const [activeTab, setActiveTab] = useState('ENGINE');

  const currentAgents = activeTab === 'ENGINE' ? agents : geAgents;
  const countLabel = activeTab === 'ENGINE' ? 'ENGINES_AVAILABLE' : 'ENTERPRISE_AGENTS';

  return (
    <div className="w-[400px] flex flex-col bg-white h-full overflow-hidden border-l border-slate-100 shadow-xl z-10 transition-all duration-300">

      {/* Header & Tabs */}
      <div className="flex flex-col border-b border-slate-100 bg-slate-50/80 backdrop-blur-sm shrink-0">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2 text-slate-700 font-mono text-xs font-bold tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            AGENT_CONTROL_TOWER
          </div>
          <button
            onClick={onRefresh}
            className="p-1.5 hover:bg-slate-200 rounded-md text-slate-500 transition-colors"
            title="Refresh Agents"
          >
            <RefreshCcw size={14} className={cn(isGeLoading && "animate-spin")} />
          </button>
        </div>

        <div className="px-4 pb-3">
          <div className="flex bg-slate-200/50 p-1 rounded-lg gap-1">
            <button
              onClick={() => setActiveTab('ENGINE')}
              className={cn(
                "flex-1 py-1.5 rounded-md text-[10px] mono font-bold transition-all flex items-center justify-center gap-2",
                activeTab === 'ENGINE'
                  ? "bg-white text-slate-900 shadow-sm ring-1 ring-slate-200"
                  : "text-slate-500 hover:text-slate-700 hover:bg-slate-200/50"
              )}
            >
              <Box size={12} />
              AGENT_ENGINE
            </button>
            <button
              onClick={() => setActiveTab('ENTERPRISE')}
              className={cn(
                "flex-1 py-1.5 rounded-md text-[10px] mono font-bold transition-all flex items-center justify-center gap-2",
                activeTab === 'ENTERPRISE'
                  ? "bg-white text-indigo-600 shadow-sm ring-1 ring-indigo-100"
                  : "text-slate-500 hover:text-indigo-600 hover:bg-indigo-50/50"
              )}
            >
              <ShieldCheck size={12} />
              GEMINI_ENTERPRISE
            </button>
          </div>
        </div>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
        <div className="px-2 py-1 flex justify-between items-center text-[10px] font-mono text-slate-400 uppercase tracking-wider">
          <span>{countLabel}</span>
          <span>{currentAgents.length}</span>
        </div>

        {currentAgents.length === 0 && (
          <div className="flex flex-col items-center justify-center h-32 text-slate-400 text-xs font-mono opacity-60">
            <Activity size={24} className="mb-2 opacity-50" />
            <span>NO_AGENTS_FOUND</span>
          </div>
        )}

        {currentAgents.map((agent) => (
          <div
            key={agent.uid}
            onClick={() => onSelect(agent.uid)}
            className={cn(
              "group relative p-3 rounded-xl border transition-all cursor-pointer hover:shadow-sm",
              selectedId === agent.uid
                ? "bg-slate-900 text-white border-slate-900 ring-2 ring-slate-900 ring-offset-2 z-10"
                : "bg-white border-slate-100 hover:border-slate-300 text-slate-600"
            )}
          >
            <div className="flex justify-between items-start mb-1">
              <h3 className={cn(
                "font-bold text-xs font-mono truncate pr-6 transition-colors",
                selectedId === agent.uid ? "text-white" : "text-slate-700"
              )}>{agent.display_name}</h3>

              <div className="flex gap-1">
                {agent.is_ge_agent && (
                  <span className="px-1.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-500 text-[9px] font-bold border border-indigo-500/20">
                    GE
                  </span>
                )}
                {agent.isInterceptor && !agent.is_ge_agent && (
                  <span className="px-1.5 py-0.5 rounded-full bg-blue-500/10 text-blue-500 text-[9px] font-bold border border-blue-500/20">
                    INT
                  </span>
                )}
              </div>
            </div>

            <div className={cn(
              "text-[10px] font-mono mb-2 truncate transition-colors",
              selectedId === agent.uid ? "text-slate-400" : "text-slate-400"
            )}>
              ID: {agent.uid.substring(0, 18)}...
            </div>

            {agent.reasoning_engine_link && (
              <div className="flex items-center gap-1 text-[9px] text-emerald-500 font-mono bg-emerald-500/5 px-2 py-1 rounded-md border border-emerald-500/10 w-fit">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                LINKED: {agent.reasoning_engine_link.split('/').pop().substring(0, 8)}...
              </div>
            )}

            {/* Actions Toolbar - Only visible on hover or selected */}
            <div className={cn(
              "absolute right-2 top-2 flex flex-col gap-1 transition-all duration-200",
              selectedId === agent.uid ? "opacity-100 translate-x-0" : "opacity-0 translate-x-2 group-hover:opacity-100 group-hover:translate-x-0"
            )}>
              {/* Contextual Actions based on type */}
              {!agent.is_ge_agent && (
                <button
                  onClick={(e) => { e.stopPropagation(); onDelete(agent.uid, agent.display_name); }}
                  className="p-1.5 rounded-md hover:bg-rose-500 hover:text-white text-slate-300 transition-colors"
                  title="Delete Engine"
                >
                  <Trash2 size={12} />
                </button>
              )}

              {!agent.is_ge_agent ? (
                <button
                  onClick={(e) => { e.stopPropagation(); onRegisterGE(agent.resource_name); }}
                  className="p-1.5 rounded-md hover:bg-indigo-500 hover:text-white text-slate-300 transition-colors"
                  title="Register in Gemini Enterprise"
                >
                  <ShieldCheck size={12} />
                </button>
              ) : (
                <button
                  onClick={(e) => { e.stopPropagation(); onDeregisterGE(agent.resource_name); }}
                  className="p-1.5 rounded-md hover:bg-rose-500 hover:text-white text-slate-300 transition-colors"
                  title="Deregister from Gemini Enterprise"
                >
                  <ShieldX size={12} />
                </button>
              )}
            </div>

            {/* Expanded Controls for Selected Agent */}
            {selectedId === agent.uid && (
              <div className="mt-3 pt-3 border-t border-slate-700/50 space-y-2 animate-in slide-in-from-top-2 fade-in duration-200">
                <div className="flex items-center gap-1 bg-slate-800/50 p-1 rounded-lg">
                  <input
                    type="text"
                    value={geQuery}
                    onChange={(e) => setGeQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && onTestSearch(agent.uid, geQuery, geMode)}
                    placeholder="Test Agent..."
                    className="bg-transparent border-none text-white text-[10px] w-full focus:ring-0 px-2 placeholder:text-slate-500"
                  />
                  <button
                    onClick={(e) => { e.stopPropagation(); onTestSearch(agent.uid, geQuery, geMode); }}
                    className="p-1.5 bg-blue-600 hover:bg-blue-500 rounded-md text-white transition-colors"
                  >
                    <Play size={10} />
                  </button>
                </div>
                <div className="flex justify-between px-1">
                  <div className="flex gap-1">
                    {['SEARCH', 'ANSWER'].map(m => (
                      <button
                        key={m}
                        onClick={(e) => { e.stopPropagation(); setGeMode(m); }}
                        className={cn(
                          "px-2 py-0.5 text-[8px] rounded font-bold transition-colors",
                          geMode === m ? "bg-blue-500/20 text-blue-400" : "text-slate-500 hover:text-slate-400"
                        )}
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer Actions */}
      <div className="p-3 bg-slate-50 border-t border-slate-100">
        <button
          onClick={onDeploy}
          disabled={isGeLoading}
          className="w-full py-2 bg-slate-900 text-white rounded-lg text-xs font-bold font-mono hover:bg-slate-800 transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          {isGeLoading ? <RefreshCcw size={12} className="animate-spin" /> : <Command size={12} className="group-hover:scale-110 transition-transform" />}
          DEPLOY_NEW_ENGINE
        </button>
      </div>
    </div>
  );
};

// --- Layout Wrapper for Scrolling Fix ---
const LayoutStyles = () => (
  <style dangerouslySetInnerHTML={{
    __html: `
    .monolith-grid {
      display: grid;
      grid-template-columns: 1fr;
      height: 100%;
    }
    @media (min-width: 1024px) {
      .monolith-grid {
        grid-template-columns: 1fr 340px !important;
      }
    }
    @media (min-width: 1280px) {
      .monolith-grid {
        grid-template-columns: 1fr 440px 340px !important;
      }
    }
    .custom-scrollbar::-webkit-scrollbar {
      width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #e2e8f0;
      border-radius: 2px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: #cbd5e1;
    }
  `}} />
);

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [agents, setAgents] = useState([]);
  const [geAgents, setGeAgents] = useState([]); // New state for GE Agents
  const [selectedAgentId, setSelectedAgentId] = useState(null);
  const [geMode, setGeMode] = useState('SEARCH');
  const [geQuery, setGeQuery] = useState("What are your capabilities?");
  const [lastPayload, setLastPayload] = useState(null);
  const [geLoading, setGeLoading] = useState(false);
  const scrollRef = useRef(null);

  const fetchAgents = async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/api/agents`);
      const data = await resp.json();
      setAgents(data);
      if (data.length > 0 && !selectedAgentId) {
        setSelectedAgentId(data[0].resource_name);
      }
    } catch (err) {
      console.error("Failed to fetch agents", err);
    }
  };

  const fetchGeAgents = async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/api/ge-agents`);
      const data = await resp.json();
      setGeAgents(data);
    } catch (err) {
      console.error("Failed to fetch GE agents", err);
    }
  };

  useEffect(() => {
    fetchAgents();
    fetchGeAgents();
  }, []);

  const handleRefresh = () => {
    setGeLoading(true);
    Promise.all([fetchAgents(), fetchGeAgents()]).finally(() => setGeLoading(false));
  };




  const handleDeleteAgent = async (uid, displayName) => {
    if (!window.confirm(`Are you sure you want to delete ${displayName}?`)) return;

    setGeLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: `REQUEST: DELETE_ENGINE ${uid}` }]);

    try {
      // UID might be full path or just ID. Backend handles both.
      // But if it's a path, we might need to be careful.
      // The backend expects resource_id.
      const encodedId = encodeURIComponent(uid);
      const resp = await fetch(`${BACKEND_URL}/api/agents/${encodedId}`, {
        method: 'DELETE'
      });

      if (resp.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: `SUCCESS: Engine ${displayName} deleted.` }]);
        // Refresh lists
        fetchAgents();
        // If selected was deleted, deselect
        if (selectedAgentId === uid) setSelectedAgentId(null);
      } else {
        const errData = await resp.json();
        throw new Error(errData.detail || "Deletion failed");
      }
    } catch (err) {
      console.error("Delete failed", err);
      setMessages(prev => [...prev, { role: 'assistant', content: `ERROR: Delete failed. ${err.message}` }]);
      alert(`Failed to delete agent: ${err.message}`);
    } finally {
      setGeLoading(false);
    }
  };

  const handleRegisterGE = async (name) => {

    setGeLoading(true);
    try {
      const encodedName = encodeURIComponent(name);
      const resp = await fetch(`${BACKEND_URL}/api/agents/${encodedName}/register-ge`, {
        method: 'POST'
      });
      const data = await resp.json();
      console.log("GE Registration Success:", data);
      alert("Agent Registered in Gemini Enterprise!");
    } catch (err) {
      console.error("Failed to register GE", err);
      alert("Registration failed: check backend logs.");
    } finally {
      setGeLoading(false);
    }
  };

  const handleDeregisterGE = async (name) => {
    setGeLoading(true);
    try {
      const encodedName = encodeURIComponent(name);
      const resp = await fetch(`${BACKEND_URL}/api/agents/${encodedName}/deregister-ge`, {
        method: 'POST'
      });
      const data = await resp.json();
      console.log("GE Deregistration Success:", data);
      alert("Agent Deregistered from Gemini Enterprise.");
    } catch (err) {
      console.error("Failed to deregister GE", err);
      alert("Deregistration failed.");
    } finally {
      setGeLoading(false);
    }
  };

  const handleTestSearch = async (uid, overrideQuery, mode = 'SEARCH') => {
    setGeLoading(true);
    const query = overrideQuery || "What are your capabilities?";
    const endpoint = mode === 'SEARCH' ? '/api/ge_search' : '/api/ge_answer';

    try {
      // Create a dummy message to show action
      const shortUid = uid.split('/').pop();
      setMessages(prev => [...prev, { role: 'user', content: `DEBUG: Invoking GE_${mode} for AGENT: ${shortUid}\nQUERY: ${query}` }]);

      const resp = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          engine_id: uid // Passes UID, backend handles mapping if needed
        })
      });
      const data = await resp.json();
      console.log("GE Search Result:", data);
      setLastPayload(data); // Show the raw response in the HUD
      setMessages(prev => [...prev, { role: 'assistant', content: "GE_SEARCH_TEST: Results delivered to INTERCEPTION_HUD." }]);
    } catch (err) {
      console.error("Search test failed", err);
      alert("GE Search Test failed. Check interceptor logs.");
    } finally {
      setGeLoading(false);
    }
  };

  const handleDeployAgent = async () => {
    const name = window.prompt("Enter Display Name for the new Interceptor:", "GE_Interceptor_V2");
    if (!name) return;

    setGeLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: `REQUEST: Deploy new engine "${name}"` }]);
    setMessages(prev => [...prev, { role: 'assistant', content: "PROVISIONING: Starting Vertex AI Reasoning Engine deployment. This may take 2-3 minutes..." }]);

    try {
      const resp = await fetch(`${BACKEND_URL}/api/agents/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: name })
      });
      const data = await resp.json();
      if (resp.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: `SUCCESS: Engine deployed as ${data.resource_name}. Refreshing list...` }]);
        fetchAgents();
      } else {
        throw new Error(data.detail || "Deployment failed");
      }
    } catch (err) {
      console.error("Deployment error:", err);
      setMessages(prev => [...prev, { role: 'assistant', content: `ERROR: Deployment failed. ${err.message}` }]);
    } finally {
      setGeLoading(false);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (text) => {
    console.log("handleSend triggered with text:", text, "agent:", selectedAgentId);
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      console.log(`Fetching ${BACKEND_URL}/api/chat...`);
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: "session_" + Math.random().toString(36).substr(2, 9),
          agent_resource_name: selectedAgentId
        })
      });

      if (!response.ok) {
        console.error("Backend error response:", response.status);
        throw new Error("Backend offline");
      }
      console.log("Backend connection successful, reading stream...");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: 'assistant', content: "" };
      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            setLastPayload(data);

            if (data.content?.parts?.[0]?.text) {
              assistantMsg.content += data.content.parts[0].text;
              setMessages(prev => {
                const newMsgs = [...prev];
                newMsgs[newMsgs.length - 1] = { ...assistantMsg };
                return newMsgs;
              });
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: "SYSTEM_ERROR: CONNECTION_REFUSED" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen bg-slate-50 flex flex-col selection:bg-slate-900 selection:text-white p-6 md:p-8 lg:p-10 box-border overflow-hidden">
      <LayoutStyles />
      <div className="flex-1 flex flex-col bg-white border border-slate-200 shadow-2xl shadow-slate-200/50 relative overflow-hidden rounded-[2.5rem]">
        <Header />

        <main className="flex-1 monolith-grid overflow-hidden relative">
          {/* Column 1: Chat Journey */}
          <section className="flex flex-col bg-white relative min-w-0 min-h-0 h-full overflow-hidden architectural-grid">
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-12 space-y-10 custom-scrollbar">
              <AnimatePresence>
                {messages.length === 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="h-full flex flex-col items-center justify-center space-y-10 text-center"
                  >
                    <div className="relative">
                      <div className="absolute inset-0 bg-slate-100 blur-3xl rounded-full" />
                      <div className="relative w-24 h-24 bg-white border border-slate-200 rounded-[2rem] flex items-center justify-center shadow-xl">
                        <Command size={40} strokeWidth={1.5} className="text-slate-900" />
                      </div>
                    </div>
                    <div>
                      <h2 className="text-3xl font-black tracking-tight text-slate-900 mb-3 mono italic">SECURE_GATEWAY_UP</h2>
                      <p className="text-slate-400 max-w-sm mx-auto uppercase text-[10px] font-bold tracking-[0.2em] leading-loose">
                        ADK Payload Logic is operational. <br /> Monitoring all gRPC transactions in real-time.
                      </p>
                    </div>
                  </motion.div>
                )}
                {messages.map((m, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="flex flex-col gap-4 w-full"
                  >
                    <div className={cn(
                      "text-[10px] mono uppercase tracking-[0.2em] font-black flex items-center gap-3",
                      m.role === 'user' ? "text-slate-400" : "text-blue-600"
                    )}>
                      {m.role === 'user' ? (
                        <>
                          <ChevronRight size={10} className="text-slate-300" />
                          EVENT: USER_INPUT
                        </>
                      ) : (
                        <>
                          <Zap size={10} className="fill-blue-600" />
                          EVENT: INTERCEPTED_REPLY
                        </>
                      )}
                    </div>
                    <div className={cn(
                      "p-8 rounded-[2rem] text-[14px] leading-[1.8] border w-full",
                      m.role === 'user'
                        ? "bg-slate-50 border-slate-100 text-slate-600 ml-auto max-w-[90%]"
                        : "bg-white border-slate-200 text-slate-800 shadow-sm"
                    )}>
                      {m.content?.split('```').map((part, idx) => {
                        if (idx % 2 === 1) { // Code block
                          const lang = part.split('\n')[0].trim();
                          const content = part.split('\n').slice(1).join('\n').trim();
                          return (
                            <div key={idx} className="my-8 bg-slate-900 rounded-3xl overflow-hidden shadow-2xl">
                              <div className="bg-slate-800 px-6 py-3 text-[9px] mono text-slate-400 font-black uppercase flex justify-between">
                                <span>{lang || 'BLOB_DATA'}</span>
                                <span className="text-blue-400">ENCRYPTED</span>
                              </div>
                              <pre className="p-8 text-blue-200/90 whitespace-pre-wrap break-all overflow-x-auto text-[12px] leading-relaxed mono">
                                {content}
                              </pre>
                            </div>
                          );
                        }
                        return <div key={idx} className="whitespace-pre-wrap break-words">{part}</div>;
                      }) || (loading && <span className="animate-pulse text-blue-600 font-black italic">SEARCHING_NODES...</span>)}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
            <ChatInput onSend={handleSend} disabled={loading} />
          </section>

          {/* Column 2: Payload HUD */}
          <aside className="hidden xl:flex h-full min-w-0 min-h-0">
            <PayloadPane payload={lastPayload} />
          </aside>

          {/* Column 3: Agent Manager (Tray) */}
          <aside className="hidden lg:flex h-full min-w-0 min-h-0">
            <AgentManager
              agents={agents}
              geAgents={geAgents}
              selectedId={selectedAgentId}
              onSelect={setSelectedAgentId}
              onRefresh={handleRefresh}
              onDelete={handleDeleteAgent}
              onRegisterGE={handleRegisterGE}
              onDeregisterGE={handleDeregisterGE}
              onTestSearch={handleTestSearch}
              onDeploy={handleDeployAgent}
              isGeLoading={geLoading}
              geMode={geMode}
              setGeMode={setGeMode}
              geQuery={geQuery}
              setGeQuery={setGeQuery}
            />
          </aside>
        </main>

        {/* Footer Status Bar */}
        <footer className="h-8 bg-slate-900 flex items-center px-8 justify-between text-white font-mono text-[9px] uppercase font-black tracking-widest z-20">
          <div className="flex gap-8">
            <div className="flex items-center gap-2"><Lock size={12} className="text-green-400" /> ZERO_LEAK_PROTOCOL</div>
            <div className="flex items-center gap-2 font-bold"><Activity size={12} className="text-blue-400" /> SYNC_ENABLED</div>
          </div>
          <div className="flex items-center gap-4">
            <span className="opacity-40">BUILD_921.A</span>
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
          </div>
        </footer>
      </div>
    </div>
  );
}

const Lock = Shield;
