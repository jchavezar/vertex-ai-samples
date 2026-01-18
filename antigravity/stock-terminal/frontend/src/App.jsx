import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import DashboardHeader from './components/DashboardHeader';
import PerformanceChart from './components/PerformanceChart';
import KeyStats from './components/KeyStats';
import AgentInsights from './components/AgentInsights';
import SummaryPanel from './components/SummaryPanel';
import RightSidebar from './components/RightSidebar';
import AiActionButtons from './components/AiActionButtons';
import WidgetSlot from './components/WidgetSlot';

function App() {
  const [ticker, setTicker] = useState('FDS'); // Default to FactSet
  const [tickerData, setTickerData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('Snapshot');
  const [chartOverride, setChartOverride] = useState(null);
  const [widgetOverrides, setWidgetOverrides] = useState({}); // { [section]: { content, loading } }
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(true);
  const [rightSidebarWidth, setRightSidebarWidth] = useState(450);
  const [isResizing, setIsResizing] = useState(false);

  const startResizing = React.useCallback((mouseDownEvent) => {
    setIsResizing(true);
  }, []);

  const stopResizing = React.useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = React.useCallback(
    (mouseMoveEvent) => {
      if (isResizing) {
        const newWidth = window.innerWidth - mouseMoveEvent.clientX;
        if (newWidth > 200 && newWidth < 800) {
          setRightSidebarWidth(newWidth);
        }
      }
    },
    [isResizing]
  );

  useEffect(() => {
    window.addEventListener("mousemove", resize);
    window.addEventListener("mouseup", stopResizing);
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [resize, stopResizing]);

  // DEBUG: Expose for testing
  useEffect(() => {
    window.setChartOverride = setChartOverride;
    return () => { delete window.setChartOverride; };
  }, []);

  useEffect(() => {
    setChartOverride(null); // Reset override on ticker change
    setWidgetOverrides({}); // Reset widgets
    const fetchTickerInfo = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:8001/ticker-info/${ticker}`);
        const data = await response.json();
        setTickerData(data);
      } catch (err) {
        console.error("Failed to fetch ticker data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTickerInfo();
  }, [ticker]);

  const handleUpdateWidget = (section, content, isLoading = false) => {
    setWidgetOverrides(prev => ({
      ...prev,
      [section]: { content, loading: isLoading }
    }));
  };

  const handleGenerateWidget = (section) => {
    handleUpdateWidget(section, null, true); // Set loading

    // Extract tickers from chart context if available
    let tickersToAnalyze = ticker;
    if (chartOverride && chartOverride.series && chartOverride.series.length > 0) {
      tickersToAnalyze = chartOverride.series.map(s => s.ticker).join(', ');
    } else if (chartOverride && chartOverride.ticker) {
      tickersToAnalyze = chartOverride.ticker;
    }

    if (window.triggerAgent) {
      window.triggerAgent(
        `Generate ${section} analysis for ${tickersToAnalyze}. IMPORTANT: Wrap the response in [WIDGET:${section}]...[/WIDGET] tags.`,
        { preserveChart: true, expectedWidget: section }
      );
    }
  };



  return (
    <div className="app-container">
      {isSidebarOpen && (
        <Sidebar setTicker={setTicker} activeView={activeView} setActiveView={setActiveView} />
      )}

      <div
        className="sidebar-toggle-strip"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        title={isSidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
        style={{
          width: '12px',
          background: '#f8f9fa',
          borderRight: '1px solid var(--border)',
          borderLeft: isSidebarOpen ? 'none' : '1px solid var(--border)', // Ensure border when closed
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          zIndex: 10,
          position: 'relative',
          transition: 'background 0.2s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = '#eef1f4'}
        onMouseLeave={(e) => e.currentTarget.style.background = '#f8f9fa'}
      >
        <div style={{
          height: '24px',
          width: '4px',
          background: '#d1d9e0',
          borderRadius: '2px'
        }} />
      </div>

      <main className="main-content">

        <DashboardHeader ticker={ticker} externalData={tickerData} loading={loading} />

        <div className="content-scrollable">
          {activeView === 'Snapshot' ? (
            <div className="grid-layout">
              {!chartOverride && (
                <div style={{ gridColumn: 'span 12' }}>
                  <AgentInsights ticker={ticker} />
                </div>
              )}

              <div style={{ gridColumn: chartOverride ? 'span 8' : 'span 8' }}>
                <PerformanceChart
                  ticker={chartOverride?.ticker || ticker}
                  externalData={chartOverride}
                  defaultData={tickerData}
                />
              </div>

              <div style={{ gridColumn: 'span 4' }}>
                <WidgetSlot
                  section="Profile"
                  sectionKey="Profile"
                  override={widgetOverrides['Profile']}
                  isAiMode={!!chartOverride}
                  onGenerate={handleGenerateWidget}
                  originalComponent={<SummaryPanel ticker={ticker} externalData={tickerData} />}
                />
              </div>

              {['Trading', 'Valuation', 'Dividends', 'Estimates'].map(section => (
                <div style={{ gridColumn: 'span 3' }} key={section}>
                  <WidgetSlot
                    section={section}
                    override={widgetOverrides[section]}
                    isAiMode={!!chartOverride}
                    onGenerate={handleGenerateWidget}
                    originalComponent={<KeyStats section={section} ticker={ticker} externalData={tickerData} />}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
              <h2>{activeView} View</h2>
              <p>This section is currently under development. Please check back later or use the Snapshot view.</p>
            </div>
          )}
        </div>
      </main>

      <div
        className="sidebar-toggle-strip right"
        onMouseDown={startResizing}
        title="Resize Chat"
        style={{
          width: '12px',
          background: isResizing ? '#eef1f4' : '#f8f9fa',
          borderLeft: '1px solid var(--border)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'col-resize',
          zIndex: 10,
          position: 'relative',
          transition: 'background 0.2s',
          userSelect: 'none'
        }}
      >
        <div style={{
          height: '24px',
          width: '4px',
          background: '#d1d9e0',
          borderRadius: '2px'
        }} />
      </div>

      <RightSidebar
        dashboardData={tickerData}
        chartOverride={chartOverride}
        setChartOverride={setChartOverride}
        onUpdateWidget={handleUpdateWidget}
        isOpen={isRightSidebarOpen}
        width={rightSidebarWidth}
      />
    </div>
  );
}

export default App;
