import React from 'react';
import { TrendingUp, Database, Code2, Search, ArrowRight } from 'lucide-react';

interface PresetPromptsProps {
  onSelect: (prompt: string) => void;
}

export const PresetPrompts: React.FC<PresetPromptsProps> = ({ onSelect }) => {
  const cards = [
    {
      title: 'Cloud Cost Optimization & ROI',
      desc: 'Query engineering cloud spend, compute 5-year NPV for rightsizing, and render interactive chart.',
      icon: TrendingUp,
      prompt: 'Query our enterprise database for cloud_spend metrics in engineering, run a 5-year financial projection for a $350k optimization investment saving $1.2M annually, and generate an interactive visualization artifact comparing baseline vs optimized run-rates.',
      badge: 'Database + Finance Tools',
      color: 'border-cyan-200 hover:border-cyan-400 bg-cyan-50/30'
    },
    {
      title: 'ARR Growth & SaaS Multiples',
      desc: 'Retrieve quarterly revenue run-rates and ground against enterprise valuation benchmarks.',
      icon: Database,
      prompt: 'Query the enterprise database for Annual Recurring Revenue (ARR) across all quarters, search market benchmarks for enterprise SaaS multiples, and provide an executive summary with a chart artifact.',
      badge: 'Search + Data Warehouse',
      color: 'border-indigo-200 hover:border-indigo-400 bg-indigo-50/30'
    },
    {
      title: 'Python Numerical Monte Carlo',
      desc: 'Execute isolated Python simulation for volatility modeling and standard deviation distribution.',
      icon: Code2,
      prompt: 'Execute a Python simulation analyzing customer churn variance over 1,000 runs with a baseline 4.5% churn and ±1.2% volatility. Show statistical mean, standard deviation, and generate an interactive chart artifact.',
      badge: 'Python Sandbox',
      color: 'border-emerald-200 hover:border-emerald-400 bg-emerald-50/30'
    },
    {
      title: 'Compliance & Threat Intelligence',
      desc: 'Ground real-time regulatory compliance standards for autonomous multi-agent workloads.',
      icon: Search,
      prompt: 'Perform enterprise search grounding on 2026 SOC2 and FedRAMP compliance requirements for agentic AI deployments, highlight key risk factors, and produce an executive strategy brief.',
      badge: 'Grounding + Brief',
      color: 'border-amber-200 hover:border-amber-400 bg-amber-50/30'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 select-none">
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-50 border border-cyan-200 text-cyan-800 text-xs font-semibold uppercase tracking-wider mb-3">
          <span>Enterprise Multi-Tool Reasoning Engine</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
          How can ADK assist your strategic operations today?
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-lg mx-auto">
          Autonomous multi-agent orchestration with Gemini 3.7 reasoning tokens, live tool telemetry, and instant interactive artifacts.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelect(card.prompt)}
              className={`p-4 rounded-xl border ${card.color} text-left transition-all hover:shadow-xs group cursor-pointer flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="p-2 rounded-lg bg-white border border-slate-200 shadow-2xs group-hover:scale-105 transition-transform">
                    <Icon className="w-4 h-4 text-slate-800" />
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 px-2 py-0.5 rounded bg-white/80 border border-slate-200">
                    {card.badge}
                  </span>
                </div>
                <h3 className="text-xs sm:text-sm font-semibold text-slate-900 group-hover:text-cyan-900">
                  {card.title}
                </h3>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                  {card.desc}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-medium text-cyan-700 group-hover:text-cyan-800">
                <span>Deploy Workflow</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
