import React from 'react';
import { User, DollarSign, ShoppingBag, CreditCard, RefreshCw } from 'lucide-react';

export default function CardholderComparison({ cardholders = {} }) {
  const dinorah = cardholders['DINORAH GUERRA'] || {};
  const jesus = cardholders['JESUS CHAVEZ'] || {};

  const totalSpent = (dinorah.net_spent || 0) + (jesus.net_spent || 0);
  const dinorahPct = totalSpent > 0 ? ((dinorah.net_spent / totalSpent) * 100).toFixed(1) : 0;
  const jesusPct = totalSpent > 0 ? ((jesus.net_spent / totalSpent) * 100).toFixed(1) : 0;

  return (
    <div className="space-y-6">
      {/* Overview Share Progress Bar */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Net Household Spend Share</span>
          <span className="text-xs font-semibold text-slate-300">${totalSpent.toLocaleString(undefined, { minimumFractionDigits: 2 })} Total Net</span>
        </div>

        {/* Progress Bar */}
        <div className="h-4 w-full bg-slate-950 rounded-full overflow-hidden flex p-0.5 border border-slate-800">
          <div
            style={{ width: `${dinorahPct}%` }}
            className="h-full bg-gradient-to-r from-violet-600 to-indigo-500 rounded-l-full transition-all duration-500"
          />
          <div
            style={{ width: `${jesusPct}%` }}
            className="h-full bg-gradient-to-r from-cyan-500 to-teal-400 rounded-r-full transition-all duration-500"
          />
        </div>

        <div className="flex justify-between mt-3 text-xs font-medium">
          <div className="flex items-center gap-2 text-violet-300">
            <div className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
            <span>Dinorah Guerra: {dinorahPct}% (${dinorah.net_spent?.toLocaleString()})</span>
          </div>
          <div className="flex items-center gap-2 text-cyan-300">
            <div className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
            <span>Jesus Chavez: {jesusPct}% (${jesus.net_spent?.toLocaleString()})</span>
          </div>
        </div>
      </div>

      {/* Side by Side Member Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Dinorah Guerra */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-violet-950/20 via-slate-900/60 to-slate-900/60 border border-violet-500/30 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-violet-300 font-bold text-lg">
                DG
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Dinorah Guerra</h3>
                <p className="text-xs text-slate-400">Card ending in -84002 ({dinorah.transaction_count} txs)</p>
              </div>
            </div>
            <span className="px-3 py-1 text-xs font-bold rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20">
              {dinorahPct}% of total
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Gross Spent</span>
              <p className="text-lg font-bold text-slate-100">${dinorah.total_gross?.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Refunds</span>
              <p className="text-lg font-bold text-emerald-400">${dinorah.total_refunds?.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Net Spent</span>
              <p className="text-lg font-bold text-violet-300">${dinorah.net_spent?.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Avg Transaction</span>
              <p className="text-lg font-bold text-slate-100">${dinorah.avg_transaction}</p>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">Top Category & Merchant</h4>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs">
              <span className="text-slate-400">Top Category:</span>
              <span className="font-semibold text-violet-300">{dinorah.top_category}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs mt-2">
              <span className="text-slate-400">Top Merchant:</span>
              <span className="font-semibold text-indigo-300">{dinorah.top_merchant}</span>
            </div>
          </div>
        </div>

        {/* Jesus Chavez */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-cyan-950/20 via-slate-900/60 to-slate-900/60 border border-cyan-500/30 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-300 font-bold text-lg">
                JC
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Jesus Chavez</h3>
                <p className="text-xs text-slate-400">Card ending in -84002 ({jesus.transaction_count} txs)</p>
              </div>
            </div>
            <span className="px-3 py-1 text-xs font-bold rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
              {jesusPct}% of total
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Gross Spent</span>
              <p className="text-lg font-bold text-slate-100">${jesus.total_gross?.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Refunds</span>
              <p className="text-lg font-bold text-emerald-400">${jesus.total_refunds?.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Net Spent</span>
              <p className="text-lg font-bold text-cyan-300">${jesus.net_spent?.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">Avg Transaction</span>
              <p className="text-lg font-bold text-slate-100">${jesus.avg_transaction}</p>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">Top Category & Merchant</h4>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs">
              <span className="text-slate-400">Top Category:</span>
              <span className="font-semibold text-cyan-300">{jesus.top_category}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs mt-2">
              <span className="text-slate-400">Top Merchant:</span>
              <span className="font-semibold text-teal-300">{jesus.top_merchant}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
