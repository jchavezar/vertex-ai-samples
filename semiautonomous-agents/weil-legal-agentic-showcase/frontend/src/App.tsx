import React, { useState } from 'react';
import { 
  Presentation, 
  Cpu, 
  Terminal, 
  Layers, 
  Database, 
  ShieldCheck, 
  Sparkles,
  ExternalLink,
  ChevronRight,
  Code2,
  Tv
} from 'lucide-react';
import { SlidesDeckView } from './components/SlidesDeckView';
import { ADKMultiAgentView } from './components/ADKMultiAgentView';
import { AntigravitySandboxView } from './components/AntigravitySandboxView';
import { PrivacyProLegoView } from './components/PrivacyProLegoView';
import { LegalVaultMCPView } from './components/LegalVaultMCPView';
import { Constellation3DView } from './components/Constellation3DView';
import { CodeSnippetOverlayModal } from './components/CodeSnippetOverlayModal';

export function App() {
  const [activeTab, setActiveTab] = useState<'slides' | 'adk' | 'antigravity' | 'privacy_pro' | 'vault' | 'constellation'>('slides');
  const [injectedPrompt, setInjectedPrompt] = useState<string>('');
  const [showGlobalCodeModal, setShowGlobalCodeModal] = useState<boolean>(false);
  const [isBoardroomMode, setIsBoardroomMode] = useState<boolean>(false);

  const handleNavigateFromSlide = (targetTab: string, prompt?: string) => {
    if (prompt) {
      setInjectedPrompt(prompt);
    }
    setActiveTab(targetTab as any);
  };

  return (
    <div className={`min-h-screen max-w-full overflow-x-hidden flex flex-col bg-slate-50 text-slate-800 font-sans ${isBoardroomMode ? 'text-base' : ''}`}>
      {/* Top Executive Navigation Bar - Responsive & Sticky */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 py-2.5 flex items-center justify-between gap-3 shadow-xs shrink-0 max-w-full">
        {/* Brand & Client Identification */}
        <div className="flex items-center gap-3 shrink-0">
          <span className="w-2 h-7 bg-blue-700 rounded-full shrink-0"></span>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs sm:text-sm font-bold text-slate-900 font-mono tracking-wider uppercase whitespace-nowrap">
                WEIL
              </span>
              <span className="text-xs text-slate-300 font-mono">/</span>
              <span className="text-xs text-blue-600 font-semibold whitespace-nowrap hidden sm:inline">
                Google Cloud AI
              </span>
            </div>
            <h1 className="text-xs font-bold text-slate-700 tracking-tight whitespace-nowrap hidden lg:block">
              Legal-Tech Platform
            </h1>
          </div>
        </div>

        {/* Center Tabs Navigation */}
        <nav className="flex items-center gap-1 bg-slate-100/90 p-1 rounded-xl border border-slate-200/80 shrink-0">
          <button
            onClick={() => setActiveTab('slides')}
            className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs transition cursor-pointer ${
              activeTab === 'slides' 
                ? 'bg-white text-slate-950 shadow-xs border border-slate-200/90 font-bold' 
                : 'text-slate-600 hover:text-slate-900 font-medium'
            }`}
          >
            <Presentation className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span className="whitespace-nowrap"><span className="hidden md:inline">Presentation </span>Deck</span>
          </button>

          <button
            onClick={() => setActiveTab('adk')}
            className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs transition cursor-pointer ${
              activeTab === 'adk' 
                ? 'bg-white text-slate-950 shadow-xs border border-slate-200/90 font-bold' 
                : 'text-slate-600 hover:text-slate-900 font-medium'
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span className="whitespace-nowrap">ADK Team</span>
          </button>

          <button
            onClick={() => setActiveTab('antigravity')}
            className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs transition cursor-pointer ${
              activeTab === 'antigravity' 
                ? 'bg-white text-slate-950 shadow-xs border border-slate-200/90 font-bold' 
                : 'text-slate-600 hover:text-slate-900 font-medium'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
            <span className="whitespace-nowrap">Antigravity</span>
          </button>

          <button
            onClick={() => setActiveTab('privacy_pro')}
            className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs transition cursor-pointer ${
              activeTab === 'privacy_pro' 
                ? 'bg-white text-slate-950 shadow-xs border border-slate-200/90 font-bold' 
                : 'text-slate-600 hover:text-slate-900 font-medium'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span className="whitespace-nowrap">Privacy Legos</span>
          </button>

          <button
            onClick={() => setActiveTab('vault')}
            className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs transition cursor-pointer ${
              activeTab === 'vault' 
                ? 'bg-white text-slate-950 shadow-xs border border-slate-200/90 font-bold' 
                : 'text-slate-600 hover:text-slate-900 font-medium'
            }`}
          >
            <Database className="w-3.5 h-3.5 text-amber-600 shrink-0" />
            <span className="whitespace-nowrap">Legal Vault</span>
          </button>

          <button
            onClick={() => setActiveTab('constellation')}
            className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs transition cursor-pointer ${
              activeTab === 'constellation' 
                ? 'bg-purple-900 text-white shadow-xs border border-purple-800 font-bold' 
                : 'text-purple-700 hover:text-purple-900 hover:bg-purple-50 font-semibold'
            }`}
          >
            <Sparkles className={`w-3.5 h-3.5 shrink-0 ${activeTab === 'constellation' ? 'text-amber-300' : 'text-purple-600'}`} />
            <span className="whitespace-nowrap font-bold">3D Constellation</span>
          </button>
        </nav>

        {/* Right Controls: Code Inspector, Boardroom Toggle & Session Lead */}
        <div className="flex items-center gap-2 shrink-0 border-l border-slate-200/80 pl-3">
          {/* Universal Code Snippet Overlay Button */}
          <button
            onClick={() => setShowGlobalCodeModal(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-amber-300 border border-slate-700 text-xs font-semibold transition cursor-pointer shadow-2xs hover:shadow-xs"
            title="Inspect formatted Python / ADK code overlay"
          >
            <Code2 className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span className="hidden xl:inline">Inspect Code</span>
          </button>

          {/* 100-inch Boardroom Display Mode Toggle */}
          <button
            onClick={() => setIsBoardroomMode(!isBoardroomMode)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer border ${
              isBoardroomMode
                ? 'bg-amber-500 text-slate-950 border-amber-600 font-bold shadow-xs'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
            }`}
            title="Toggle 100-inch Boardroom Screen Scaler"
          >
            <Tv className="w-3.5 h-3.5 shrink-0" />
            <span className="hidden xl:inline">100" Display</span>
          </button>

          {/* Session Lead Badge */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200 text-right">
            <div className="hidden 2xl:block">
              <p className="text-[9px] text-slate-400 font-mono tracking-wider uppercase font-semibold">LEAD</p>
              <p className="text-xs font-bold text-slate-800 whitespace-nowrap">Jesus Chavez</p>
            </div>
            <div 
              className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-700 flex items-center justify-center text-xs font-bold text-white shadow-xs border border-white/40 shrink-0"
              title="Session Lead: Jesus Chavez • Google Cloud AI"
            >
              JC
            </div>
          </div>
        </div>
      </header>

      {/* Main Viewport Container */}
      <main className={`flex-1 w-full mx-auto ${activeTab === 'constellation' ? 'p-2 sm:p-4 max-w-[1920px] flex flex-col' : 'max-w-[1680px] p-4 sm:p-6 lg:p-8'} bg-slate-50`}>
        {activeTab === 'slides' && (
          <SlidesDeckView onNavigateToDemo={handleNavigateFromSlide} />
        )}
        {activeTab === 'adk' && (
          <ADKMultiAgentView initialPrompt={injectedPrompt} />
        )}
        {activeTab === 'antigravity' && (
          <AntigravitySandboxView initialPrompt={injectedPrompt} isBoardroomMode={isBoardroomMode} />
        )}
        {activeTab === 'privacy_pro' && (
          <PrivacyProLegoView />
        )}
        {activeTab === 'vault' && (
          <LegalVaultMCPView />
        )}
        {activeTab === 'constellation' && (
          <Constellation3DView />
        )}
      </main>

      {/* Persistent Security & Protocol Footer */}
      <footer className="bg-white border-t border-slate-200/80 px-4 sm:px-8 py-2 flex items-center justify-between text-xs text-slate-500 shrink-0 flex-wrap gap-2">
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <span className="flex items-center gap-1.5 text-slate-800 font-bold bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            Zero-Leak Protocol Enforced
          </span>
          <span className="text-slate-300 hidden md:inline">•</span>
          <span className="font-medium hidden md:inline">Zero Data Retention</span>
          <span className="text-slate-300 hidden lg:inline">•</span>
          <span className="font-medium hidden lg:inline">VPC-SC Air-Gapped MicroVM Execution</span>
        </div>

        <div className="flex items-center gap-2 sm:gap-3 font-medium">
          <span className="hidden sm:inline">Weil, Gotshal & Manges LLP</span>
          <span className="text-slate-300 hidden sm:inline">•</span>
          <span className="font-mono text-slate-500 font-bold">September 9, 2026</span>
        </div>
      </footer>

      {/* Universal Code Modal */}
      <CodeSnippetOverlayModal
        isOpen={showGlobalCodeModal}
        onClose={() => setShowGlobalCodeModal(false)}
        activeClaim={45.0}
        initialFileName="dispute_monte_carlo.py"
        isBoardroomMode={isBoardroomMode}
      />
    </div>
  );
}

export default App;
