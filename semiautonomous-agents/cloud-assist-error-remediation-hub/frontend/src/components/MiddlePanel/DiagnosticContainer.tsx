import React, { useState } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';
import { ExecutiveRecapCard } from './ExecutiveRecapCard';
import { HypothesesCard } from './HypothesesCard';
import { RemediationStepsCard } from './RemediationStepsCard';
import { ReActEvidenceCard } from './ReActEvidenceCard';
import { ParallelSandboxCard } from './ParallelSandboxCard';
import { HybridAgentFlowCard } from './HybridAgentFlowCard';
import { CloudRunAppAutoHealCard } from './CloudRunAppAutoHealCard';
import { CollapsibleCard } from './CollapsibleCard';
import { Sparkles, Activity, FileText, Target, Cpu, Wrench, ShieldCheck, Maximize2, Minimize2, Layers } from 'lucide-react';

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
  const [globalCollapseKey, setGlobalCollapseKey] = useState<number>(0);
  const [globalState, setGlobalState] = useState<boolean | null>(null);

  const handleExpandAll = () => {
    setGlobalState(false);
    setGlobalCollapseKey((prev) => prev + 1);
  };

  const handleCollapseAll = () => {
    setGlobalState(true);
    setGlobalCollapseKey((prev) => prev + 1);
  };

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
    <div className="flex-1 overflow-y-auto p-6 space-y-5">
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

      {/* Flexible Section Accordion Controls Toolbar */}
      <div className="flex items-center justify-between bg-slate-950/70 border border-slate-800 px-4 py-2 rounded-xl text-xs">
        <div className="flex items-center space-x-2 text-slate-400">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span className="font-semibold text-slate-200">Diagnostic Pipeline Views</span>
          <span className="text-[11px] text-slate-500">(6 Collapsible Sections)</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleExpandAll}
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition-colors flex items-center gap-1.5 text-[11px] font-bold"
            title="Expand all diagnostic sections"
          >
            <Maximize2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Expand All</span>
          </button>
          <button
            onClick={handleCollapseAll}
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition-colors flex items-center gap-1.5 text-[11px] font-bold"
            title="Collapse all diagnostic sections"
          >
            <Minimize2 className="w-3.5 h-3.5 text-purple-400" />
            <span>Collapse All</span>
          </button>
        </div>
      </div>

      {/* Stage 0: 5-Stage Hybrid Execution Flow & Policy Gate */}
      <CollapsibleCard
        key={`flow-${globalCollapseKey}`}
        title="5-Stage Hybrid Execution Flow & Policy Gate"
        icon={<Activity className="w-4 h-4 text-cyan-400" />}
        badge={<span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active Policy Gate</span>}
        defaultCollapsed={globalState !== null ? globalState : false}
      >
        <HybridAgentFlowCard selectedError={selectedError} diagnostic={diagnostic} />
      </CollapsibleCard>

      {/* Container 1: Executive Recap */}
      <CollapsibleCard
        key={`recap-${globalCollapseKey}`}
        title="Executive Investigation Recap"
        icon={<FileText className="w-4 h-4 text-blue-400" />}
        badge={<span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">Gemini Cloud Assist</span>}
        defaultCollapsed={globalState !== null ? globalState : false}
      >
        <ExecutiveRecapCard recapText={diagnostic.recapText} executionState={diagnostic.executionState} />
      </CollapsibleCard>

      {/* Container 2: Ranked Root-Cause Hypotheses & Clickable Remediation */}
      <CollapsibleCard
        key={`hyp-${globalCollapseKey}`}
        title="Ranked Root-Cause Hypotheses & Interactive Fix Engine"
        icon={<Target className="w-4 h-4 text-purple-400" />}
        badge={
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
            {diagnostic.hypotheses.length} {diagnostic.hypotheses.length === 1 ? 'Hypothesis' : 'Hypotheses'} Ranked
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
      >
        <HypothesesCard hypotheses={diagnostic.hypotheses} serviceName={selectedError.serviceName} />
      </CollapsibleCard>

      {/* Container 2.5: Autonomous Parallel Sandbox Subagents */}
      <CollapsibleCard
        key={`sandbox-${globalCollapseKey}`}
        title="Autonomous Parallel Sandbox Subagents"
        icon={<Cpu className="w-4 h-4 text-emerald-400" />}
        badge={<span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">Antigravity Sandbox Pool</span>}
        defaultCollapsed={globalState !== null ? globalState : false}
      >
        <ParallelSandboxCard selectedError={selectedError} diagnostic={diagnostic} />
      </CollapsibleCard>

      {/* Container 2.8: Cloud Run Application Auto-Healing & Live Visual Preview */}
      <CollapsibleCard
        key={`autoheal-${globalCollapseKey}`}
        title="Cloud Run Application-Level Auto-Healing & Live Visual Preview"
        icon={<Sparkles className="w-4 h-4 text-cyan-400" />}
        badge={<span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">Gemini 3.5 Flash Lite Powered</span>}
        defaultCollapsed={globalState !== null ? globalState : false}
      >
        <CloudRunAppAutoHealCard selectedError={selectedError} />
      </CollapsibleCard>

      {/* Container 3: Structured Interactive Remediation Roadmap */}
      {diagnostic.hypotheses.length > 0 && (
        <CollapsibleCard
          key={`steps-${globalCollapseKey}`}
          title="Proactive Remediation Roadmap"
          icon={<Wrench className="w-4 h-4 text-amber-400" />}
          badge={<span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">Step-by-Step Recovery</span>}
          defaultCollapsed={globalState !== null ? globalState : false}
        >
          <RemediationStepsCard recommendationText={diagnostic.hypotheses[0].recommendationText} />
        </CollapsibleCard>
      )}

      {/* Container 4: Autonomous ReAct Evidence */}
      <CollapsibleCard
        key={`evidence-${globalCollapseKey}`}
        title="Autonomous ReAct Diagnostic Trace"
        icon={<ShieldCheck className="w-4 h-4 text-cyan-400" />}
        badge={
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
            {diagnostic.evidence.length} Observers Verified
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
      >
        <ReActEvidenceCard evidence={diagnostic.evidence} />
      </CollapsibleCard>
    </div>
  );
};
