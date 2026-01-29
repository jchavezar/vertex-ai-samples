import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Peer } from './types';

interface DeltaInsightBarProps {
  primaryTicker: string;
  selectedPeer: Peer;
  onDeepDive: () => void;
}

const DeltaInsightBar: React.FC<DeltaInsightBarProps> = ({ primaryTicker, selectedPeer, onDeepDive }) => {
  return (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 50, opacity: 0 }}
      className="fixed bottom-12 left-1/2 -translate-x-1/2 w-full max-w-4xl z-50 px-4"
    >
      <div className="bg-[#1A1D25] rounded-3xl border border-white/10 shadow-[0_30px_60px_rgba(0,0,0,0.8)] p-6 flex items-center justify-between gap-8 backdrop-blur-2xl">
        <div className="flex items-start gap-4 flex-1">
          <div className="mt-1 bg-blue-500/10 p-2 rounded-xl border border-blue-500/20 text-blue-400">
            <Sparkles size={20} />
          </div>
          <div className="flex-1">
            <div className="text-blue-400 font-black text-[10px] uppercase tracking-[0.2em] mb-1">
              Holographic Analysis Engine
            </div>
            <h4 className="text-white font-black text-xl mb-1">
              Delta Insight: {primaryTicker} vs {selectedPeer.ticker}
            </h4>
            <p className="text-white/50 text-[13px] leading-relaxed max-w-xl">
              {selectedPeer.comparison_thesis || `Isolated agent detected a structural alpha gap in **${selectedPeer.ticker}** execution compared to **${primaryTicker}**'s latest cycle.`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-8 pl-8 border-l border-white/5">
          <div className="text-right">
            <div className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-1">Valuation Gap</div>
            <div className="text-2xl font-black text-white whitespace-nowrap">
              {selectedPeer.valuation_gap || '12.4x'} <span className="text-blue-400 text-sm">P/E Premium</span>
            </div>
          </div>
          
          <button
            onClick={onDeepDive}
            className="group flex items-center gap-3 bg-blue-600 hover:bg-blue-500 text-white font-black px-6 py-4 rounded-2xl transition-all shadow-[0_10px_30px_rgba(37,99,235,0.4)] active:scale-95"
          >
            <span>Neural Deep Dive</span>
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default DeltaInsightBar;
