import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { SplitViewToggle } from './components/SplitViewToggle';
import { LegacyEnterpriseView } from './components/LegacyEnterpriseView';
import { AgentNativeCanvas } from './components/AgentNativeCanvas';
import { RefactorPipelineModal } from './components/RefactorPipelineModal';

export function App() {
  const [currentView, setCurrentView] = useState<'legacy' | 'refactor' | 'agent'>('legacy');
  const [refactorModalOpen, setRefactorModalOpen] = useState(false);
  const [latencyMs, setLatencyMs] = useState(1400);

  const handleTriggerRefactor = () => {
    setRefactorModalOpen(true);
  };

  const handleRefactorComplete = () => {
    setCurrentView('agent');
    setLatencyMs(45);
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
      {/* Top EBC Navigation */}
      <Navbar
        currentView={currentView}
        onViewChange={setCurrentView}
        onOpenRefactorModal={handleTriggerRefactor}
        latencyMs={latencyMs}
      />

      {/* Split/Timeline Navigation */}
      <SplitViewToggle
        currentView={currentView}
        onViewChange={setCurrentView}
        onOpenRefactorModal={handleTriggerRefactor}
      />

      {/* Main View Area */}
      <main className="flex-1 pb-16">
        {currentView === 'legacy' ? (
          <LegacyEnterpriseView
            onUpdateLatency={setLatencyMs}
            onTriggerRefactor={handleTriggerRefactor}
          />
        ) : (
          <AgentNativeCanvas onUpdateLatency={setLatencyMs} />
        )}
      </main>

      {/* Refactor Pipeline Modal */}
      <RefactorPipelineModal
        isOpen={refactorModalOpen}
        onClose={() => setRefactorModalOpen(false)}
        onCompleteAndSwitchView={handleRefactorComplete}
      />
    </div>
  );
}

export default App;
