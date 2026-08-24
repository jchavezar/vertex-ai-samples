import React from 'react';
import { Cpu } from 'lucide-react';

export const AgentSwarmStatus: React.FC = () => {
  const sentinels = [
    {
      name: 'Liquidity Rebalancer Agent',
      role: 'Autonomous Treasury Optimization',
      status: 'ACTIVE_POLLING',
      interval: '50ms',
      color: 'cyan',
    },
    {
      name: 'Supply Chain Sentinel',
      role: 'Maritime & Supplier Fragility Radar',
      status: 'MONITORING',
      interval: '120ms',
      color: 'rose',
    },
    {
      name: 'Basel III Governance Guardrail',
      role: 'Regulatory Capital Tier Enforcement',
      status: 'VERIFIED_100%',
      interval: 'Instant',
      color: 'emerald',
    },
  ];

  return (
    <div className="cyber-glass rounded-2xl p-4 border border-cyan-500/20">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-cyan-400" />
          <span className="text-xs font-bold text-slate-200 tracking-wider uppercase font-mono">
            Autonomous A2A Sentinel Mesh
          </span>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
          3 / 3 SENTINELS ONLINE
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {sentinels.map((s) => (
          <div
            key={s.name}
            className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80 flex items-center justify-between"
          >
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-200">{s.name}</span>
              </div>
              <span className="text-[10px] text-slate-400 block">{s.role}</span>
            </div>
            <div className="text-right font-mono">
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                  s.color === 'cyan'
                    ? 'bg-cyan-950 text-cyan-400 border border-cyan-800'
                    : s.color === 'rose'
                    ? 'bg-rose-950 text-rose-400 border border-rose-800'
                    : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                }`}
              >
                {s.status}
              </span>
              <span className="text-[9px] text-slate-500 block mt-0.5">
                {s.interval}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
