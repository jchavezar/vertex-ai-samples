import { useState, useEffect } from 'react';
import type { SankeyData, TrendsData } from '../types';
import { fetchSankey, fetchTrends } from '../api';
import { SankeyDiagram } from '../charts/SankeyDiagram';
import { SpendingBar } from '../charts/SpendingBar';
import { MemberComparison } from '../charts/MemberComparison';

interface Props {
  period: string;
}

export function Reports({ period }: Props) {
  const [sankey, setSankey] = useState<SankeyData>({ nodes: [], links: [] });
  const [trends, setTrends] = useState<TrendsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchSankey(period),
      fetchTrends(6),
    ]).then(([sankeyData, trendsData]) => {
      setSankey(sankeyData);
      setTrends(trendsData);
      setLoading(false);
    });
  }, [period]);

  if (loading) return <div className="loading"><div className="spinner" />Loading reports...</div>;

  return (
    <div>
      <div className="reports-section">
        <div className="card">
          <div className="card-header">
            <h3>Cash Flow: Category &rarr; Merchant</h3>
          </div>
          <SankeyDiagram data={sankey} />
        </div>
      </div>

      {trends && (
        <div className="reports-section">
          <div className="card">
            <div className="card-header">
              <h3>Monthly Spending</h3>
            </div>
            <SpendingBar data={trends.period_totals} />
          </div>
        </div>
      )}

      {trends?.member_totals && Object.keys(trends.member_totals).length > 0 && (
        <div className="reports-section">
          <div className="card">
            <div className="card-header">
              <h3>Spending by Card Member</h3>
            </div>
            <MemberComparison data={trends.member_totals} />
          </div>
        </div>
      )}
    </div>
  );
}
