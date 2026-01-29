import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useDashboardStore } from '../../store/dashboardStore';
import { AgentInsights } from './AgentInsights';
import { PerformanceChart } from './PerformanceChart';
import { SummaryPanel } from './SummaryPanel';
import { KeyStats } from './KeyStats';
import { WidgetSlot } from './WidgetSlot';
import { Terminal, Zap } from 'lucide-react';
import { CompsAnalysisView } from './CompsAnalysisView';

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

  useEffect(() => {
    const fetchTickerInfo = async () => {
      if (!ticker) return;
      try {
        // Assuming the backend is running on port 8001 as in the original app
        // In a real scenario, this might need an environment variable
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

  if (activeView === 'Battlecards') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.8, filter: 'blur(20px)' }}
        animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
        exit={{ opacity: 0, scale: 1.2, filter: 'blur(20px)' }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="w-full h-full relative"
      >
        <div className="absolute inset-0 bg-blue-500/10 animate-pulse pointer-events-none z-0" />
        <CompsAnalysisView />
      </motion.div>
    );
  }

  if (activeView !== 'Snapshot') {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-[var(--text-muted)] animate-in fade-in zoom-in-95 duration-700">
        <div className="absolute inset-0 bg-blue-500/5 backdrop-blur-3xl animate-pulse -z-10" />
        <div className="mb-6 opacity-50 relative">
          <Terminal size={48} className="mx-auto" />
          <div className="absolute inset-0 bg-blue-400 blur-2xl opacity-20 animate-pulse" />
        </div>
        <h2 className="text-xl font-bold text-[var(--text-primary)] mb-3 tracking-tighter uppercase">{activeView} Analysis</h2>
        <p className="max-w-md text-center text-sm opacity-60">This module is currently being optimized by the Agentic engine for real-time intelligence sync.</p>
        <button
          onClick={() => setActiveView('Snapshot')}
          className="mt-8 px-6 py-3 bg-white/5 border border-white/10 text-[var(--text-primary)] rounded-full font-bold hover:bg-white/10 transition-all hover:scale-105 active:scale-95 shadow-xl"
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
    <div className="flex flex-col gap-5 p-4 animate-in slide-in-from-bottom-2 duration-500 w-full">
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

      <div className="grid grid-cols-12 gap-5 w-full">
      {!chartOverride && (
        <div className="col-span-12">
          <AgentInsights ticker={ticker} />
        </div>
      )}

      <div className={`${chartOverride ? 'col-span-8' : 'col-span-8'}`}>
        <PerformanceChart
          ticker={chartOverride?.ticker || ticker}
          externalData={chartOverride}
          defaultData={tickerData}
        />
      </div>

      <div className="col-span-4">
        <WidgetSlot
          section="Profile"
          override={widgetOverrides['Profile']}
          isAiMode={!!chartOverride}
          onGenerate={handleGenerateWidget}
          tickers={tickersToAnalyze}
          originalComponent={<SummaryPanel ticker={ticker} externalData={tickerData} />}
        />
      </div>

      {['Trading', 'Valuation', 'Dividends', 'Estimates'].map(section => (
        <div className="col-span-3" key={section}>
          <WidgetSlot
            section={section}
            override={widgetOverrides[section]}
            isAiMode={!!chartOverride}
            onGenerate={handleGenerateWidget}
            tickers={tickersToAnalyze}
            originalComponent={<KeyStats section={section} ticker={ticker} externalData={tickerData} />}
          />
        </div>
      ))}
    </div>
    </div>
  );
};