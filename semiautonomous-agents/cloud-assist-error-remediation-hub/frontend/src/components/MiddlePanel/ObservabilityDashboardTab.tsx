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
  Server
} from 'lucide-react';

interface TelemetrySignal {
  activeIncidents: number;
  criticalBlockers: number;
  mttrSeconds: number;
  autoHealedRatePercent: number;
  cloudRunHealthPercent: number;
  totalLogsAnalyzed: number;
  traceCorrelationsFound: number;
}

interface ConstellationNode {
  id: string;
  label: string;
  serviceType: string;
  status: string;
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
  nodes: ConstellationNode[];
  edges: ConstellationEdge[];
}

export const ObservabilityDashboardTab: React.FC = () => {
  const [data, setData] = useState<TelemetryData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ConstellationNode | null>(null);
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
        <p className="text-xs font-mono">Loading Real GCP Signal Indicators & Constellation Topology...</p>
      </div>
    );
  }

  const { signals, nodes, edges } = data;

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/40 flex items-center justify-center shadow-lg shadow-cyan-500/10">
            <Radio className="w-5 h-5 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex flex-wrap items-center gap-2">
              <span>GCP Observability Signals & Inter-Service Constellation Topology</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                Live Cloud Logging & Trace Correlation
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Correlates distributed request spans across Cloud Scheduler, Cloud Run, IAM, and Secret Manager
            </p>
          </div>
        </div>

        <div className="text-[11px] font-mono text-slate-400 bg-black/60 px-3 py-1.5 rounded-xl border border-slate-800 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>Project: <strong className="text-cyan-300">{data.projectId}</strong></span>
        </div>
      </div>

      {/* 4 Real-Time Signal Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Active Incidents */}
        <div className="p-4 rounded-xl bg-slate-900 border border-rose-500/40 shadow-xl space-y-2">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>Active Signals & Incidents</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-white font-mono">{signals.activeIncidents}</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
              {signals.criticalBlockers} Critical
            </span>
          </div>
          <p className="text-[10px] text-slate-400">Captured in Cloud Logging error stream</p>
        </div>

        {/* MTTR */}
        <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/40 shadow-xl space-y-2">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>MTTR (Mean Time to Remediate)</span>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-emerald-400 font-mono">{signals.mttrSeconds}s</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Fast Sub-Second
            </span>
          </div>
          <p className="text-[10px] text-slate-400">Parallel sandbox worker pool latency</p>
        </div>

        {/* Auto-Healed Recovery Rate */}
        <div className="p-4 rounded-xl bg-slate-900 border border-cyan-500/40 shadow-xl space-y-2">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>Auto-Healing Recovery Rate</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-cyan-300 font-mono">{signals.autoHealedRatePercent}%</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Zero Downtime
            </span>
          </div>
          <p className="text-[10px] text-slate-400">Automatic code diff & recovery harness</p>
        </div>

        {/* Cloud Run Service Health */}
        <div className="p-4 rounded-xl bg-slate-900 border border-purple-500/40 shadow-xl space-y-2">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>Cloud Run Health Index</span>
            <Server className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-purple-300 font-mono">{signals.cloudRunHealthPercent}%</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              98.4% Up
            </span>
          </div>
          <p className="text-[10px] text-slate-400">Evaluated across container revisions</p>
        </div>
      </div>

      {/* INTERACTIVE CONSTELLATION GRAPH OVERLAY */}
      <div className="rounded-2xl bg-gradient-to-br from-[#090d16] via-[#0e1626] to-[#090d16] border border-cyan-500/40 p-5 shadow-2xl space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white tracking-tight">Inter-Service Dependency Constellation Map</h3>
          </div>
          <span className="text-[10px] text-slate-400 font-mono bg-black/60 px-2.5 py-1 rounded border border-slate-800">
            Click any node below to inspect Cloud Trace correlation
          </span>
        </div>

        {/* Interactive Constellation Node Buttons Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-2">
          {nodes.map((node) => {
            const isDegraded = node.status === 'DEGRADED';
            return (
              <button
                key={node.id}
                onClick={() => setSelectedNode(node)}
                className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between space-y-3 ${
                  isDegraded
                    ? 'bg-rose-950/40 border-rose-500/60 hover:bg-rose-900/60 shadow-lg shadow-rose-500/10'
                    : 'bg-slate-900/80 border-cyan-500/40 hover:bg-slate-800 hover:border-cyan-400 shadow-md'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`w-2.5 h-2.5 rounded-full ${isDegraded ? 'bg-rose-500 animate-ping' : 'bg-cyan-400'}`}></span>
                  <span className={`text-[9px] font-bold font-mono px-1.5 py-0.5 rounded ${
                    isDegraded ? 'bg-rose-500/20 text-rose-300' : 'bg-cyan-500/20 text-cyan-300'
                  }`}>
                    {isDegraded ? 'DEGRADED' : 'HEALTHY'}
                  </span>
                </div>
                <div>
                  <div className="text-xs font-bold text-white tracking-tight">{node.label}</div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">{node.serviceType}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* NODE DETAILS DRAWER MODAL */}
      {selectedNode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-5 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Radio className="w-5 h-5 text-cyan-400" />
                <div>
                  <h3 className="text-sm font-bold text-white">{selectedNode.label}</h3>
                  <p className="text-[11px] text-slate-400 font-mono">{selectedNode.serviceType}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase">Distributed Trace Correlation Link</span>
                <div className="text-cyan-300 font-bold select-all">{selectedNode.traceId}</div>
              </div>

              <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase">Service Telemetry Details</span>
                <div className="text-slate-200 leading-relaxed">{selectedNode.details}</div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedNode(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs"
              >
                Close Drawer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
