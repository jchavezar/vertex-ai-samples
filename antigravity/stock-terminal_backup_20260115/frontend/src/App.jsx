import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import DashboardHeader from './components/DashboardHeader';
import PerformanceChart from './components/PerformanceChart';
import KeyStats from './components/KeyStats';
import AgentInsights from './components/AgentInsights';
import SummaryPanel from './components/SummaryPanel';
import RightSidebar from './components/RightSidebar';

function App() {
  const [ticker, setTicker] = useState('FDS'); // Default to FactSet
  const [tickerData, setTickerData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('Snapshot');

  useEffect(() => {
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

  return (
    <div className="app-container">
      <Sidebar setTicker={setTicker} activeView={activeView} setActiveView={setActiveView} />

      <main className="main-content">
        <DashboardHeader ticker={ticker} externalData={tickerData} loading={loading} />

        <div className="content-scrollable">
          {activeView === 'Snapshot' ? (
            <div className="grid-layout">
              <div style={{ gridColumn: 'span 12' }}>
                <AgentInsights ticker={ticker} />
              </div>

              <div style={{ gridColumn: 'span 8' }}>
                <PerformanceChart ticker={ticker} externalData={tickerData} />
              </div>
              <div style={{ gridColumn: 'span 4' }}>
                <SummaryPanel ticker={ticker} externalData={tickerData} />
              </div>

              <div style={{ gridColumn: 'span 3' }}>
                <KeyStats section="Trading" ticker={ticker} externalData={tickerData} />
              </div>
              <div style={{ gridColumn: 'span 3' }}>
                <KeyStats section="Valuation" ticker={ticker} externalData={tickerData} />
              </div>
              <div style={{ gridColumn: 'span 3' }}>
                <KeyStats section="Dividends" ticker={ticker} externalData={tickerData} />
              </div>
              <div style={{ gridColumn: 'span 3' }}>
                <KeyStats section="Estimates" ticker={ticker} externalData={tickerData} />
              </div>
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
              <h2>{activeView} View</h2>
              <p>This section is currently under development. Please check back later or use the Snapshot view.</p>
            </div>
          )}
        </div>
      </main>

      <RightSidebar dashboardData={tickerData} />
    </div>
  );
}

export default App;
