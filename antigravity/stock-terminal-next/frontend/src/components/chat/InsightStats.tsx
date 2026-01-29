import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { clsx } from 'clsx';

export interface InsightStat {
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'neutral';
}

interface InsightStatsProps {
  stats: InsightStat[];
  theme?: 'light' | 'dark';
}

export const InsightStats: React.FC<InsightStatsProps> = ({ stats, theme = 'dark' }) => {
  const isDark = theme === 'dark';

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
      {stats.map((stat, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          className={clsx(
            "p-3 rounded-xl border transition-all duration-300 group",
            isDark 
              ? "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20" 
              : "bg-white border-slate-200 hover:border-blue-200 shadow-sm"
          )}
        >
          <div className="flex justify-between items-start mb-1">
            <span className={clsx(
              "text-[10px] font-black uppercase tracking-wider opacity-60",
              isDark ? "text-blue-400" : "text-blue-600"
            )}>
              {stat.label}
            </span>
            {stat.trend === 'up' && <ArrowUpRight size={12} className="text-emerald-500" />}
            {stat.trend === 'down' && <ArrowDownRight size={12} className="text-rose-500" />}
            {stat.trend === 'neutral' && <Minus size={12} className="text-slate-400" />}
          </div>
          <div className={clsx(
            "text-lg font-black tracking-tight",
            isDark ? "text-white" : "text-slate-900"
          )}>
            {stat.value}
          </div>
        </motion.div>
      ))}
    </div>
  );
};
