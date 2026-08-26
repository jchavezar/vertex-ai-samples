import React, { useState } from 'react';
import { ActiveModule } from './types';
import { Header } from './components/Header';
import { ExecutiveKpis } from './components/ExecutiveKpis';
import { VoiceAssistantModule } from './components/VoiceAssistantModule';
import { CreativeStudioModule } from './components/CreativeStudioModule';
import { AgentSwarmModule } from './components/AgentSwarmModule';
import { ShieldCheck, Cpu } from 'lucide-react';

export const App: React.FC = () => {
  const [activeModule, setActiveModule] = useState<ActiveModule>('voice');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between text-slate-900 selection:bg-blue-100">
      
      {/* Header with Navigation */}
      <Header
        activeModule={activeModule}
        onSelectModule={(mod) => setActiveModule(mod)}
      />

      {/* Global Executive Top Metrics */}
      <ExecutiveKpis />

      {/* Main Module Content */}
      <main className="flex-1 w-full pb-12">
        {activeModule === 'voice' && <VoiceAssistantModule />}
        {activeModule === 'creative' && <CreativeStudioModule />}
        {activeModule === 'swarm' && <AgentSwarmModule />}
      </main>

      {/* Executive Boardroom Footer */}
      <footer className="w-full bg-white border-t border-slate-200 py-6 px-6 shadow-inner">
        <div className="max-w-[1720px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs sm:text-sm text-slate-500 font-medium">
          <div className="flex items-center gap-3">
            <span className="font-black text-slate-800 tracking-wide">
              EBC EXECUTIVE AI SHOWCASE
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 text-slate-600">
              <Cpu className="w-4 h-4 text-blue-600" /> Google Cloud Vertex AI
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 font-bold text-xs">
              <ShieldCheck className="w-3.5 h-3.5" /> Protocolo Zero-Leak Activo
            </span>
            <span className="text-slate-400">
              Versión 1.0.0 • Pantalla Directiva 100"
            </span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;
