import React, { useState, useEffect } from 'react';
import { Terminal } from 'lucide-react';
import Sidebar from './components/Sidebar';
import DashboardHeader from './components/DashboardHeader';
import PerformanceChart from './components/PerformanceChart';
import KeyStats from './components/KeyStats';
import AgentInsights from './components/AgentInsights';
import SummaryPanel from './components/SummaryPanel';
import RightSidebar from './components/RightSidebar';
import AiActionButtons from './components/AiActionButtons';
import WidgetSlot from './components/WidgetSlot';
import FinancialsView from './components/FinancialsView';
import AdvancedSearchView from './components/AdvancedSearchView';
import ReportsGenerator from './components/ReportsGenerator';

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
  const [theme, setTheme] = useState('light'); // default needs to be light
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportSteps, setReportSteps] = useState([]);
  const [reportStatus, setReportStatus] = useState('');
  // Report Persistence State
  const [reportTicker, setReportTicker] = useState('');
  const [reportTemplate, setReportTemplate] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [reportProgress, setReportProgress] = useState(0);
  const [reportProgressStep, setReportProgressStep] = useState('');
  const [reportStepsCompleted, setReportStepsCompleted] = useState([]);


  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark-theme' : 'light-theme';
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  // Model selection state (lifted from RightSidebar)
  const [selectedModel, setSelectedModel] = useState('gemini-3-flash-preview');
  const [selectedComplexModel, setSelectedComplexModel] = useState('gemini-3-flash-preview');

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

    // Allow components to trigger sidebar toggle
    const handleToggle = () => setIsRightSidebarOpen(prev => !prev);
    window.addEventListener('toggle-right-sidebar', handleToggle);

    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
      window.removeEventListener('toggle-right-sidebar', handleToggle);
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
    setTickerData(null);    // CLEAR previous data immediately to prevent lag/mismatch
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

  const handleUpdateWidget = (section, content, isLoading = false, usedModel = null) => {
    setWidgetOverrides(prev => ({
      ...prev,
      [section]: {
        content,
        loading: isLoading,
        model: usedModel || (prev[section]?.model)
      }
    }));
  };

  const handleGenerateWidget = async (section) => {
    handleUpdateWidget(section, null, true, selectedModel); // Set loading status and track intended model

    // Extract tickers from chart context if available to provide multi-company analysis
    let tickersToAnalyze = [ticker];
    if (chartOverride && chartOverride.series && chartOverride.series.length > 0) {
      tickersToAnalyze = chartOverride.series.map(s => s.ticker);
    } else if (chartOverride && chartOverride.ticker) {
      tickersToAnalyze = [chartOverride.ticker];
    }

    try {
      console.log(`[App] Triggering async widget analysis for ${section}...`);

      const response = await fetch('http://localhost:8001/generate-widget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: tickersToAnalyze,
          section: section,
          session_id: "default_chat",
          model: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error(`Widget fetch failed with status: ${response.status}`);
      }

      const data = await response.json();
      console.log(`[App] Received analysis for ${section}:`, data);

      // Update the widget with actual content and clear loading state
      handleUpdateWidget(section, data.content, false, selectedModel);

    } catch (err) {
      console.error(`[App] Failed to generate widget ${section}:`, err);
      handleUpdateWidget(section, `Error: Failed to fetch ${section} analysis.`, false);
    }
  };



  return (
    <div className="app-container">
      {isSidebarOpen && (
        <Sidebar setTicker={setTicker} activeView={activeView} setActiveView={setActiveView} theme={theme} />
      )}

      <div
        className="sidebar-toggle-strip"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        title={isSidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
        style={{
          width: '12px',
          background: 'var(--bg-app)',
          borderRight: '1px solid var(--border)',
          borderLeft: isSidebarOpen ? 'none' : '1px solid var(--border)', // Ensure border when closed
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          zIndex: 10,
          position: 'relative',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'var(--bg-app)'}
      >
        <div style={{
          height: '24px',
          width: '4px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '999px'
        }} />
      </div>

      <main className="main-content">

        <DashboardHeader
          ticker={ticker}
          externalData={tickerData}
          loading={loading}
          theme={theme}
          onToggleTheme={toggleTheme}
        />


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

              {/* Compute active tickers for context-aware buttons */}
              {(() => {
                let tickersToAnalyze = [ticker];
                if (chartOverride && chartOverride.series && chartOverride.series.length > 0) {
                  tickersToAnalyze = chartOverride.series.map(s => s.ticker);
                } else if (chartOverride && chartOverride.ticker) {
                  tickersToAnalyze = [chartOverride.ticker];
                }

                return (
                  <>
                     <div style={{ gridColumn: 'span 4' }}>
                       <WidgetSlot
                         section="Profile"
                         sectionKey="Profile"
                         override={widgetOverrides['Profile']}
                         isAiMode={!!chartOverride}
                         onGenerate={handleGenerateWidget}
                         tickers={tickersToAnalyze}
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
                            tickers={tickersToAnalyze}
                            originalComponent={<KeyStats section={section} ticker={ticker} externalData={tickerData} />}
                          />
                        </div>
                      ))}
                  </>
                );
              })()}
            </div>
          ) : activeView.includes('Income Statement') || activeView.includes('Financials') || activeView === 'Balance Sheet' || activeView === 'Cash Flow' ? (
            <FinancialsView ticker={ticker} />
            ) : activeView === 'Advanced Search' ? (
              <AdvancedSearchView />
              ) : activeView === 'Reports Generator' ? (
                <ReportsGenerator
                  setIsGeneratingReport={setIsGeneratingReport}
                  setReportSteps={setReportSteps}
                  setReportStatus={setReportStatus}
                  // Persistence Props
                  ticker={reportTicker}
                  setTicker={setReportTicker}
                  selectedTemplate={reportTemplate}
                  setSelectedTemplate={setReportTemplate}
                  reportData={reportData}
                  setReportData={setReportData}
                  progress={reportProgress}
                  setProgress={setReportProgress}
                  progressStep={reportProgressStep}
                  setProgressStep={setReportProgressStep}
                  stepsCompleted={reportStepsCompleted}
                  setStepsCompleted={setReportStepsCompleted}
                  isGenerating={isGeneratingReport}
                />
          ) : (
                <div style={{ padding: '80px 40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <div style={{ marginBottom: '24px', opacity: 0.5 }}>
                    <Terminal size={48} style={{ margin: '0 auto' }} />
                  </div>
                  <h2 style={{ color: 'var(--text-primary)', marginBottom: '12px' }}>{activeView} Analysis</h2>
                  <p>This module is currently being optimized by the Agentic engine.</p>
                  <button
                    onClick={() => setActiveView('Snapshot')}
                    style={{
                      marginTop: '24px',
                      padding: '10px 20px',
                      background: 'var(--brand-gradient)',
                      borderRadius: '8px',
                      color: '#fff',
                      fontWeight: 600
                    }}
                  >
                    Return to Snapshot
                  </button>
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
          background: isResizing ? 'rgba(255,255,255,0.08)' : 'var(--bg-app)',
          borderLeft: '1px solid rgba(255,255,255,0.05)',
          borderRight: '1px solid rgba(255,255,255,0.05)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'col-resize',
          zIndex: 10,
          position: 'relative',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          userSelect: 'none'
        }}
      >
        <div style={{
          height: '24px',
          width: '4px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '999px'
        }} />
      </div>

      <RightSidebar
        dashboardData={tickerData}
        chartOverride={chartOverride}
        setChartOverride={setChartOverride}
        onUpdateWidget={handleUpdateWidget}
        isOpen={isRightSidebarOpen}
        width={rightSidebarWidth}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        selectedComplexModel={selectedComplexModel}
        setSelectedComplexModel={setSelectedComplexModel}
        isGeneratingReport={isGeneratingReport}
        reportSteps={reportSteps}
        reportStatus={reportStatus}
      />



    </div>
  );
}

export default App;
