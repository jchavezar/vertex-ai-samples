import React from 'react';
import { motion } from 'framer-motion';
import LogoWithFallback from './LogoWithFallback';

interface NeuralSyncOverlayProps {
  ticker: string;
  context: string;
  syncProgress: number;
  syncStatus: string;
  reasoning: string[];
}

const NeuralSyncOverlay: React.FC<NeuralSyncOverlayProps> = ({ ticker, context, syncProgress, syncStatus, reasoning }) => (
  <div className="absolute inset-0 z-[1000] bg-black/90 backdrop-blur-2xl flex flex-col items-center justify-center p-8 overflow-hidden">
    <div className="absolute inset-0 bg-[url('/assets/grid_texture.png')] opacity-10 animate-pulse" />

    {/* Noise Texture Overlay */}
    <div className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-overlay bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />

    {/* High-frequency pulsing glow */}
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div className="w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse-fast" />
    </div>

    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="relative z-10 w-full max-w-4xl space-y-8"
    >
      <div className="flex flex-col items-center space-y-2">
        <div className="relative">
          <svg className="w-48 h-48 -rotate-90">
            <circle cx="96" cy="96" r="88" className="stroke-white/5" strokeWidth="4" fill="transparent" />
            <motion.circle
              cx="96" cy="96" r="88"
              className="stroke-blue-500"
              strokeWidth="4"
              fill="transparent"
              strokeDasharray="552.92"
              animate={{ strokeDashoffset: 552.92 - (552.92 * syncProgress / 100) }}
              transition={{ duration: 0.5 }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-black text-white font-mono">{Math.round(syncProgress)}%</span>
            <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Convergence</span>
          </div>
        </div>
        <h2 className="text-2xl font-black text-white tracking-widest uppercase italic pt-4">Neural Syncing: {ticker}</h2>
        <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full">
          <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          <span className="text-[10px] font-black text-blue-400 tracking-widest uppercase">{context || 'Full Spectrum Analysis'}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
          <div className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Active Target</div>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-black/40 rounded-xl border border-white/10 flex items-center justify-center shadow-inner">
              <LogoWithFallback ticker={ticker} className="w-10 h-10 object-contain" />
            </div>
            <div>
              <div className="text-2xl font-black text-white">{ticker}</div>
              <div className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Sector_AI_Infra</div>
            </div>
          </div>
          <div className="pt-4 border-t border-white/5 space-y-2">
            <div className="flex justify-between text-[10px] font-bold">
              <span className="text-gray-500">Latency</span>
              <span className="text-blue-400">12ms</span>
            </div>
            <div className="flex justify-between text-[10px] font-bold">
              <span className="text-gray-500">Agents Active</span>
              <span className="text-blue-400">07</span>
            </div>
          </div>
        </div>

        <div className="col-span-2 bg-black/40 border border-blue-500/30 rounded-2xl p-6 shadow-2xl relative">
          <div className="absolute top-4 right-6 flex items-center gap-2">
            <span className="text-[8px] font-black text-emerald-400 uppercase tracking-widest animate-pulse">Live_Feed</span>
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          </div>
          <div className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-4">Neural Log Stream</div>
          <div className="h-48 overflow-y-auto font-mono text-xs text-blue-200/80 space-y-1.5 custom-scrollbar pr-2">
            {reasoning.length > 0 ? (
              reasoning.map((step: string, i: number) => (
                <motion.p key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
                  <span className="text-blue-500/50 pr-2">[{i.toString().padStart(2, '0')}]</span>
                  {step}
                </motion.p>
              ))
            ) : (
              <div className="opacity-30">
                <p>&gt; Initializing quantum link...</p>
                <p>&gt; Establishing secure pipe...</p>
                <p>&gt; Handshaking with remote agents...</p>
              </div>
            )}
          </div>
          <div className="mt-4 pt-4 border-t border-white/5 text-[10px] font-bold text-gray-500 text-center tracking-widest">
            {syncStatus}
          </div>
        </div>
      </div>
    </motion.div>
    <style>{`
    .custom-scrollbar::-webkit-scrollbar { width: 2px; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.3); border-radius: 10px; }
    @keyframes pulse-fast { 0%, 100% { opacity: 0.3; transform: scale(1); } 50% { opacity: 0.6; transform: scale(1.1); } }
    .animate-pulse-fast { animation: pulse-fast 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
  `}</style>
  </div>
);

export default React.memo(NeuralSyncOverlay);
