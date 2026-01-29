import React from 'react';
import { motion } from 'framer-motion';
import { Network, Sparkles, Zap, X as CloseIcon } from 'lucide-react';
import LogoWithFallback from './LogoWithFallback';
import PeerCard from './PeerCard';
import { PEERS_MOCK } from './mocks';
import { Peer } from './types';

interface CompsArenaProps {
  ticker: string;
  intelPeers: Peer[] | null;
  selectedPeers: string[];
  togglePeerSelection: (ticker: string) => void;
  setShowTopology: (show: boolean) => void;
  setShowDeepDive: (show: boolean) => void;
  setShowDiff: (show: boolean) => void;
  setSyncStatus: (status: 'idle' | 'active' | 'synchronized') => void;
}

const CompsArena: React.FC<CompsArenaProps> = ({
  ticker,
  intelPeers,
  selectedPeers,
  togglePeerSelection,
  setShowTopology,
  setShowDeepDive,
  setShowDiff,
  setSyncStatus
}) => {
  const peers = intelPeers || PEERS_MOCK;

  return (
    <div className="relative w-full min-h-screen bg-[#050608] flex flex-col p-8 overflow-y-auto custom-scrollbar">
      {/* Background Decor */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-blue-500/10 via-transparent to-transparent" />
        <div className="absolute top-0 left-2/4 w-px h-full bg-gradient-to-b from-blue-500/5 via-transparent to-transparent" />
        <div className="absolute top-0 left-3/4 w-px h-full bg-gradient-to-b from-blue-500/10 via-transparent to-transparent" />
      </div>

      {/* Header / Central Anchor */}
      <div className="relative z-10 flex flex-col items-center mb-16 pt-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center text-center"
        >
          <div className="relative w-24 h-24 mb-6">
            <LogoWithFallback ticker={ticker} className="w-full h-full object-contain filter drop-shadow-[0_0_15px_rgba(59,130,246,0.3)]" />
            <div className="absolute inset-0 bg-blue-500/10 rounded-full blur-2xl -z-10" />
          </div>
          <h1 className="text-4xl font-black text-white tracking-widest mb-2">{ticker}</h1>
          <div className="flex items-center gap-4 text-blue-400/60 uppercase tracking-[0.4em] text-[10px] font-bold">
            <div className="h-px w-8 bg-blue-500/30" />
            Neural Intelligence Hub
            <div className="h-px w-8 bg-blue-500/30" />
          </div>
        </motion.div>
      </div>

      {/* Grid Area */}
      <div className="relative z-10 max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-40">
        {peers.map((peer: Peer, idx: number) => (
          <motion.div
            key={peer.ticker}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.05 }}
          >
            <PeerCard
              peer={peer}
              isSelected={selectedPeers.includes(peer.ticker)}
              onClick={() => togglePeerSelection(peer.ticker)}
            />
          </motion.div>
        ))}
      </div>

      {/* Persistent Controls */}
      <div className="fixed bottom-12 left-1/2 -translate-x-1/2 flex items-center gap-6 z-[3000] px-8 py-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl">
        <button
          onClick={() => setShowTopology(true)}
          className="px-6 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white rounded-xl text-[11px] font-bold tracking-widest transition-all flex items-center gap-2.5 group"
        >
          <Network size={14} className="group-hover:text-blue-400 transition-colors" />
          TOPOLOGY
        </button>

        <div className="w-px h-8 bg-white/10" />

        <button
          onClick={() => setShowDeepDive(true)}
          disabled={selectedPeers.length === 0}
          className={`px-8 py-3 rounded-xl text-xs font-black tracking-widest transition-all flex items-center gap-2.5 group ${selectedPeers.length > 0
              ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.4)]'
              : 'bg-white/5 text-white/20 cursor-not-allowed'
            }`}
        >
          <Sparkles size={16} className={selectedPeers.length > 0 ? 'animate-pulse' : ''} />
          NEURAL DEEP DIVE
          {selectedPeers.length > 0 && (
            <span className="ml-1 px-2 py-0.5 rounded-md bg-white/20 text-[10px]">{selectedPeers.length}</span>
          )}
        </button>

        {selectedPeers.length === 2 && (
          <button
            onClick={() => setShowDiff(true)}
            className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black tracking-widest transition-all shadow-[0_0_20px_rgba(16,185,129,0.4)] flex items-center gap-2.5 animate-in slide-in-from-bottom-2"
          >
            <Zap size={16} />
            COMPARE
          </button>
        )}

        <div className="w-px h-8 bg-white/10" />

        <button
          onClick={() => setSyncStatus('idle')}
          className="p-2.5 bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/40 text-white/40 hover:text-red-400 rounded-xl transition-all"
          title="Exit Recon"
        >
          <CloseIcon size={18} />
        </button>
      </div>
    </div>
  );
};

export default React.memo(CompsArena);
