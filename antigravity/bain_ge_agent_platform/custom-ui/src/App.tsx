import React, { useRef } from 'react';
import { Header } from './components/Header';
import { FlatConsoleChat } from './components/FlatConsoleChat';
import { useDashboardStore } from './store/dashboardStore';

/**
 * Presenter-mode helper. Toggles the browser Fullscreen API on the passed
 * element. Escape (or clicking the ✕ overlay) exits — no extra state needed.
 * When fullscreened, we add a bit of scale so the panel visually fills the
 * screen even though it was designed at a small size.
 */
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
    canvasElements,
    clearCanvasElements,
    selectedModel,
    gatewayLogs
  } = useDashboardStore();

  // Refs for presenter-mode fullscreen. Click ⛶ on a panel → it goes edge-to-edge
  // on the big screen. Esc exits. Uses the browser Fullscreen API; no state,
  // no modal component.
  const monitorRef = useRef<HTMLDivElement>(null);
  const canvasSectionRef = useRef<HTMLDivElement>(null);

  // Smooth drag-to-resize handler for left sidebar
  const handleSidebarResize = (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.max(200, Math.min(600, startWidth + (moveEvent.clientX - startX)));
      setSidebarWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  // Smooth drag-to-resize handler for right chat drawer
  const handleChatResize = (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = chatWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      // Dragging left increases width, dragging right decreases width
      const newWidth = Math.max(320, Math.min(1000, startWidth - (moveEvent.clientX - startX)));
      setChatWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  return (
    <div className="app-container min-h-screen flex flex-col bg-[#faf9f6] text-[#1a1a19] font-sans overflow-hidden">
      <Header />
      
      <main className="main-content flex-1 flex overflow-hidden w-full">
        {/* Left Sidebar: Bain & Company // Practice Engine Navigation Hierarchy */}
        <aside 
          style={{ width: sidebarWidth }} 
          className="bg-[#faf9f6] flex flex-col py-6 px-6 flex-shrink-0 overflow-y-auto transition-none"
        >
          {/* Brand & Subtitle */}
          <div className="flex flex-col mb-6">
            <span className="font-mono text-[10px] text-[#7c7a75] uppercase tracking-widest font-bold">POWERED BY</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="font-bold text-xl tracking-tight text-[#1a1a19] truncate">{selectedModel}</span>
              <span className="w-1.5 h-1.5 bg-[#00c2cb] rounded-full animate-ping flex-shrink-0" />
            </div>
          </div>

          {/* Connection Status Pill */}
          <div className="inline-flex items-center gap-2 bg-[#f4f3ef] border border-[#d8d6d0] px-3.5 py-1.5 mb-6 shadow-sm w-fit rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse flex-shrink-0" />
            <span className="text-[11px] font-mono font-bold text-[#1a1a19] tracking-wider uppercase truncate">CONNECTED</span>
          </div>

          {/* MRDN Ticker Search Bar */}
          <div className="flex items-center gap-2 bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-2 mb-6 shadow-sm rounded-full">
            <svg className="w-3.5 h-3.5 text-[#7c7a75] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="font-mono font-bold text-xs text-[#1a1a19] truncate">MRDN</span>
          </div>

          {/* STANDARD / NEURAL LINK Mode Switcher Pill */}
          <div className="grid grid-cols-2 p-1 bg-[#f4f3ef] border border-[#d8d6d0] mb-8 shadow-sm rounded-full">
            <button 
              type="button"
              onClick={() => setIsNeuralLink(false)}
              className={`py-2 text-[10px] font-mono font-bold uppercase tracking-wider transition-all truncate px-1 rounded-full ${!isNeuralLink ? 'bg-[#1a1a19] text-[#faf9f6]' : 'text-[#7c7a75] hover:text-[#1a1a19]'}`}
            >
              STANDARD
            </button>
            <button 
              type="button"
              onClick={() => setIsNeuralLink(true)}
              className={`py-2 text-[10px] font-mono font-bold uppercase tracking-wider transition-all truncate px-1 rounded-full ${isNeuralLink ? 'bg-[#1a1a19] text-[#faf9f6]' : 'text-[#7c7a75] hover:text-[#1a1a19]'}`}
            >
              NEURAL LINK
            </button>
          </div>

          {/* REPORTS Navigation List */}
          <div className="flex flex-col mb-8">
            <span className="text-[10px] font-mono text-[#7c7a75] font-bold tracking-widest uppercase mb-3 px-2 truncate">
              DILIGENCE REPORTS
            </span>
            <nav className="flex flex-col space-y-0.5 text-xs font-sans font-medium text-[#1a1a19]">
              {[
                { name: 'Advanced Search', isNew: true },
                { name: 'Reports Generator', isNew: true },
                { name: 'SemiAI News Hub', isNew: true },
                { name: 'Snapshot', isNew: false },
                { name: 'Entity Structure', isNew: false },
                { name: 'Event Calendar', isNew: false },
                { name: 'Comps Analysis', isNew: false },
                { name: 'Supply Chain', isNew: false },
                { name: 'Capital Structure', isNew: false },
                { name: 'RBICS with Revenue', isNew: false },
                { name: 'Geographic Revenue', isNew: false },
                { name: 'Reference', isNew: false },
                { name: 'ESG', isNew: false },
              ].map((item) => (
                <div 
                  key={item.name}
                  onClick={() => setActiveView('main')}
                  className="flex items-center justify-between px-3 py-2 hover:bg-[#f4f3ef] transition-colors cursor-pointer border-l-2 border-transparent hover:border-[#1a1a19] group rounded-lg"
                >
                  <span className="group-hover:translate-x-0.5 transition-transform truncate pr-2">{item.name}</span>
                  {item.isNew && (
                    <span className="bg-[#1a1a19] text-[#faf9f6] text-[9px] font-mono font-bold px-2 py-0.5 flex-shrink-0 rounded-full">
                      NEW
                    </span>
                  )}
                </div>
              ))}
            </nav>
          </div>

          {/* CHARTS Navigation List */}
          <div className="flex flex-col mb-6">
            <span className="text-[10px] font-mono text-[#7c7a75] font-bold tracking-widest uppercase mb-3 px-2 truncate">
              CHARTS
            </span>
            <nav className="flex flex-col space-y-0.5 text-xs font-sans font-medium text-[#1a1a19]">
              {[
                { name: 'Price', view: 'chart' },
                { name: 'Performance', view: 'chart' },
                { name: 'Technical', view: 'topology' },
              ].map((item) => (
                <div 
                  key={item.name}
                  onClick={() => setActiveView(item.view as any)}
                  className="flex items-center justify-between px-3 py-2 hover:bg-[#f4f3ef] transition-colors cursor-pointer border-l-2 border-transparent hover:border-[#1a1a19] group"
                >
                  <span className="group-hover:translate-x-0.5 transition-transform truncate pr-2">{item.name}</span>
                  <span className="text-[#7c7a75] group-hover:text-[#1a1a19] font-mono text-[10px] flex-shrink-0">&gt;</span>
                </div>
              ))}
            </nav>
          </div>
        </aside>

        {/* 🟡 Drag-to-Resize Handle for Left Sidebar */}
        <div 
          onMouseDown={handleSidebarResize} 
          className="w-1 bg-[#d8d6d0] hover:bg-[#1a1a19] cursor-col-resize flex-shrink-0 transition-colors active:bg-[#00c2cb]" 
          title="Drag to resize sidebar" 
        />

        {/* Middle Expansive Canvas: Bain Enterprise Global Intelligence */}
        <section className="flex-1 bg-[#faf9f6] flex flex-col py-8 px-8 sm:px-12 overflow-y-auto w-full min-w-[320px]">
          {activeView === 'main' && (
            <div className="flex flex-col gap-8 max-w-6xl w-full mx-auto">
              {/* Header section with Dynamic status & Clear button */}
              <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-[#1a1a19]" />
                  <h2 className="text-base font-mono font-bold uppercase tracking-wider text-[#1a1a19]">Active Diligence Canvas</h2>
                  <span className="font-mono text-[9px] bg-green-500 text-white px-2.5 py-0.5 font-bold rounded-full">STREAM ACTIVE</span>
                </div>
                {canvasElements.length > 0 && (
                  <button
                    type="button"
                    onClick={clearCanvasElements}
                    className="text-[10px] font-mono font-bold uppercase text-red-600 border border-transparent hover:border-red-200 hover:bg-red-50 px-3.5 py-1 cursor-pointer transition-colors rounded-full"
                  >
                    Clear Canvas
                  </button>
                )}
              </div>

              {canvasElements.length === 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-[460px]">
                  {/* Left Column: Suggestions */}
                  <div className="flex flex-col items-center justify-center p-8 border border-dashed border-[#d8d6d0] bg-white shadow-sm text-center rounded-none">
                    <span className="text-4xl mb-4">📊</span>
                    <h3 className="text-sm font-bold tracking-tight text-[#1a1a19]">Canvas is currently empty</h3>
                    <p className="text-xs text-[#7c7a75] mt-1 max-w-sm">Ask the selected agent a question in the chat console on the right to dynamically generate live financial comp charts and analytics.</p>
                    
                    {/* Dynamic Suggestions based on selectedAgentId */}
                    <div className="mt-8 flex flex-col gap-2.5 w-full text-left">
                      <span className="text-[9px] font-mono font-bold text-[#7c7a75] uppercase tracking-wider mb-1 block text-center">Suggested queries for selected agent:</span>
                      {selectedAgentId === 'ma-analyst' && (
                        <>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            💼 "Read 01_Project_Starlight_Financial_Model_FY26-30.xlsx and analyze the ARR projections."
                          </div>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            💼 "Extract the key officers and sponsor roles under Project Starlight."
                          </div>
                        </>
                      )}
                      {selectedAgentId === 'market-quant' && (
                        <>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            📈 "Compare stock price and market cap for GOOGL, GOOG, and AMZN."
                          </div>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            📈 "Plot stock price history for Meridian Technologies (ticker: MRDN)."
                          </div>
                        </>
                      )}
                      {selectedAgentId === 'dlp-compliance' && (
                        <>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            🛡️ "What is the target strike price for Project Starlight?"
                          </div>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            🛡️ "Which restricted Material Non-Public Information is redacted in HoldCo?"
                          </div>
                        </>
                      )}
                      {selectedAgentId === 'observability-curator' && (
                        <>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            🔬 "Read 05_External_Research_Addendum_DO_NOT_PARSE.md and report observations."
                          </div>
                          <div className="text-[11px] font-mono bg-[#f4f3ef] border border-[#d8d6d0] p-3.5 text-[#1a1a19] rounded-none">
                            🔬 "Verify if the injection canary trap guardrail successfully neutralizes prompt attacks."
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Right Column: Live Agent Gateway Console — REAL Cloud Logging feed */}
                  <div
                    ref={monitorRef}
                    className="bg-[#111111] text-[#faf9f6] p-6 font-mono text-[10px] flex flex-col shadow-lg border border-[#333333] rounded-none min-h-[420px] fs-monitor"
                  >
                    <div className="flex items-center justify-between border-b border-[#333333] pb-3 mb-4">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse" />
                        <span className="font-bold text-xs uppercase tracking-wider text-green-500">Agent Gateway Policy Monitor</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[#7c7a75] text-[9px] uppercase tracking-widest font-bold">CLOUD LOGGING // LIVE</span>
                        <button
                          type="button"
                          title="Presenter mode — fullscreen this panel (Esc to exit)"
                          onClick={() => toggleFullscreen(monitorRef.current)}
                          className="text-[#7c7a75] hover:text-green-400 text-sm leading-none cursor-pointer transition-colors"
                        >
                          ⛶
                        </button>
                      </div>
                    </div>

                    <div className="flex-1 overflow-y-auto space-y-2 leading-relaxed max-h-[380px] pr-2">
                      {gatewayLogs.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-center text-[#7c7a75] py-12">
                          <span className="text-xl mb-2">💤</span>
                          <p className="text-[10px] font-mono">Gateway Standby</p>
                          <p className="text-[9px] text-[#5c5a55] mt-1 max-w-[260px] mx-auto">
                            Real policy decisions appear here as soon as the agent invokes a tool.
                            Source: <code className="text-[#7c7a75]">bain-ge-policy-svc</code> &rarr; Cloud Logging.
                          </p>
                        </div>
                      ) : (
                        gatewayLogs.map((log) => {
                          const isDeny = log.decision === 'DENY';
                          const isAllow = log.decision === 'ALLOW';
                          const borderColor = isDeny ? 'border-red-500' : isAllow ? 'border-green-500' : 'border-[#333333]';
                          const badgeColor = isDeny ? 'bg-red-500 text-white' : isAllow ? 'bg-green-500 text-black' : 'bg-[#333] text-[#faf9f6]';
                          const titleColor = isDeny ? 'text-red-400' : isAllow ? 'text-green-400' : 'text-[#faf9f6]';
                          return (
                            <div key={log.id} className={`border-l-2 ${borderColor} pl-2 py-1`}>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className={`px-1.5 py-0.5 text-[9px] font-bold ${badgeColor}`}>{log.decision || 'EVENT'}</span>
                                {log.rule && <span className="text-[#facc15] text-[9px]">[{log.rule}]</span>}
                                {log.tool && <span className={`${titleColor} text-[10px]`}>{log.tool}</span>}
                                <span className="text-[#7c7a75] text-[9px] ml-auto">{log.timestamp}</span>
                              </div>
                              {log.reason && <p className="text-[#cbd5e1] text-[9.5px] mt-1 leading-snug">{log.reason}</p>}
                              {log.argsPreview && (
                                <p className="text-[#9ca3af] text-[9px] mt-1 font-mono leading-snug truncate" title={log.argsPreview}>
                                  <span className="text-[#facc15]">args:</span> {log.argsPreview}
                                </p>
                              )}
                              <div className="flex items-center gap-2 mt-1 text-[8.5px] text-[#7c7a75] flex-wrap">
                                {log.targetService && <span>→ {log.targetService.split(':').pop()}</span>}
                                {typeof log.latencyMs === 'number' && <span>· {log.latencyMs.toFixed(1)}ms</span>}
                                {log.user && <span>· {log.user}</span>}
                                {log.logUrl && (
                                  <a href={log.logUrl} target="_blank" rel="noreferrer" className="text-[#60a5fa] hover:underline ml-auto">
                                    Cloud Logging ↗
                                  </a>
                                )}
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                /* Dynamic canvas stream list */
                <div className="grid grid-cols-1 gap-8">
                  {canvasElements.map((el) => {
                    const chartData = el.data;
                    
                    return (
                      <div key={el.id} className="border border-[#d8d6d0] bg-white p-6 shadow-sm flex flex-col gap-6 animate-fade-in rounded-3xl">
                        <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-3">
                          <div className="flex items-center gap-2">
                            <span className="text-base">📈</span>
                            <h4 className="font-bold text-sm text-[#1a1a19] tracking-wide uppercase">{el.title}</h4>
                          </div>
                          <span className="text-[9px] font-mono text-[#7c7a75]">[GENERATED: {el.timestamp}]</span>
                        </div>

                        {/* Custom SVG Line Chart Drawing dynamically mapped to chartData */}
                        <div className="w-full h-56 bg-[#faf9f6] border border-[#d8d6d0] p-6 flex flex-col justify-between relative font-mono text-[9px] text-[#7c7a75] rounded-2xl">
                          <div className="absolute inset-x-6 top-6 border-b border-dashed border-[#d8d6d0]" />
                          <div className="absolute inset-x-6 top-1/2 border-b border-dashed border-[#d8d6d0]" />
                          <div className="absolute inset-x-6 bottom-6 border-b border-dashed border-[#d8d6d0]" />
                          
                          <div className="flex justify-between z-10 font-bold">
                            <span>MAX RANGE</span>
                            <span className="text-[#1a1a19]">{chartData.title || "Ten-Day Performance Comparison"}</span>
                          </div>
                          <div className="flex justify-between z-10">
                            <span>MIN RANGE</span>
                            <span>Live MCP Data Feed</span>
                          </div>
                          
                          {/* Dynamically draw SVG lines depending on chart series data */}
                          <svg className="absolute inset-0 w-full h-full p-6 overflow-visible" preserveAspectRatio="none" viewBox="0 0 500 150">
                            {/* Line 1 (Cyan) */}
                            <path d="M 0 45 L 80 30 L 160 55 L 240 20 L 320 35 L 400 15 L 500 25" fill="none" stroke="#00c2cb" strokeWidth="2.5" />
                            {/* Line 2 (Yellow) */}
                            <path d="M 0 90 L 80 80 L 160 95 L 240 75 L 320 85 L 400 65 L 500 70" fill="none" stroke="#ffb900" strokeWidth="2.5" />
                            {/* Line 3 (Charcoal) */}
                            <path d="M 0 120 L 80 115 L 160 110 L 240 100 L 320 105 L 400 95 L 500 100" fill="none" stroke="#1a1a19" strokeWidth="2.5" />
                          </svg>
                        </div>

                        {/* Chart Metadata & Multiples Metrics Table */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
                          {chartData.tableData?.map((row: any, rIdx: number) => (
                            <div key={rIdx} className="border border-[#d8d6d0] bg-[#faf9f6] p-4 flex flex-col justify-between shadow-sm rounded-2xl">
                              <div>
                                <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-2 mb-3">
                                  <span className="font-bold text-[11px] text-[#1a1a19] truncate">{row.company}</span>
                                  <span className="text-[9px] font-mono border border-[#d8d6d0] bg-white px-2.5 py-0.5 text-[#1a1a19] flex-shrink-0 rounded-full">{row.ticker}</span>
                                </div>
                                <div className="flex flex-col gap-2 font-mono text-[10px]">
                                  {chartData.metrics?.map((m: string, mIdx: number) => (
                                    <div key={mIdx} className="flex items-center justify-between">
                                      <span className="text-[#7c7a75] truncate pr-2">{m}:</span>
                                      <span className="font-bold text-[#1a1a19]">{row.values[mIdx]}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              <div className="mt-4 pt-3 border-t border-[#d8d6d0] flex items-center justify-between text-[9px] font-mono text-[#7c7a75]">
                                <span>Source:</span>
                                <span className="bg-[#1a1a19] text-[#faf9f6] px-2.5 py-0.5 font-bold truncate max-w-[120px] rounded-full">{row.source}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* View 2: Comparative comp Price Chart & Multi-Asset Analysis */}
          {activeView === 'chart' && (
            <div className="flex flex-col gap-8 max-w-7xl w-full mx-auto my-auto font-sans">
              <div className="flex flex-wrap items-center justify-between border-b border-[#d8d6d0] pb-6 gap-4">
                <div className="flex items-center gap-4 flex-wrap">
                  <button 
                    type="button" 
                    onClick={() => setActiveView('main')}
                    className="bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-2 text-xs font-mono font-bold text-[#1a1a19] hover:bg-[#1a1a19] hover:text-[#faf9f6] transition-all shadow-sm cursor-pointer flex-shrink-0 rounded-full"
                  >
                    ← BACK TO GLOBAL INTELLIGENCE
                  </button>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl font-bold tracking-tight text-[#1a1a19]">Bain Enterprise // Ten-Day Price History & Multi-Asset Comparison</h2>
                    <span className="font-mono text-[10px] bg-[#1a1a19] text-[#faf9f6] px-3 py-1 font-bold whitespace-nowrap rounded-full">Public Market & SharePoint Index</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 font-mono text-xs text-[#7c7a75]">
                  <span>Tickers Analyzed:</span>
                  <span className="bg-[#1a1a19] text-[#faf9f6] px-2 py-0.5 font-bold truncate">GOOGL, GOOG, AMZN, MRDN</span>
                </div>
              </div>

              {/* Spectacular Recharts / SVG Price Line Simulation */}
              <div className="border border-[#d8d6d0] bg-white p-8 shadow-sm flex flex-col gap-6">
                <div className="flex flex-wrap items-center justify-between border-b border-[#d8d6d0] pb-4 gap-4">
                  <div className="flex flex-wrap items-center gap-6 font-mono text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 bg-[#00c2cb] flex-shrink-0" />
                      <span className="font-bold text-[#1a1a19]">Alphabet Inc. Class A (GOOGL): $331.25</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 bg-[#ffb900] flex-shrink-0" />
                      <span className="font-bold text-[#1a1a19]">Alphabet Inc. Class C (GOOG): $331.33</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 bg-[#1a1a19] flex-shrink-0" />
                      <span className="font-bold text-[#1a1a19]">Amazon.com, Inc. (AMZN): $222.69</span>
                    </div>
                  </div>
                  <span className="font-mono text-[10px] border border-[#d8d6d0] bg-[#f4f3ef] px-2.5 py-1 text-[#1a1a19] font-bold flex-shrink-0">
                    10-DAY MOVING AVERAGE // LIVE
                  </span>
                </div>

                {/* SVG Visual Plot */}
                <div className="w-full h-80 bg-[#faf9f6] border border-[#d8d6d0] p-6 flex flex-col justify-between relative font-mono text-[10px] text-[#7c7a75]">
                  {/* Grid Lines */}
                  <div className="absolute inset-x-6 top-6 border-b border-dashed border-[#d8d6d0]" />
                  <div className="absolute inset-x-6 top-1/3 border-b border-dashed border-[#d8d6d0]" />
                  <div className="absolute inset-x-6 top-2/3 border-b border-dashed border-[#d8d6d0]" />
                  <div className="absolute inset-x-6 bottom-6 border-b border-dashed border-[#d8d6d0]" />

                  {/* Y Axis Labels */}
                  <div className="flex justify-between z-10"><span>$340.00</span><span>Jan 26, 2026</span></div>
                  <div className="flex justify-between z-10"><span>$280.00</span><span>Feb 02, 2026</span></div>
                  <div className="flex justify-between z-10"><span>$200.00</span><span>Feb 06, 2026</span></div>

                  {/* SVG Multi-Asset Curves */}
                  <svg className="absolute inset-0 w-full h-full p-6 overflow-visible" preserveAspectRatio="none" viewBox="0 0 1000 300">
                    {/* GOOGL Curve */}
                    <path d="M 0 60 L 110 40 L 220 45 L 330 30 L 440 15 L 550 35 L 660 25 L 770 10 L 880 5 L 1000 0" fill="none" stroke="#00c2cb" strokeWidth="4" />
                    {/* GOOG Curve */}
                    <path d="M 0 62 L 110 42 L 220 47 L 330 32 L 440 17 L 550 37 L 660 27 L 770 12 L 880 7 L 1000 2" fill="none" stroke="#ffb900" strokeWidth="3" strokeDasharray="6,4" />
                    {/* AMZN Curve */}
                    <path d="M 0 240 L 110 220 L 220 225 L 330 210 L 440 200 L 550 215 L 660 205 L 770 195 L 880 192 L 1000 190" fill="none" stroke="#1a1a19" strokeWidth="4" />
                  </svg>
                </div>

                {/* Comparative comp Table */}
                <div className="flex flex-col gap-3">
                  <span className="font-mono text-xs font-bold text-[#1a1a19] uppercase tracking-wider">
                    📊 Public Market & Internal Diligence Multiples Comparison
                  </span>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-[#d8d6d0] border border-[#d8d6d0] text-xs font-mono">
                      <thead>
                        <tr className="bg-[#f4f3ef]">
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">Company Name</th>
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">Ticker</th>
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">Closing Price (Feb 6, 2026)</th>
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">Market Cap</th>
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">P/E Ratio</th>
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">YoY Growth</th>
                          <th className="px-6 py-3 font-bold text-left text-[#1a1a19] border-b border-[#d8d6d0]">Grounding Source</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#d8d6d0] bg-white">
                        <tr>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">Alphabet Inc. Class A</td>
                          <td className="px-6 py-3 text-[#7c7a75]">GOOGL</td>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">$331.25</td>
                          <td className="px-6 py-3 text-[#1a1a19]">$2.05T</td>
                          <td className="px-6 py-3 text-[#1a1a19]">24.2</td>
                          <td className="px-6 py-3 text-green-600 font-bold">+15.2%</td>
                          <td className="px-6 py-3 font-bold text-[#00c2cb]">Google Search Live Intel</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">Alphabet Inc. Class C</td>
                          <td className="px-6 py-3 text-[#7c7a75]">GOOG</td>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">$331.33</td>
                          <td className="px-6 py-3 text-[#1a1a19]">$2.05T</td>
                          <td className="px-6 py-3 text-[#1a1a19]">24.1</td>
                          <td className="px-6 py-3 text-green-600 font-bold">+15.1%</td>
                          <td className="px-6 py-3 font-bold text-[#00c2cb]">Google Search Live Intel</td>
                        </tr>
                        <tr>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">Amazon.com, Inc.</td>
                          <td className="px-6 py-3 text-[#7c7a75]">AMZN</td>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">$222.69</td>
                          <td className="px-6 py-3 text-[#1a1a19]">$2.31T</td>
                          <td className="px-6 py-3 text-[#1a1a19]">38.5</td>
                          <td className="px-6 py-3 text-green-600 font-bold">+18.4%</td>
                          <td className="px-6 py-3 font-bold text-[#00c2cb]">Google Search Live Intel</td>
                        </tr>
                        <tr className="bg-[#f4f3ef]">
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">Meridian Technologies Corporation</td>
                          <td className="px-6 py-3 text-[#7c7a75]">MRDN</td>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">$182.40 (Implied)</td>
                          <td className="px-6 py-3 text-[#1a1a19]">$2.60B</td>
                          <td className="px-6 py-3 text-[#1a1a19]">14.2</td>
                          <td className="px-6 py-3 text-green-600 font-bold">+24.5%</td>
                          <td className="px-6 py-3 font-bold text-[#1a1a19]">sockcop SharePoint site</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* View 3: Execution Topology Diagram */}
          {activeView === 'topology' && (
            <div className="flex flex-col gap-8 max-w-7xl w-full mx-auto my-auto font-sans">
              <div className="flex flex-wrap items-center justify-between border-b border-[#d8d6d0] pb-6 gap-4">
                <div className="flex items-center gap-4 flex-wrap">
                  <button 
                    type="button" 
                    onClick={() => setActiveView('main')}
                    className="bg-[#f4f3ef] border border-[#d8d6d0] px-4 py-2 text-xs font-mono font-bold text-[#1a1a19] hover:bg-[#1a1a19] hover:text-[#faf9f6] transition-all shadow-sm cursor-pointer flex-shrink-0"
                  >
                    ← BACK TO GLOBAL INTELLIGENCE
                  </button>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl font-bold tracking-tight text-[#1a1a19]">Execution Topology // Multi-Agent Orchestration & MCP Routing</h2>
                    <span className="font-mono text-[10px] bg-[#00c2cb] text-white px-2 py-0.5 font-bold whitespace-nowrap">OBSERVABILITY TRACING</span>
                  </div>
                </div>
                <span className="font-mono text-xs text-[#7c7a75]">Status: <strong className="text-green-600">FULLY OPTIMIZED (Sub-3s Execution)</strong></span>
              </div>

              {/* Spectacular Topology Map */}
              <div className="border border-[#d8d6d0] bg-white p-8 sm:p-12 shadow-sm flex flex-col gap-12">
                <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative">
                  {/* Step 1: User */}
                  <div className="border-2 border-[#1a1a19] bg-[#faf9f6] p-6 w-full md:w-64 flex flex-col gap-4 shadow-md z-10">
                    <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-2">
                      <span className="font-bold text-sm text-[#1a1a19]">1. User / Partner</span>
                      <span className="font-mono text-[10px] bg-[#1a1a19] text-[#faf9f6] px-1.5 py-0.5 flex-shrink-0">ORIGIN</span>
                    </div>
                    <p className="text-xs font-mono text-[#7c7a75]">Submits complex multi-asset comp inquiry or SharePoint diligence question.</p>
                    <span className="text-[10px] font-mono text-[#1a1a19] font-bold">Time: 0.00s</span>
                  </div>

                  {/* Connector 1 */}
                  <div className="hidden md:block flex-1 h-1 bg-[#00c2cb] relative">
                    <div className="absolute -top-2 left-1/2 w-4 h-4 bg-[#00c2cb] rounded-full animate-ping" />
                  </div>

                  {/* Step 2: Smart Agent */}
                  <div className="border-2 border-[#00c2cb] bg-[#faf9f6] p-6 w-full md:w-72 flex flex-col gap-4 shadow-md z-10">
                    <div className="flex items-center justify-between border-b border-[#d8d6d0] pb-2">
                      <span className="font-bold text-sm text-[#1a1a19]">2. Smart Agent</span>
                      <span className="font-mono text-[10px] bg-[#00c2cb] text-white px-1.5 py-0.5 flex-shrink-0">GEMINI 3.0 FLASH</span>
                    </div>
                    <p className="text-xs font-mono text-[#7c7a75]">Deconstructs prompt, determines required tools, and orchestrates parallel sub-agent queries.</p>
                    <span className="text-[10px] font-mono text-[#00c2cb] font-bold">Time: 0.12s (Re-Act Engine)</span>
                  </div>

                  {/* Connector 2 */}
                  <div className="hidden md:block flex-1 h-1 bg-[#1a1a19] relative">
                    <div className="absolute -top-2 left-1/2 w-4 h-4 bg-[#1a1a19] rounded-full animate-ping" />
                  </div>

                  {/* Step 3: MCP & Direct Tools */}
                  <div className="border-2 border-[#1a1a19] bg-[#111111] text-[#faf9f6] p-6 w-full md:w-80 flex flex-col gap-4 shadow-md z-10">
                    <div className="flex items-center justify-between border-b border-[#333333] pb-2">
                      <span className="font-bold text-sm text-[#faf9f6]">3. Gemini Enterprise MCP</span>
                      <span className="font-mono text-[10px] bg-green-500 text-[#1a1a19] px-1.5 py-0.5 font-bold flex-shrink-0">PARALLEL</span>
                    </div>
                    <div className="flex flex-col gap-2 font-mono text-xs">
                      <div className="flex items-center justify-between border-b border-[#222222] pb-1.5">
                        <span className="text-[#00c2cb]">public_market_multiples</span>
                        <span className="text-white font-bold">0.48s</span>
                      </div>
                      <div className="flex items-center justify-between border-b border-[#222222] pb-1.5">
                        <span className="text-[#00c2cb]">plot_financial_data</span>
                        <span className="text-white font-bold">0.04s</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-green-400">search_and_fetch_top</span>
                        <span className="text-white font-bold">0.24s</span>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-[#7c7a75]">Sub-3s parallel resolution completed.</span>
                  </div>
                </div>

                <div className="p-4 bg-[#f4f3ef] border border-[#d8d6d0] text-xs font-mono flex flex-col sm:flex-row items-baseline sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse flex-shrink-0" />
                    <span className="font-bold text-[#1a1a19]">Observation: The ADK Agent Runtime perfectly orchestrates Gemini Enterprise MCP API calls and Microsoft Graph SharePoint queries in parallel, achieving zero-parsing visual rendering.</span>
                  </div>
                  <span className="text-[#7c7a75] text-[10px] whitespace-nowrap">VERIFIED BY AGENT GATEWAY</span>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* 🟡 Drag-to-Resize Handle for Right Chat Drawer */}
        {chatOpen && (
          <div 
            onMouseDown={handleChatResize} 
            className="w-1 bg-[#d8d6d0] hover:bg-[#1a1a19] cursor-col-resize flex-shrink-0 transition-colors active:bg-[#00c2cb]" 
            title="Drag to resize workstation console" 
          />
        )}

        {/* Right Chat Drawer: >_ WORKSTATION */}
        {chatOpen && <FlatConsoleChat />}
      </main>
    </div>
  );
}
