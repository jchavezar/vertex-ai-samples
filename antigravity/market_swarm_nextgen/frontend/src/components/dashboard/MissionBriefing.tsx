import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Zap, Search, ArrowRight } from 'lucide-react';
import StrategicIntelBackground from './StrategicIntelBackground';

interface MissionBriefingProps {
  ticker: string;
  setTicker: (ticker: string) => void;
  context: string;
  setContext: (context: string) => void;
  handleSearch: () => void;
}

const MissionBriefing: React.FC<MissionBriefingProps> = ({ ticker, setTicker, context, setContext, handleSearch }) => (
  <div className="relative w-full h-[85vh] flex flex-col items-center justify-center p-8 overflow-hidden">
    <StrategicIntelBackground />

    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative z-10 w-full max-w-2xl text-center space-y-12"
    >
      <div className="space-y-4">
        <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-black tracking-[0.2em] uppercase">
          <ShieldCheck size={14} />
          Strategic Intel Reconnaissance
        </div>
        <h1 className="text-6xl font-black text-white tracking-tighter leading-none italic uppercase">
          Battle<span className="text-blue-500">cards</span>
        </h1>
        <p className="text-gray-400 font-medium tracking-tight">Enter a target ticker to initiate neural competitive reconnaissance.</p>
      </div>

      <div className="relative group p-[1px] rounded-3xl bg-gradient-to-r from-blue-600/30 via-white/10 to-purple-600/30 shadow-[0_0_50px_rgba(59,130,246,0.2)]">
        <div className="bg-black/60 backdrop-blur-3xl rounded-3xl p-8 space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-1 space-y-2">
              <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Target Ticker</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                  <Zap className="w-4 h-4 text-blue-500/50 group-focus-within:text-blue-400 transition-colors" />
                </div>
                <input
                  type="text"
                  placeholder="NVDA"
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white font-black tracking-widest focus:border-blue-500/50 focus:bg-white/10 outline-none transition-all"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>
            <div className="col-span-2 space-y-2">
              <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Strategic Focus</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                  <Search className="w-4 h-4 text-white/20" />
                </div>
                <input
                  type="text"
                  placeholder="e.g. 'Data Center Moat', 'Edge AI Latency'"
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white font-medium focus:border-blue-500/50 focus:bg-white/10 outline-none transition-all"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleSearch}
            className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-black tracking-widest flex items-center justify-center gap-3 transition-all group shadow-2xl shadow-blue-600/20"
          >
            INITIATE NEURAL RECON
            <ArrowRight size={20} className="group-hover:translate-x-2 transition-transform" />
          </button>
        </div>
      </div>
    </motion.div>
  </div>
);

export default React.memo(MissionBriefing);
