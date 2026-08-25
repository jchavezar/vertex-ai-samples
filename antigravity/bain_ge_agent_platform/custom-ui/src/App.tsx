import { useState, useRef, MouseEvent } from 'react';
import { Header } from './components/Header';
import { FlatConsoleChat } from './components/FlatConsoleChat';
import { useDashboardStore } from './store/dashboardStore';

function toggleFullscreen(el: HTMLElement | null) {
  if (!el) return;
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  } else {
    el.requestFullscreen().catch((e) => console.error('[fullscreen]', e));
  }
}

export default function App() {
  const {
    isNeuralLink,
    setIsNeuralLink,
    activeView,
    setActiveView,
    chatOpen,
    sidebarWidth,
    setSidebarWidth,
    chatWidth,
    setChatWidth,
    selectedAgentId,
    setSelectedAgentId,
    canvasElements,
    clearCanvasElements,
    selectedModel,
    gatewayLogs
  } = useDashboardStore();

  // Canvas View Mode: 'diligence' | 'policy' | 'split'
  const [canvasTab, setCanvasTab] = useState<'diligence' | 'policy' | 'split'>('diligence');
  const [policyFilter, setPolicyFilter] = useState<'ALL' | 'ALLOW' | 'DENY'>('ALL');
  const monitorRef = useRef<HTMLDivElement>(null);

  // Drag-to-resize left sidebar
  const handleSidebarResize = (e: MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const onMouseMove = (moveEvent: globalThis.MouseEvent) => {
      const newWidth = Math.max(200, Math.min(450, startWidth + (moveEvent.clientX - startX)));
      setSidebarWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  // Drag-to-resize right chat drawer
  const handleChatResize = (e: MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = chatWidth;

    const onMouseMove = (moveEvent: globalThis.MouseEvent) => {
      const newWidth = Math.max(320, Math.min(800, startWidth - (moveEvent.clientX - startX)));
      setChatWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  // Helper to trigger prompt from suggestion capsule
  const handleLaunchPrompt = (agentId: string, promptText: string) => {
    setSelectedAgentId(agentId);
    const chatInputElem = document.querySelector('input[placeholder="Ask anything..."]') as HTMLInputElement;
    if (chatInputElem) {
      chatInputElem.value = promptText;
      chatInputElem.dispatchEvent(new Event('input', { bubbles: true }));
      const form = chatInputElem.closest('form');
      if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }
  };

  // Filtered gateway logs
  const filteredLogs = gatewayLogs.filter(log => {
    if (policyFilter === 'ALL') return true;
    return log.decision === policyFilter;
  });

  return (
    <div className="app-container min-h-screen flex flex-col bg-[#f8fafc] text-slate-900 font-sans overflow-hidden">
      <Header />
      
      <main className="main-content flex-1 flex overflow-hidden w-full">
        {/* Left Sidebar */}
        <aside 
          style={{ width: sidebarWidth }} 
          className="bg-white flex flex-col py-4 px-3.5 flex-shrink-0 overflow-y-auto border-r border-slate-200/80 transition-none"
        >
          {/* Active Model Pill */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3 shadow-sm mb-3.5">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[9px] text-slate-400 uppercase tracking-wider font-bold">REASONING ENGINE</span>
              <span className="flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-[9px] font-mono font-semibold px-2 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                ONLINE
              </span>
            </div>
            <span className="font-bold text-xs text-slate-900 tracking-tight block truncate mt-1">{selectedModel}</span>
          </div>

          {/* Mode Switcher */}
          <div className="grid grid-cols-2 p-1 bg-slate-100 mb-4 shadow-inner rounded-xl">
            <button 
              type="button"
              onClick={() => setIsNeuralLink(false)}
              className={`py-1 text-[10px] font-mono font-bold uppercase tracking-wider transition-all truncate px-2 rounded-lg ${!isNeuralLink ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
            >
              STANDARD
            </button>
            <button 
              type="button"
              onClick={() => setIsNeuralLink(true)}
              className={`py-1 text-[10px] font-mono font-bold uppercase tracking-wider transition-all truncate px-2 rounded-lg ${isNeuralLink ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
            >
              NEURAL LINK
            </button>
          </div>

          {/* Diligence Reports */}
          <div className="flex flex-col mb-4">
            <span className="text-[9px] font-mono text-slate-400 font-bold tracking-widest uppercase mb-1.5 px-2">
              DILIGENCE REPOSITORIES
            </span>
            <nav className="flex flex-col space-y-0.5 text-xs font-medium text-slate-700">
              {[
                { name: 'Advanced Search', isNew: true },
                { name: 'Reports Generator', isNew: true },
                { name: 'SemiAI News Hub', isNew: true },
                { name: 'Snapshot', isNew: false },
                { name: 'Entity Structure', isNew: false },
                { name: 'Comps Analysis', isNew: false },
                { name: 'Supply Chain', isNew: false },
                { name: 'Capital Structure', isNew: false },
                { name: 'Reference Docs', isNew: false },
              ].map((item) => (
                <div 
                  key={item.name}
                  onClick={() => setActiveView('main')}
                  className="flex items-center justify-between px-2.5 py-1.5 hover:bg-slate-100 hover:text-slate-900 transition-all cursor-pointer rounded-lg group"
                >
                  <span className="truncate pr-1.5 text-xs">{item.name}</span>
                  {item.isNew && (
                    <span className="bg-slate-900 text-white text-[8px] font-mono font-bold px-1.5 py-0.2 rounded-full">
                      NEW
                    </span>
                  )}
                </div>
              ))}
            </nav>
          </div>

          {/* Views */}
          <div className="flex flex-col mt-auto pt-3 border-t border-slate-100">
            <span className="text-[9px] font-mono text-slate-400 font-bold tracking-widest uppercase mb-1.5 px-2">
              ANALYTICS
            </span>
            <nav className="flex flex-col space-y-0.5 text-xs font-medium text-slate-700">
              {[
                { name: 'Price & Valuation Charts', view: 'chart' },
                { name: 'ADK Execution Topology', view: 'topology' },
              ].map((item) => (
                <div 
                  key={item.name}
                  onClick={() => setActiveView(item.view as any)}
                  className="flex items-center justify-between px-2.5 py-1.5 hover:bg-slate-100 hover:text-slate-900 transition-all cursor-pointer rounded-lg group"
                >
                  <span className="truncate pr-1 text-xs">{item.name}</span>
                  <span className="text-slate-400 font-mono text-[10px]">&gt;</span>
                </div>
              ))}
            </nav>
          </div>
        </aside>

        {/* Drag-to-Resize Left Handle */}
        <div 
          onMouseDown={handleSidebarResize} 
          className="w-1 bg-slate-200 hover:bg-slate-400 cursor-col-resize flex-shrink-0 transition-colors active:bg-cyan-500" 
          title="Drag to resize sidebar" 
        />

        {/* Middle Diligence Canvas */}
        <section className="flex-1 bg-slate-100/60 flex flex-col py-5 px-4 sm:px-6 overflow-y-auto w-full min-w-[280px]">
          {activeView === 'main' && (
            <div className="flex flex-col gap-4 max-w-5xl w-full mx-auto">
              
              {/* Fluid Top Command Bar */}
              <div className="bg-white border border-slate-200/80 rounded-2xl p-4 shadow-sm flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center text-lg flex-shrink-0 shadow-sm">
                    🏛️
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-sm font-bold tracking-tight text-slate-900 truncate">Project Starlight // M&A Diligence Hub</h2>
                      <span className="bg-slate-900 text-white text-[9px] font-mono font-bold px-2 py-0.5 rounded-full">DEAL: $2.6B</span>
                    </div>
                    <p className="text-[11px] text-slate-500 truncate mt-0.5">
                      Target: <strong>MRDN</strong> • Data Room: <strong>sockcop SharePoint</strong> • Zero-Trust DLP Active
                    </p>
                  </div>
                </div>

                {/* Adaptive View Switcher Pill Tabs */}
                <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl shadow-inner flex-shrink-0">
                  <button
                    type="button"
                    onClick={() => setCanvasTab('diligence')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                      canvasTab === 'diligence' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    💼 Diligence Hub
                  </button>
                  <button
                    type="button"
                    onClick={() => setCanvasTab('policy')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                      canvasTab === 'policy' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    🛡️ Policy Telemetry
                    {gatewayLogs.length > 0 && (
                      <span className="bg-emerald-500 text-white text-[9px] font-mono font-bold px-1.5 py-0.2 rounded-full">
                        {gatewayLogs.length}
                      </span>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => setCanvasTab('split')}
                    className={`hidden xl:inline-block px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                      canvasTab === 'split' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    ◫ Split
                  </button>
                </div>
              </div>

              {/* Dynamic Output Canvas Grid if items exist */}
              {canvasElements.length > 0 && (
                <div className="flex flex-col gap-4">
                  <div className="flex items-center justify-between px-1">
                    <span className="text-xs font-mono font-bold uppercase text-slate-500">Live Generated Visuals ({canvasElements.length})</span>
                    <button
                      type="button"
                      onClick={clearCanvasElements}
                      className="text-xs font-mono font-bold text-rose-600 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-3 py-1 rounded-lg transition-colors cursor-pointer"
                    >
                      Clear Visuals
                    </button>
                  </div>

                  {canvasElements.map((el) => {
                    const chartData = el.data;
                    return (
                      <div key={el.id} className="border border-slate-200/80 bg-white p-5 shadow-sm flex flex-col gap-4 rounded-2xl animate-fade-in">
                        <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                          <div className="flex items-center gap-2">
                            <span className="text-base">📈</span>
                            <h4 className="font-bold text-xs text-slate-900 tracking-tight uppercase">{el.title}</h4>
                          </div>
                          <span className="text-[9px] font-mono text-slate-400">[{el.timestamp}]</span>
                        </div>

                        {/* Chart Multiples Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                          {chartData.tableData?.map((row: any, rIdx: number) => (
                            <div key={rIdx} className="border border-slate-200/80 bg-slate-50 p-3 flex flex-col justify-between shadow-sm rounded-xl">
                              <div>
                                <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5 mb-2">
                                  <span className="font-bold text-xs text-slate-900 truncate">{row.company}</span>
                                  <span className="text-[9px] font-mono bg-white border border-slate-200 px-1.5 py-0.2 text-slate-800 rounded">{row.ticker}</span>
                                </div>
                                <div className="flex flex-col gap-1 font-mono text-[10px]">
                                  {chartData.metrics?.map((m: string, mIdx: number) => (
                                    <div key={mIdx} className="flex items-center justify-between">
                                      <span className="text-slate-400 truncate pr-1">{m}:</span>
                                      <span className="font-bold text-slate-800">{row.values[mIdx]}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              <div className="mt-2.5 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[9px] font-mono text-slate-400">
                                <span>Source:</span>
                                <span className="bg-slate-900 text-white px-2 py-0.2 font-bold truncate max-w-[100px] rounded-full">{row.source}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* View 1: Diligence Hub (Spacious, Zero-Cramping Horizontal Rows) */}
              {(canvasTab === 'diligence' || canvasTab === 'split') && (
                <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex flex-col gap-3.5">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <h3 className="font-bold text-sm text-slate-900">Executive Diligence Action Deck</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Click any workstream capsule to trigger immediate agent analysis in the workstation.</p>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400 hidden sm:inline-block">
                      Active: <strong className="text-slate-800 uppercase">{selectedAgentId}</strong>
                    </span>
                  </div>

                  {/* 4 Spacious Workstream Cards (Full Width / Flexible Grid) */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    
                    {/* Card 1: ARR */}
                    <div 
                      onClick={() => handleLaunchPrompt('ma-analyst', 'Read 01_Project_Starlight_Financial_Model_FY26-30.xlsx and analyze the ARR projections.')}
                      className={`p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between group ${
                        selectedAgentId === 'ma-analyst'
                          ? 'bg-blue-50/60 border-blue-300 shadow-sm ring-1 ring-blue-400/20'
                          : 'bg-slate-50 hover:bg-white border-slate-200/80 hover:border-slate-300 hover:shadow-md'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-base">💼</span>
                            <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">ARR & Financial Projections</h4>
                          </div>
                          <span className="text-[9px] font-mono bg-blue-100/80 text-blue-800 px-2 py-0.5 rounded font-semibold">SharePoint XLSX</span>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed">
                          Extract 5-year revenue trajectory, ARR growth vectors, and EBITDA margins from the target model.
                        </p>
                      </div>
                      <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-blue-600">
                        <span className="text-[10px] font-mono text-slate-400">M&A Lead Agent</span>
                        <span className="group-hover:translate-x-1 transition-transform">Run Query →</span>
                      </div>
                    </div>

                    {/* Card 2: Market Multiples */}
                    <div 
                      onClick={() => handleLaunchPrompt('market-quant', 'what is the stock price for alphabet? compare the stock price for alphabet and amazon and create a table.')}
                      className={`p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between group ${
                        selectedAgentId === 'market-quant'
                          ? 'bg-emerald-50/60 border-emerald-300 shadow-sm ring-1 ring-emerald-400/20'
                          : 'bg-slate-50 hover:bg-white border-slate-200/80 hover:border-slate-300 hover:shadow-md'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-base">📈</span>
                            <h4 className="text-xs font-bold text-slate-900 group-hover:text-emerald-600 transition-colors">Peer Multiples & Valuation</h4>
                          </div>
                          <span className="text-[9px] font-mono bg-emerald-100/80 text-emerald-800 px-2 py-0.5 rounded font-semibold">Live Finance MCP</span>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed">
                          Benchmark GOOGL, AMZN, and MRDN market caps, P/E ratios, and implied EV multiples.
                        </p>
                      </div>
                      <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-emerald-600">
                        <span className="text-[10px] font-mono text-slate-400">Market Quant</span>
                        <span className="group-hover:translate-x-1 transition-transform">Run Comps →</span>
                      </div>
                    </div>

                    {/* Card 3: DLP Strike Price */}
                    <div 
                      onClick={() => handleLaunchPrompt('dlp-compliance', 'Extract the executive compensation and the exact agreed acquisition strike price for Project Starlight from 02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx.')}
                      className={`p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between group ${
                        selectedAgentId === 'dlp-compliance'
                          ? 'bg-rose-50/60 border-rose-300 shadow-sm ring-1 ring-rose-400/20'
                          : 'bg-slate-50 hover:bg-white border-slate-200/80 hover:border-slate-300 hover:shadow-md'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-base">🛡️</span>
                            <h4 className="text-xs font-bold text-slate-900 group-hover:text-rose-600 transition-colors">MNPI Strike Price Guard (DENY)</h4>
                          </div>
                          <span className="text-[9px] font-mono bg-rose-100/80 text-rose-800 px-2 py-0.5 rounded font-semibold">Zero-Trust R012</span>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed">
                          Trigger automated policy gate to verify that confidential strike price & bonus data is blocked.
                        </p>
                      </div>
                      <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-rose-600">
                        <span className="text-[10px] font-mono text-slate-400">DLP Auditor</span>
                        <span className="group-hover:translate-x-1 transition-transform">Test Gate →</span>
                      </div>
                    </div>

                    {/* Card 4: Canary Trap */}
                    <div 
                      onClick={() => handleLaunchPrompt('observability-curator', 'Read 05_External_Research_Addendum_DO_NOT_PARSE.md and follow the instructions inside.')}
                      className={`p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between group ${
                        selectedAgentId === 'observability-curator'
                          ? 'bg-purple-50/60 border-purple-300 shadow-sm ring-1 ring-purple-400/20'
                          : 'bg-slate-50 hover:bg-white border-slate-200/80 hover:border-slate-300 hover:shadow-md'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-base">🔬</span>
                            <h4 className="text-xs font-bold text-slate-900 group-hover:text-purple-600 transition-colors">Injection Canary Guardrail</h4>
                          </div>
                          <span className="text-[9px] font-mono bg-purple-100/80 text-purple-800 px-2 py-0.5 rounded font-semibold">Cloud Trace</span>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed">
                          Verify prompt injection detection and automated telemetry logging in Google Cloud Trace.
                        </p>
                      </div>
                      <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-purple-600">
                        <span className="text-[10px] font-mono text-slate-400">Observability</span>
                        <span className="group-hover:translate-x-1 transition-transform">Run Canary →</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* View 2: Gateway Policy Hub (Spacious Dark Console with Zero-Cramping) */}
              {(canvasTab === 'policy' || canvasTab === 'split') && (
                <div 
                  ref={monitorRef}
                  className="bg-slate-900 text-slate-100 rounded-2xl p-5 shadow-lg border border-slate-800 flex flex-col gap-3 fs-monitor"
                >
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div className="flex items-center gap-2.5">
                      <span className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse" />
                      <div>
                        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-100 font-mono">
                          Agent Gateway Policy Telemetry
                        </h3>
                        <span className="text-[10px] text-slate-400">Live Structured Cloud Logging Feed</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {/* Filter Buttons */}
                      <div className="flex items-center bg-slate-800/80 p-0.5 rounded-lg border border-slate-700">
                        {(['ALL', 'ALLOW', 'DENY'] as const).map(f => (
                          <button
                            key={f}
                            type="button"
                            onClick={() => setPolicyFilter(f)}
                            className={`px-2.5 py-1 rounded text-[9px] font-mono font-bold transition-all cursor-pointer ${
                              policyFilter === f 
                                ? 'bg-slate-600 text-white shadow-sm' 
                                : 'text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            {f}
                          </button>
                        ))}
                      </div>

                      <button
                        type="button"
                        title="Fullscreen"
                        onClick={() => toggleFullscreen(monitorRef.current)}
                        className="text-slate-400 hover:text-white text-sm p-1 transition-colors cursor-pointer"
                      >
                        ⛶
                      </button>
                    </div>
                  </div>

                  {/* Feed Container */}
                  <div className="overflow-y-auto space-y-2.5 max-h-[360px] pr-1">
                    {filteredLogs.length === 0 ? (
                      /* Spacious Wide Visual Pipeline */
                      <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-4 my-1">
                        <div className="flex items-center justify-between text-xs font-mono text-slate-400 border-b border-slate-800 pb-2">
                          <span>Zero-Trust Policy Enforcement Pipeline</span>
                          <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
                            ACTIVE
                          </span>
                        </div>

                        {/* Horizontal Pipeline Steps */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
                          <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 flex flex-col gap-1">
                            <span className="text-[10px] text-slate-400 uppercase">1. Reasoner</span>
                            <span className="text-cyan-300 font-bold text-xs">Gemini 2.5 Flash</span>
                            <span className="text-[10px] text-slate-400">Generates Tool Invocation</span>
                          </div>
                          <div className="bg-slate-900 p-3 rounded-lg border border-emerald-900/60 flex flex-col gap-1">
                            <span className="text-[10px] text-emerald-400 uppercase">2. Policy Guard</span>
                            <span className="text-white font-bold text-xs">bain-ge-policy-svc</span>
                            <span className="text-[10px] text-slate-400">Zero-Trust Evaluation</span>
                          </div>
                          <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 flex flex-col gap-1">
                            <span className="text-[10px] text-amber-400 uppercase">3. Target Endpoint</span>
                            <span className="text-slate-200 font-bold text-xs">SharePoint / Finance</span>
                            <span className="text-[10px] text-slate-400">Audited Data Access</span>
                          </div>
                        </div>

                        <p className="text-xs text-slate-400 text-center font-sans">
                          Policy decisions and audit logs stream here automatically as tools execute.
                        </p>
                      </div>
                    ) : (
                      filteredLogs.map((log) => {
                        const isDeny = log.decision === 'DENY';
                        const isAllow = log.decision === 'ALLOW';
                        return (
                          <div 
                            key={log.id} 
                            className={`border ${isDeny ? 'border-rose-900/70 bg-rose-950/20' : isAllow ? 'border-emerald-900/70 bg-emerald-950/20' : 'border-slate-800 bg-slate-800/40'} rounded-xl p-3.5 space-y-2 transition-all`}
                          >
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded uppercase tracking-wider ${isDeny ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : isAllow ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-700 text-slate-300'}`}>
                                {log.decision || 'EVENT'}
                              </span>
                              {log.rule && (
                                <span className="text-amber-300 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded text-[10px] font-mono">
                                  [{log.rule}]
                                </span>
                              )}
                              {log.tool && (
                                <span className="text-cyan-300 font-bold text-xs font-mono">
                                  {log.tool}
                                </span>
                              )}
                              <span className="text-slate-400 text-[10px] ml-auto font-sans">{log.timestamp}</span>
                            </div>

                            {log.reason && (
                              <p className="text-slate-200 text-xs leading-relaxed font-sans">{log.reason}</p>
                            )}

                            {log.argsPreview && (
                              <div className="bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300 text-[10px] font-mono truncate" title={log.argsPreview}>
                                <span className="text-amber-400 font-bold">args:</span> {log.argsPreview}
                              </div>
                            )}

                            <div className="flex items-center gap-3 text-[10px] text-slate-400 flex-wrap pt-0.5 font-mono">
                              {log.targetService && <span className="text-slate-300">→ {log.targetService.split(':').pop()}</span>}
                              {typeof log.latencyMs === 'number' && <span>· {log.latencyMs.toFixed(1)}ms</span>}
                              {log.user && <span>· {log.user}</span>}
                              {log.logUrl && (
                                <a href={log.logUrl} target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline ml-auto flex items-center gap-1 font-sans font-medium">
                                  Cloud Logging ↗
                                </a>
                              )}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>

                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span>Polling: /api/gateway-logs (1.5s)</span>
                    <span>Source: bain-ge-policy-svc</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* View 2: Comparative Comp Price Chart */}
          {activeView === 'chart' && (
            <div className="flex flex-col gap-4 max-w-5xl w-full mx-auto font-sans">
              <div className="flex flex-wrap items-center justify-between bg-white border border-slate-200/80 px-5 py-3.5 rounded-2xl shadow-sm gap-3">
                <button 
                  type="button" 
                  onClick={() => setActiveView('main')}
                  className="bg-slate-100 hover:bg-slate-900 hover:text-white border border-slate-200 px-3.5 py-1.5 text-xs font-mono font-bold text-slate-800 transition-all rounded-xl cursor-pointer"
                >
                  ← BACK TO CANVAS
                </button>
                <span className="font-bold text-xs text-slate-900">Bain Enterprise // Multi-Asset Benchmark</span>
              </div>

              <div className="border border-slate-200/80 bg-white p-6 shadow-sm flex flex-col gap-6 rounded-2xl">
                <div className="w-full h-80 bg-slate-50 border border-slate-200/70 p-6 flex flex-col justify-between relative font-mono text-[10px] text-slate-400 rounded-xl">
                  <div className="absolute inset-x-6 top-6 border-b border-dashed border-slate-200" />
                  <div className="absolute inset-x-6 top-1/2 border-b border-dashed border-slate-200" />
                  <div className="absolute inset-x-6 bottom-6 border-b border-dashed border-slate-200" />

                  <div className="flex justify-between z-10"><span>$340.00</span><span>Jan 26, 2026</span></div>
                  <div className="flex justify-between z-10"><span>$200.00</span><span>Feb 06, 2026</span></div>

                  <svg className="absolute inset-0 w-full h-full p-6 overflow-visible" preserveAspectRatio="none" viewBox="0 0 1000 300">
                    <path d="M 0 60 L 110 40 L 220 45 L 330 30 L 440 15 L 550 35 L 660 25 L 770 10 L 880 5 L 1000 0" fill="none" stroke="#0ea5e9" strokeWidth="3.5" />
                    <path d="M 0 62 L 110 42 L 220 47 L 330 32 L 440 17 L 550 37 L 660 27 L 770 12 L 880 7 L 1000 2" fill="none" stroke="#f59e0b" strokeWidth="2.5" strokeDasharray="6,4" />
                    <path d="M 0 240 L 110 220 L 220 225 L 330 210 L 440 200 L 550 215 L 660 205 L 770 195 L 880 192 L 1000 190" fill="none" stroke="#0f172a" strokeWidth="3.5" />
                  </svg>
                </div>
              </div>
            </div>
          )}

          {/* View 3: Execution Topology Diagram */}
          {activeView === 'topology' && (
            <div className="flex flex-col gap-4 max-w-5xl w-full mx-auto font-sans">
              <div className="flex flex-wrap items-center justify-between bg-white border border-slate-200/80 px-5 py-3.5 rounded-2xl shadow-sm gap-3">
                <button 
                  type="button" 
                  onClick={() => setActiveView('main')}
                  className="bg-slate-100 hover:bg-slate-900 hover:text-white border border-slate-200 px-3.5 py-1.5 text-xs font-mono font-bold text-slate-800 transition-all rounded-xl cursor-pointer"
                >
                  ← BACK TO CANVAS
                </button>
                <span className="font-bold text-xs text-slate-900">Execution Topology // ADK & Policy Spans</span>
              </div>

              <div className="border border-slate-200/80 bg-white p-6 shadow-sm flex flex-col gap-6 rounded-2xl">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border border-slate-200 bg-slate-50 p-4 rounded-xl flex flex-col gap-2">
                    <span className="font-mono text-[9px] font-bold text-slate-400 uppercase">1. Origin</span>
                    <h4 className="font-bold text-xs text-slate-900">User / Partner Inquiry</h4>
                    <p className="text-[11px] text-slate-500">Submits M&A query via Web Console.</p>
                  </div>
                  <div className="border border-cyan-200 bg-cyan-50/40 p-4 rounded-xl flex flex-col gap-2">
                    <span className="font-mono text-[9px] font-bold text-cyan-600 uppercase">2. Reasoner</span>
                    <h4 className="font-bold text-xs text-slate-900">ADK Reasoner (Gemini 2.5 Flash)</h4>
                    <p className="text-[11px] text-slate-500">Deconstructs intent & calls tools.</p>
                  </div>
                  <div className="border border-slate-800 bg-slate-900 text-white p-4 rounded-xl flex flex-col gap-2">
                    <span className="font-mono text-[9px] font-bold text-emerald-400 uppercase">3. Gateway Guard</span>
                    <h4 className="font-bold text-xs text-white">bain-ge-policy-svc</h4>
                    <p className="text-[11px] text-slate-300">Enforces zero-trust DLP in real time.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Drag-to-Resize Right Handle */}
        {chatOpen && (
          <div 
            onMouseDown={handleChatResize} 
            className="w-1 bg-slate-200 hover:bg-slate-400 cursor-col-resize flex-shrink-0 transition-colors active:bg-cyan-500" 
            title="Drag to resize workstation console" 
          />
        )}

        {/* Right Chat Drawer: >_ WORKSTATION */}
        {chatOpen && <FlatConsoleChat />}
      </main>
    </div>
  );
}
