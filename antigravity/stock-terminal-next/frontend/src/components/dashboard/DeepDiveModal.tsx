import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Cpu, X as CloseIcon, Zap } from 'lucide-react';
import LogoWithFallback from './LogoWithFallback';

import { Peer } from './types';

interface DeepDiveModalProps {
  showDeepDive: boolean;
  setShowDeepDive: (show: boolean) => void;
  selectedPeers: string[];
  intelPeers: Peer[] | null;
  context: string;
  handleSync: () => void;
  isSyncing: boolean;
}

import { PEERS_MOCK } from './mocks';

const DeepDiveModal: React.FC<DeepDiveModalProps> = ({ showDeepDive, setShowDeepDive, selectedPeers, intelPeers, context, handleSync, isSyncing }) => (
  <AnimatePresence>
    {showDeepDive && (
      <div className="fixed inset-0 z-[5000] flex items-center justify-center p-8 bg-black/80 backdrop-blur-xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 30 }}
          className="relative w-full max-w-6xl max-h-[90vh] bg-[#0a0c10] border border-white/10 rounded-[32px] overflow-hidden shadow-[0_0_100px_rgba(0,0,0,1)] flex flex-col"
        >
          <div className="p-8 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-blue-600/5 to-transparent">
            <div className="flex items-center gap-3">
              <Sparkles className="text-blue-400" size={24} />
              <h2 className="text-2xl font-black text-white tracking-tight uppercase italic">Neural Deep Dive Analysis</h2>
              <button
                onClick={handleSync}
                disabled={isSyncing}
                className={`ml-4 flex items-center gap-2 px-6 py-2 bg-[#00f2ff]/10 hover:bg-[#00f2ff]/20 border border-[#00f2ff]/30 text-[#00f2ff] rounded-full text-xs font-black tracking-widest transition-all group ${isSyncing ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Cpu size={14} className={isSyncing ? 'animate-spin' : 'group-hover:rotate-180 transition-transform'} />
                {isSyncing ? 'SYNCING...' : 'FORCE RE-SYNC'}
              </button>
            </div>
            <button onClick={() => setShowDeepDive(false)} className="p-3 bg-white/5 hover:bg-white/10 rounded-full transition-all">
              <CloseIcon size={24} className="text-white/60" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-10 custom-scrollbar">
            <div className="grid grid-cols-2 gap-12">
              {selectedPeers.map(t => {
                const peerData = (intelPeers || PEERS_MOCK).find((p: Peer) => p.ticker === t);
                if (!peerData) return null;
                return (
                  <div key={t} className="space-y-8">
                    <div className="flex items-center gap-6">
                      <div className="w-20 h-20 bg-black/40 rounded-2xl border border-white/10 flex items-center justify-center p-3">
                        <LogoWithFallback ticker={t} className="w-full h-full object-contain" />
                      </div>
                      <div>
                        <h3 className="text-3xl font-black text-white">{peerData.name}</h3>
                        <p className="text-blue-400 font-bold tracking-widest uppercase text-sm">{t} // STRATEGIC_PEER</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-white/5 border border-white/5 rounded-2xl space-y-1">
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Moat Strategy</span>
                        <p className="text-sm text-gray-200 font-medium leading-relaxed">{peerData.identity}</p>
                      </div>
                      <div className="p-4 bg-white/5 border border-white/5 rounded-2xl space-y-1">
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">CEO Posture</span>
                        <p className="text-sm text-gray-200 font-medium leading-relaxed">{peerData.ceo_sentiment}</p>
                      </div>
                    </div>

                    <div className="p-6 bg-blue-500/5 border border-blue-500/10 rounded-2xl space-y-3">
                      <div className="flex items-center gap-2">
                        <Zap size={14} className="text-yellow-400" />
                        <span className="text-xs font-black text-white uppercase tracking-widest">Neural Thesis</span>
                      </div>
                      <p className="text-sm text-gray-300 leading-relaxed italic">
                        {peerData.comparison_thesis || `${peerData.name} is currently positioned as a primary threat in the ${context || 'current'} market landscape, leveraging ${peerData.last_launch} as a tactical spearhead.`}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="p-8 bg-blue-500/5 border-t border-white/5">
            <div className="flex items-center gap-4 text-xs font-bold text-blue-400 tracking-[0.2em] uppercase">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
              Neural Model: Gemini 2.5 Strategic Advanced // Mode: Deep_Dive_Active
            </div>
          </div>
        </motion.div>
      </div>
    )}
  </AnimatePresence>
);

export default React.memo(DeepDiveModal);
