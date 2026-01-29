import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import WorkflowTopologyOverlay from './WorkflowTopologyOverlay';
import { HolographicDiffOverlay } from './HolographicDiffOverlay';
import { useDashboardStore } from '../../store/dashboardStore';

// Modular components
import MissionBriefing from './MissionBriefing';
import NeuralSyncOverlay from './NeuralSyncOverlay';
import CompsArena from './CompsArena';
import DeepDiveModal from './DeepDiveModal';

import { PEERS_MOCK } from './mocks';
import { Peer } from './types';

const API_BASE_URL = 'http://localhost:8001';

export const CompsAnalysisView: React.FC = () => {
  const { ticker, compsAnalysis, setCompsAnalysis, setTicker } = useDashboardStore();
  const [selectedPeers, setSelectedPeers] = useState<string[]>([]);
  const [showDeepDive, setShowDeepDive] = useState(false);
  const [showDiff, setShowDiff] = useState(false);
  const [showTopology, setShowTopology] = useState(false);
  const [context, setContext] = useState("");
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState("Initializing Neural Recon...");
  const [syncProgress, setSyncProgress] = useState(0);

  useEffect(() => {
    const startSync = async () => {
      if (!ticker) return;
      setCompsAnalysis({ syncStatus: 'active', intel: null, reasoning: [] });
      setSyncProgress(0);
      setIsSyncing(true);
      setSyncStatus("Neural Recon Initiated...");
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
                setSyncStatus(event.message || "Neural Syncing...");
              } else if (event.type === 'reasoning') {
                const cleaned = event.message.replace(/^>+/, '').trim();
                setSyncProgress(p => Math.min(p + 1, 95));
                setSyncStatus(cleaned);
                setCompsAnalysis({
                  reasoning: [...(useDashboardStore.getState().compsAnalysis.reasoning || []), cleaned]
                });
              } else if (event.type === 'intel') {
                const parsedIntel: { peers: Peer[] } = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                setCompsAnalysis({
                  intel: parsedIntel,
                  syncStatus: 'synchronized'
                });
                setSyncProgress(100);
                setSyncStatus("Neural Convergence Complete");
                setIsSyncing(false);
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
        setIsSyncing(false);
        setSyncStatus("Sync Failed");
      }
    };
    if (compsAnalysis.syncStatus === 'active') startSync();
  }, [ticker, context, compsAnalysis.syncStatus, setCompsAnalysis]);

  const handleSearch = () => {
    if (ticker.trim()) setCompsAnalysis({ syncStatus: 'active' });
  };

  const togglePeerSelection = (t: string) => {
    setSelectedPeers(prev => prev.includes(t) ? prev.filter(p => p !== t) : [...prev, t].slice(-2));
  };

  const handleSync = () => setCompsAnalysis({ syncStatus: 'active' });

  return (
    <div className="w-full h-full bg-[#050608]">
      <AnimatePresence mode="wait">
        {compsAnalysis.syncStatus === 'idle' && (
          <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <MissionBriefing
              ticker={ticker}
              setTicker={setTicker}
              context={context}
              setContext={setContext}
              handleSearch={handleSearch}
            />
          </motion.div>
        )}
        {compsAnalysis.syncStatus === 'active' && (
          <motion.div key="active" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <NeuralSyncOverlay
              ticker={ticker}
              context={context}
              syncProgress={syncProgress}
              syncStatus={syncStatus}
              reasoning={compsAnalysis.reasoning || []}
            />
          </motion.div>
        )}
        {compsAnalysis.syncStatus === 'synchronized' && (
          <motion.div key="arena" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}>
            <CompsArena
              ticker={ticker}
              intelPeers={compsAnalysis.intel?.peers || null}
              selectedPeers={selectedPeers}
              togglePeerSelection={togglePeerSelection}
              setShowTopology={setShowTopology}
              setShowDeepDive={setShowDeepDive}
              setShowDiff={setShowDiff}
              setSyncStatus={(status) => setCompsAnalysis({ syncStatus: status })}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <DeepDiveModal
        showDeepDive={showDeepDive}
        setShowDeepDive={setShowDeepDive}
        selectedPeers={selectedPeers}
        intelPeers={compsAnalysis.intel?.peers || null}
        context={context}
        handleSync={handleSync}
        isSyncing={isSyncing}
      />

      <AnimatePresence>
        {showTopology && <WorkflowTopologyOverlay onClose={() => setShowTopology(false)} />}
      </AnimatePresence>

      <AnimatePresence>
        {showDiff && selectedPeers.length === 2 && (
          <HolographicDiffOverlay
            peerA={(compsAnalysis.intel?.peers || PEERS_MOCK).find((p: Peer) => p.ticker === selectedPeers[0])!}
            peerB={(compsAnalysis.intel?.peers || PEERS_MOCK).find((p: Peer) => p.ticker === selectedPeers[1])!}
            onClose={() => setShowDiff(false)}
          />
        )}
      </AnimatePresence>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.3); border-radius: 10px; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        .animate-float { animation: float 6s ease-in-out infinite; }
      `}</style>
    </div>
  );
};
