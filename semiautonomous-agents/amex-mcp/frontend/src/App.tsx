import { useState, useEffect } from 'react';
import type { Page, StatementSummary } from './types';
import { fetchStatements } from './api';
import { Sidebar } from './components/Sidebar';
import { PeriodSelector } from './components/PeriodSelector';
import { Dashboard } from './pages/Dashboard';
import { Transactions } from './pages/Transactions';
import { Reports } from './pages/Reports';

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [periods, setPeriods] = useState<StatementSummary[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('');

  useEffect(() => {
    fetchStatements().then((data) => {
      setPeriods(data);
      if (data.length > 0) setSelectedPeriod(data[0].period);
    });
  }, []);

  const renderPage = () => {
    if (!selectedPeriod) return <div className="loading"><div className="spinner" />Loading...</div>;
    switch (page) {
      case 'dashboard':
        return <Dashboard period={selectedPeriod} periods={periods} />;
      case 'transactions':
        return <Transactions period={selectedPeriod} />;
      case 'reports':
        return <Reports period={selectedPeriod} />;
      default:
        return <Dashboard period={selectedPeriod} periods={periods} />;
    }
  };

  const pageTitle: Record<Page, string> = {
    dashboard: 'Dashboard',
    transactions: 'Transactions',
    reports: 'Reports',
    subscriptions: 'Subscriptions',
    insights: 'Insights',
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={page} onNavigate={setPage} />
      <main className="main-content">
        <div className="page-header">
          <h2>{pageTitle[page]}</h2>
          <PeriodSelector
            periods={periods}
            selected={selectedPeriod}
            onChange={setSelectedPeriod}
          />
        </div>
        {renderPage()}
      </main>
    </div>
  );
}
