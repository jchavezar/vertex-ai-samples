import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle2,
  Cpu,
  Database,
  ArrowRight,
  Code2,
  Activity,
  Zap,
  X,
} from 'lucide-react';
import { RefactorEvent } from '../types';
import { subscribeToRefactorStream } from '../services/api';

interface RefactorPipelineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCompleteAndSwitchView: () => void;
}

export const RefactorPipelineModal: React.FC<RefactorPipelineModalProps> = ({
  isOpen,
  onClose,
  onCompleteAndSwitchView,
}) => {
  const [currentStage, setCurrentStage] = useState(1);
  const [progress, setProgress] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [selectedCodeArtifact, setSelectedCodeArtifact] = useState<string | null>(null);

  const startPipeline = () => {
    setProgress(5);
    setIsFinished(false);
    setSummary(null);
    setLogs(['[SYS_INIT] Initializing Antigravity Autonomous Refactor Engine...']);

    const unsubscribe = subscribeToRefactorStream((evt: RefactorEvent) => {
      setProgress(evt.progress_percentage);
      setCurrentStage(evt.current_stage);

      if (evt.step) {
        setLogs((prev) => [
          ...prev,
          `[STAGE_${evt.step!.stage_id}] ${evt.step!.stage_name}: ${evt.step!.title} (${evt.step!.status})`,
        ]);

        if (evt.step.code_artifact) {
          setSelectedCodeArtifact(evt.step.code_artifact);
        }
      }

      if (evt.event === 'pipeline_finished') {
        setIsFinished(true);
        setSummary(evt.summary);
        setLogs((prev) => [
          ...prev,
          '[SYS_FINISH] Autonomous Refactor completed successfully in 4.8s. Agent-Native Canvas is ready.',
        ]);
      }
    });

    return unsubscribe;
  };

  useEffect(() => {
    if (isOpen) {
      const unsub = startPipeline();
      return () => {
        if (unsub) unsub();
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 md:p-8">
      <div className="bg-[#0f172a] border border-cyan-500/40 rounded-2xl max-w-5xl w-full max-h-[90vh] flex flex-col shadow-2xl shadow-cyan-950/60 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-600 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <div className="h-full w-full bg-slate-900 rounded-[10px] flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-cyan-400 animate-spin" style={{ animationDuration: '4s' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-extrabold text-slate-100 text-sm tracking-wide">
                  ANTIGRAVITY AUTONOMOUS REFACTOR PIPELINE
                </h2>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800 rounded font-bold">
                  {isFinished ? 'SYNTHESIS COMPLETE' : 'PROCESSING AST...'}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Transforming 2015 Relational ERP Table into 2026 Reactive Generative UI
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Tracker Bar */}
        <div className="px-6 py-3 bg-slate-900/40 border-b border-slate-800/80">
          <div className="flex items-center justify-between text-xs font-mono mb-2">
            <span className="text-cyan-400 font-bold">
              Refactor Progress: {progress}%
            </span>
            <span className="text-slate-400">
              Stage {currentStage} of 3
            </span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-emerald-400 transition-all duration-500 rounded-full shadow-lg shadow-cyan-500/50"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Modal Body: 3-Stage Cards + Code / Terminal Preview */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* Stage Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Stage 1 */}
            <div
              className={`p-4 rounded-xl border transition-all ${
                currentStage === 1
                  ? 'bg-cyan-950/30 border-cyan-500/80 ring-1 ring-cyan-500/40'
                  : currentStage > 1
                  ? 'bg-slate-900/60 border-emerald-500/40'
                  : 'bg-slate-900/30 border-slate-800 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4 text-cyan-400" />
                  <span className="font-bold text-xs text-slate-200">1. Schema Discovery</span>
                </div>
                {currentStage > 1 ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : (
                  <Activity className="h-4 w-4 text-cyan-400 animate-spin" />
                )}
              </div>
              <p className="text-[11px] text-slate-400">
                Scans legacy 20-column DDL, unindexed joins, and 4.2s latency bottlenecks.
              </p>
              <div className="mt-3 text-[10px] font-mono text-cyan-300/80 bg-cyan-950/60 p-2 rounded border border-cyan-900/40">
                &bull; 160 ERP records analyzed<br />
                &bull; 20 columns AST parsed
              </div>
            </div>

            {/* Stage 2 */}
            <div
              className={`p-4 rounded-xl border transition-all ${
                currentStage === 2
                  ? 'bg-cyan-950/30 border-cyan-500/80 ring-1 ring-cyan-500/40'
                  : currentStage > 2
                  ? 'bg-slate-900/60 border-emerald-500/40'
                  : 'bg-slate-900/30 border-slate-800 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-indigo-400" />
                  <span className="font-bold text-xs text-slate-200">2. ADK Tool Synthesis</span>
                </div>
                {currentStage > 2 ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : currentStage === 2 ? (
                  <Activity className="h-4 w-4 text-indigo-400 animate-spin" />
                ) : null}
              </div>
              <p className="text-[11px] text-slate-400">
                Generates Google ADK tool declarations and wires Gemini 2.5/3 reasoning graph.
              </p>
              <div className="mt-3 text-[10px] font-mono text-indigo-300/80 bg-indigo-950/60 p-2 rounded border border-indigo-900/40">
                &bull; 6 ADK tools synthesized<br />
                &bull; A2A Sentinel mesh active
              </div>
            </div>

            {/* Stage 3 */}
            <div
              className={`p-4 rounded-xl border transition-all ${
                currentStage === 3 && !isFinished
                  ? 'bg-cyan-950/30 border-cyan-500/80 ring-1 ring-cyan-500/40'
                  : isFinished
                  ? 'bg-emerald-950/30 border-emerald-500/80'
                  : 'bg-slate-900/30 border-slate-800 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-emerald-400" />
                  <span className="font-bold text-xs text-slate-200">3. Generative Canvas</span>
                </div>
                {isFinished ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : currentStage === 3 ? (
                  <Activity className="h-4 w-4 text-emerald-400 animate-spin" />
                ) : null}
              </div>
              <p className="text-[11px] text-slate-400">
                Builds dynamic React 19 Generative UI with 50ms What-If shock engine.
              </p>
              <div className="mt-3 text-[10px] font-mono text-emerald-300/80 bg-emerald-950/60 p-2 rounded border border-emerald-900/40">
                &bull; 50ms reactive recalculation<br />
                &bull; 1-click Board Memo generator
              </div>
            </div>
          </div>

          {/* Code Artifact & Live Stream Terminal */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Synthesized Code Viewer */}
            <div className="bg-slate-950 rounded-xl border border-slate-800 p-4 flex flex-col">
              <div className="flex items-center justify-between mb-2 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <Code2 className="h-4 w-4 text-cyan-400" />
                  <span className="text-xs font-mono font-bold text-slate-300">
                    Synthesized Artifact Preview
                  </span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">
                  ADK Python / React 19 AST
                </span>
              </div>
              <pre className="text-[11px] font-mono text-cyan-300 bg-slate-900/80 p-3 rounded border border-slate-800 overflow-x-auto max-h-48 overflow-y-auto leading-relaxed">
                {selectedCodeArtifact || '# Synthesizing ADK & Generative Canvas artifacts...'}
              </pre>
            </div>

            {/* Live Terminal Stream Log */}
            <div className="bg-slate-950 rounded-xl border border-slate-800 p-4 flex flex-col">
              <div className="flex items-center justify-between mb-2 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-emerald-400" />
                  <span className="text-xs font-mono font-bold text-slate-300">
                    Live Refactor Execution Stream
                  </span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                  SSE STREAM ACTIVE
                </span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 bg-slate-900/80 p-3 rounded border border-slate-800 max-h-48 overflow-y-auto space-y-1.5">
                {logs.map((log, i) => (
                  <div key={i} className="text-slate-300">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Performance Comparison Banner */}
          {isFinished && summary && (
            <div className="bg-gradient-to-r from-cyan-950/60 via-slate-900 to-emerald-950/60 border border-cyan-500/50 p-4 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <span className="text-xs font-bold text-emerald-400 tracking-wide uppercase flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  Autonomous Refactor Certified
                </span>
                <p className="text-xs text-slate-300 font-medium">
                  {summary.performance_gain} &bull; {summary.dev_time_saved}
                </p>
              </div>

              <div className="flex items-center gap-3 font-mono text-xs">
                <div className="px-3 py-1.5 rounded bg-slate-800/80 border border-slate-700 text-amber-300">
                  Legacy: 4,200ms
                </div>
                <ArrowRight className="h-4 w-4 text-cyan-400" />
                <div className="px-3 py-1.5 rounded bg-emerald-900/60 border border-emerald-500 text-emerald-300 font-bold">
                  Modern: 45ms
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
          >
            Close Pipeline View
          </button>

          <button
            onClick={() => {
              onClose();
              onCompleteAndSwitchView();
            }}
            disabled={!isFinished}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs shadow-lg transition-all ${
              isFinished
                ? 'bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-500 text-slate-950 hover:brightness-110 shadow-emerald-500/25'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            <span>Launch Agent-Native Canvas (2026)</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
