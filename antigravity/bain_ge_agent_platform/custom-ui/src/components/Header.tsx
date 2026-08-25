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
    <header className="w-full bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-6 py-3 flex flex-wrap items-center justify-between font-sans flex-shrink-0 gap-4 shadow-sm">
      {/* Left: Bain & Company Brand + Live Diligence Context */}
      <div className="flex flex-wrap items-center gap-6 flex-1 min-w-[300px]">
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-2.5">
            <span className="font-extrabold text-base sm:text-lg tracking-tight text-slate-900 uppercase">
              BAIN & COMPANY
            </span>
            <span className="text-xs font-mono font-medium text-slate-400">
              / GEMINI ENTERPRISE
            </span>
            <span className="text-[10px] font-mono bg-slate-900 text-white px-2 py-0.5 font-bold tracking-wider rounded-md">
              LIVE DILIGENCE
            </span>
          </div>
          <span className="text-[11px] font-medium text-slate-500 tracking-wide truncate">
            MERIDIAN TECHNOLOGIES (MRDN) • M&A ADVISORY ENGINE
          </span>
        </div>

        {/* Live Financial Ticker Summary Card */}
        <div className="hidden lg:flex items-center gap-6 border-l border-slate-200 pl-6 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <div className="flex items-baseline gap-1">
                <span className="text-[11px] font-mono text-slate-400 font-semibold">USD</span>
                <span className="font-bold text-xl tracking-tight text-slate-900 font-mono">207.32</span>
              </div>
            </div>
            <span className="text-[11px] font-mono font-semibold text-rose-600 bg-rose-50 border border-rose-200/80 px-2 py-0.5 rounded-full flex items-center gap-0.5">
              ▼ -0.89%
            </span>
          </div>

          <div className="flex flex-col border-l border-slate-200 pl-6">
            <span className="text-[10px] font-mono text-slate-400 font-semibold uppercase tracking-wider">MARKET CAP</span>
            <span className="font-bold text-sm text-slate-800 font-mono mt-0.5">7.76B</span>
          </div>

          <div className="flex flex-col border-l border-slate-200 pl-6">
            <span className="text-[10px] font-mono text-slate-400 font-semibold uppercase tracking-wider">P/E RATIO</span>
            <span className="font-bold text-sm text-slate-800 font-mono mt-0.5">13.2</span>
          </div>
        </div>
      </div>

      {/* Right: Model Selection, ADC Proxy, Entra Auth, and Settings */}
      <div className="flex flex-wrap items-center gap-3 flex-shrink-0">
        {/* Model Selection Dropdown */}
        <div className="flex items-center gap-2 border border-slate-200 bg-slate-50/80 hover:bg-slate-100/80 transition-colors px-3 py-1.5 shadow-sm rounded-xl">
          <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
          <span className="text-[10px] font-mono text-slate-500 uppercase font-bold hidden sm:inline">MODEL:</span>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-transparent text-xs font-mono font-semibold text-slate-800 focus:outline-none cursor-pointer pl-0.5 truncate max-w-[180px] sm:max-w-none"
          >
            <option value="Gemini 3.0 Flash (Global)">Gemini 3.0 Flash (Global)</option>
            <option value="Gemini 2.5 Flash">Gemini 2.5 Flash</option>
            <option value="Gemini 2.5 Pro">Gemini 2.5 Pro</option>
            <option value="Gemini 3.0 Pro (Global)">Gemini 3.0 Pro (Global)</option>
          </select>
        </div>

        {/* ADC PROXY Status Badge */}
        <div 
          className="flex items-center gap-2 bg-slate-900 text-white px-3.5 py-1.5 text-xs font-mono font-medium tracking-wider cursor-help shadow-sm rounded-xl"
          title="ADC Proxy Active: Forwarding /api traffic to Vertex AI Agent Runtime in us-central1 via Local Google Cloud credentials"
        >
          <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          ADC PROXY
        </div>

        {/* Entra ID Microsoft Auth Button */}
        <button 
          type="button"
          onClick={() => setShowAuthDrawer(true)}
          className="flex items-center gap-2 bg-slate-50 hover:bg-slate-100 border border-slate-200/90 px-3.5 py-1.5 text-xs font-sans font-medium text-slate-800 transition-all cursor-pointer shadow-sm rounded-xl"
          title="View Two-Pillar Enterprise Auth Configuration"
        >
          <div className="grid grid-cols-2 gap-0.5 w-3.5 h-3.5 flex-shrink-0">
            <div className="bg-[#f25022]" />
            <div className="bg-[#7fba00]" />
            <div className="bg-[#00a4ef]" />
            <div className="bg-[#ffb900]" />
          </div>
          <span className="font-semibold text-slate-800 truncate max-w-[140px] sm:max-w-none">
            {entraToken ? (accountName || 'Bain Partner') : 'Sign in with Microsoft'}
          </span>
          {entraToken && <span className="w-2 h-2 bg-emerald-500 rounded-full flex-shrink-0" />}
        </button>

        {/* Technical Flow / Settings Gear Overlay Modal Button */}
        <button 
          type="button"
          onClick={() => setShowAuthDrawer(true)}
          className="bg-slate-50 hover:bg-slate-100 border border-slate-200/90 p-2 text-slate-500 hover:text-slate-900 transition-colors cursor-pointer shadow-sm flex-shrink-0 rounded-xl"
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
