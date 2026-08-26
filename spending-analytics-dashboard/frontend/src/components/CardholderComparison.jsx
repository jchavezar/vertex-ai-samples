import React from 'react';
import { User, DollarSign, ShoppingBag, CreditCard, RefreshCw, Users } from 'lucide-react';
import { getUserConfig, ALL_EXECUTIVE_USERS_LIST } from '../utils/userConfig';

export default function CardholderComparison({ cardholders = {} }) {
  // Normalize cardholders map
  const memberStats = ALL_EXECUTIVE_USERS_LIST.map(user => {
    // Find matching key in cardholders object
    let stat = null;
    for (const [k, v] of Object.entries(cardholders)) {
      if (k.toUpperCase().includes(user.name) || k.toUpperCase().includes(user.short.toUpperCase())) {
        stat = v;
        break;
      }
    }
    return {
      user,
      gross: stat?.total_gross || 0,
      refunds: stat?.total_refunds || 0,
      net: stat?.net_spent || 0,
      count: stat?.transaction_count || 0,
      avg: stat?.avg_transaction || 0,
      topCat: stat?.top_category || 'Shopping',
      topMerchant: stat?.top_merchant || 'Bergdorf Goodman'
    };
  });

  const totalSpent = memberStats.reduce((sum, m) => sum + m.net, 0);

  return (
    <div className="space-y-6">
      {/* Overview Share Progress Bar */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Users className="w-4 h-4 text-indigo-400" />
            Executive Net Spend Share (5 Corporate Cardholders)
          </span>
          <span className="text-xs font-semibold text-slate-300 font-mono">
            ${totalSpent.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Total Net
          </span>
        </div>

        {/* 5-Color Progress Bar */}
        <div className="h-4 w-full bg-slate-950 rounded-full overflow-hidden flex p-0.5 border border-slate-800">
          {memberStats.map(m => {
            const pct = totalSpent > 0 ? (m.net / totalSpent) * 100 : 20;
            return (
              <div
                key={m.user.name}
                style={{ width: `${pct}%`, backgroundColor: m.user.color }}
                className="h-full first:rounded-l-full last:rounded-r-full transition-all duration-500"
                title={`${m.user.short}: ${pct.toFixed(1)}% ($${m.net.toLocaleString()})`}
              />
            );
          })}
        </div>

        {/* 5 User Legend */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-4 text-xs font-medium">
          {memberStats.map(m => {
            const pct = totalSpent > 0 ? ((m.net / totalSpent) * 100).toFixed(1) : '0.0';
            return (
              <div key={m.user.name} className="flex items-center gap-2 p-2 rounded-xl bg-slate-950/50 border border-slate-800/60">
                <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: m.user.color }} />
                <div className="min-w-0">
                  <div className="font-bold text-slate-200 truncate">{m.user.short}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{pct}% (${m.net.toLocaleString()})</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Grid of 5 Executive Member Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {memberStats.map(m => {
          const pct = totalSpent > 0 ? ((m.net / totalSpent) * 100).toFixed(1) : '0.0';
          return (
            <div 
              key={m.user.name}
              className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-800/80">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg border ${m.user.avatarBg}`}>
                      {m.user.tag}
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">{m.user.name}</h3>
                      <p className="text-xs text-slate-400">{m.user.role} • Card {m.user.card}</p>
                    </div>
                  </div>
                  <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${m.user.badgeClass}`}>
                    {pct}%
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-5">
                  <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Gross Spent</span>
                    <p className="text-base font-bold text-slate-100 font-mono">${m.gross?.toLocaleString()}</p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Refunds</span>
                    <p className="text-base font-bold text-emerald-400 font-mono">${m.refunds?.toLocaleString()}</p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Net Spent</span>
                    <p className="text-base font-bold text-indigo-300 font-mono">${m.net?.toLocaleString()}</p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Tx Count</span>
                    <p className="text-base font-bold text-slate-200 font-mono">{m.count} txs</p>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/60 space-y-1.5 text-xs">
                <div className="flex justify-between items-center text-slate-400">
                  <span>Top Category:</span>
                  <span className="font-semibold text-slate-200">{m.topCat}</span>
                </div>
                <div className="flex justify-between items-center text-slate-400">
                  <span>Top Merchant:</span>
                  <span className="font-semibold text-indigo-300">{m.topMerchant}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
