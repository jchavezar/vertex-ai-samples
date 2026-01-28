import React from 'react';
import { motion } from 'framer-motion';
import { X, Zap, BarChart3, Info } from 'lucide-react';
import { useDashboardStore } from '../../store/dashboardStore';
import { PeerPackGrid } from './PeerPackGrid';
import { clsx } from 'clsx';

export const AnalysisOverlay: React.FC = () => {
  const { activeAnalysisData, setAnalysisData, theme: globalTheme } = useDashboardStore();
  const isDark = globalTheme === 'dark';

  if (!activeAnalysisData) return null;

  const renderContent = () => {
    switch (activeAnalysisData.type) {
      case 'peer_pack':
        return (
          <div className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <BarChart3 className="text-blue-500" size={24} />
              <h2 className={clsx("text-2xl font-black mt-1", isDark ? "text-white" : "text-slate-900")}>
                Peer Pack: {activeAnalysisData.ticker}
              </h2>
            </div>
            <PeerPackGrid peers={activeAnalysisData.peers} theme={globalTheme} />
          </div>
        );
      case 'market_pulse':
        return (
          <div className="p-6">
            <div className="flex items-center gap-2 mb-8">
              <Zap className="text-amber-500" size={24} />
              <h2 className={clsx("text-2xl font-black mt-1", isDark ? "text-white" : "text-slate-900")}>
                Market Pulse: {activeAnalysisData.ticker}
              </h2>
            </div>

            <div className={clsx(
              "rounded-3xl p-8 border mb-6",
              isDark ? "bg-white/5 border-white/10" : "bg-white border-slate-200 shadow-sm"
            )}>
              <div className="flex justify-between items-center mb-10">
                <div>
                  <span className="text-[10px] uppercase tracking-widest font-black opacity-50 block mb-1">Sentiment</span>
                  <span className="text-3xl font-black text-emerald-500">{activeAnalysisData.sentiment}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase tracking-widest font-black opacity-50 block mb-1">Momentum</span>
                  <span className="text-3xl font-black text-blue-500">{activeAnalysisData.momentum}</span>
                </div>
              </div>

              <div className="relative h-2 w-full bg-slate-200 dark:bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '85%' }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.5)]"
                />
              </div>
              <div className="flex justify-between mt-3 text-[10px] font-bold opacity-40 uppercase tracking-tighter">
                <span>Bearish</span>
                <span>Neutral</span>
                <span>Bullish</span>
              </div>
            </div>

            <div className={clsx(
              "rounded-2xl p-4 flex gap-3 items-start",
              isDark ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" : "bg-blue-50/50 text-blue-600 border border-blue-100"
            )}>
              <Info size={18} className="mt-0.5 shrink-0" />
              <p className="text-xs font-semibold leading-relaxed">
                Strategist Note: Accumulation patterns suggest a breakout attempt within the next 48 hours. Volume is 20% above 10-day average.
              </p>
            </div>
          </div>
        );
      default:
        return <div className="p-6 text-center opacity-50">Unknown analysis type</div>;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={clsx(
        "h-full overflow-y-auto border-l scrollbar-hide flex flex-col",
        isDark ? "bg-[#0a0a0a] border-white/10" : "bg-slate-50 border-slate-200"
      )}
    >
      <div className="sticky top-0 z-10 flex justify-end p-4">
        <button
          onClick={() => setAnalysisData(null)}
          className={clsx(
            "p-2 rounded-full transition-colors",
            isDark ? "hover:bg-white/10 text-white/50 hover:text-white" : "hover:bg-slate-200 text-slate-400 hover:text-slate-600"
          )}
        >
          <X size={20} />
        </button>
      </div>
      {renderContent()}
    </motion.div>
  );
};
