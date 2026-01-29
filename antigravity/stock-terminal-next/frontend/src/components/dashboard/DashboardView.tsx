import React, { useEffect } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { useAgentInsights, InsightCard, SuggestedActionsCard } from './AgentInsights';
import { PerformanceChart } from './PerformanceChart';
import { SummaryPanel } from './SummaryPanel';

import { WidgetSlot } from './WidgetSlot';
import { Terminal, Zap } from 'lucide-react';
import {
  TradingStats,
  ValuationStats,
  DividendStats,
  ConsensusStats
} from './MarketDataFooter';

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
    <div className="flex flex-col gap-5 p-4 w-full h-full overflow-hidden">
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
      <div className="flex flex-col w-full max-w-[1920px] mx-auto pb-2 px-2 pt-2 gap-4 h-full min-h-0">

        {/* ROW 1: Main Workspace (Chart + Profile) - Takes available height */}
        <div className="flex-1 grid grid-cols-12 gap-5 min-h-0">
          {/* LEFT: Main Chart (Primary Focus) */}
          <div className="col-span-12 xl:col-span-9 h-full min-h-0 flex flex-col">
            <div className="arch-card rounded-2xl group/chart p-1 flex-1 relative min-h-0 shadow-sm">
              <div className="absolute top-4 right-4 z-10 opacity-0 group-hover/chart:opacity-100 transition-opacity">
                <span className="text-[10px] font-bold text-[var(--text-muted)] border border-[var(--border-subtle)] px-2 py-1 rounded bg-[var(--bg-app)]/80 backdrop-blur-sm">REAL-TIME FEED</span>
              </div>
              <PerformanceChart
                ticker={chartOverride?.ticker || ticker}
                externalData={chartOverride}
                defaultData={tickerData}
              />
            </div>
          </div>

          {/* RIGHT: Profile & Market Stats (Context Column) */}
          <div className="hidden xl:flex xl:col-span-3 h-full flex-col gap-4 overflow-y-auto no-scrollbar pb-4">
            <div className="arch-card rounded-2xl p-4 shadow-sm border-[var(--border-subtle)]">
              <WidgetSlot
                section="Profile"
                override={widgetOverrides['Profile']}
                isAiMode={!!chartOverride}
                onGenerate={handleGenerateWidget}
                tickers={tickersToAnalyze}
                originalComponent={<SummaryPanel ticker={ticker} externalData={tickerData} />}
              />
            </div>

            {/* Market Data Consolidated Container */}
            <div className="arch-card rounded-2xl p-6 flex flex-col gap-10 shadow-sm border-[var(--border-subtle)] bg-[var(--bg-card)]">
              <TradingStats tickerData={tickerData} layout="vertical" />
              <ValuationStats tickerData={tickerData} layout="vertical" />
              <DividendStats tickerData={tickerData} layout="vertical" />
              <ConsensusStats tickerData={tickerData} layout="vertical" />
            </div>
          </div>
        </div>

        {/* ROW 2: Context Items (4 Columns) - Fixed Height */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-[140px] shrink-0 mb-4">
          <div className="h-full arch-card rounded-2xl shadow-sm border-[var(--border-subtle)] overflow-hidden">
            <InsightCard data={insights[1]} color="gray" />
          </div>
          <div className="h-full arch-card rounded-2xl shadow-sm border-[var(--border-subtle)] overflow-hidden">
            <InsightCard data={insights[2]} color="gray" />
          </div>
          <div className="h-full arch-card rounded-2xl shadow-sm border-[var(--border-subtle)] overflow-hidden">
            <InsightCard data={insights[0]} color="gray" />
          </div>
          <div className="h-full arch-card rounded-2xl shadow-sm border-[var(--border-subtle)] overflow-hidden">
            <SuggestedActionsCard actions={suggestedActions} />
          </div>
        </div>

      </div>
    </div>
  );
};