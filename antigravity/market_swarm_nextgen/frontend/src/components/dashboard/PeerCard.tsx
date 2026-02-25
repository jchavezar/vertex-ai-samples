import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LogoWithFallback from './LogoWithFallback';
import { Peer } from './types';

interface PeerCardProps {
  peer: Peer;
  isSelected: boolean;
  onClick: () => void;
}

const PeerCard: React.FC<PeerCardProps> = ({ peer, isSelected, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);
  const isPositive = peer.change > 0;

  // High-fidelity asset mapping
  const tickerLower = peer.ticker.toLowerCase();
  const has3DIcon = ['nvda', 'amd', 'apple', 'amzn', 'msft', 'googl'].includes(tickerLower);
  const iconPath = `/assets/${tickerLower}_3d_icon.png`;

  return (
    <motion.div
      layout
      whileHover={{ y: -5, scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      className={`relative cursor-pointer group rounded-2xl overflow-hidden border transition-all duration-500 scanline-effect ${isSelected
        ? 'border-blue-500 shadow-[0_0_50px_rgba(59,130,246,0.3)] bg-blue-500/5'
        : 'border-white/10 bg-[#0A0C11]/80 hover:border-white/20'
        }`}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="cinematic-vignette opacity-40" />
      {/* Quantum-Finance Textures */}
      <div
        className="absolute inset-0 pointer-events-none transition-opacity duration-700 opacity-[0.1] group-hover:opacity-[0.2]"
        style={{
          backgroundImage: `url(${isPositive ? '/assets/emerald_texture.png' : '/assets/obsidian_texture.png'})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          mixBlendMode: 'overlay'
        }}
      />

      <div className="relative p-6 h-full flex flex-col min-h-[220px] z-10 backdrop-blur-xl">
        {/* Top Header: Logo + Percentage Change */}
        <div className="flex justify-between items-start mb-6">
          <div className="w-16 h-16 rounded-xl bg-black/50 backdrop-blur-md p-3 border border-white/10 flex items-center justify-center shadow-2xl">
            {has3DIcon ? (
              <img
                src={iconPath}
                alt={peer.ticker}
                className="w-full h-full object-contain filter drop-shadow-[0_4px_8px_rgba(0,0,0,0.5)]"
              />
            ) : (
              <LogoWithFallback ticker={peer.ticker} className="w-full h-full object-contain" />
            )}
          </div>
          <div className={`text-[12px] font-black px-3 py-1.5 rounded-full backdrop-blur-md shadow-lg border ${isPositive
            ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
            : 'bg-red-500/20 text-red-400 border-red-500/30'
            }`}>
            {isPositive ? '+' : ''}{peer.change}%
          </div>
        </div>

        {/* Company Identity */}
        <div className="mb-6">
          <h3 className="text-2xl font-black text-white leading-none mb-1 tracking-tight uppercase">
            {peer.name.split(' ')[0]}
          </h3>
          <div className="text-[12px] font-mono font-black tracking-[0.3em] text-white/30 uppercase">
            {peer.ticker}
          </div>
        </div>

        {/* Status Metrics (Bottom Left Style) */}
        <div className="space-y-2 mt-auto">
          {peer.key_metrics?.slice(0, 2).map((metric, idx) => (
            <div key={idx} className="flex items-center gap-2 text-white/70 text-[11px] font-bold uppercase tracking-widest">
              {idx === 0 ? (
                <svg className="w-3.5 h-3.5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              ) : (
                <svg className="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
              )}
              {metric}
            </div>
          )) || (
              <>
                <div className="flex items-center gap-2 text-white/70 text-[11px] font-bold uppercase tracking-widest">
                  <svg className="w-3.5 h-3.5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  STRATEGIC TARGET
                </div>
                <div className="flex items-center gap-2 text-white/70 text-[11px] font-bold uppercase tracking-widest">
                  <svg className="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                  {peer.marketCap} MCAP
                </div>
              </>
            )}
        </div>

        {/* Bottom Status Bars */}
        <div className="mt-4 pt-4 border-t border-white/5 flex gap-1 h-3">
          <div className="h-full flex-1 rounded-full bg-emerald-500 opacity-60" />
          <div className="h-full flex-1 rounded-full bg-white/20" />
          <div className="h-full flex-1 rounded-full bg-red-500 opacity-60" />
          <div className="h-full flex-1 rounded-full bg-white/20" />
        </div>
      </div>

      {/* Selection Border */}
      {isSelected && (
        <motion.div
          layoutId="selection-border"
          className="absolute inset-0 border-2 border-blue-500 z-20 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        />
      )}

      {/* Micro-Preview Overlay on Hover */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, scale: 1.1 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1 }}
            className="absolute inset-0 z-30 bg-blue-600/95 backdrop-blur-xl p-6 flex flex-col justify-center items-center text-center space-y-6"
          >
            {/* HUD Corner Accents */}
            <div className="absolute top-4 left-4 w-4 h-4 border-t-2 border-l-2 border-white/40" />
            <div className="absolute top-4 right-4 w-4 h-4 border-t-2 border-r-2 border-white/40" />
            <div className="absolute bottom-4 left-4 w-4 h-4 border-b-2 border-l-2 border-white/40" />
            <div className="absolute bottom-4 right-4 w-4 h-4 border-b-2 border-r-2 border-white/40" />

            <div className="text-white/60 text-[10px] uppercase font-black tracking-widest flex items-center gap-2">
              <div className="w-1 h-1 rounded-full bg-white animate-pulse" />
              Neural Insight
            </div>
            <p className="text-white text-[15px] font-bold leading-tight italic px-2">
              "{peer.ceo_sentiment?.slice(0, 100)}..."
            </p>
            <div className="space-y-2">
              <div className="text-[8px] font-black text-white/40 uppercase tracking-widest">Identity_Node</div>
              <div className="px-6 py-2 bg-white/10 rounded-lg border border-white/20 text-[12px] text-white font-black uppercase tracking-tight">
                {peer.identity}
              </div>
            </div>
            <div className="flex items-center gap-2 text-white/50 text-[9px] font-black uppercase tracking-widest pt-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              PEER SYNC ACTIVE
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default React.memo(PeerCard);
