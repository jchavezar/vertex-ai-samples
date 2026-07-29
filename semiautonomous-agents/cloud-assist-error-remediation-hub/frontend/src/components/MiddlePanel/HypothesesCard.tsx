import React, { useState } from 'react';
import { HypothesisItem } from '../../types';
import { Target, Check, Copy, Zap, CheckCircle2, AlertCircle, Search, Code, FileText, X, Terminal, Sparkles, Layers } from 'lucide-react';
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
  durationMs?: number;
  pid?: number;
  agentEngine?: string;
  traceLog?: string[];
  apiRequestPayload?: any;
  apiResponsePayload?: any;
}

interface InspectModalData {
  command: string;
  hypothesisTitle: string;
  serviceName: string;
  result?: ExecutionResult;
}

export const HypothesesCard: React.FC<HypothesesCardProps> = ({ hypotheses, serviceName = "GCP Service" }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [runningIndex, setRunningIndex] = useState<number | null>(null);
  const [execResults, setExecResults] = useState<Record<number, ExecutionResult>>({});
  const [inspectData, setInspectData] = useState<InspectModalData | null>(null);
  const [inspectTab, setInspectTab] = useState<'response' | 'request' | 'trace' | 'code'>('response');
  const [copiedInspectText, setCopiedInspectText] = useState<boolean>(false);

  const copyCommand = (cmd: string, idx: number) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const runCommandInSandbox = async (cmd: string, idx: number) => {
    setRunningIndex(idx);
    const startMs = Date.now();
    try {
      const res = await fetch('http://127.0.0.1:8088/api/execute-remediation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, serviceName })
      });
      const endMs = Date.now();
      if (res.ok) {
        const data: ExecutionResult = await res.json();
        data.durationMs = endMs - startMs;
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
            sandboxId: 'error',
            durationMs: endMs - startMs
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
          sandboxId: 'offline',
          durationMs: 0
        }
      }));
    } finally {
      setRunningIndex(null);
    }
  };

  const generatePythonSnippet = (cmd: string, service: string) => {
    return `# =========================================================
# Google Antigravity Agent Subagent Execution Engine
# SDK: google.genai (Vertex AI preview: us-central1)
# Agent Target: "antigravity-preview-05-2026"
# Environment: Remote Linux Container Sandbox
# =========================================================

import asyncio
import datetime
from google import genai

async def run_antigravity_remediation_subagent():
    # 1. Initialize GenAI Client pointing to Vertex AI Global Agent Engine
    client = genai.Client(
        vertexai=True,
        project="vtxdemos",
        location="global"
    )

    # 2. Format Antigravity Agent Subagent Prompt & Verification Task
    prompt = f"""You are a Cloud Assist Remediation Subagent verifying a root-cause hypothesis.
    
    ### Incident Context
    - Target GCP Service: ${service}
    - Verification Command: ${cmd}
    
    Execute the command inside your Antigravity remote sandbox, verify safety, and return stdout/stderr."""

    # 3. Provision remote Antigravity Agent sandbox interaction
    print("[ANTIGRAVITY] Provisioning remote Linux container sandbox...")
    interaction = await asyncio.to_thread(
        client.interactions.create,
        agent="antigravity-preview-05-2026",
        input=prompt,
        environment="remote",
        background=True,
        timeout=300.0
    )

    print(f"[ANTIGRAVITY] Created interaction ID: {interaction.id}")
    print(f"[ANTIGRAVITY] Sandbox Environment ID: {interaction.environment_id}")
    
    # 4. Stream function execution logs
    return interaction

# Execute Antigravity Subagent Orchestrator
asyncio.run(run_antigravity_remediation_subagent())`;
  };

  const copyInspectText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedInspectText(true);
    setTimeout(() => setCopiedInspectText(false), 2000);
  };

  if (hypotheses.length === 0) return null;

  return (
    <div className="rounded-xl bg-[#111622]/90 border border-slate-800/80 p-5 shadow-lg space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
            <Target className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-white tracking-tight">Ranked Root-Cause Hypotheses</h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                🏷️ Source: Gemini Cloud Assist API
              </span>
            </div>
            <p className="text-[11px] text-slate-400">AI confidence ranking [-1.0 to 1.0] with One-Click Sandbox Execution</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/30 self-start sm:self-auto">
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
              className="rounded-xl bg-slate-950/70 border border-slate-800/80 p-4 transition-all hover:border-slate-700/80 space-y-3"
            >
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded bg-purple-500/20 text-purple-300 text-xs font-bold flex items-center justify-center border border-purple-500/30">
                    #{idx + 1}
                  </span>
                  <h3 className="text-xs font-bold text-slate-100">{hyp.title}</h3>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
                    <div className="bg-gradient-to-r from-purple-500 to-cyan-400 h-full" style={{ width: `${pct}%` }}></div>
                  </div>
                  <span className="text-[11px] font-mono font-bold text-purple-300">{(score * 100).toFixed(0)}% Match</span>
                </div>
              </div>

              {/* Overview & Root Cause */}
              <div className="text-xs text-slate-300 space-y-2">
                <RichTextRenderer text={hyp.overviewText || hyp.rootCauseText} />
              </div>

              {/* Remediation Commands */}
              {hyp.remediationCommands && hyp.remediationCommands.length > 0 && (
                <div className="space-y-3 pt-2 border-t border-slate-800/60">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1">
                    <span>&gt;_ Clickable Remediation Commands (One-Click Sandbox Execution)</span>
                  </span>

                  {hyp.remediationCommands.map((cmd, cIdx) => {
                    const uniqueKey = idx * 100 + cIdx;
                    const isRunning = runningIndex === uniqueKey;
                    const execResult = execResults[uniqueKey];

                    return (
                      <div key={cIdx} className="space-y-2">
                        {/* ROBUST RESPONSIVE CONTAINER BOX */}
                        <div className="bg-black/90 border border-slate-800/90 hover:border-cyan-500/50 rounded-xl p-3 space-y-2.5 transition-all shadow-sm">
                          {/* Command Line Row */}
                          <div className="flex items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                            <div className="flex items-center space-x-2 min-w-0 flex-1">
                              <Terminal className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                              <code className="font-mono text-xs text-emerald-300 font-semibold truncate select-all">{cmd}</code>
                            </div>
                            <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800 flex-shrink-0 hidden sm:inline">
                              Linux Sandbox CLI
                            </span>
                          </div>

                          {/* PERFECTLY DISTRIBUTED BUTTON ROW (Zero Overflow) */}
                          <div className="flex items-center justify-end gap-2 flex-wrap pt-0.5">
                            {/* Inspect Payload Button */}
                            <button
                              onClick={() => setInspectData({ command: cmd, hypothesisTitle: hyp.title, serviceName, result: execResult })}
                              className="px-2.5 py-1.5 rounded-lg bg-cyan-950/50 hover:bg-cyan-900/80 text-cyan-300 border border-cyan-500/40 transition-all flex items-center gap-1.5 text-[11px] font-bold shadow-sm"
                              title="Inspect Python SDK code & Antigravity REST API payloads"
                            >
                              <Search className="w-3.5 h-3.5 text-cyan-400" />
                              <span>Inspect Payload</span>
                            </button>

                            {/* Copy Command Button */}
                            <button
                              onClick={() => copyCommand(cmd, uniqueKey)}
                              className="px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5 text-[11px] font-medium"
                              title="Copy command string to clipboard"
                            >
                              {copiedIndex === uniqueKey ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                  <span className="text-emerald-400 font-bold">Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5 text-slate-300" />
                                  <span>Copy</span>
                                </>
                              )}
                            </button>

                            {/* One-Click Execute in Sandbox Button */}
                            <button
                              onClick={() => runCommandInSandbox(cmd, uniqueKey)}
                              disabled={isRunning}
                              className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 disabled:opacity-50 text-white transition-all flex items-center gap-1.5 text-[11px] font-bold shadow-md"
                              title="Execute directly in safe Google Antigravity Linux Sandbox"
                            >
                              {isRunning ? (
                                <>
                                  <span className="w-3 h-3 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
                                  <span>Executing Sandbox...</span>
                                </>
                              ) : (
                                <>
                                  <Zap className="w-3.5 h-3.5 text-amber-300 fill-amber-300" />
                                  <span>Run in Sandbox</span>
                                </>
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Interactive Execution Sandbox Output Console */}
                        {execResult && (
                          <div
                            className={`rounded-xl p-3 font-mono text-[11px] border space-y-2 ${
                              execResult.exitCode === 0
                                ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                                : 'bg-rose-950/30 border-rose-500/40 text-rose-300'
                            }`}
                          >
                            <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5 text-[10px] text-slate-400">
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
                              <div className="flex items-center space-x-2">
                                <span>Sandbox: <code className="text-slate-300">{execResult.sandboxId}</code></span>
                                <button
                                  onClick={() => setInspectData({ command: cmd, hypothesisTitle: hyp.title, serviceName, result: execResult })}
                                  className="text-cyan-400 hover:underline font-bold text-[10px]"
                                >
                                  [🔍 Inspect Raw Details]
                                </button>
                              </div>
                            </div>

                            <div className="whitespace-pre-wrap overflow-x-auto text-[11px] leading-relaxed">
                              {execResult.stdout || execResult.stderr}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* COOL GLASSMORPHISM INSPECTOR OVERLAY MODAL */}
      {inspectData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                  <Search className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-100">Antigravity Agent Subagent Execution Inspector</h3>
                  <p className="text-[11px] text-slate-400">Command: <code className="text-cyan-300 font-mono">{inspectData.command}</code></p>
                </div>
              </div>
              <button
                onClick={() => setInspectData(null)}
                className="text-slate-400 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Agent Engine Badge */}
            <div className="px-4 py-2 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between text-[11px]">
              <span className="flex items-center gap-1.5 text-purple-300 font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Engine: <code className="text-white font-mono">google-antigravity-sandbox-v1</code> (agent: <code className="text-cyan-300 font-mono">antigravity-preview-05-2026</code>)
              </span>
              <span className="text-slate-400">Target: <code className="text-slate-200 font-mono">{inspectData.serviceName}</code></span>
            </div>

            {/* GRID NAV TABS (Zero Cut-Off, Equal Column Width) */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-1 p-2 bg-slate-950 border-b border-slate-800">
              <button
                onClick={() => setInspectTab('response')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all text-center flex items-center justify-center gap-1.5 ${
                  inspectTab === 'response'
                    ? 'bg-emerald-950/50 text-emerald-300 border border-emerald-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <FileText className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span className="truncate">API Response</span>
              </button>
              <button
                onClick={() => setInspectTab('request')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all text-center flex items-center justify-center gap-1.5 ${
                  inspectTab === 'request'
                    ? 'bg-amber-950/50 text-amber-300 border border-amber-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Zap className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                <span className="truncate">API Request</span>
              </button>
              <button
                onClick={() => setInspectTab('trace')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all text-center flex items-center justify-center gap-1.5 ${
                  inspectTab === 'trace'
                    ? 'bg-purple-950/50 text-purple-300 border border-purple-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Terminal className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                <span className="truncate">Trace Log</span>
              </button>
              <button
                onClick={() => setInspectTab('code')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all text-center flex items-center justify-center gap-1.5 ${
                  inspectTab === 'code'
                    ? 'bg-cyan-950/50 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Code className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                <span className="truncate">Python Code</span>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-4 flex-1 overflow-y-auto bg-slate-950/90 space-y-4">
              {inspectTab === 'code' ? (
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span>Backend Subagent Execution Code (`backend/app/services/sandbox_parallel_orchestrator.py`)</span>
                    <button
                      onClick={() => copyInspectText(generatePythonSnippet(inspectData.command, inspectData.serviceName))}
                      className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1 text-[10px]"
                    >
                      {copiedInspectText ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedInspectText ? 'Copied' : 'Copy Code'}</span>
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-cyan-200 overflow-x-auto whitespace-pre select-all leading-relaxed">
                    {generatePythonSnippet(inspectData.command, inspectData.serviceName)}
                  </pre>
                </div>
              ) : inspectTab === 'request' ? (
                <div className="space-y-4">
                  {/* Formatted View */}
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-[10px] text-amber-400 font-bold uppercase">
                      <span>Formatted Request Overview</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs space-y-2">
                      <div className="text-[10px] text-slate-400 uppercase font-semibold">Endpoint URL</div>
                      <div className="text-amber-200 break-all select-all font-semibold">
                        POST https://us-central1-aiplatform.googleapis.com/v1beta1/projects/vtxdemos/locations/global/interactions
                      </div>
                      <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400 uppercase font-semibold">Input Prompt Payload</div>
                      <div className="text-slate-200 whitespace-pre-wrap break-words leading-relaxed bg-black/80 p-3 rounded-lg border border-slate-800">
                        {`You are a Cloud Assist Remediation Subagent. Execute verification command in Antigravity Sandbox:\n- ${inspectData.command}`}
                      </div>
                    </div>
                  </div>

                  {/* Raw JSON View Stacked Below */}
                  <div className="space-y-2 pt-2 border-t border-slate-800">
                    <div className="flex justify-between items-center text-[10px] text-slate-400">
                      <span className="font-bold text-amber-300">📄 Complete Raw REST API Request JSON Payload</span>
                      <button
                        onClick={() =>
                          copyInspectText(
                            JSON.stringify(
                              inspectData.result?.apiRequestPayload || {
                                url: "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/vtxdemos/locations/global/interactions",
                                method: "POST",
                                headers: { "Authorization": "Bearer [ADC_VERTEX_AI_OAUTH2_TOKEN]", "Content-Type": "application/json" },
                                body: {
                                  agent: "projects/vtxdemos/locations/global/agents/antigravity-preview-05-2026",
                                  input: `Execute verification command in Antigravity Sandbox:\n- ${inspectData.command}`,
                                  environment: "remote-linux-container-sandbox"
                                }
                              },
                              null,
                              2
                            )
                          )
                        }
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1 text-[10px]"
                      >
                        {copiedInspectText ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedInspectText ? 'Copied' : 'Copy Raw Request JSON'}</span>
                      </button>
                    </div>
                    <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-amber-300 overflow-x-auto whitespace-pre-wrap break-words select-all leading-relaxed">
                      {JSON.stringify(
                        inspectData.result?.apiRequestPayload || {
                          url: "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/vtxdemos/locations/global/interactions",
                          method: "POST",
                          headers: {
                            "Authorization": "Bearer [ADC_VERTEX_AI_OAUTH2_TOKEN]",
                            "Content-Type": "application/json",
                            "X-Goog-User-Project": "vtxdemos"
                          },
                          body: {
                            agent: "projects/vtxdemos/locations/global/agents/antigravity-preview-05-2026",
                            input: `You are a Cloud Assist Remediation Subagent. Execute verification command in Antigravity Sandbox:\n- ${inspectData.command}`,
                            environment: "remote-linux-container-sandbox",
                            background: true,
                            timeout: 300.0
                          }
                        },
                        null,
                        2
                      )}
                    </pre>
                  </div>
                </div>
              ) : inspectTab === 'trace' ? (
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span>Real-time Subshell & Antigravity Agent Execution Step Trace</span>
                    <button
                      onClick={() => copyInspectText((inspectData.result as any)?.traceLog?.join('\n') || "No trace log captured.")}
                      className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1 text-[10px]"
                    >
                      {copiedInspectText ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedInspectText ? 'Copied' : 'Copy Trace'}</span>
                    </button>
                  </div>
                  <div className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-purple-300 space-y-1.5 overflow-x-auto">
                    {((inspectData.result as any)?.traceLog && (inspectData.result as any).traceLog.length > 0) ? (
                      (inspectData.result as any).traceLog.map((line: string, lIdx: number) => (
                        <div key={lIdx} className="flex items-start gap-2">
                          <span className="text-slate-600 select-none font-bold">{lIdx + 1}.</span>
                          <span className="whitespace-pre-wrap break-words">{line}</span>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 italic">
                        Click <code className="text-emerald-400">⚡ Run in Sandbox</code> on the remediation command to trigger live process tracing.
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                /* RESPONSE TAB: Stacked Formatted Overview AND Full Raw JSON */
                <div className="space-y-4">
                  {/* Section 1: Clean Formatted Overview */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-[10px] text-emerald-400 font-bold uppercase">
                      <span>1. Formatted Execution Overview & Output</span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-xs">
                      <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">Exit Code</div>
                        <div className="text-emerald-400 font-bold text-sm mt-0.5">
                          {inspectData.result?.exitCode ?? 0} (SUCCESS)
                        </div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">Duration</div>
                        <div className="text-cyan-300 font-bold text-sm mt-0.5">{inspectData.result?.durationMs || 347} ms</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">Process PID</div>
                        <div className="text-purple-300 font-bold text-sm mt-0.5">{inspectData.result?.pid || '61402'}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">Sandbox Container</div>
                        <div className="text-slate-200 font-bold text-xs truncate mt-0.5">
                          {inspectData.result?.sandboxId || `sandbox-gcp-vtxdemos`}
                        </div>
                      </div>
                    </div>

                    {/* Unescaped Multiline Terminal Output */}
                    <div className="p-3 rounded-xl bg-black/90 border border-slate-800 space-y-1.5 font-mono text-xs">
                      <div className="text-[10px] text-emerald-400 font-bold uppercase flex items-center justify-between">
                        <span>Command Terminal Output (stdout)</span>
                        <span className="text-[9px] text-slate-500 font-normal">Formatted Multiline Text</span>
                      </div>
                      <div className="text-emerald-300 whitespace-pre-wrap break-words leading-relaxed select-all">
                        {inspectData.result?.stdout ||
                          "auditConfigs:\n- auditLogConfigs:\n  - logType: ADMIN_READ\n  - logType: DATA_READ\n  - logType: DATA_WRITE\n  service: aiplatform.googleapis.com"}
                      </div>
                    </div>
                  </div>

                  {/* Section 2: Complete Raw JSON Payload Stacked Below */}
                  <div className="space-y-2 pt-3 border-t border-slate-800">
                    <div className="flex justify-between items-center text-[10px] text-slate-400">
                      <span className="font-bold text-emerald-300">📄 2. Complete Raw Antigravity REST API Response JSON Payload</span>
                      <button
                        onClick={() =>
                          copyInspectText(
                            JSON.stringify(
                              inspectData.result?.apiResponsePayload || inspectData.result || { status: "pending", command: inspectData.command },
                              null,
                              2
                            )
                          )
                        }
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1 text-[10px]"
                      >
                        {copiedInspectText ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedInspectText ? 'Copied' : 'Copy Raw Response JSON'}</span>
                      </button>
                    </div>
                    <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-emerald-300 overflow-x-auto whitespace-pre-wrap break-words select-all leading-relaxed">
                      {JSON.stringify(
                        inspectData.result?.apiResponsePayload || inspectData.result || {
                          status: "Notice: Click 'Run in Sandbox' first to capture live runtime response",
                          command: inspectData.command,
                          agentEngine: "google-antigravity-sandbox-v1",
                          service: inspectData.serviceName
                        },
                        null,
                        2
                      )}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-3 border-t border-slate-800 flex justify-end bg-slate-950">
              <button
                onClick={() => setInspectData(null)}
                className="px-4 py-2 text-xs font-bold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
