import React, { useEffect, useState, useRef } from 'react';
import { Activity, ShieldAlert, Cpu, Network, Zap, Play, Square, Settings, Database, Server } from 'lucide-react';

interface TelemetryEvent {
  raw?: any;
  type?: string;
  data?: any;
  event?: any;
  tag?: string;
  reasoning?: string[];
  metrics?: any[];
  [key: string]: any;
}

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

const LogEntry = ({ entry, index, isSelected, onSelect }: { entry: { timestamp: Date, payload: any }, index: number, isSelected: boolean, onSelect: () => void }) => {
  const timeStr = formatTimestamp(entry.timestamp);
  let content = '';
  let colorClass = 'text-green-400';
  let icon = <Activity size={14} />;

  if (entry.payload?.type === 'error') {
    colorClass = 'text-red-400';
    icon = <ShieldAlert size={14} className="text-red-500" />;
    content = String(entry.payload?.event || 'Unknown error');
  } else if (entry.payload?.tag === 'sharepoint') {
    colorClass = 'text-blue-400';
    icon = <Database size={14} className="text-blue-500" />;
    content = JSON.stringify(entry.payload?.event, null, 2);
  } else if (entry.payload?.tag === 'public') {
    colorClass = 'text-purple-400';
    icon = <Network size={14} className="text-purple-500" />;
    content = JSON.stringify(entry.payload?.event, null, 2);
  } else if (entry.payload?.type === 'telemetry') {
    colorClass = 'text-yellow-400';
    icon = <Zap size={14} className="text-yellow-500" />;
    content = `[TELEMETRY] Latency Metrics: ${JSON.stringify(entry.payload?.data)} | Tokens: ${JSON.stringify(entry.payload?.tokens)}`;
  } else {
    colorClass = 'text-gray-400';
    icon = <Server size={14} className="text-gray-500" />;
    content = JSON.stringify(entry.payload, null, 2);
  }

  // Truncate massively long content for the live feed
  if (content.length > 500) {
    content = content.substring(0, 500) + '... [TRUNCATED]';
  }

  return (
    <div 
      className={`flex flex-row items-start space-x-3 mb-2 px-2 py-1.5 rounded transition-colors group cursor-pointer ${isSelected ? 'bg-white/10 border-l-2 border-emerald-400' : 'hover:bg-white/5 border-l-2 border-transparent'}`}
      onClick={onSelect}
    >
      <div className="shrink-0 mt-0.5">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xs text-gray-500 font-mono">[{timeStr}]</span>
          {entry.payload?.tag && (
             <span className="text-[10px] uppercase tracking-wider font-semibold text-white/50 bg-white/10 px-1.5 py-0.5 rounded">
               {entry.payload.tag}
             </span>
          )}
        </div>
        <pre className={`text-xs font-mono whitespace-pre-wrap ${colorClass}`}>
          {content}
        </pre>
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
    </div>
  );
}
