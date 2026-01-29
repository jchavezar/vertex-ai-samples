import React from 'react';
import { motion } from 'framer-motion';
import { X as CloseIcon, Zap, TrendingUp, ShieldCheck, Target, Cpu, Activity } from 'lucide-react';

import { Peer } from './types';

interface HolographicDiffOverlayProps {
  peerA: Peer;
  peerB: Peer;
  onClose: () => void;
}

export const HolographicDiffOverlay: React.FC<HolographicDiffOverlayProps> = ({ peerA, peerB, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[6000] flex items-center justify-center p-8 bg-black/90 backdrop-blur-2xl overflow-hidden"
    >
      {/* Background Cinematic Effects */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute inset-0 bg-[url('/assets/grid_texture.png')] opacity-10" />
      </div>

      <motion.div
        initial={{ scale: 0.9, y: 40, opacity: 0 }}
        animate={{ scale: 1, y: 0, opacity: 1 }}
        exit={{ scale: 0.9, y: 40, opacity: 0 }}
        className="relative z-10 w-full max-w-7xl h-full max-h-[90vh] bg-black/40 border border-white/10 rounded-[40px] shadow-[0_0_100px_rgba(59,130,246,0.15)] overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="p-8 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="px-4 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] flex items-center gap-2">
              <Zap size={14} />
              Neural Diff Engine v4.0
            </div>
            <h2 className="text-2xl font-black text-white italic uppercase tracking-tighter">Strategic Comparison</h2>
          </div>
          <button
            onClick={onClose}
            className="p-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-white/60 hover:text-white transition-all"
          >
            <CloseIcon size={24} />
          </button>
        </div>

        {/* Comparison Arena */}
        <div className="flex-1 overflow-y-auto p-12 custom-scrollbar">
          <div className="grid grid-cols-11 gap-8 items-center h-full">

            {/* Peer A */}
            <div className="col-span-5 space-y-12">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-32 h-32 bg-blue-500/5 border border-blue-500/20 rounded-3xl flex items-center justify-center p-6 shadow-[0_0_40px_rgba(59,130,246,0.1)]">
                  <span className="text-4xl font-black text-white">{peerA.ticker}</span>
                </div>
                <div>
                  <h3 className="text-3xl font-black text-white">{peerA.name}</h3>
                  <p className="text-blue-400 font-bold uppercase tracking-widest text-xs">Primary Subject</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <MetricCard label="Market Momentum" value={`${peerA.change}%`} icon={<Activity size={12} />} color="text-emerald-400" />
                <MetricCard label="Market Cap" value={peerA.marketCap} icon={<TrendingUp size={12} />} />
              </div>

              <PerspectiveSection title="Strategic Moat" content={peerA.identity} icon={<ShieldCheck size={16} />} />
              <PerspectiveSection title="Leadership Posture" content={peerA.ceo_sentiment} icon={<Target size={16} />} />
            </div>

            {/* VS Divider */}
            <div className="col-span-1 flex flex-col items-center justify-center h-full">
              <div className="w-px h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
              <div className="my-8 w-12 h-12 rounded-full border border-blue-500/50 bg-blue-500/10 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.3)]">
                <span className="text-blue-400 font-black italic tracking-tighter">VS</span>
              </div>
              <div className="w-px h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
            </div>

            {/* Peer B */}
            <div className="col-span-5 space-y-12">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-32 h-32 bg-purple-500/5 border border-purple-500/20 rounded-3xl flex items-center justify-center p-6 shadow-[0_0_40px_rgba(168,85,247,0.1)]">
                  <span className="text-4xl font-black text-white">{peerB.ticker}</span>
                </div>
                <div>
                  <h3 className="text-3xl font-black text-white">{peerB.name}</h3>
                  <p className="text-purple-400 font-bold uppercase tracking-widest text-xs">Comparison Target</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <MetricCard label="Market Momentum" value={`${peerB.change}%`} icon={<Activity size={12} />} color="text-emerald-400" />
                <MetricCard label="Market Cap" value={peerB.marketCap} icon={<TrendingUp size={12} />} />
              </div>

              <PerspectiveSection title="Strategic Moat" content={peerB.identity} icon={<ShieldCheck size={16} />} color="border-purple-500/20" />
              <PerspectiveSection title="Leadership Posture" content={peerB.ceo_sentiment} icon={<Target size={16} />} color="border-purple-500/20" />
            </div>

          </div>
        </div>

        {/* Footer Info */}
        <div className="p-8 border-t border-white/5 bg-blue-500/5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Cpu size={16} className="text-blue-400" />
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-[0.3em]">Neural Thesis Cross-Analysis Active</span>
          </div>
          <div className="text-[10px] font-black text-blue-400/60 uppercase tracking-widest">
            Gemini 2.5 Strategic Advanced // Diff Mode
          </div>
        </div>
      </motion.div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.2); border-radius: 10px; }
      `}</style>
    </motion.div>
  );
};

const MetricCard = ({ label, value, icon, color = "text-white" }: { label: string, value: string, icon: React.ReactNode, color?: string }) => (
  <div className="p-5 bg-white/5 border border-white/5 rounded-2xl space-y-2">
    <div className="flex items-center gap-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">
      {icon}
      {label}
    </div>
    <div className={`text-2xl font-black ${color}`}>{value}</div>
  </div>
);

const PerspectiveSection = ({ title, content, icon, color = "border-blue-500/20" }: { title: string, content: string, icon: React.ReactNode, color?: string }) => (
  <div className={`p-6 bg-white/5 border ${color} rounded-2xl space-y-4`}>
    <div className="flex items-center gap-3">
      <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
        {icon}
      </div>
      <h4 className="text-xs font-black text-white uppercase tracking-widest">{title}</h4>
    </div>
    <p className="text-sm text-gray-400 leading-relaxed font-medium">{content}</p>
  </div>
);
