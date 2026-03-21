import { useEffect, useState, useRef } from 'react';
import { Activity, ShieldAlert, Cpu, Network, Zap, Play, Square, Settings, Database } from 'lucide-react';
import NexusChatOverlay from './NexusChatOverlay';

const formatTimestamp = (date: Date) => {
  const options: Intl.DateTimeFormatOptions = {
    timeZone: 'America/New_York',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  };
  const timeString = date.toLocaleTimeString('en-US', options);
  return `${timeString}.${date.getMilliseconds().toString().padStart(3, '0')}`;
};

const getEventMetadata = (payload: any) => {
  if (payload?.type === 'error') {
    return {
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/50',
      icon: <ShieldAlert size={14} className="text-red-500" />,
      tag: 'ERROR'
    };
  }
  
  const tag = payload?.tag || payload?.type || 'event';
  const type = payload?.type || '';
  
  if (tag === 'user_request') {
    return { 
      color: 'text-white', 
      bgColor: 'bg-white/5',
      borderColor: 'border-white/20',
      icon: <Database size={14} className="text-slate-400" />, 
      tag: 'USER_PROMPT' 
    };
  }

  if (type === 'thought') {
    return { 
      color: 'text-slate-400', 
      bgColor: 'bg-slate-500/5',
      borderColor: 'border-slate-500/20',
      icon: <Cpu size={14} className="text-slate-500" />, 
      tag: 'THOUGHT' 
    };
  }

  if (type === 'tool_call' || type === 'tool_result') {
    return { 
      color: 'text-indigo-400', 
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/30',
      icon: <Zap size={14} className="text-indigo-500" />, 
      tag: 'TOOL_TRACE' 
    };
  }

  switch (tag.toLowerCase()) {
    case 'router':
      return { 
        color: 'text-fuchsia-400', 
        bgColor: 'bg-fuchsia-500/10',
        borderColor: 'border-fuchsia-500/30',
        icon: <Cpu size={14} className="text-fuchsia-500" />, 
        tag: 'ROUTER' 
      };
    case 'sharepoint':
    case 'security_proxy':
      return { 
        color: 'text-blue-400', 
        bgColor: 'bg-blue-500/10',
        borderColor: 'border-blue-500/30',
        icon: <Database size={14} className="text-blue-500" />, 
        tag: 'SHAREPOINT' 
      };
    case 'servicenow':
      return { 
        color: 'text-orange-400', 
        bgColor: 'bg-orange-500/10',
        borderColor: 'border-orange-500/30',
        icon: <Zap size={14} className="text-orange-500" />, 
        tag: 'SERVICENOW' 
      };
    case 'api_output':
      return { 
        color: 'text-cyan-400', 
        bgColor: 'bg-cyan-500/10',
        borderColor: 'border-cyan-500/30',
        icon: <Network size={14} className="text-cyan-500" />, 
        tag: 'API_TRACE' 
      };
    case 'telemetry':
      return { 
        color: 'text-yellow-400', 
        bgColor: 'bg-yellow-500/10',
        borderColor: 'border-yellow-500/30',
        icon: <Zap size={14} className="text-yellow-500" />, 
        tag: 'METRICS' 
      };
    case 'public':
      return { 
        color: 'text-purple-400', 
        bgColor: 'bg-purple-500/10',
        borderColor: 'border-purple-500/30',
        icon: <Network size={14} className="text-purple-500" />, 
        tag: 'PUBLIC_WEB' 
      };
    default:
      return { 
        color: 'text-emerald-400', 
        bgColor: 'bg-emerald-500/5',
        borderColor: 'border-emerald-500/20',
        icon: <Activity size={14} className="text-emerald-500" />, 
        tag: tag.toUpperCase() 
      };
  }
};

const FormattedContent = ({ payload, meta }: { payload: any, meta: any }) => {
  const { color } = meta;
  
  if (payload?.tag === 'user_request') {
    return (
      <div className="space-y-1">
        <div className="text-[10px] text-slate-500 uppercase tracking-tighter">Model: {payload.model} | Mode: {payload.mode}</div>
        <div className="text-sm font-semibold text-white leading-snug">
          {payload.prompt}
        </div>
      </div>
    );
  }

  if (payload?.type === 'thought') {
    return (
      <div className="bg-white/5 rounded p-2 border border-white/5">
        <div className="text-[9px] text-slate-500 uppercase mb-1 flex items-center">
          <Cpu size={10} className="mr-1" /> AI Reasoning ({payload.author})
        </div>
        <div className="text-[11px] text-slate-400 italic font-serif leading-relaxed line-clamp-4">
          {payload.text}
        </div>
      </div>
    );
  }

  if (payload?.type === 'tool_call') {
    return (
      <div className="space-y-1">
        <div className="flex items-center space-x-2">
          <Zap size={12} className="text-indigo-400" />
          <span className="text-indigo-300 font-bold uppercase text-[10px]">Action Triggered</span>
          <span className="text-white font-mono text-[11px] bg-indigo-500/20 px-1.5 rounded">{payload.name}</span>
        </div>
        <div className="text-[10px] text-slate-500 font-mono truncate">
          Args: {JSON.stringify(payload.args)}
        </div>
      </div>
    );
  }

  if (payload?.type === 'tool_result') {
    const resStr = JSON.stringify(payload.result);
    return (
      <div className="space-y-1 border-l border-indigo-500/20 pl-2 ml-1">
        <div className="text-[9px] text-indigo-400/60 uppercase">Action Response</div>
        <div className="text-[11px] text-slate-400 font-mono line-clamp-2 italic">
          {resStr.length > 300 ? resStr.substring(0, 300) + '...' : resStr}
        </div>
      </div>
    );
  }

  if (payload?.type === 'agent_text') {
    return (
      <div className="text-[11px] text-emerald-300 leading-relaxed font-medium">
        {payload.text}
      </div>
    );
  }

  if (payload?.type === 'error') {
    return <div className={`font-bold ${color}`}>{payload.event || payload.message || 'Unknown Error Event'}</div>;
  }

  if (payload?.tag === 'api_output') {
    const event = payload.event || {};
    return (
      <div className="space-y-1">
        <div className="flex items-center space-x-2">
          <span className="px-1 bg-cyan-500/20 text-cyan-300 font-bold rounded text-[10px]">{event.method}</span>
          <span className="text-slate-400 truncate text-[11px]">{event.url}</span>
        </div>
        {event.response_chunk && (
          <div className="text-[11px] text-slate-500 italic truncate max-w-xl">
            {typeof event.response_chunk === 'string' ? event.response_chunk.substring(0, 200) : JSON.stringify(event.response_chunk).substring(0, 200)}
          </div>
        )}
      </div>
    );
  }

  if (payload?.tag === 'servicenow' && !payload?.type) {
    const event = payload.event || {};
    return (
      <div className="space-y-1">
        <div className="text-orange-300 font-medium text-[11px]">ServiceNow Legacy Trace</div>
        <div className="text-[10px] text-slate-500 font-mono truncate">
          {JSON.stringify(event)}
        </div>
      </div>
    );
  }

  if (payload?.type === 'telemetry') {
    return (
      <div className="grid grid-cols-2 gap-4 text-[11px]">
        <div className="flex flex-col">
          <span className="text-slate-500 uppercase text-[9px]">Latency</span>
          <span className="text-yellow-400 font-mono">{JSON.stringify(payload.data)}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-slate-500 uppercase text-[9px]">Usage</span>
          <span className="text-yellow-400 font-mono">{JSON.stringify(payload.tokens)}</span>
        </div>
      </div>
    );
  }

  // Fallback for general logs
  const displayContent = payload?.event || payload?.data || payload;
  const contentStr = typeof displayContent === 'string' ? displayContent : JSON.stringify(displayContent);
  
  return (
    <div className={`font-mono text-[11px] ${color} line-clamp-3`}>
      {contentStr}
    </div>
  );
};

const LogEntry = ({ entry, index, isSelected, onSelect }: { entry: { timestamp: Date, payload: any }, index: number, isSelected: boolean, onSelect: () => void }) => {
  const meta = getEventMetadata(entry.payload);
  const timeStr = formatTimestamp(entry.timestamp);

  return (
    <div 
      className={`flex flex-col border-l-2 mb-2 transition-all cursor-pointer overflow-hidden ${isSelected ? 'bg-white/10 border-white shadow-[0_0_20px_rgba(255,255,255,0.05)] translate-x-1' : `hover:bg-white/5 ${meta.borderColor} border-l-transparent`}`}
      onClick={onSelect}
    >
      <div className={`px-3 py-2 ${meta.bgColor} flex items-center justify-between border-b border-white/5`}>
        <div className="flex items-center space-x-3">
          <div className="shrink-0">{meta.icon}</div>
          <span className="text-[10px] text-slate-500 font-mono">[{timeStr}]</span>
          <span className={`text-[9px] font-bold tracking-[0.2em] px-2 py-0.5 rounded-full bg-black/40 ${meta.color}`}>
            {meta.tag}
          </span>
        </div>
        <div className="text-[9px] text-slate-600 font-mono">#{index.toString().padStart(4, '0')}</div>
      </div>
      
      <div className="px-3 py-3">
        <FormattedContent payload={entry.payload} meta={meta} />
      </div>
    </div>
  );
};

export default function App() {
  const [logs, setLogs] = useState<{ timestamp: Date, payload: any }[]>([]);
  const [selectedLog, setSelectedLog] = useState<{ timestamp: Date, payload: any } | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [nyTime, setNyTime] = useState("");
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setNyTime(now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour12: false }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);
  
  // Stats
  const [totalEvents, setTotalEvents] = useState(0);
  const [errorCount, setErrorCount] = useState(0);

  useEffect(() => {
    let ws: WebSocket;
    
    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setIsConnected(true);
      };
      
      ws.onmessage = (event) => {
        if (!isPaused) {
          try {
            const data = JSON.parse(event.data);
            setTotalEvents(prev => prev + 1);
            if (data?.type === 'error' || data?.error) {
               setErrorCount(prev => prev + 1);
            }
            setLogs(prev => [...prev, { timestamp: new Date(), payload: data }].slice(-500)); // Keep last 500
          } catch (e) {
            console.error("Failed to parse websocket message", e);
          }
        }
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        setTimeout(connect, 3000); // Reconnect loop
      };
    };

    connect();

    return () => {
      ws.close();
    };
  }, [isPaused]);

  useEffect(() => {
    if (!isPaused && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isPaused]);

  return (
    <div className="h-screen w-screen bg-[#050a14] text-slate-200 flex flex-col font-sans overflow-hidden">
      {/* Header Pipeline */}
      <header className="shrink-0 border-b border-white/10 bg-[#0a101d]/80 backdrop-blur-xl px-6 py-4 flex flex-row items-center justify-between z-10">
        <div className="flex items-center space-x-3">
          <div className="relative flex h-3 w-3">
            {isConnected && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span className={`relative inline-flex rounded-full h-3 w-3 ${isConnected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
          </div>
          <h1 className="text-lg font-semibold tracking-wide flex items-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            <Cpu className="mr-2 text-emerald-400" size={20} />
            Observability Nexus
          </h1>
        </div>
        
        <div className="flex items-center space-x-6">
          {nyTime && (
            <div className="flex flex-col items-end text-xs font-mono">
              <span className="text-slate-500 uppercase">NY Time</span>
              <span className="text-blue-400 font-bold text-sm" suppressHydrationWarning>{nyTime}</span>
            </div>
          )}
          <div className="h-8 w-px bg-white/10 hidden sm:block"></div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <div className="flex flex-col items-end">
              <span className="text-slate-500 uppercase">Live Events</span>
              <span className="text-emerald-400 font-bold text-sm">{totalEvents}</span>
            </div>
            <div className="w-px h-8 bg-white/10"></div>
            <div className="flex flex-col items-end">
              <span className="text-slate-500 uppercase">Anomalies</span>
              <span className="text-red-400 font-bold text-sm">{errorCount}</span>
            </div>
          </div>
          
          <button 
            onClick={() => setIsPaused(!isPaused)}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-semibold uppercase tracking-wider transition-colors ${isPaused ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' : 'bg-white/5 hover:bg-white/10 text-slate-300 border border-transparent'}`}
          >
            {isPaused ? <Play size={14} /> : <Square size={14} />}
            <span>{isPaused ? 'Resume' : 'Pause'}</span>
          </button>
        </div>
      </header>

      {/* Main Grid Architecture */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Side: Live Feed */}
        <section className="flex-1 flex flex-col border-r border-white/10 bg-[#070c18] relative">
          <div className="absolute top-0 left-0 w-full h-12 bg-gradient-to-b from-[#070c18] to-transparent z-10 pointer-events-none"></div>
          
          <div className="px-4 py-3 border-b border-white/5 flex items-center text-xs font-semibold text-slate-400 tracking-widest uppercase">
            <Activity size={14} className="mr-2" />
            Neural Telemetry Feed
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            {logs.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-4">
                <Network size={48} className="opacity-20" />
                <p className="text-sm tracking-wider uppercase">Listening for Agent Activity...</p>
              </div>
            ) : (
              logs.map((log, i) => <LogEntry key={i} entry={log} index={i} isSelected={selectedLog === log} onSelect={() => setSelectedLog(log)} />)
            )}
            <div ref={logsEndRef} />
          </div>
        </section>

        {/* Right Side: Graph / Deep Dive (Placeholder for structural aesthetic) */}
        <aside className="w-96 flex flex-col bg-[#0a101d]">
          <div className="p-4 border-b border-white/5 flex items-center justify-between text-xs font-semibold text-slate-400 tracking-widest uppercase">
            <div className="flex items-center">
              <Settings size={14} className="mr-2" />
              Agent Profile
            </div>
          </div>
          
          <div className="flex-1 flex flex-col min-h-0 bg-[#0a101d] overflow-hidden">
            {selectedLog ? (
              <div className="flex-1 overflow-y-auto w-full custom-scrollbar p-0 m-0">
                <div className="border-b border-white/5 bg-white/5 p-4 shrink-0">
                  <h3 className="text-white font-medium flex items-center mb-1">
                    <ShieldAlert className="mr-2 text-blue-400" size={16} />
                    {selectedLog.payload.tag?.toUpperCase() || selectedLog.payload.type?.toUpperCase() || 'EVENT PAYLOAD'}
                  </h3>
                  <div className="text-slate-500 text-xs font-mono">{formatTimestamp(selectedLog.timestamp)} [America/New_York]</div>
                </div>
                <div className="p-4">
                  <pre className="text-[11px] text-emerald-400 font-mono whitespace-pre-wrap break-words leading-relaxed w-full">
                    {JSON.stringify(selectedLog.payload, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="p-6">
                <div className="bg-white/5 rounded-lg p-5 border border-white/5 shadow-2xl">
                  <h3 className="text-white font-medium mb-4 flex items-center opacity-50">
                    <Activity className="mr-2 text-slate-400" size={16} />
                    Awaiting Selection
                  </h3>
                  <div className="space-y-4 font-mono text-xs opacity-50">
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-slate-500">Status</span>
                      <span className="text-emerald-400">Listening to Stream</span>
                    </div>
                  </div>
                </div>
                <div className="mt-8 text-xs text-slate-500 leading-relaxed font-mono">
                  Select a trace packet in the feed to expand its full JSON schema and deep data structures dynamically.
                </div>
              </div>
            )}
          </div>
        </aside>
      </main>
      
      {/* Bot Chat Overlay (Floating) */}
      <NexusChatOverlay logs={logs} />
    </div>
  );
}
