import React from 'react';
import { useDashboardStore } from '../store/dashboardStore';

export function Header() {
  const { 
    entraToken, 
    accountName, 
    setShowAuthDrawer, 
    selectedModel, 
    setSelectedModel 
  } = useDashboardStore();

  return (
    <header className="w-full bg-[#faf9f6] border-b border-[#d8d6d0] px-6 py-3.5 flex flex-wrap items-center justify-between font-sans flex-shrink-0 gap-6">
      {/* Left: Ticker & Market Status */}
      <div className="flex flex-wrap items-center gap-8 flex-1 min-w-[320px]">
        <div className="flex flex-col gap-1 min-w-[280px]">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="font-bold text-lg sm:text-xl tracking-tight text-[#1a1a19] uppercase whitespace-nowrap">
              BAIN & COMPANY
            </span>
            <span className="text-xs font-mono text-[#7c7a75] whitespace-nowrap">
              // GEMINI ENTERPRISE AGENT PLATFORM
            </span>
            <span className="text-[10px] font-mono bg-[#1a1a19] text-[#faf9f6] px-2 py-0.5 font-bold whitespace-nowrap">
              LIVE DILIGENCE
            </span>
          </div>
          <span className="text-[11px] font-mono text-[#7c7a75] uppercase tracking-wider truncate">
            MERIDIAN TECHNOLOGIES (MRDN) • M&A ADVISORY ENGINE
          </span>
        </div>

        {/* Live Financial Ticker Summary */}
        <div className="flex items-center gap-6 sm:gap-8 border-l border-[#d8d6d0] pl-6 sm:pl-8 flex-wrap">
          <div className="flex flex-col">
            <div className="flex items-baseline gap-1.5">
              <span className="text-xs font-mono text-[#7c7a75]">USD</span>
              <span className="font-bold text-xl sm:text-2xl tracking-tight text-[#1a1a19] font-mono">207.32</span>
            </div>
            <span className="text-xs font-mono text-red-600 flex items-center gap-1 font-bold">
              ▼ -0.89%
            </span>
          </div>

          <div className="flex flex-col border-l border-[#d8d6d0] pl-6 sm:pl-8">
            <span className="text-[10px] font-mono text-[#7c7a75] uppercase tracking-wider">MARKET CAP</span>
            <span className="font-bold text-base sm:text-lg text-[#1a1a19] font-mono mt-0.5">7.76B</span>
          </div>

          <div className="flex flex-col border-l border-[#d8d6d0] pl-6 sm:pl-8">
            <span className="text-[10px] font-mono text-[#7c7a75] uppercase tracking-wider">P/E RATIO</span>
            <span className="font-bold text-base sm:text-lg text-[#1a1a19] font-mono mt-0.5">13.2</span>
          </div>
        </div>
      </div>

      {/* Right: Model Selection, ADC Proxy, Entra Auth, and Settings */}
      <div className="flex flex-wrap items-center gap-4 flex-shrink-0">
        {/* Model Selection Dropdown */}
        <div className="flex items-center gap-2 border border-[#d8d6d0] bg-[#f4f3ef] px-4 py-1.5 shadow-sm rounded-full">
          <span className="w-2 h-2 rounded-full bg-[#00c2cb] animate-pulse" />
          <span className="text-[10px] font-mono text-[#7c7a75] uppercase font-bold hidden sm:inline">MODEL:</span>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-transparent text-xs font-mono font-bold text-[#1a1a19] focus:outline-none cursor-pointer pl-1 truncate max-w-[180px] sm:max-w-none"
          >
            <option value="Gemini 3.0 Flash (Global)">Gemini 3.0 Flash (Global)</option>
            <option value="Gemini 2.5 Flash">Gemini 2.5 Flash</option>
            <option value="Gemini 2.5 Pro">Gemini 2.5 Pro</option>
            <option value="Gemini 3.0 Pro (Global)">Gemini 3.0 Pro (Global)</option>
          </select>
        </div>

        {/* ADC PROXY Status Badge */}
        <div 
          className="flex items-center gap-2 bg-[#1a1a19] text-[#faf9f6] px-3.5 py-1.5 text-xs font-mono font-bold tracking-wider cursor-help border border-[#1a1a19] hidden md:flex rounded-full"
          title="ADC Proxy Active: Forwarding /api traffic to Vertex AI Agent Runtime in us-central1 via Local Google Cloud credentials"
        >
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          ADC PROXY
        </div>

        {/* Entra ID Microsoft Auth Button */}
        <button 
          type="button"
          onClick={() => setShowAuthDrawer(true)}
          className="flex items-center gap-2.5 bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-1.5 text-xs font-sans font-medium text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer shadow-sm rounded-full"
          title="View Two-Pillar Enterprise Auth Configuration"
        >
          <div className="grid grid-cols-2 gap-0.5 w-3.5 h-3.5">
            <div className="bg-[#f25022]" />
            <div className="bg-[#7fba00]" />
            <div className="bg-[#00a4ef]" />
            <div className="bg-[#ffb900]" />
          </div>
          <span className="font-bold font-sans truncate max-w-[140px] sm:max-w-none">
            {entraToken ? (accountName || 'Bain Partner') : 'Sign in with Microsoft'}
          </span>
          {entraToken && <span className="w-1.5 h-1.5 bg-green-500 rounded-full flex-shrink-0" />}
        </button>

        {/* Technical Flow / Settings Gear Overlay Modal Button */}
        <button 
          type="button"
          onClick={() => setShowAuthDrawer(true)}
          className="bg-[#f4f3ef] border border-[#d8d6d0] p-2 text-[#7c7a75] hover:text-[#1a1a19] hover:bg-[#d8d6d0] transition-colors cursor-pointer shadow-sm flex-shrink-0 rounded-full"
          title="Open Technical Flow & Auth Settings Overlay"
        >
          <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </header>
  );
}
