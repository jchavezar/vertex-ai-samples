import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';
import LogoWithFallback from './LogoWithFallback';
import { Peer } from './types';

interface PeerCardProps {
  peer: Peer;
  isSelected: boolean;
  onClick: () => void;
}

const PeerCard: React.FC<PeerCardProps> = ({ peer, isSelected, onClick }) => {
  return (
    <motion.div
      layout
      whileHover={{ y: -5 }}
      whileTap={{ scale: 0.98 }}
      className={`relative cursor-pointer group rounded-xl overflow-hidden border transition-all duration-300 ${isSelected
        ? 'border-blue-500 shadow-[0_0_30px_rgba(59,130,246,0.3)] bg-blue-500/10'
        : 'border-white/10 bg-[#0A0C10] hover:border-white/20'
        }`}
      onClick={onClick}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none" />

      <div className="relative p-5 h-full flex flex-col min-h-[180px]">
        <div className="flex justify-between items-start mb-4">
          <div className="w-12 h-12 rounded-xl bg-white/5 p-2 border border-white/10 flex items-center justify-center group-hover:bg-white/10 transition-colors">
            <LogoWithFallback ticker={peer.ticker} className="w-full h-full object-contain" />
          </div>
          <div className={`flex flex-col items-end`}>
            <div className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${peer.change > 0
              ? 'bg-green-500/10 text-green-400 border-green-500/20'
              : 'bg-red-500/10 text-red-400 border-red-500/20'
              }`}>
              {peer.change > 0 ? '+' : ''}{peer.change}%
            </div>
          </div>
        </div>

        <div className="flex-1">
          <h3 className="text-sm font-bold text-white leading-tight mb-1 group-hover:text-blue-400 transition-colors">{peer.name}</h3>
          <div className="text-[10px] font-mono tracking-wider text-gray-500 uppercase">{peer.ticker}</div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-gray-400 text-[10px]">
            <TrendingUp size={12} className="text-blue-400/70" />
            <span className="font-mono">{peer.marketCap}</span>
          </div>
          <div className="text-[9px] font-bold text-blue-500/70 tracking-tighter uppercase italic">
            Peer Match
          </div>
        </div>
      </div>

      {isSelected && (
        <motion.div
          layoutId="selection-glow"
          className="absolute inset-0 border-2 border-blue-500/50 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        />
      )}
    </motion.div>
  );
};

export default React.memo(PeerCard);
