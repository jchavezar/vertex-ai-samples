import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, Sparkles, X as CloseIcon } from 'lucide-react';
import LogoWithFallback from './LogoWithFallback';
import PeerCard from './PeerCard';
import NeuralDeepDiveModal from './NeuralDeepDiveModal';
import { Peer } from './types';
import { PEERS_MOCK } from './mocks';

interface CompsArenaProps {
  ticker: string;
  intelPeers: Peer[] | null;
  selectedPeers: string[];
  togglePeerSelection: (ticker: string) => void;
  setShowTopology: (show: boolean) => void;
  setShowDeepDive: (show: boolean) => void;
  setSyncStatus: (status: 'idle' | 'active' | 'synchronized') => void;
}

const CompsArena: React.FC<CompsArenaProps> = ({
  ticker,
  intelPeers,
  selectedPeers,
  togglePeerSelection,
  setShowTopology,
  setShowDeepDive,
  setSyncStatus
}) => {
  const peers = intelPeers || PEERS_MOCK;
  const [internalSelectedPeer, setInternalSelectedPeer] = useState<Peer | null>(null);

  const handleDeepDive = (peer: Peer) => {
    setInternalSelectedPeer(peer);
    setShowDeepDive(true);
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#050608] flex items-center justify-center">
      {/* 3D Neural Background Mesh */}
      <div
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `url('/assets/grid_texture.png')`,
          backgroundSize: '100px 100px',
          maskImage: 'radial-gradient(circle at center, black, transparent 80%)'
        }}
      />

      {/* Sync Status Overlay */}
      <div className="absolute top-10 left-10 z-40 space-y-4">
        <div className="flex items-center gap-3 bg-white/5 border border-white/10 px-6 py-3 rounded-2xl backdrop-blur-xl">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Neural Sync Mode: ACTIVE</span>
        </div>
      </div>

      <div className="relative w-full max-w-7xl h-[800px] flex items-center justify-center perspective-1200 preserve-3d">
        {/* Central Neural Anchor (Mission Hub) */}
        <motion.div
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="relative z-20 w-[300px] h-[300px] rounded-full flex flex-col items-center justify-center gap-4 text-center group preserve-3d"
        >
          {/* Quantum Rings */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute inset-[-20px] rounded-full border border-blue-500/10 border-t-blue-500/40"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute inset-[-40px] rounded-full border border-white/5 border-b-white/20"
          />

          {/* Banana-Frost Heavy Glass effect */}
          <div className="absolute inset-0 rounded-full backdrop-blur-[80px] bg-white/5 border-[1.5px] border-white/20 shadow-[0_40px_100px_rgba(0,0,0,1),inset_0_0_80px_rgba(255,255,255,0.05)] overflow-hidden">
            {/* Shimmer Overlay */}
            <motion.div
              animate={{ x: ['-100%', '200%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 opacity-50"
            />
          </div>

          <div className="relative z-10 space-y-2">
            <div className="w-20 h-20 mx-auto rounded-3xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 shadow-[0_0_30px_rgba(59,130,246,0.1)]">
              <LogoWithFallback ticker={ticker} className="w-14 h-14 object-contain filter drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
            </div>
            <div className="space-y-1">
              <h2 className="text-4xl font-black text-white tracking-tighter italic uppercase">{ticker}</h2>
              <p className="text-[9px] font-bold text-blue-400 uppercase tracking-[0.4em] animate-pulse">Neural Sector Hub</p>
            </div>
          </div>

          {/* Radiant Glow */}
          <div className="absolute inset-[-40px] bg-blue-500/15 rounded-full blur-[100px] -z-10 animate-pulse" />
        </motion.div>

        {/* 3D Arc Peer Distribution */}
        <div className="absolute inset-0 z-10 flex items-center justify-center" style={{ transformStyle: 'preserve-3d' }}>
          {peers.map((peer, index) => {
            const angle = (index - (peers.length - 1) / 2) * (180 / Math.max(peers.length - 1, 3));
            const radius = 600;
            const x = Math.sin((angle * Math.PI) / 180) * radius;
            const z = Math.cos((angle * Math.PI) / 180) * radius - 800;
            const rotateY = -angle;

            return (
              <motion.div
                key={peer.ticker}
                initial={{ opacity: 0, scale: 0.8, z: -500 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  x,
                  z,
                  rotateY,
                  transition: { delay: index * 0.1 + 0.5, duration: 1.2, ease: [0.22, 1, 0.36, 1] }
                }}
                className="absolute"
                style={{ transformStyle: 'preserve-3d' }}
              >
                <PeerCard
                  peer={peer}
                  isSelected={selectedPeers.includes(peer.ticker)}
                  onClick={() => togglePeerSelection(peer.ticker)}
                />
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Persistent AI Interaction Controls */}
      <div className="fixed bottom-16 left-1/2 -translate-x-1/2 z-[3000] bg-black/40 border border-white/10 rounded-full px-12 py-6 backdrop-blur-[40px] shadow-[0_40px_80px_rgba(0,0,0,0.9)] flex items-center gap-14">
        <motion.button
          whileHover={{ scale: 1.1, y: -4 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setShowTopology(true)}
          className="flex flex-col items-center gap-2 group"
        >
          <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/20 group-hover:border-blue-500/40 transition-all duration-300">
            <Network size={22} strokeWidth={1.5} />
          </div>
          <span className="text-[9px] font-black tracking-widest text-white/30 group-hover:text-blue-400 transition-colors uppercase">Topology</span>
        </motion.button>

        <div className="h-10 w-px bg-white/10" />

        <motion.button
          whileHover={{ scale: 1.1, y: -4 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {
            if (selectedPeers.length > 0) {
              const p = peers.find(p => p.ticker === selectedPeers[0]);
              if (p) handleDeepDive(p);
            }
          }}
          disabled={selectedPeers.length === 0}
          className={`flex flex-col items-center gap-2 group ${selectedPeers.length === 0 ? 'opacity-30 cursor-not-allowed' : ''}`}
        >
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 ${selectedPeers.length > 0
            ? 'bg-blue-600 border border-blue-400 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)] animate-pulse'
            : 'bg-white/5 border border-white/10 text-white/40'
            }`}>
            <Sparkles size={24} strokeWidth={1.5} />
          </div>
          <span className={`text-[9px] font-black tracking-widest uppercase transition-colors ${selectedPeers.length > 0 ? 'text-white' : 'text-white/30'
            }`}>Deep Dive</span>
        </motion.button>

        <div className="h-10 w-px bg-white/10" />

        <motion.button
          whileHover={{ scale: 1.1, y: -4 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setSyncStatus('idle')}
          className="flex flex-col items-center gap-2 group"
        >
          <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-red-400 group-hover:bg-red-500/20 group-hover:border-red-500/40 transition-all duration-300">
            <CloseIcon size={22} strokeWidth={1.5} />
          </div>
          <span className="text-[9px] font-black tracking-widest text-white/30 group-hover:text-red-400 transition-colors uppercase">Abort</span>
        </motion.button>
      </div>

      {/* Internal Modal for specific peer deep dive */}
      <AnimatePresence>
        {internalSelectedPeer && (
          <NeuralDeepDiveModal
            isOpen={!!internalSelectedPeer}
            onClose={() => setInternalSelectedPeer(null)}
            primaryTicker={ticker}
            selectedPeer={internalSelectedPeer}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default React.memo(CompsArena);
