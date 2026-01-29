import React, { useEffect } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { useAgentInsights, InsightCard, SuggestedActionsCard } from './AgentInsights';
import { PerformanceChart } from './PerformanceChart';
import { SummaryPanel } from './SummaryPanel';

import { WidgetSlot } from './WidgetSlot';
import { Terminal, Zap } from 'lucide-react';
import { MarketDataFooter } from './MarketDataFooter';

export const DashboardView: React.FC = () => {
  const { 
    ticker, 
    tickerData, 
    setTickerData, 
    activeView, 
    setActiveView, 
    chartOverride, 
    widgetOverrides,
    setWidgetOverride
  } = useDashboardStore();

  const { insights, suggestedActions } = useAgentInsights(ticker);

  useEffect(() => {
    const fetchTickerInfo = async () => {
      if (!ticker) return;
      try {
        const response = await fetch(`http://localhost:8001/ticker-info/${ticker}`);
        if (response.ok) {
          const data = await response.json();
          setTickerData(data);
        } else {
            console.error("Failed to fetch ticker data");
        }
      } catch (err) {
        console.error("Failed to fetch ticker data:", err);
      }
    };
    fetchTickerInfo();
  }, [ticker, setTickerData]);

  const handleGenerateWidget = async (section: string) => {
    setWidgetOverride(section, { loading: true, content: null });
    
    let tickersToAnalyze = [ticker];
    if (chartOverride && chartOverride.series && chartOverride.series.length > 0) {
      tickersToAnalyze = chartOverride.series.map((s: any) => s.ticker);
    } else if (chartOverride && chartOverride.ticker) {
      tickersToAnalyze = [chartOverride.ticker];
    }

    try {
      const response = await fetch('http://localhost:8001/generate-widget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: tickersToAnalyze,
          section: section,
          session_id: "default_chat",
          model: 'gemini-2.5-flash-lite'
        })
      });

      if (!response.ok) {
        throw new Error(`Widget fetch failed with status: ${response.status}`);
      }

      const data = await response.json();
      setWidgetOverride(section, { loading: false, content: data.content, model: 'gemini-2.5-flash-lite' });

    } catch (err) {
      console.error(`Failed to generate widget ${section}:`, err);
      setWidgetOverride(section, { loading: false, content: `Error: Failed to fetch ${section} analysis.` });
    }
  };

  if (activeView !== 'Snapshot') {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-[var(--text-muted)]">
        <div className="mb-6 opacity-50">
          <Terminal size={48} className="mx-auto" />
        </div>
        <h2 className="text-xl font-bold text-[var(--text-primary)] mb-3">{activeView} Analysis</h2>
        <p>This module is currently being optimized by the Agentic engine.</p>
        <button
          onClick={() => setActiveView('Snapshot')}
          className="mt-6 px-5 py-2.5 bg-[var(--brand)] text-white rounded-lg font-semibold hover:opacity-90 transition-opacity"
        >
          Return to Snapshot
        </button>
      </div>
    );
  }

  // Determine tickers to analyze for context-aware buttons
  let tickersToAnalyze = [ticker];
  if (chartOverride && chartOverride.series && chartOverride.series.length > 0) {
    tickersToAnalyze = chartOverride.series.map((s: any) => s.ticker).filter(Boolean);
  } else if (chartOverride && chartOverride.ticker) {
    tickersToAnalyze = [chartOverride.ticker];
  } else if (chartOverride && chartOverride.title) {
     const titleWords = chartOverride.title.split(/[\s()]+/);
     const suspectedTicker = titleWords.find((w: string) => /^[A-Z0-9.\-]{1,10}$/.test(w) && w !== 'REVENUE' && w !== 'VS');
     if (suspectedTicker) {
       tickersToAnalyze = [suspectedTicker];
     } else if (chartOverride.title.toUpperCase().includes('AMAZON')) {
       tickersToAnalyze = ['AMZN'];
     }
  }
  if (!tickersToAnalyze.length) tickersToAnalyze = [ticker];


  return (
    <div className="flex flex-col gap-5 p-4 w-full h-full">
      {/* Macro Context Overlay */}
      {activeView !== 'Snapshot' && (
        <div className="bg-gradient-to-r from-blue-600/20 to-cyan-500/20 border border-blue-500/30 rounded-2xl p-4 mb-2 flex items-center justify-between backdrop-blur-md shadow-lg shadow-blue-500/5 transition-all">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
              <Zap size={24} className="animate-pulse" />
            </div>
            <div>
              <h2 className="text-lg font-black tracking-tight text-[var(--text-primary)]">Workstation Lens: {activeView}</h2>
              <p className="text-xs text-[var(--text-muted)] font-medium">Strategist mode active. Correlating broad market indices with sector-specific alpha drivers.</p>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-blue-400 uppercase tracking-widest">Macro-Aware</span>
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Peer-Pack Sync</span>
          </div>
        </div>
      )}

      {/* NEW LAYOUT: Main Workspace (Chart Top-Left) + Context Grid */}
      <div className="flex flex-col w-full max-w-[1920px] mx-auto pb-6 px-2 pt-2 gap-5 h-full">

        {/* ROW 1: Main Workspace (Chart + Profile) - Takes available height */}
        <div className="flex-1 grid grid-cols-12 gap-5 min-h-0">
          {/* LEFT: Main Chart (Primary Focus) */}
          <div className="col-span-9 h-full">
            <div className="arch-card rounded-xl group/chart p-1 h-full relative">
              <div className="absolute top-0 right-0 p-6 z-10 opacity-0 group-hover/chart:opacity-100 transition-opacity">
                <span className="text-xs font-mono text-[var(--text-muted)] border border-[var(--border)] px-2 py-1 rounded">LIVE</span>
              </div>
              <PerformanceChart
                ticker={chartOverride?.ticker || ticker}
                externalData={chartOverride}
                defaultData={tickerData}
              />
            </div>
          </div>

          {/* RIGHT: Profile (Secondary Info) */}
          <div className="col-span-3 h-full">
            <WidgetSlot
              section="Profile"
              override={widgetOverrides['Profile']}
              isAiMode={!!chartOverride}
              onGenerate={handleGenerateWidget}
              tickers={tickersToAnalyze}
              originalComponent={<SummaryPanel ticker={ticker} externalData={tickerData} />}
            />
          </div>
        </div>

        {/* ROW 2: Context Items (4 Columns) - Fixed Height */}
        <div className="grid grid-cols-4 gap-4 h-[180px] shrink-0">
          {/* Earnings Context */}
          <div className="h-full">
            <InsightCard data={insights[1]} color="indigo" />
          </div>
          {/* Industry Comp */}
          <div className="h-full">
            <InsightCard data={insights[2]} color="sky" />
          </div>
          {/* Meeting Prep */}
          <div className="h-full">
            <InsightCard data={insights[0]} color="blue" />
          </div>
          {/* Suggested Actions */}
          <div className="h-full">
            <SuggestedActionsCard actions={suggestedActions} />
          </div>
        </div>

        {/* BOTTOM: Market Footer */}
        <div className="shrink-0 mt-auto">
          <div className="arch-card rounded-xl border-t border-[var(--border-highlight)] bg-[var(--bg-panel)]">
            <div className="flex flex-col lg:flex-row items-center h-20 px-6">
              {/* Label */}
              <div className="flex items-center gap-4 pr-8 border-r border-[var(--border)] h-full lg:min-w-[170px] shrink-0">
                <div className="w-1.5 h-8 bg-[var(--text-primary)]"></div>
                <div>
                  <h3 className="text-lg font-black text-[var(--text-primary)] tracking-widest uppercase leading-none">MARKET</h3>
                  <p className="text-[9px] text-[var(--text-muted)] font-mono font-bold leading-none mt-1.5">REAL-TIME DATA</p>
                </div>
              </div>

              {/* Unified Data Table */}
              <MarketDataFooter tickerData={tickerData} />
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};