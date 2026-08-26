import React from 'react';
import {
  Layers,
  Search,
  Database,
  Code2,
  TrendingUp,
  Bot,
  Zap
} from 'lucide-react';
import type { ToolDefinition } from '../types';

interface SidebarProps {
  tools: ToolDefinition[];
  onSelectPrompt: (prompt: string) => void;
  isOpen: boolean;
}

const PRESET_WORKFLOWS = [
  {
    title: 'Cloud Cost Optimization & ROI',
    icon: TrendingUp,
    category: 'Finance & Infra',
    prompt: 'Query our enterprise database for cloud_spend metrics in engineering, run a 5-year financial projection for a $350k optimization investment saving $1.2M annually, and generate an interactive visualization artifact comparing baseline vs optimized run-rates.',
  },
  {
    title: 'ARR & Net Retention Analysis',
    icon: Database,
    category: 'Revenue Operations',
    prompt: 'Query the enterprise database for Annual Recurring Revenue (ARR) across all quarters, search market benchmarks for enterprise SaaS multiples, and provide an executive summary with a chart artifact.',
  },
  {
    title: 'Python Numerical Monte Carlo',
    icon: Code2,
    category: 'Quantitative Sandbox',
    prompt: 'Execute a Python simulation analyzing customer churn variance over 1,000 runs with a baseline 4.5% churn and ±1.2% volatility. Show statistical mean, standard deviation, and generate an interactive chart artifact.',
  },
  {
    title: 'Market Grounding & Compliance',
    icon: Search,
    category: 'Intelligence',
    prompt: 'Perform enterprise search grounding on 2026 SOC2 and FedRAMP compliance requirements for agentic AI deployments, highlight key risk factors, and produce an executive strategy brief.',
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ tools, onSelectPrompt, isOpen }) => {
  return (
    <aside
      className={`${
        isOpen ? 'w-72' : 'w-0 -ml-72 md:w-64 md:ml-0'
      } transition-all duration-300 border-r border-slate-200 bg-slate-50/70 backdrop-blur-xs flex flex-col h-[calc(100vh-3.5rem)] shrink-0 overflow-hidden select-none`}
    >
      {/* Workspace Context */}
      <div className="p-3 border-b border-slate-200 bg-white/50">
        <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center justify-between">
          <span>Enterprise Environment</span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            Connected
          </span>
        </div>
        <div className="p-2 rounded-md bg-slate-100/80 border border-slate-200 text-xs text-slate-700 space-y-1">
          <div className="flex items-center justify-between font-mono">
            <span className="text-slate-500">Project:</span>
            <span className="font-semibold text-slate-800">vtxdemos</span>
          </div>
          <div className="flex items-center justify-between font-mono">
            <span className="text-slate-500">Region:</span>
            <span className="text-slate-800">us-central1 / global</span>
          </div>
          <div className="flex items-center justify-between font-mono">
            <span className="text-slate-500">Mode:</span>
            <span className="text-cyan-700 font-semibold">Autonomous ADK</span>
          </div>
        </div>
      </div>

      {/* Preset Strategic Workflows */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        <div>
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5 text-amber-500" />
            <span>Strategic Workflows</span>
          </div>
          <div className="space-y-1.5">
            {PRESET_WORKFLOWS.map((wf, idx) => {
              const Icon = wf.icon;
              return (
                <button
                  key={idx}
                  onClick={() => onSelectPrompt(wf.prompt)}
                  className="w-full text-left p-2.5 rounded-lg border border-slate-200 bg-white hover:border-cyan-300 hover:bg-cyan-50/30 transition-all text-xs group cursor-pointer shadow-2xs"
                >
                  <div className="flex items-start space-x-2">
                    <div className="p-1 rounded bg-slate-100 group-hover:bg-cyan-100 text-slate-600 group-hover:text-cyan-700 transition-colors mt-0.5">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-slate-800 group-hover:text-cyan-950 truncate">
                        {wf.title}
                      </div>
                      <div className="text-[10px] text-slate-600 truncate">{wf.category}</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Live Registered Tools Inventory */}
        <div>
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-500" />
            <span>Active ADK Toolset ({tools.length})</span>
          </div>
          <div className="space-y-1.5">
            {tools.length > 0 ? (
              tools.map((tool) => (
                <div
                  key={tool.name}
                  className="p-2 rounded-lg bg-white border border-slate-200 text-xs shadow-2xs hover:border-slate-300 transition-colors flex items-center justify-between gap-1.5 min-w-0"
                >
                  <span className="font-mono text-[11px] font-semibold text-slate-800 truncate flex-1 min-w-0">
                    {tool.name}
                  </span>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 shrink-0 whitespace-nowrap">
                    {tool.badge || tool.category}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-2 text-center text-xs text-slate-500 bg-white rounded border border-slate-200">
                Loading tool definitions...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-200 bg-white/70 text-[11px] text-slate-600 flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <Bot className="w-3.5 h-3.5 text-slate-400" />
          <span>ADK Enterprise Runtime</span>
        </div>
        <span className="font-mono text-slate-500">v2.7.1</span>
      </div>
    </aside>
  );
};
