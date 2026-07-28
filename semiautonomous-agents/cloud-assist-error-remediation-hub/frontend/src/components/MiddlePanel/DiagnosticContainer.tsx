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
  isLightMode?: boolean;
}

export const DiagnosticContainer: React.FC<DiagnosticContainerProps> = ({
  selectedError,
  diagnostic,
  isLoading,
  isLightMode = false
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
      <div className={`flex-1 flex flex-col items-center justify-center p-12 text-center ${isLightMode ? 'bg-[#fafafa] text-slate-800' : ''}`}>
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-xl border ${
          isLightMode
            ? 'bg-white border-slate-300 text-slate-900'
            : 'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border-slate-700/80 text-cyan-400'
        }`}>
          <Sparkles className="w-7 h-7" />
        </div>
        <h3 className={`text-sm font-bold tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>No Issue Selected</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1.5 leading-relaxed font-mono">
          Select an error from the left Cloud Logging panel to trigger autonomous Gemini Cloud Assist diagnosis and proactive remediation.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className={`flex-1 flex flex-col items-center justify-center p-12 text-center space-y-6 ${isLightMode ? 'bg-[#fafafa]' : ''}`}>
        <div className="relative">
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center border animate-pulse ${
            isLightMode
              ? 'bg-white border-slate-300 text-slate-900'
              : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
          }`}>
            <Sparkles className="w-7 h-7" />
          </div>
        </div>

        <div className="space-y-2">
          <h3 className={`text-sm font-bold tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>
            Gemini Cloud Assist Diagnostic Pipeline Active
          </h3>
          <p className={`text-xs ${isLightMode ? 'text-slate-600 font-mono' : 'text-slate-400'}`}>
            Running autonomous 4-Step lifecycle on <code className={isLightMode ? 'text-slate-950 font-bold' : 'text-cyan-400'}>{selectedError.serviceName}</code>...
          </p>
        </div>

        {/* Live Step Tracker */}
        <div className={`w-full max-w-md rounded-2xl p-4 text-left space-y-3 shadow-sm border ${
          isLightMode
            ? 'bg-white border-slate-300 text-slate-900 font-mono'
            : 'bg-slate-950/80 border-slate-800 text-slate-300'
        }`}>
          <div className={`flex items-center space-x-3 text-xs ${isLightMode ? 'text-emerald-700 font-bold' : 'text-emerald-400'}`}>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span>1. Seeding symptom observation into Investigation...</span>
          </div>
          <div className={`flex items-center space-x-3 text-xs ${isLightMode ? 'text-sky-700 font-bold' : 'text-cyan-300'}`}>
            <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse"></span>
            <span>2. Creating immutable state snapshot revision...</span>
          </div>
          <div className={`flex items-center space-x-3 text-xs ${isLightMode ? 'text-slate-700 font-bold' : 'text-slate-300'}`}>
            <span className="w-2 h-2 rounded-full bg-slate-500"></span>
            <span>3. Executing autonomous ReAct diagnostic observers...</span>
          </div>
          <div className={`flex items-center space-x-3 text-xs ${isLightMode ? 'text-slate-600' : 'text-slate-400'}`}>
            <span className="w-2 h-2 rounded-full bg-slate-400"></span>
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
      <div className={`p-5 rounded-2xl border shadow-md transition-colors duration-300 ${
        isLightMode
          ? 'bg-white border-slate-300 text-slate-950 shadow-slate-200/50'
          : 'bg-gradient-to-r from-slate-900/90 via-[#131a29]/90 to-slate-900/90 border-slate-800/90 text-white'
      }`}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-1.5">
              <span
                className={`text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full uppercase ${
                  selectedError.severity === 'CRITICAL'
                    ? isLightMode
                      ? 'bg-rose-100 text-rose-800 border border-rose-300 font-mono'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : isLightMode
                      ? 'bg-amber-100 text-amber-800 border border-amber-300 font-mono'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {selectedError.severity}
              </span>
              <span className="text-xs opacity-50">&bull;</span>
              <span className={`text-xs font-bold font-mono ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`}>
                {selectedError.serviceName}
              </span>
              <span className="text-xs opacity-50">&bull;</span>
              <span className={`text-xs font-mono ${isLightMode ? 'text-slate-600' : 'text-slate-400'}`}>
                {selectedError.resourceType}
              </span>
            </div>
            <h1 className={`text-base font-extrabold tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>
              {selectedError.summary}
            </h1>
          </div>

          <div className="text-right flex-shrink-0">
            <span className={`text-[10px] font-mono ${isLightMode ? 'text-slate-600 font-bold' : 'text-slate-400'}`}>
              Investigation: {diagnostic.investigationName.split('/').pop()}
            </span>
          </div>
        </div>

        <div className={`mt-3.5 pt-3 border-t font-mono text-xs p-3 rounded-xl overflow-x-auto ${
          isLightMode
            ? 'bg-slate-50 border-slate-200 text-slate-900 font-medium'
            : 'bg-black/50 border-slate-800/60 text-slate-300'
        }`}>
          {selectedError.fullText}
        </div>
      </div>

      {/* Flexible Section Accordion Controls Toolbar */}
      <div className={`flex items-center justify-between border px-4 py-2.5 rounded-2xl text-xs ${
        isLightMode
          ? 'bg-white border-slate-300 text-slate-900 shadow-sm'
          : 'bg-slate-950/70 border-slate-800 text-slate-200'
      }`}>
        <div className="flex items-center space-x-2">
          <Layers className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
          <span className={`font-bold ${isLightMode ? 'text-slate-950 font-mono' : 'text-slate-200'}`}>Diagnostic Pipeline Views</span>
          <span className={`text-[11px] ${isLightMode ? 'text-slate-500 font-mono' : 'text-slate-500'}`}>(6 Collapsible Sections)</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleExpandAll}
            className={`px-3 py-1 rounded-lg border text-[11px] font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
              isLightMode
                ? 'bg-slate-100 hover:bg-slate-200 border-slate-300 text-slate-900 font-mono'
                : 'bg-slate-800 hover:bg-slate-700 border-transparent text-slate-200'
            }`}
            title="Expand all diagnostic sections"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            <span>Expand All</span>
          </button>
          <button
            onClick={handleCollapseAll}
            className={`px-3 py-1 rounded-lg border text-[11px] font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
              isLightMode
                ? 'bg-slate-100 hover:bg-slate-200 border-slate-300 text-slate-900 font-mono'
                : 'bg-slate-800 hover:bg-slate-700 border-transparent text-slate-200'
            }`}
            title="Collapse all diagnostic sections"
          >
            <Minimize2 className="w-3.5 h-3.5" />
            <span>Collapse All</span>
          </button>
        </div>
      </div>

      {/* Stage 0: 5-Stage Hybrid Execution Flow & Policy Gate */}
      <CollapsibleCard
        key={`flow-${globalCollapseKey}`}
        title="5-Stage Hybrid Execution Flow & Policy Gate"
        icon={<Activity className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />}
        badge={
          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
            isLightMode
              ? 'bg-emerald-100 text-emerald-800 border-emerald-300 font-mono'
              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
          }`}>
            Active Policy Gate
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
        isLightMode={isLightMode}
      >
        <HybridAgentFlowCard selectedError={selectedError} diagnostic={diagnostic} />
      </CollapsibleCard>

      {/* Container 1: Executive Recap */}
      <CollapsibleCard
        key={`recap-${globalCollapseKey}`}
        title="Executive Investigation Recap"
        icon={<FileText className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-blue-400'}`} />}
        badge={
          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
            isLightMode
              ? 'bg-sky-100 text-sky-800 border-sky-300 font-mono'
              : 'bg-blue-500/10 text-blue-300 border-blue-500/20'
          }`}>
            Gemini Cloud Assist
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
        isLightMode={isLightMode}
      >
        <ExecutiveRecapCard recapText={diagnostic.recapText} executionState={diagnostic.executionState} />
      </CollapsibleCard>

      {/* Container 2: Ranked Root-Cause Hypotheses & Clickable Remediation */}
      <CollapsibleCard
        key={`hyp-${globalCollapseKey}`}
        title="Ranked Root-Cause Hypotheses & Interactive Fix Engine"
        icon={<Target className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-purple-400'}`} />}
        badge={
          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
            isLightMode
              ? 'bg-purple-100 text-purple-800 border-purple-300 font-mono'
              : 'bg-purple-500/10 text-purple-300 border-purple-500/20'
          }`}>
            {diagnostic.hypotheses.length} {diagnostic.hypotheses.length === 1 ? 'Hypothesis' : 'Hypotheses'} Ranked
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
        isLightMode={isLightMode}
      >
        <HypothesesCard hypotheses={diagnostic.hypotheses} serviceName={selectedError.serviceName} />
      </CollapsibleCard>

      {/* Container 2.5: Autonomous Parallel Sandbox Subagents */}
      <CollapsibleCard
        key={`sandbox-${globalCollapseKey}`}
        title="Autonomous Parallel Sandbox Subagents"
        icon={<Cpu className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-emerald-400'}`} />}
        badge={
          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
            isLightMode
              ? 'bg-emerald-100 text-emerald-800 border-emerald-300 font-mono'
              : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
          }`}>
            Antigravity Sandbox Pool
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
        isLightMode={isLightMode}
      >
        <ParallelSandboxCard selectedError={selectedError} diagnostic={diagnostic} />
      </CollapsibleCard>

      {/* Container 2.8: Cloud Run Application Auto-Healing & Live Visual Preview */}
      <CollapsibleCard
        key={`autoheal-${globalCollapseKey}`}
        title="Cloud Run Application-Level Auto-Healing & Live Visual Preview"
        icon={<Sparkles className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />}
        badge={
          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
            isLightMode
              ? 'bg-purple-100 text-purple-800 border-purple-300 font-mono'
              : 'bg-purple-500/20 text-purple-300 border-purple-500/30'
          }`}>
            Gemini 3.5 Flash Lite Powered
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
        isLightMode={isLightMode}
      >
        <CloudRunAppAutoHealCard selectedError={selectedError} isLightMode={isLightMode} />
      </CollapsibleCard>

      {/* Container 3: Structured Interactive Remediation Roadmap */}
      {diagnostic.hypotheses.length > 0 && (
        <CollapsibleCard
          key={`steps-${globalCollapseKey}`}
          title="Proactive Remediation Roadmap"
          icon={<Wrench className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-amber-400'}`} />}
          badge={
            <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
              isLightMode
                ? 'bg-amber-100 text-amber-800 border-amber-300 font-mono'
                : 'bg-amber-500/10 text-amber-300 border-amber-500/20'
            }`}>
              Step-by-Step Recovery
            </span>
          }
          defaultCollapsed={globalState !== null ? globalState : false}
          isLightMode={isLightMode}
        >
          <RemediationStepsCard recommendationText={diagnostic.hypotheses[0].recommendationText} />
        </CollapsibleCard>
      )}

      {/* Container 4: Autonomous ReAct Evidence */}
      <CollapsibleCard
        key={`evidence-${globalCollapseKey}`}
        title="Autonomous ReAct Diagnostic Trace"
        icon={<ShieldCheck className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />}
        badge={
          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
            isLightMode
              ? 'bg-cyan-100 text-cyan-800 border-cyan-300 font-mono'
              : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20'
          }`}>
            {diagnostic.evidence.length} Observers Verified
          </span>
        }
        defaultCollapsed={globalState !== null ? globalState : false}
        isLightMode={isLightMode}
      >
        <ReActEvidenceCard evidence={diagnostic.evidence} />
      </CollapsibleCard>
    </div>
  );
};
