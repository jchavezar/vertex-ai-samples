import React from 'react';
import { Sparkles, AlertTriangle, TrendingDown, Award, Lightbulb, CheckCircle2, ChevronRight } from 'lucide-react';

export default function AIAuditDrawer({ auditData, isLoading, onRefresh }) {
  if (isLoading) {
    return (
      <div className="p-12 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl flex flex-col items-center justify-center text-center">
        <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 mb-4 animate-bounce">
          <Sparkles className="w-8 h-8 animate-spin" />
        </div>
        <h3 className="text-lg font-bold text-slate-100 mb-1">Gemini 2.5 AI is Analyzing Expenses...</h3>
        <p className="text-xs text-slate-400 max-w-md">Scanning 138 transactions, detecting spending anomalies, categorizing merchant patterns, and building your personalized wealth audit.</p>
      </div>
    );
  }

  if (!auditData) {
    return (
      <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl text-center">
        <p className="text-slate-400 text-sm">No audit data available yet. Click "AI Audit Report" in the navbar to generate.</p>
      </div>
    );
  }

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'high':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">High Spike</span>;
      case 'medium':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">Pattern Note</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Insight</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Persona Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-violet-900/40 via-indigo-900/30 to-slate-900/60 border border-violet-500/30 backdrop-blur-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Award className="w-5 h-5 text-amber-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">AI Household Spending Profile</span>
            </div>
            <h2 className="text-2xl font-black text-white tracking-tight">
              {auditData.spending_persona_title || 'The NYC Gourmet & Fashion Enthusiasts'}
            </h2>
          </div>
          <button
            onClick={onRefresh}
            className="self-start md:self-auto px-4 py-2 text-xs font-semibold rounded-xl bg-violet-600/30 hover:bg-violet-600/50 text-violet-200 border border-violet-500/40 transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" /> Re-Analyze with Gemini
          </button>
        </div>
      </div>

      {/* Executive Narrative */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
        <h3 className="text-base font-bold text-slate-100 mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" /> Executive Financial Narrative
        </h3>
        <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
          {auditData.executive_summary}
        </p>
      </div>

      {/* Grid: Detected Patterns & Anomalies */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Detected Patterns */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-violet-400" /> AI-Detected Spending Patterns
          </h3>
          <div className="space-y-4">
            {auditData.detected_patterns?.map((pattern, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/60 hover:border-violet-500/30 transition-all">
                <div className="flex items-center justify-between mb-1.5">
                  <h4 className="text-xs font-bold text-slate-200">{pattern.title}</h4>
                  {getSeverityBadge(pattern.severity)}
                </div>
                <p className="text-xs text-slate-400 leading-normal">{pattern.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Top Anomalies */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
          <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" /> Top Spending Anomalies & Spikes
          </h3>
          <div className="space-y-4">
            {auditData.top_anomalies?.map((anomaly, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-950/50 border border-amber-500/20 bg-amber-500/5">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-amber-300">{anomaly.merchant_or_category}</span>
                  <span className="text-xs font-mono font-bold text-rose-400">${anomaly.amount}</span>
                </div>
                <p className="text-xs text-slate-300">{anomaly.insight}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

        {/* Actionable Savings Tips */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-950/30 via-slate-900/60 to-slate-900/60 border border-emerald-500/30 backdrop-blur-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-emerald-400" /> AI Wealth Strategy & Savings Plan
            </h3>
            <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              💎 Actionable Monthly Reductions
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {auditData.actionable_savings_tips?.map((tip, i) => {
              const title = typeof tip === 'string' ? tip : tip.title || tip.recommendation;
              const desc = tip.description || '';
              const monthly = tip.monthly_savings || tip.savings || 0;
              const annual = tip.annual_savings || (monthly ? monthly * 12 : 0);

              return (
                <div key={i} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-emerald-500/40 transition-all flex flex-col justify-between space-y-2">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-bold text-slate-100 mb-1">{title}</p>
                      {desc && <p className="text-[11px] text-slate-400 leading-relaxed">{desc}</p>}
                    </div>
                  </div>

                  {(monthly > 0 || annual > 0) && (
                    <div className="flex items-center gap-2 pt-2 border-t border-slate-800/60 pl-8">
                      {monthly > 0 && (
                        <span className="text-[11px] font-bold text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          Save ${monthly}/mo
                        </span>
                      )}
                      {annual > 0 && (
                        <span className="text-[11px] font-medium text-slate-400">
                          (${annual.toLocaleString()}/yr)
                        </span>
                      )}
                      {tip.difficulty && (
                        <span className="text-[10px] text-slate-500 ml-auto uppercase font-bold">
                          {tip.difficulty}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Cost Optimization Roadmap */}
          {auditData.cost_optimization_roadmap && auditData.cost_optimization_roadmap.length > 0 && (
            <div className="pt-4 border-t border-slate-800/80 mt-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-1.5">
                <ChevronRight className="w-4 h-4 text-emerald-400" /> Phased Cost Reduction Roadmap
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {auditData.cost_optimization_roadmap.map((phase, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800 flex items-center justify-between gap-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                        {phase.phase}
                      </span>
                      <p className="text-xs font-semibold text-slate-200 mt-1">{phase.target}</p>
                    </div>
                    <span className="text-xs font-bold font-mono text-emerald-300 whitespace-nowrap">
                      {phase.potential_cut}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
}

