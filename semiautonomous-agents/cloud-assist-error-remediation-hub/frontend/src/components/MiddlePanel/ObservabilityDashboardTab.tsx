import React, { useState, useEffect } from 'react';
import {
  Activity,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Radio,
  Clock,
  Layers,
  Cpu,
  ShieldCheck,
  Search,
  X,
  ExternalLink,
  Sparkles,
  TrendingUp,
  Server,
  BarChart2,
  Maximize2,
  Eye,
  Flame,
  Target
} from 'lucide-react';

interface TelemetrySignal {
  activeIncidents: number;
  criticalBlockers: number;
  mttrSeconds: number;
  autoHealedRatePercent: number;
  cloudRunHealthPercent: number;
  totalLogsAnalyzed: number;
  traceCorrelationsFound: number;
  divergenceIndex?: number;
  systemThreatLevel?: string;
}

interface ConstellationNode {
  id: string;
  label: string;
  serviceType: string;
  status: string;
  anomalyScore?: number;
  x: number;
  y: number;
  errorCount: number;
  traceId: string;
  details: string;
}

interface ConstellationEdge {
  from: string;
  to: string;
  label: string;
  status: string;
}

interface TelemetryData {
  projectId: string;
  generatedAt: string;
  signals: TelemetrySignal;
  rehoboamWaveform?: number[];
  nodes: ConstellationNode[];
  edges: ConstellationEdge[];
}

export const ObservabilityDashboardTab: React.FC = () => {
  const [data, setData] = useState<TelemetryData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ConstellationNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [isDivergenceTriggered, setIsDivergenceTriggered] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8088/api/telemetry-dashboard')
      .then((res) => res.json())
      .then((json: TelemetryData) => {
        setData(json);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load telemetry dashboard:", err);
        setIsLoading(false);
      });
  }, []);

  if (isLoading || !data) {
    return (
      <div className="p-12 text-center text-slate-400 space-y-3">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-xs font-mono">Loading Real GCP Signal Indicators & Westworld Rehoboam Anomaly System...</p>
      </div>
    );
  }

  const { signals, nodes, edges } = data;
  const currentDivergence = isDivergenceTriggered ? 0.88 : (signals.divergenceIndex || 0.14);
  const defaultWaveform = [
    12, 15, 14, 18, 16, 22, 19, 14, 15, 88, 94, 76, 32, 20, 16,
    14, 18, 22, 19, 15, 14, 16, 18, 20, 15, 14, 16, 18, 15, 14
  ];
  const waveform = data.rehoboamWaveform || defaultWaveform;

  // Map node coordinates for SVG lines
  const getNodePos = (id: string) => {
    const n = nodes.find((item) => item.id === id);
    return n ? { x: n.x, y: n.y } : { x: 0, y: 0 };
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500/20 via-purple-500/20 to-cyan-500/20 border border-rose-500/40 flex items-center justify-center shadow-lg shadow-rose-500/10">
            <Eye className="w-5 h-5 text-rose-400 animate-pulse" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex flex-wrap items-center gap-2">
              <span>"REHOBOAM" OMNISCIENT ANOMALY CORE</span>
              <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-semibold">
                Big Brother GCP Anomaly Radar
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Real-Time System Equilibrium & Anomaly Divergence Monitoring across Google Cloud Infrastructure
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsDivergenceTriggered(!isDivergenceTriggered)}
            className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-2 shadow-lg cursor-pointer ${
              isDivergenceTriggered
                ? 'bg-gradient-to-r from-rose-600 to-red-700 text-white border-rose-400 shadow-rose-500/20 animate-pulse'
                : 'bg-slate-900 hover:bg-slate-800 text-cyan-300 border-cyan-500/40 hover:border-cyan-400'
            }`}
          >
            <Flame className="w-4 h-4 text-rose-400" />
            <span>{isDivergenceTriggered ? '⚠️ CRITICAL DIVERGENCE ACTIVE' : '👁️ Trigger Systemic Divergence'}</span>
          </button>

          <div className="text-[11px] font-mono text-slate-400 bg-black/60 px-3 py-2 rounded-xl border border-slate-800 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Project: <strong className="text-cyan-300">{data.projectId}</strong></span>
          </div>
        </div>
      </div>

      {/* REHOBOAM ANOMALY WAVEFORM & SYSTEM EQUILIBRIUM CANVAS */}
      <div className="rounded-3xl bg-gradient-to-b from-[#06040a] via-[#0d0914] to-[#06040a] border border-rose-500/50 p-6 shadow-2xl space-y-5 relative overflow-hidden">
        {/* Ambient Dark Space Grid Pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(#f43f5e_1px,transparent_1px)] [background-size:32px_32px] opacity-15 pointer-events-none"></div>

        {/* Top Status Header */}
        <div className="flex justify-between items-center border-b border-rose-900/40 pb-4 relative z-10">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-rose-500 animate-ping"></div>
            <span className="text-xs font-black tracking-widest uppercase text-white font-mono">Rehoboam System Equilibrium Matrix</span>
          </div>
          <div className="flex items-center space-x-4 font-mono text-xs">
            <div className="text-slate-400">
              Divergence Index: <strong className={currentDivergence > 0.5 ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                {currentDivergence.toFixed(2)}
              </strong>
            </div>
            <div className={`px-3 py-1 rounded-full text-[10px] font-bold border ${
              currentDivergence > 0.5
                ? 'bg-rose-950/80 text-rose-300 border-rose-500/60 animate-pulse'
                : 'bg-emerald-950/80 text-emerald-300 border-emerald-500/60'
            }`}>
              {currentDivergence > 0.5 ? 'CRITICAL SYSTEM DIVERGENCE' : 'EQUILIBRIUM STABLE'}
            </div>
          </div>
        </div>

        {/* Rehoboam Circular Waveform Radar & Anomaly Waveform Spikes Graph */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10 items-center">
          {/* Rehoboam Radial Waveform Eye */}
          <div className="flex flex-col items-center justify-center p-6 bg-black/60 rounded-2xl border border-rose-900/40 relative">
            <div className="relative w-48 h-48 flex items-center justify-center">
              {/* Concentric Pulsing Rehoboam Rings */}
              <div className={`absolute inset-0 rounded-full border-2 border-dashed ${isDivergenceTriggered ? 'border-rose-500 animate-[spin_8s_linear_infinite]' : 'border-cyan-500/40 animate-[spin_20s_linear_infinite]'}`}></div>
              <div className={`absolute inset-4 rounded-full border ${isDivergenceTriggered ? 'border-rose-400/80 animate-ping' : 'border-purple-500/30'}`}></div>
              <div className={`absolute inset-10 rounded-full border-2 ${isDivergenceTriggered ? 'border-red-500 bg-rose-950/40' : 'border-cyan-400/50 bg-black/60'}`}></div>
              
              {/* Center Omniscient Eye Pupil */}
              <div className="relative z-10 flex flex-col items-center justify-center text-center space-y-1">
                <Target className={`w-8 h-8 ${isDivergenceTriggered ? 'text-rose-500 animate-bounce' : 'text-cyan-400'}`} />
                <span className="text-[10px] font-mono font-bold text-white uppercase tracking-widest">
                  {isDivergenceTriggered ? 'ANOMALY DETECTED' : 'SYSTEM OK'}
                </span>
                <span className="text-[9px] font-mono text-slate-400">14,820 Logs/s</span>
              </div>
            </div>
            <div className="mt-4 text-[10px] font-mono text-slate-400 text-center">
              Rehoboam Omniscient Radar Lens • GCP Project <code className="text-cyan-300">vtxdemos</code>
            </div>
          </div>

          {/* Anomaly Divergence Spikes Timeline Chart (Westworld Waveform) */}
          <div className="lg:col-span-2 p-5 bg-black/60 rounded-2xl border border-rose-900/40 space-y-3">
            <div className="flex justify-between items-center border-b border-slate-800/80 pb-2">
              <span className="text-xs font-bold text-white font-mono flex items-center gap-2">
                <Activity className="w-4 h-4 text-rose-400" />
                <span>Real-Time System Divergence Waveform Spikes</span>
              </span>
              <span className="text-[10px] font-mono text-rose-400">Sampling Rate: 500ms</span>
            </div>

            {/* SVG Anomaly Spikes Waveform Chart */}
            <div className="h-36 w-full flex items-end justify-between gap-1 pt-4">
              {waveform.map((val, idx) => {
                const isSpike = val > 50 || (isDivergenceTriggered && idx > 20);
                const heightPercent = isDivergenceTriggered ? Math.min(100, val + Math.floor(Math.random() * 20) + 15) : val;
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group">
                    <div
                      style={{ height: `${heightPercent}%` }}
                      className={`w-full rounded-t transition-all duration-300 ${
                        isSpike || isDivergenceTriggered
                          ? 'bg-gradient-to-t from-rose-700 via-rose-500 to-red-400 shadow-[0_0_12px_rgba(244,63,94,0.8)]'
                          : 'bg-gradient-to-t from-cyan-900 via-cyan-600 to-teal-400 opacity-60 hover:opacity-100'
                      }`}
                    ></div>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/60">
              <span>00:00:00 UTC</span>
              <span className="text-rose-400 font-bold">Divergence Spike #3: ZeroDivisionError in /api/cart/checkout</span>
              <span>LIVE NOW</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2D VISUAL GALAXY CONSTELLATION MAP OVERLAY */}
      <div className="rounded-3xl bg-gradient-to-b from-[#050811] via-[#0b1324] to-[#050811] border border-cyan-500/40 p-6 shadow-2xl space-y-4 relative overflow-hidden">
        <div className="flex justify-between items-center border-b border-slate-800/80 pb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white tracking-tight">2D Microservice Dependency Constellation Star Map</h3>
          </div>
          <span className="text-[10px] text-cyan-300 font-mono bg-cyan-950/80 px-3 py-1 rounded-full border border-cyan-500/40 shadow-lg">
            ✨ Click any star node or laser beam to inspect Cloud Trace correlation
          </span>
        </div>

        {/* 2D Interactive SVG Visual Constellation Topology Map */}
        <div className="relative w-full h-[280px] bg-black/40 rounded-2xl border border-slate-800/80 overflow-hidden backdrop-blur-sm">
          <svg className="w-full h-full absolute inset-0 pointer-events-none">
            <defs>
              <linearGradient id="beamGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#3b82f6" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="degradedBeamGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.4" />
              </linearGradient>
            </defs>

            {/* Connecting Flow Beams (SVG Animated Path Lines) */}
            {edges.map((edge, idx) => {
              const start = getNodePos(edge.from);
              const end = getNodePos(edge.to);
              const isDegradedBeam = edge.from === 'node-cloudrun' || edge.to === 'node-cloudrun' || isDivergenceTriggered;

              return (
                <g key={idx}>
                  <line
                    x1={`${(start.x / 960) * 100}%`}
                    y1={`${(start.y / 280) * 100}%`}
                    x2={`${(end.x / 960) * 100}%`}
                    y2={`${(end.y / 280) * 100}%`}
                    stroke={isDegradedBeam ? 'url(#degradedBeamGradient)' : 'url(#beamGradient)'}
                    strokeWidth="2.5"
                    strokeDasharray="6 6"
                    className="animate-[dash_15s_linear_infinite]"
                  />
                </g>
              );
            })}
          </svg>

          {/* Render 2D Interactive Constellation Nodes */}
          {nodes.map((node) => {
            const isDegraded = node.status === 'DEGRADED' || isDivergenceTriggered;
            const isSelected = selectedNode?.id === node.id;
            const isHovered = hoveredNode === node.id;

            return (
              <div
                key={node.id}
                onClick={() => setSelectedNode(node)}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                style={{
                  left: `${(node.x / 960) * 88 + 4}%`,
                  top: `${(node.y / 280) * 70 + 10}%`,
                }}
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 z-20 ${
                  isHovered || isSelected ? 'scale-110' : 'scale-100'
                }`}
              >
                {/* Glowing Outer Star Orbit Halo */}
                <div
                  className={`w-20 h-20 rounded-full flex flex-col items-center justify-center p-2 text-center transition-all ${
                    isDegraded
                      ? 'bg-rose-950/80 border-2 border-rose-500 shadow-[0_0_25px_rgba(244,63,94,0.5)]'
                      : 'bg-slate-900/90 border-2 border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)]'
                  }`}
                >
                  <span className={`w-3 h-3 rounded-full mb-1 ${isDegraded ? 'bg-rose-500 animate-ping' : 'bg-cyan-400 animate-pulse'}`}></span>
                  <span className="text-[11px] font-extrabold text-white leading-tight tracking-tight">{node.label}</span>
                  <span className={`text-[9px] font-mono font-bold mt-1 px-1.5 py-0.2 rounded ${
                    isDegraded ? 'bg-rose-500/30 text-rose-200' : 'bg-cyan-500/30 text-cyan-200'
                  }`}>
                    {isDegraded ? 'DIVERGENT' : '200 OK'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* NODE DETAILS & DISTRIBUTED CLOUD TRACE GANTT CHART INSPECTOR MODAL */}
      {selectedNode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
          <div className="bg-slate-900 border border-cyan-500/50 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
                  <Radio className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">{selectedNode.label}</h3>
                  <p className="text-[11px] text-slate-400 font-mono">{selectedNode.serviceType}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Distributed Span Waterfall Gantt Chart */}
            <div className="space-y-3 font-mono text-xs">
              <div className="p-3.5 rounded-xl bg-black/60 border border-slate-800 space-y-2">
                <span className="text-[10px] text-cyan-300 font-bold uppercase tracking-wider">Distributed Span Waterfall Gantt Chart</span>
                <div className="space-y-2 pt-1 text-[11px]">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 w-36">Cloud Scheduler:</span>
                    <div className="flex-1 bg-slate-800 h-4 rounded overflow-hidden relative">
                      <div className="bg-emerald-500 h-full w-[10%]"></div>
                    </div>
                    <span className="text-emerald-400 font-bold ml-2">12ms</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 w-36">Cloud Run Storefront:</span>
                    <div className="flex-1 bg-slate-800 h-4 rounded overflow-hidden relative">
                      <div className="bg-rose-500 h-full w-[85%]"></div>
                    </div>
                    <span className="text-rose-400 font-bold ml-2">142ms (500)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 w-36">IAM Policy Guard:</span>
                    <div className="flex-1 bg-slate-800 h-4 rounded overflow-hidden relative">
                      <div className="bg-cyan-400 h-full w-[15%]"></div>
                    </div>
                    <span className="text-cyan-300 font-bold ml-2">8ms</span>
                  </div>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-black/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Distributed Trace Link</span>
                <div className="text-cyan-300 font-bold select-all">{selectedNode.traceId}</div>
              </div>

              <div className="p-3.5 rounded-xl bg-black/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Service Telemetry Details</span>
                <div className="text-slate-200 leading-relaxed">{selectedNode.details}</div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedNode(null)}
                className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
              >
                Close Trace Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
