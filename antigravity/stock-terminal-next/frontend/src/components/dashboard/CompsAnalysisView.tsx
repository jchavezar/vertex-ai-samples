import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useDashboardStore } from '../../store/dashboardStore';

// Modular components
import MissionBriefing from './MissionBriefing';
import NeuralSyncOverlay from './NeuralSyncOverlay';
import CompsArena from './CompsArena';
import WorkflowTopologyOverlay from './WorkflowTopologyOverlay';
import { LogOverlay } from './LogOverlay';

import { Peer } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const CompsAnalysisView: React.FC = () => {
  const { ticker, compsAnalysis, setCompsAnalysis, setTicker } = useDashboardStore();
  const [selectedPeers, setSelectedPeers] = useState<string[]>([]);
  const [showTopology, setShowTopology] = useState(false);
  const [context, setContext] = useState("");
  const [syncProgress, setSyncProgress] = useState(0);
  const [syncStatusText, setSyncStatusText] = useState("Initializing Neural Recon...");
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    const startSync = async () => {
      if (!ticker) return;

      // Reset state for new sync
      setCompsAnalysis({ syncStatus: 'active', intel: null, reasoning: [] });
      setSyncProgress(0);
      setSyncStatusText("Neural Recon Initiated...");

      try {
        const response = await fetch(`${API_BASE_URL}/comps-analysis/stream?ticker=${ticker}&context=${encodeURIComponent(context)}`);
        const reader = response.body?.getReader();
        if (!reader) return;

        const decoder = new TextDecoder();
        let buffer = '';
        let hasMore = true;

        while (hasMore) {
          const { done, value } = await reader.read();
          if (done) {
            hasMore = false;
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const event = JSON.parse(line);
              if (event.type === 'neural_sync') {
                setSyncStatusText(event.message || "Neural Syncing...");
                console.info(`[SYSTEM] ${event.message}`);
              } else if (event.type === 'reasoning') {
                const cleaned = event.message.replace(/^>+/, '').trim();
                setSyncProgress(p => Math.min(p + 1, 95));
                setSyncStatusText(cleaned);
                console.log(`[RECON] ${cleaned}`);

                // Get current reasoning and add new one
                const currentReasoning = useDashboardStore.getState().compsAnalysis.reasoning || [];
                setCompsAnalysis({
                  reasoning: [...currentReasoning, cleaned]
                });
              } else if (event.type === 'intel') {
                const parsedIntel: { peers: Peer[] } = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                console.info(`[INTEL] Convergence successful for ${ticker}`);

                setCompsAnalysis({
                  intel: parsedIntel,
                  syncStatus: 'synchronized'
                });
                setSyncProgress(100);
                setSyncStatusText("Neural Convergence Complete");
              }
            } catch (e) {
              console.error("Error parsing event line", line, e);
            }
          }
        }
      } catch (err) {
        console.error("Comps Sync Failed", err);
        setCompsAnalysis({ syncStatus: 'idle' });
        setSyncProgress(0);
        setSyncStatusText("Sync Failed");
      }
    };

    if (compsAnalysis.syncStatus === 'active') {
      startSync();
    }
  }, [ticker, context, compsAnalysis.syncStatus, setCompsAnalysis]);

  const togglePeerSelection = (t: string) => {
    setSelectedPeers(prev => prev.includes(t) ? prev.filter(p => p !== t) : [...prev, t].slice(-2));
  };

  return (
    <div className="w-full h-full bg-[#050608] relative overflow-hidden">
      <div className="cinematic-vignette opacity-60" />
      <AnimatePresence mode="wait">
        {compsAnalysis.syncStatus === 'idle' && (
          <motion.div
            key="briefing"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1, filter: 'blur(20px)' }}
            transition={{ duration: 1.2, ease: [0.43, 0.13, 0.23, 0.96] }}
            className="w-full h-full"
          >
            <MissionBriefing
              ticker={ticker}
              setTicker={setTicker}
              context={context}
              setContext={setContext}
              handleSearch={() => setCompsAnalysis({ syncStatus: 'active' })}
            />
          </motion.div>
        )}

        {compsAnalysis.syncStatus === 'active' && (
          <motion.div
            key="sync"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 2, filter: 'blur(40px)' }}
            transition={{ duration: 1.5, ease: "circIn" }}
            className="w-full h-full"
          >
            <NeuralSyncOverlay
              ticker={ticker}
              context={context}
              syncProgress={syncProgress}
              syncStatus={syncStatusText}
              reasoning={compsAnalysis.reasoning || []}
            />
          </motion.div>
        )}

        {compsAnalysis.syncStatus === 'synchronized' && (
          <motion.div
            key="arena"
            initial={{ opacity: 0, scale: 0.5, filter: 'blur(30px)' }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={{ duration: 2, ease: [0.23, 1, 0.32, 1] }}
            className="w-full h-full"
          >
            {/* Entry Flash */}
            <motion.div
              initial={{ opacity: 1 }}
              animate={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
              className="absolute inset-0 bg-white z-[100] pointer-events-none"
            />

            <CompsArena
              ticker={ticker}
              intelPeers={compsAnalysis.intel?.peers || null}
              selectedPeers={selectedPeers}
              togglePeerSelection={togglePeerSelection}
              setShowTopology={setShowTopology}
              setShowDeepDive={() => { }} // Internal to CompsArena now
              setSyncStatus={(status) => setCompsAnalysis({ syncStatus: status })}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Global Terminal Toggle */}
      <div className="absolute top-10 right-10 z-[5000] flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowLogs(!showLogs)}
          className={`px-5 py-2.5 rounded-xl border flex items-center gap-3 transition-all duration-300 ${showLogs
            ? 'bg-cyan-500/20 border-cyan-400 text-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.3)]'
            : 'bg-white/5 border-white/10 text-white/40 hover:bg-white/10 hover:text-white'
            }`}
        >
          <div className={`w-1.5 h-1.5 rounded-full ${showLogs ? 'bg-cyan-400 animate-pulse' : 'bg-white/20'}`} />
          <span className="text-[10px] font-black uppercase tracking-widest">Neural Console</span>
        </motion.button>
      </div>

      <LogOverlay isOpen={showLogs} onClose={() => setShowLogs(false)} />

      <AnimatePresence>
        {showTopology && (
          <WorkflowTopologyOverlay
            onClose={() => setShowTopology(false)}
          />
        )}
      </AnimatePresence>


    </div>
  );
};
