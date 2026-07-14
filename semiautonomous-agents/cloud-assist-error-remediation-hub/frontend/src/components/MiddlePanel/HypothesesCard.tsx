import React, { useState } from 'react';
import { HypothesisItem } from '../../types';
import { Target, Check, Copy, Terminal, Zap, Play, CheckCircle2, AlertCircle } from 'lucide-react';
import { RichTextRenderer } from '../RichTextRenderer';

interface HypothesesCardProps {
  hypotheses: HypothesisItem[];
  serviceName?: string;
}

interface ExecutionResult {
  command: string;
  exitCode: number;
  stdout: string;
  stderr: string;
  executedAt: string;
  sandboxId: string;
}

export const HypothesesCard: React.FC<HypothesesCardProps> = ({ hypotheses, serviceName = "GCP Service" }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [runningIndex, setRunningIndex] = useState<number | null>(null);
  const [execResults, setExecResults] = useState<Record<number, ExecutionResult>>({});

  const copyCommand = (cmd: string, idx: number) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const runCommandInSandbox = async (cmd: string, idx: number) => {
    setRunningIndex(idx);
    try {
      const res = await fetch('http://127.0.0.1:8088/api/execute-remediation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, serviceName })
      });
      if (res.ok) {
        const data: ExecutionResult = await res.json();
        setExecResults((prev) => ({ ...prev, [idx]: data }));
      } else {
        setExecResults((prev) => ({
          ...prev,
          [idx]: {
            command: cmd,
            exitCode: 1,
            stdout: '',
            stderr: `API Execution Error: Status ${res.status}`,
            executedAt: new Date().toISOString(),
            sandboxId: 'error'
          }
        }));
      }
    } catch (err: any) {
      setExecResults((prev) => ({
        ...prev,
        [idx]: {
          command: cmd,
          exitCode: 1,
          stdout: '',
          stderr: `Network Error: Could not reach sandbox engine on port 8088.`,
          executedAt: new Date().toISOString(),
          sandboxId: 'offline'
        }
      }));
    } finally {
      setRunningIndex(null);
    }
  };

  if (hypotheses.length === 0) return null;

  return (
    <div className="rounded-xl bg-[#111622]/90 border border-slate-800/80 p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
            <Target className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Ranked Root-Cause Hypotheses</h2>
            <p className="text-[11px] text-slate-400">AI confidence ranking [-1.0 to 1.0] with One-Click Sandbox Execution</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/30">
          {hypotheses.length} {hypotheses.length === 1 ? 'Hypothesis' : 'Hypotheses'} Ranked
        </span>
      </div>

      <div className="space-y-4">
        {hypotheses.map((hyp, idx) => {
          const score = hyp.relevanceScore !== undefined && hyp.relevanceScore !== null ? hyp.relevanceScore : 0.85;
          const pct = Math.min(100, Math.max(0, Math.round(score * 100)));

          return (
            <div
              key={hyp.id || idx}
              className="rounded-xl bg-slate-950/70 border border-slate-800/80 p-4 transition-all hover:border-slate-700/80"
            >
              {/* Header: Title + Numeric Relevance Badge */}
              <div className="flex items-start justify-between gap-3 mb-2.5">
                <h3 className="text-xs font-bold text-white leading-relaxed flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-300 flex items-center justify-center text-[10px] font-mono font-bold">
                    #{idx + 1}
                  </span>
                  <span>{hyp.title}</span>
                </h3>

                <div className="flex items-center space-x-2 flex-shrink-0">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Relevance:</span>
                  <span
                    className={`text-xs font-mono font-bold px-2 py-0.5 rounded-md border ${
                      score >= 0.8
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-sm shadow-emerald-500/10'
                        : score >= 0.5
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                        : 'bg-slate-800 text-slate-300 border-slate-700'
                    }`}
                  >
                    {score.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    score >= 0.8
                      ? 'bg-gradient-to-r from-emerald-500 to-cyan-400'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                  }`}
                  style={{ width: `${pct}%` }}
                ></div>
              </div>

              {/* Root Cause Technical Overview with Rich Markdown Rendering */}
              <div className="mb-3 bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/60">
                <RichTextRenderer text={hyp.overviewText} />
              </div>

              {/* Clickable Remediation CLI Commands with One-Click Sandbox Execution */}
              {hyp.remediationCommands && hyp.remediationCommands.length > 0 && (
                <div className="mt-3 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1.5 text-[11px] font-semibold text-cyan-400">
                      <Terminal className="w-3.5 h-3.5" />
                      <span>Clickable Remediation Commands (One-Click Sandbox Execution)</span>
                    </div>
                  </div>

                  {hyp.remediationCommands.map((cmd, cIdx) => {
                    const uniqueKey = idx * 100 + cIdx;
                    const isRunning = runningIndex === uniqueKey;
                    const execResult = execResults[uniqueKey];

                    return (
                      <div key={cIdx} className="space-y-2">
                        <div className="flex items-center justify-between bg-black/70 border border-slate-800 rounded-lg p-2.5 font-mono text-[11px] text-emerald-300 hover:border-cyan-500/40 transition-colors">
                          <code className="overflow-x-auto mr-3">{cmd}</code>

                          <div className="flex items-center space-x-1.5 flex-shrink-0">
                            {/* Copy Button */}
                            <button
                              onClick={() => copyCommand(cmd, uniqueKey)}
                              className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1 text-[10px]"
                              title="Copy command to clipboard"
                            >
                              {copiedIndex === uniqueKey ? (
                                <>
                                  <Check className="w-3 h-3 text-emerald-400" />
                                  <span className="text-emerald-400">Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3 h-3" />
                                  <span>Copy</span>
                                </>
                              )}
                            </button>

                            {/* One-Click Execute in Sandbox Button */}
                            <button
                              onClick={() => runCommandInSandbox(cmd, uniqueKey)}
                              disabled={isRunning}
                              className="px-2.5 py-1 rounded bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 disabled:opacity-50 text-white transition-all flex items-center gap-1 text-[10px] font-bold shadow-sm"
                              title="Execute directly in secure Antigravity Linux Sandbox"
                            >
                              {isRunning ? (
                                <>
                                  <span className="w-2.5 h-2.5 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
                                  <span>Running...</span>
                                </>
                              ) : (
                                <>
                                  <Zap className="w-3 h-3 text-amber-300 fill-amber-300" />
                                  <span>Run in Sandbox</span>
                                </>
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Interactive Execution Sandbox Output Console */}
                        {execResult && (
                          <div
                            className={`rounded-lg p-3 font-mono text-[11px] border space-y-1.5 ${
                              execResult.exitCode === 0
                                ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                                : 'bg-rose-950/30 border-rose-500/40 text-rose-300'
                            }`}
                          >
                            <div className="flex items-center justify-between border-b border-slate-800/80 pb-1 text-[10px] text-slate-400">
                              <div className="flex items-center space-x-1.5">
                                {execResult.exitCode === 0 ? (
                                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                                ) : (
                                  <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                                )}
                                <span className="font-bold">
                                  {execResult.exitCode === 0
                                    ? 'SUCCESS: Executed in Antigravity Sandbox'
                                    : 'EXECUTION ERROR'}
                                </span>
                              </div>
                              <span>Sandbox: {execResult.sandboxId}</span>
                            </div>

                            <div className="whitespace-pre-wrap overflow-x-auto text-[11px]">
                              {execResult.stdout || execResult.stderr}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Affected Resource */}
              {hyp.relevantResources && hyp.relevantResources.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">Affected Resource:</span>
                  {hyp.relevantResources.map((r, rIdx) => (
                    <code
                      key={rIdx}
                      className="text-[10px] font-mono text-cyan-300 bg-cyan-950/40 border border-cyan-800/50 px-2 py-0.5 rounded"
                    >
                      {r.split('/').pop()}
                    </code>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
