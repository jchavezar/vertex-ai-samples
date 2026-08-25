import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Sparkles, RefreshCw, Trash2, ChevronDown, ChevronUp, CheckCircle2, AlertTriangle, Info, Play, Radio, Square, Cpu, Zap } from 'lucide-react';

export default function PipelineTraceConsole({ isOpen, onClose }) {
  const [traces, setTraces] = useState([]);
  const [pipelineState, setPipelineState] = useState({ is_running: false, processed: 0, total: 0, percentage: 0, active_workers: 8, matched_gmail_count: 0, elapsed_seconds: 0 });
  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const scrollRef = useRef(null);

  const fetchTraces = async () => {
    try {
      const [traceRes, statusRes] = await Promise.all([
        fetch('/api/agent/traces'),
        fetch('/api/agent/pipeline-status')
      ]);
      if (traceRes.ok) {
        const data = await traceRes.json();
        setTraces(data.traces || []);
      }
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setPipelineState(statusData);
      }
    } catch (err) {
      console.error("Failed to fetch traces:", err);
    }
  };

  const startParallelPipeline = async () => {
    try {
      await fetch('/api/agent/start-parallel-pipeline?concurrency=8', { method: 'POST' });
      fetchTraces();
    } catch (err) {
      console.error("Failed to start pipeline:", err);
    }
  };

  const stopParallelPipeline = async () => {
    try {
      await fetch('/api/agent/stop-parallel-pipeline', { method: 'POST' });
      fetchTraces();
    } catch (err) {
      console.error("Failed to stop pipeline:", err);
    }
  };

  const clearTraces = async () => {
    try {
      await fetch('/api/agent/clear-traces', { method: 'POST' });
      setTraces([]);
    } catch (err) {
      console.error("Failed to clear traces:", err);
    }
  };

  useEffect(() => {
    fetchTraces();
    const interval = setInterval(fetchTraces, 800); // 800ms fast polling for active live stream
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isAutoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [traces, isAutoScroll]);

  if (!isOpen) return null;

  const getStepBadge = (step, status) => {
    if (status === 'SUCCESS' || step === 'PIPELINE_COMPLETE' || step === 'GMAIL_MATCH' || step === 'CLUSTER_COMPLETE' || step === 'VECTOR_INDEX_COMPLETE') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
    if (status === 'WARNING' || step === 'FALLBACK_TRIGGER' || step === 'CLUSTER_STOP' || step === 'VECTOR_WARN') {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    }
    if (step.startsWith('GMAIL')) {
      return 'bg-red-500/10 text-red-400 border-red-500/30';
    }
    if (step.startsWith('VECTOR') || step.startsWith('EMBED')) {
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    }
    if (step.startsWith('GEMINI') || step.startsWith('CLUSTER')) {
      return 'bg-violet-500/10 text-violet-400 border-violet-500/30';
    }
    return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
  };

  const getWorkerBadge = (workerId) => {
    if (workerId === 'EMBED_AGENT' || workerId === 'AGENT_EMBED') {
      return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_8px_rgba(6,182,212,0.4)]';
    }
    if (workerId === 'CLUSTER' || workerId === 'MAIN') {
      return 'bg-violet-500/20 text-violet-300 border-violet-500/40';
    }
    const colors = [
      'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
      'bg-pink-500/20 text-pink-300 border-pink-500/40',
      'bg-amber-500/20 text-amber-300 border-amber-500/40',
      'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      'bg-blue-500/20 text-blue-300 border-blue-500/40',
      'bg-purple-500/20 text-purple-300 border-purple-500/40',
      'bg-rose-500/20 text-rose-300 border-rose-500/40',
      'bg-teal-500/20 text-teal-300 border-teal-500/40'
    ];
    const idx = parseInt(workerId?.replace(/\D/g, '') || '1', 10) % colors.length;
    return colors[idx];
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 w-full max-w-3xl bg-slate-950/95 border border-slate-800 rounded-3xl shadow-2xl backdrop-blur-2xl transition-all duration-300 overflow-hidden flex flex-col ${isMinimized ? 'h-14' : 'h-[32rem]'}`}>
      
      {/* Header */}
      <div className="px-5 py-3.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 shadow-md">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-100">Google ADK Parallel Agent Cluster</span>
              <span className="flex items-center gap-1 text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/30">
                <Radio className="w-2.5 h-2.5 animate-pulse" /> {pipelineState.is_running ? 'PARALLEL ENRICHMENT RUNNING' : 'LIVE AGENT STREAM'}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">8 Concurrent ADK Receipt Subagents + 1 Parallel Vertex AI Vector Embedding Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {pipelineState.is_running ? (
            <button
              onClick={stopParallelPipeline}
              className="px-3 py-1.5 rounded-xl bg-red-950/50 hover:bg-red-900/60 border border-red-500/40 text-red-300 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-md"
            >
              <Square className="w-3.5 h-3.5 fill-red-400 text-red-400" />
              <span>Stop Agents</span>
            </button>
          ) : (
            <button
              onClick={startParallelPipeline}
              className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-violet-600 hover:opacity-95 text-white text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-md shadow-indigo-600/20"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Run Parallel Cluster (8x)</span>
            </button>
          )}

          <button
            onClick={clearTraces}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
            title="Clear logs"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
          >
            {isMinimized ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>

      {/* Progress Bar & Concurrency HUD */}
      {!isMinimized && (
        <div className="px-5 py-3 bg-slate-900/60 border-b border-slate-800/80 flex flex-col gap-2.5">
          <div className="flex items-center justify-between text-[11px] font-mono">
            <span className="text-slate-300 flex items-center gap-1.5 font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              <span>Parallel Subagent Workers ({pipelineState.active_workers} Active Lanes)</span>
            </span>
            <span className="font-bold text-slate-200">
              {pipelineState.processed} / {pipelineState.total} Items ({pipelineState.percentage}%) {pipelineState.elapsed_seconds > 0 && `• ${pipelineState.elapsed_seconds}s`}
            </span>
          </div>

          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
            <div
              style={{ width: `${pipelineState.percentage}%` }}
              className="h-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-violet-500 transition-all duration-300 shadow-[0_0_12px_rgba(99,102,241,0.6)]"
            />
          </div>

          {/* 8 Parallel Worker Live Status Tiles + 1 Vector Embedding Subagent Tile */}
          <div className="grid grid-cols-3 sm:grid-cols-9 gap-1.5 pt-1">
            {Array.from({ length: 8 }).map((_, i) => {
              const workerKey = `AGENT_${i + 1}`;
              const lane = pipelineState.active_lanes?.[workerKey] || { status: 'idle', merchant: '', step: 'STANDBY', amount: 0 };
              const isActive = lane.status === 'active' || pipelineState.is_running;
              const isGmail = lane.step === 'SEARCHING_GMAIL' || lane.step === 'GMAIL_GROUNDED';
              
              return (
                <div
                  key={workerKey}
                  className={`p-1.5 rounded-xl border transition-all flex flex-col items-center text-center ${
                    isActive
                      ? 'bg-slate-900/90 border-indigo-500/40 shadow-sm shadow-indigo-500/20'
                      : 'bg-slate-950/60 border-slate-800/80 opacity-70'
                  }`}
                >
                  <div className="flex items-center gap-1 w-full justify-between">
                    <span className="text-[9px] font-black text-indigo-300 font-mono">W{i + 1}</span>
                    <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`} />
                  </div>
                  <span className="text-[10px] font-bold text-slate-100 truncate w-full mt-0.5" title={lane.merchant || 'Idle'}>
                    {lane.merchant ? lane.merchant.split(' ')[0] : 'Idle'}
                  </span>
                  <span className={`text-[8px] font-mono uppercase tracking-tighter truncate w-full ${isGmail ? 'text-cyan-400' : 'text-slate-400'}`}>
                    {lane.step || 'STANDBY'}
                  </span>
                </div>
              );
            })}

            {/* Lane 9: Vector Embedding Subagent */}
            {(() => {
              const embedLane = pipelineState.active_lanes?.['AGENT_EMBED'] || { status: 'idle', merchant: 'Vector Index Ready', step: 'STANDBY' };
              const isEmbedActive = embedLane.status === 'active';
              return (
                <div
                  className={`p-1.5 rounded-xl border transition-all flex flex-col items-center text-center ${
                    isEmbedActive
                      ? 'bg-cyan-950/70 border-cyan-500/60 shadow-md shadow-cyan-500/30'
                      : 'bg-slate-950/60 border-slate-800/80 opacity-75'
                  }`}
                >
                  <div className="flex items-center gap-1 w-full justify-between">
                    <span className="text-[9px] font-black text-cyan-300 font-mono">V-EMB</span>
                    <span className={`w-1.5 h-1.5 rounded-full ${isEmbedActive ? 'bg-cyan-400 animate-ping' : 'bg-cyan-600/50'}`} />
                  </div>
                  <span className="text-[10px] font-bold text-cyan-100 truncate w-full mt-0.5" title={embedLane.merchant}>
                    {embedLane.merchant ? embedLane.merchant.split(' ')[0] : 'Vertex AI'}
                  </span>
                  <span className="text-[8px] font-mono text-cyan-400 uppercase tracking-tighter truncate w-full">
                    {embedLane.step || 'STANDBY'}
                  </span>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* Trace Log Body */}
      {!isMinimized && (
        <div ref={scrollRef} className="p-4 flex-1 overflow-y-auto space-y-2 font-mono text-xs">
          {traces.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 space-y-2 py-12">
              <Sparkles className="w-8 h-8 text-indigo-400/60 animate-bounce" />
              <p className="text-xs font-bold text-slate-300">Parallel ADK Agent Cluster Ready</p>
              <p className="text-[11px] text-slate-400 max-w-sm">Click <span className="text-indigo-400 font-semibold">"Run Parallel Cluster (8x)"</span> to watch 8 concurrent subagents search Gmail & itemize all statements live!</p>
            </div>
          ) : (
            traces.map((trace) => (
              <div
                key={trace.id}
                className="p-2.5 rounded-2xl bg-slate-900/70 border border-slate-800/90 hover:border-indigo-500/30 transition-all flex items-start gap-2.5"
              >
                <span className="text-[10px] text-slate-500 shrink-0 pt-0.5">{trace.timestamp}</span>
                <div className="space-y-1 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-0.2 rounded-md text-[9px] font-black border uppercase tracking-wider ${getWorkerBadge(trace.worker_id)}`}>
                      {trace.worker_id || 'MAIN'}
                    </span>
                    <span className={`px-2 py-0.2 rounded-md text-[9px] font-bold border uppercase tracking-wider ${getStepBadge(trace.step, trace.status)}`}>
                      {trace.step}
                    </span>
                    <span className={`text-[10px] font-semibold ${trace.status === 'SUCCESS' ? 'text-emerald-400' : trace.status === 'WARNING' ? 'text-amber-400' : 'text-indigo-300'}`}>
                      {trace.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 break-words font-sans">{trace.detail}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
