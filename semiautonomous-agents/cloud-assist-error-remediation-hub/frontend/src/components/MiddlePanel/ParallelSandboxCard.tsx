import React, { useState } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';
import {
  Layers,
  Play,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Cpu,
  RefreshCw,
  Clock,
  Terminal,
  Sparkles
} from 'lucide-react';

interface ParallelSandboxCardProps {
  selectedError: GcpErrorItem;
  diagnostic: CloudAssistDiagnostic;
}

interface HarnessAttempt {
  attemptNum: number;
  command: string;
  exitCode: number;
  stdout: string;
  stderr: string;
  durationMs: number;
}

interface SandboxSubagentTrace {
  taskId: string;
  sandboxId: string;
  success: boolean;
  recoveredFromError: boolean;
  startedAt: string;
  completedAt: string;
  durationMs: number;
  output: string;
  attempts: HarnessAttempt[];
  finalCommand: string;
}

interface ParallelConsolidatedReport {
  errorId: string;
  serviceName: string;
  harnessPattern: string;
  totalParallelSandboxes: number;
  successfulTasks: number;
  failedTasks: number;
  autoRecoveredTasks: number;
  startedAt: string;
  completedAt: string;
  totalDurationMs: number;
  consolidationStatus: string;
  subagentTraces: SandboxSubagentTrace[];
}

export const ParallelSandboxCard: React.FC<ParallelSandboxCardProps> = ({
  selectedError,
  diagnostic
}) => {
  const [isOrchestrating, setIsOrchestrating] = useState(false);
  const [report, setReport] = useState<ParallelConsolidatedReport | null>(null);

  const handleOrchestrateParallel = async () => {
    setIsOrchestrating(true);
    setReport(null);
    try {
      const res = await fetch('http://127.0.0.1:8088/api/orchestrate-parallel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ errorItem: selectedError })
      });
      if (res.ok) {
        const data: ParallelConsolidatedReport = await res.json();
        setReport(data);
      }
    } catch (err) {
      console.error("Parallel sandbox execution failed:", err);
    } finally {
      setIsOrchestrating(false);
    }
  };

  const formatTimestamp = (isoStr?: string) => {
    if (!isoStr) return 'N/A';
    try {
      const d = new Date(isoStr);
      return d.toLocaleTimeString() + '.' + String(d.getMilliseconds()).padStart(3, '0');
    } catch (e) {
      return isoStr;
    }
  };

  return (
    <div className="rounded-xl bg-gradient-to-br from-slate-900/95 via-[#111728]/95 to-slate-900/95 border border-cyan-500/40 p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center shadow-md shadow-cyan-500/10">
            <Layers className="w-4.5 h-4.5 text-cyan-300" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <span>Autonomous Parallel Sandbox Subagents</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                Self-Healing Harness Loop
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Spawns N Linux Sandboxes in parallel with automatic error recovery harness & full timestamp audit
            </p>
          </div>
        </div>

        <button
          onClick={handleOrchestrateParallel}
          disabled={isOrchestrating}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 hover:from-cyan-500 hover:via-blue-500 hover:to-purple-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition-all"
        >
          {isOrchestrating ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
              <span>Running Parallel Harness...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Orchestrate Parallel Sandbox Fixes</span>
            </>
          )}
        </button>
      </div>

      {/* Orchestrating Spinner State */}
      {isOrchestrating && (
        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between animate-pulse">
          <div className="flex items-center space-x-3">
            <Cpu className="w-5 h-5 text-cyan-400 animate-spin" />
            <div className="text-xs text-slate-200 font-medium">
              Dispatching parallel Linux Sandboxes & executing Self-Healing Harness Retry loops...
            </div>
          </div>
          <span className="text-[11px] font-mono text-cyan-300">Parallel Worker Pool: ACTIVE</span>
        </div>
      )}

      {/* Consolidated Verification Report with Self-Healing Harness Telemetry & Exact Timestamps */}
      {report && (
        <div className="space-y-4 pt-2 border-t border-slate-800/80">
          {/* Executive Metrics Header Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between bg-emerald-950/40 border border-emerald-500/40 p-3.5 rounded-xl text-xs text-emerald-300 gap-2">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <div>
                <strong className="text-white">Zero-Drop Consolidation Verified:</strong>{' '}
                <span>{report.successfulTasks} of {report.totalParallelSandboxes} Sandboxes Succeeded</span>
                {report.autoRecoveredTasks > 0 && (
                  <span className="ml-2 px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-mono font-bold">
                    ⚡ {report.autoRecoveredTasks} Auto-Recovered by Harness
                  </span>
                )}
              </div>
            </div>

            {/* Exact Execution Timestamps */}
            <div className="flex items-center space-x-3 text-[10px] font-mono text-slate-300 bg-black/40 px-3 py-1.5 rounded-lg border border-slate-800">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>Finished: <strong className="text-cyan-300">{formatTimestamp(report.completedAt)}</strong></span>
              </div>
              <span>•</span>
              <span>Total Latency: <strong className="text-emerald-400">{report.totalDurationMs}ms</strong></span>
            </div>
          </div>

          {/* Subagent Sandbox Traces */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {report.subagentTraces.map((sub, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-950/90 border border-slate-800/90 hover:border-cyan-500/40 transition-all space-y-2.5 font-mono text-[11px]"
              >
                {/* Top Row: Task ID + Sandbox ID + Recovery Badge */}
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-cyan-300">{sub.taskId}</span>
                    {sub.recoveredFromError && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        AUTO-HEALING APPLIED
                      </span>
                    )}
                  </div>
                  <div className="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {sub.sandboxId}
                  </div>
                </div>

                {/* Exact Timestamps for this Subagent */}
                <div className="flex items-center justify-between text-[10px] text-slate-400 bg-black/50 px-2.5 py-1 rounded border border-slate-800/60">
                  <span>Start: <strong className="text-slate-300">{formatTimestamp(sub.startedAt)}</strong></span>
                  <span>End: <strong className="text-slate-300">{formatTimestamp(sub.completedAt)}</strong></span>
                  <span>Duration: <strong className="text-cyan-300">{sub.durationMs}ms</strong></span>
                </div>

                {/* Full Execution Trace & Harness Auto-Correction Log */}
                <div className="text-slate-300 whitespace-pre-wrap text-[10px] leading-relaxed max-h-40 overflow-y-auto bg-black/60 p-2.5 rounded border border-slate-800/70">
                  {sub.output}
                </div>

                {/* Final Verified Command */}
                <div className="pt-1 flex items-center justify-between text-[10px]">
                  <span className="text-slate-400">Final Executed Fix:</span>
                  <code className="text-emerald-400 font-bold truncate max-w-[200px]">
                    {sub.finalCommand}
                  </code>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
