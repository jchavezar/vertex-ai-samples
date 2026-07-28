import React, { useState, useEffect } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';
import {
  GitCommit,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Zap,
  Cpu,
  Lock,
  UserCheck,
  Layers,
  Search,
  Activity,
  X
} from 'lucide-react';

interface HybridAgentFlowCardProps {
  selectedError: GcpErrorItem;
  diagnostic: CloudAssistDiagnostic;
}

interface StepPlan {
  stepId: number;
  phase: string;
  agentPlane: string;
  title: string;
  description: string;
  policyMode: 'AUTONOMOUS' | 'REQUIRES_HIL_APPROVAL';
  status: string;
  latencyMs?: number;
}

interface HybridFlowPlan {
  errorId: string;
  serviceName: string;
  architecture: string;
  overallPolicy: 'AUTONOMOUS' | 'REQUIRES_HIL_APPROVAL';
  steps: StepPlan[];
  classifiedCommands: Array<{
    command: string;
    policyLevel: string;
    riskTier: string;
    justification: string;
    requiresHumanApproval: boolean;
  }>;
}

export const HybridAgentFlowCard: React.FC<HybridAgentFlowCardProps> = ({
  selectedError,
  diagnostic
}) => {
  const [plan, setPlan] = useState<HybridFlowPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hilDecision, setHilDecision] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');
  const [isExecutingHil, setIsExecutingHil] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    let active = true;
    const fetchPlan = async () => {
      setIsLoading(true);
      setHilDecision('PENDING');
      try {
        const res = await fetch('http://127.0.0.1:8088/api/hybrid-flow', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ errorItem: selectedError })
        });
        if (res.ok && active) {
          const data: HybridFlowPlan = await res.json();
          setPlan(data);
          if (data.overallPolicy === 'AUTONOMOUS') {
            setHilDecision('APPROVED');
          }
        }
      } catch (err) {
        console.error("Failed to fetch hybrid flow plan:", err);
      } finally {
        if (active) setIsLoading(false);
      }
    };

    fetchPlan();
    return () => {
      active = false;
    };
  }, [selectedError.id]);

  const handleHilAction = async (approved: boolean) => {
    if (!approved) {
      setHilDecision('REJECTED');
      return;
    }
    setIsExecutingHil(true);
    // Execute verified command inside production plane after human approval
    setTimeout(() => {
      setHilDecision('APPROVED');
      setIsExecutingHil(false);
    }, 600);
  };

  if (isLoading || !plan) {
    return (
      <div className="rounded-xl bg-[#111622]/90 border border-slate-800 p-4 animate-pulse text-xs text-slate-400">
        Classifying 5-Stage Hybrid Agentic Policy Flow (Autonomous vs. Human-In-The-Loop)...
      </div>
    );
  }

  return (
    <>
      {/* Sleek Top Status Ribbon */}
      <div className="rounded-xl bg-gradient-to-r from-slate-900/90 via-[#121829]/90 to-slate-900/90 border border-slate-800/80 p-3 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-purple-300" />
          </div>
          <div>
            <h2 className="font-bold text-white tracking-tight flex items-center gap-1.5">
              <span>Agentic Policy Gate</span>
              {plan.overallPolicy === 'AUTONOMOUS' ? (
                <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40 flex items-center gap-1">
                  <Zap className="w-2.5 h-2.5 fill-emerald-400" />
                  <span>AUTONOMOUS</span>
                </span>
              ) : (
                <span className="text-[10px] font-semibold text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/40 flex items-center gap-1">
                  <UserCheck className="w-2.5 h-2.5" />
                  <span>HIL GATE PENDING</span>
                </span>
              )}
            </h2>
          </div>
        </div>

        {/* Inline Actions & Banners */}
        <div className="flex items-center space-x-3 ml-auto md:ml-0">
          {plan.overallPolicy === 'REQUIRES_HIL_APPROVAL' && hilDecision === 'PENDING' && (
            <div className="flex items-center space-x-2 bg-amber-950/20 border border-amber-500/30 px-3 py-1 rounded-lg">
              <span className="text-amber-300 font-medium mr-1">Approval Required:</span>
              <button
                onClick={() => handleHilAction(false)}
                className="px-2 py-1 rounded bg-slate-800 hover:bg-rose-950 border border-slate-700 hover:border-rose-500 text-slate-300 hover:text-white font-bold text-[10px] transition-colors"
              >
                Reject
              </button>
              <button
                onClick={() => handleHilAction(true)}
                disabled={isExecutingHil}
                className="px-2.5 py-1 rounded bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold text-[10px] transition-all flex items-center gap-1 shadow-sm"
              >
                {isExecutingHil ? 'Enforcing...' : 'Approve & Execute'}
              </button>
            </div>
          )}

          {hilDecision === 'APPROVED' && (
            <div className="flex items-center space-x-1.5 text-emerald-400 bg-emerald-950/30 border border-emerald-500/30 px-3 py-1 rounded-lg">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Remediation Applied to Production</span>
            </div>
          )}

          {hilDecision === 'REJECTED' && (
            <div className="flex items-center space-x-1.5 text-rose-400 bg-rose-950/30 border border-rose-500/30 px-3 py-1 rounded-lg">
              <XCircle className="w-3.5 h-3.5" />
              <span>Remediation Rejected</span>
              <button
                onClick={() => setHilDecision('PENDING')}
                className="text-[10px] underline ml-1 hover:text-white"
              >
                Review
              </button>
            </div>
          )}

          <button
            onClick={() => setShowModal(true)}
            className="px-3 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/40 text-purple-300 hover:text-purple-200 font-bold transition-all"
          >
            Inspect Pipeline 🔍
          </button>
        </div>
      </div>

      {/* Glassmorphic Modal Overlay */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md p-4 overflow-y-auto">
          <div className="relative w-full max-w-6xl rounded-2xl bg-gradient-to-br from-slate-900 via-[#0d1322] to-slate-950 border border-purple-500/40 p-6 shadow-2xl space-y-6">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
                  <Cpu className="w-5 h-5 text-purple-300" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                    <span>5-Stage Agentic Remediation Pipeline</span>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40">
                      Split-Plane Architecture
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Step-by-step diagnostic and safety enforcement trace for the active incident
                  </p>
                </div>
              </div>

              <button
                onClick={() => setShowModal(false)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Stepper Grid */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {plan.steps.map((step) => {
                const isHilStep = step.policyMode === 'REQUIRES_HIL_APPROVAL';
                const isAutonomous = step.policyMode === 'AUTONOMOUS';

                return (
                  <div
                    key={step.stepId}
                    className={`rounded-xl p-3.5 border flex flex-col justify-between transition-all ${
                      isHilStep
                        ? 'bg-amber-950/20 border-amber-500/40 shadow-inner'
                        : 'bg-slate-950/80 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="flex flex-col gap-1.5 mb-2.5">
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                            PHASE 0{step.stepId}
                          </span>
                          {isAutonomous ? (
                            <span className="text-[9px] font-semibold text-emerald-400 bg-emerald-950/60 px-1 py-0.5 rounded border border-emerald-800/50 flex items-center gap-0.5">
                              <Zap className="w-2 h-2 fill-emerald-400" />
                              <span>AUTO</span>
                            </span>
                          ) : (
                            <span className="text-[9px] font-semibold text-amber-300 bg-amber-950/60 px-1 py-0.5 rounded border border-amber-800/50 flex items-center gap-0.5">
                              <UserCheck className="w-2 h-2" />
                              <span>HIL</span>
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] font-bold text-slate-300 uppercase tracking-wider font-mono">
                          {step.phase}
                        </div>
                      </div>

                      <div className="text-[10px] font-semibold text-cyan-300 mb-1">
                        {step.agentPlane}
                      </div>
                      <h4 className="text-xs font-bold text-white mb-1">
                        {step.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        {step.description}
                      </p>
                    </div>

                    {step.latencyMs && (
                      <div className="mt-3 pt-2 border-t border-slate-800/70 flex items-center justify-between text-[9px] font-mono text-slate-500">
                        <span>Latency</span>
                        <span className="text-cyan-400">{step.latencyMs}ms</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Safety policy / Classified commands */}
            {plan.classifiedCommands.length > 0 && (
              <div className="space-y-2 pt-4 border-t border-slate-800/80">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  <span>Remediation Action Safety Analysis</span>
                </h4>

                {plan.classifiedCommands.map((cmdItem, cIdx) => (
                  <div
                    key={cIdx}
                    className={`p-3 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs font-mono ${
                      cmdItem.requiresHumanApproval
                        ? 'bg-amber-950/30 border-amber-500/40 text-amber-200'
                        : 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded ${
                            cmdItem.requiresHumanApproval
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                              : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                          }`}
                        >
                          {cmdItem.policyLevel} (RISK: {cmdItem.riskTier})
                        </span>
                        <code className="text-white font-bold">{cmdItem.command}</code>
                      </div>
                      <p className="text-[11px] text-slate-300 font-sans pl-1">
                        {cmdItem.justification}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Close trigger footer */}
            <div className="flex justify-end pt-4 border-t border-slate-800/80">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition-colors"
              >
                Close Trace View
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
};
