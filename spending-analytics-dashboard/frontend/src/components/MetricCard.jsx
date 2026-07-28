import React from 'react';

export default function MetricCard({ title, amount, subtitle, icon: Icon, color = "indigo", trend, trendType = "positive" }) {
  const colorMap = {
    indigo: "from-indigo-600/20 to-violet-600/10 border-indigo-500/30 text-indigo-400",
    emerald: "from-emerald-600/20 to-teal-600/10 border-emerald-500/30 text-emerald-400",
    rose: "from-rose-600/20 to-pink-600/10 border-rose-500/30 text-rose-400",
    amber: "from-amber-600/20 to-orange-600/10 border-amber-500/30 text-amber-400",
    cyan: "from-cyan-600/20 to-blue-600/10 border-cyan-500/30 text-cyan-400"
  };

  const iconBgMap = {
    indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    rose: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
  };

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br ${colorMap[color]} border backdrop-blur-xl transition-all duration-300 hover:scale-[1.02] hover:shadow-xl`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-xl border ${iconBgMap[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between">
        <h3 className="text-2xl font-bold text-white tracking-tight">
          {typeof amount === 'number' ? `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : amount}
        </h3>

        {trend && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
            trendType === 'positive' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
          }`}>
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs text-slate-400 truncate">{subtitle}</p>
      )}
    </div>
  );
}
