import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Zap, Activity } from 'lucide-react';
import { Peer } from './types';

interface NeuralDeepDiveModalProps {
  isOpen: boolean;
  onClose: () => void;
  primaryTicker: string;
  selectedPeer: Peer;
}

const NeuralDeepDiveModal: React.FC<NeuralDeepDiveModalProps> = ({ isOpen, onClose, primaryTicker, selectedPeer }) => {
  const [reasoningStep, setReasoningStep] = useState(0);
  const steps = [
    `Analyzing 10-K filings for ${selectedPeer.ticker}...`,
    "Cross-referencing supply chain nodes...",
    "Evaluating competitive moat stability...",
    "Synthesizing alpha thesis...",
    "Optimizing Monte Carlo simulations..."
  ];

  useEffect(() => {
    if (isOpen) {
      const interval = setInterval(() => {
        setReasoningStep((prev) => (prev + 1) % (steps.length + 1));
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isOpen, steps.length]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
      >
        <motion.div
          initial={{ scale: 0.8, filter: 'blur(20px)', opacity: 0 }}
          animate={{ scale: 1, filter: 'blur(0px)', opacity: 1 }}
          exit={{ scale: 1.1, filter: 'blur(20px)', opacity: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="relative w-full max-w-6xl bg-[#08090C] rounded-[3rem] border border-white/10 shadow-[0_50px_150px_rgba(0,0,0,1)] overflow-hidden scanline-effect"
        >
          <div className="cinematic-vignette opacity-50" />
          {/* Header */}
          <div className="flex items-center justify-between p-8 border-b border-white/5 bg-gradient-to-r from-blue-500/5 to-transparent">
            <div className="flex items-center gap-4">
              <div className="bg-blue-500/10 p-2 rounded-xl text-blue-400 border border-blue-500/20">
                <Sparkles size={24} />
              </div>
              <h2 className="text-2xl font-black text-white tracking-widest uppercase italic">
                Neural Deep Dive Analysis
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-3 hover:bg-white/5 rounded-full text-white/40 hover:text-white transition-colors border border-transparent hover:border-white/10"
            >
              <X size={24} />
            </button>
          </div>

          <div className="p-10 grid grid-cols-12 gap-10">
            {/* Left Content: Thesis & Reasoning */}
            <div className="col-span-12 lg:col-span-5 space-y-8">
              <div className="bg-blue-500/5 border border-blue-500/20 rounded-3xl p-8 space-y-6">
                <div>
                  <h3 className="text-blue-400 font-black text-xs uppercase tracking-[0.3em] mb-3 flex items-center gap-2">
                    <Activity size={14} /> Alpha Thesis
                  </h3>
                  <p className="text-white text-lg font-medium leading-relaxed">
                    {selectedPeer.alpha_thesis || `The structural advantage in **${selectedPeer.ticker}** vs **${primaryTicker}** lies in the supply chain vertical integration. Our agents detect a **15% efficiency gap** in wafer allocation favoring the leader.`}
                  </p>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Live Agent Reasoning
                  </div>
                  <div className="space-y-2 font-mono text-[11px] text-white/40">
                    {steps.slice(0, reasoningStep + 1).map((step, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-2"
                      >
                        <span className="text-blue-500">{'>'}</span> {step}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <div className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-2">Upside Prob.</div>
                  <div className="text-4xl font-black text-emerald-400">{selectedPeer.upside || 74}%</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <div className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-2">Volatility Risk</div>
                  <div className="text-4xl font-black text-blue-400">{selectedPeer.vol_risk || 12}%</div>
                </div>
              </div>
            </div>

            {/* Right Content: Monte Carlo Simulation */}
            <div className="col-span-12 lg:col-span-7 flex flex-col">
              <div className="relative flex-1 min-h-[400px] rounded-[2.5rem] bg-[#0A0C0F] border border-white/5 overflow-hidden flex flex-col items-center justify-center group">
                {/* Neural Mesh Background */}
                <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '24px 24px' }} />

                <div className="relative z-10 flex flex-col items-center gap-8">
                  <motion.div
                    animate={{
                      scale: [1, 1.1, 1],
                      filter: ["drop-shadow(0 0 20px rgba(59,130,246,0.3))", "drop-shadow(0 0 40px rgba(59,130,246,0.6))", "drop-shadow(0 0 20px rgba(59,130,246,0.3))"]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-yellow-500"
                  >
                    <Zap size={64} strokeWidth={1} fill="currentColor" />
                  </motion.div>

                  <div className="text-center space-y-2">
                    <h3 className="text-2xl font-black text-white tracking-tight">Monte Carlo Simulation</h3>
                    <p className="text-white/30 text-xs font-mono tracking-widest uppercase">Probabilistic Competitive Manifold</p>
                  </div>

                  <div className="flex items-center gap-16 mt-8">
                    <div className="flex flex-col items-center gap-4">
                      <div className="w-20 h-20 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-xl font-black text-white/30 backdrop-blur-md">
                        {primaryTicker}
                      </div>
                      <div className="text-[11px] font-black font-mono text-blue-400 tracking-widest uppercase">Delta: 22%</div>
                    </div>

                    <div className="relative">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-[-15px] rounded-full border border-emerald-500/20 border-t-emerald-500"
                      />
                      <div className="w-24 h-24 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-2xl font-black text-white shadow-[0_0_50px_rgba(16,185,129,0.3)] backdrop-blur-xl">
                        {selectedPeer.ticker}
                      </div>
                      <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-[11px] font-black font-mono text-emerald-400 tracking-widest uppercase">Convergence: 70%</div>
                    </div>
                  </div>
                </div>

                {/* Animated Particles */}
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-blue-500/30 rounded-full"
                    animate={{
                      x: [Math.random() * 400 - 200, Math.random() * 400 - 200],
                      y: [Math.random() * 400 - 200, Math.random() * 400 - 200],
                      opacity: [0, 1, 0]
                    }}
                    transition={{ duration: Math.random() * 3 + 2, repeat: Infinity }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Footer Metadata */}
          <div className="px-10 py-6 border-t border-white/5 bg-black/40 flex justify-center">
            <div className="text-[10px] font-mono font-black text-white/10 tracking-[0.5em] uppercase">
              Generated by Core Intelligence Agent • 12ms Latency
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default NeuralDeepDiveModal;
