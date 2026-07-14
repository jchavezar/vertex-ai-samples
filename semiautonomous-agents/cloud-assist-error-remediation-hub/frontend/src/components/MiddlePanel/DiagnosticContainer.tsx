import React from 'react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';
import { ExecutiveRecapCard } from './ExecutiveRecapCard';
import { HypothesesCard } from './HypothesesCard';
import { RemediationStepsCard } from './RemediationStepsCard';
import { ReActEvidenceCard } from './ReActEvidenceCard';
import { ParallelSandboxCard } from './ParallelSandboxCard';
import { HybridAgentFlowCard } from './HybridAgentFlowCard';
import { Sparkles, Server, ShieldCheck, Activity, Terminal } from 'lucide-react';

interface DiagnosticContainerProps {
  selectedError: GcpErrorItem | null;
  diagnostic: CloudAssistDiagnostic | null;
  isLoading: boolean;
}

export const DiagnosticContainer: React.FC<DiagnosticContainerProps> = ({
  selectedError,
  diagnostic,
  isLoading
}) => {
  if (!selectedError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-700/80 flex items-center justify-center mb-4 shadow-xl">
          <Sparkles className="w-7 h-7 text-cyan-400" />
        </div>
        <h3 className="text-sm font-bold text-white tracking-tight">No Issue Selected</h3>
        <p className="text-xs text-slate-400 max-w-sm mt-1.5 leading-relaxed">
          Select an error from the left Cloud Logging panel to trigger autonomous Gemini Cloud Assist diagnosis and proactive remediation.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center space-y-6">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center animate-pulse">
            <Sparkles className="w-7 h-7 text-cyan-400" />
          </div>
          <div className="absolute -inset-2 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 opacity-25 blur-lg animate-pulse"></div>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-bold text-white tracking-tight">Gemini Cloud Assist Diagnostic Pipeline Active</h3>
          <p className="text-xs text-slate-400">
            Running autonomous 4-Step lifecycle on <code className="text-cyan-400">{selectedError.serviceName}</code>...
          </p>
        </div>

        {/* Live Step Tracker */}
        <div className="w-full max-w-md bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-left space-y-3 shadow-inner">
          <div className="flex items-center space-x-3 text-xs text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>1. Seeding symptom observation into Investigation...</span>
          </div>
          <div className="flex items-center space-x-3 text-xs text-cyan-300">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>2. Creating immutable state snapshot revision...</span>
          </div>
          <div className="flex items-center space-x-3 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span>
            <span>3. Executing autonomous ReAct diagnostic observers...</span>
          </div>
          <div className="flex items-center space-x-3 text-xs text-slate-400">
            <span className="w-2 h-2 rounded-full bg-slate-600"></span>
            <span>4. Extracting ranked hypotheses & proactive fixes...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!diagnostic) {
    return null;
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Selected Error Header Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900/90 via-[#131a29]/90 to-slate-900/90 border border-slate-800/90 shadow-md">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span
                className={`text-[10px] font-bold tracking-wider px-2 py-0.5 rounded uppercase ${
                  selectedError.severity === 'CRITICAL'
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {selectedError.severity}
              </span>
              <span className="text-xs text-slate-400">&bull;</span>
              <span className="text-xs font-semibold text-cyan-400">{selectedError.serviceName}</span>
              <span className="text-xs text-slate-400">&bull;</span>
              <span className="text-xs font-mono text-slate-400">{selectedError.resourceType}</span>
            </div>
            <h1 className="text-base font-bold text-white tracking-tight">{selectedError.summary}</h1>
          </div>

          <div className="text-right flex-shrink-0">
            <span className="text-[10px] text-slate-400 font-mono">
              Investigation: {diagnostic.investigationName.split('/').pop()}
            </span>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-800/80 font-mono text-xs text-slate-300 bg-black/50 p-2.5 rounded border border-slate-800/60 overflow-x-auto">
          {selectedError.fullText}
        </div>
      </div>

      {/* Stage 0: Interactive 5-Stage Hybrid Split-Plane Flow Diagram & Policy Gate */}
      <HybridAgentFlowCard
        selectedError={selectedError}
        diagnostic={diagnostic}
      />

      {/* Container 1: Executive Recap */}
      <ExecutiveRecapCard
        recapText={diagnostic.recapText}
        executionState={diagnostic.executionState}
      />

      {/* Container 2: Ranked Hypotheses with One-Click Clickable Sandbox Execution */}
      <HypothesesCard hypotheses={diagnostic.hypotheses} serviceName={selectedError.serviceName} />

      {/* Container 2.5: Autonomous Parallel Sandbox Subagents (Antigravity Managed Sandbox Pattern) */}
      <ParallelSandboxCard selectedError={selectedError} diagnostic={diagnostic} />

      {/* Container 3: Structured Interactive Remediation Action Roadmap */}
      {diagnostic.hypotheses.length > 0 && (
        <RemediationStepsCard
          recommendationText={diagnostic.hypotheses[0].recommendationText}
        />
      )}

      {/* Container 4: Autonomous ReAct Evidence */}
      <ReActEvidenceCard evidence={diagnostic.evidence} />
    </div>
  );
};
