import { useState, useEffect } from 'react';
import type { CategoryBreakdown, Transaction, StatementSummary } from '../types';
import { CATEGORY_COLORS } from '../types';
import { fetchCategories, fetchTransactions } from '../api';
import { SummaryCard } from '../components/SummaryCard';
import { CategoryDonut } from '../charts/CategoryDonut';

interface Props {
  period: string;
  periods: StatementSummary[];
}

export function Dashboard({ period, periods }: Props) {
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [totalSpend, setTotalSpend] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchCategories(period),
      fetchTransactions({ period }),
    ]).then(([catData, txnData]) => {
      setCategories(catData.categories);
      setTotalSpend(catData.total_spend);
      setTransactions(txnData.sort((a, b) => b.date.localeCompare(a.date)).slice(0, 10));
      setLoading(false);
    });
  }, [period]);

  if (loading) return <div className="loading"><div className="spinner" />Loading dashboard...</div>;

  const currentIdx = periods.findIndex(p => p.period === period);
  const prevPeriod = currentIdx >= 0 && currentIdx < periods.length - 1 ? periods[currentIdx + 1] : null;
  const prevTotal = prevPeriod?.total_debits || 0;
  const change = prevTotal > 0 ? ((totalSpend - prevTotal) / prevTotal) * 100 : undefined;
  const txnCount = categories.reduce((s, c) => s + c.count, 0);

  return (
    <div>
      <div className="summary-grid">
        <SummaryCard
          label="Total Spend"
          value={totalSpend.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          prefix="$"
          change={change}
        />
        <SummaryCard
          label="Transactions"
          value={String(txnCount)}
        />
        <SummaryCard
          label="Categories"
          value={String(categories.length)}
        />
        <SummaryCard
          label="Top Category"
          value={categories[0]?.category || '-'}
        />
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h3>Spending by Category</h3>
          </div>
          <CategoryDonut categories={categories} totalSpend={totalSpend} />
        </div>
        <div className="card">
          <div className="card-header">
            <h3>Top Categories</h3>
          </div>
          <ul className="merchant-list">
            {categories.slice(0, 8).map(c => (
              <li key={c.category} className="merchant-item">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 10, height: 10, borderRadius: '50%',
                    background: CATEGORY_COLORS[c.category] || '#94a3b8',
                  }} />
                  <span className="merchant-name">{c.category}</span>
                </div>
                <div>
                  <span className="merchant-amount">
                    ${c.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                  <span className="merchant-count">{c.percentage}%</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Recent Transactions</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Merchant</th>
                <th>Category</th>
                <th>Card Member</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t, i) => (
                <tr key={i}>
                  <td style={{ whiteSpace: 'nowrap' }}>{t.date}</td>
                  <td>{t.merchant_clean || t.description}</td>
                  <td>
                    <span
                      className="category-pill"
                      style={{
                        backgroundColor: (CATEGORY_COLORS[t.enriched_category] || '#94a3b8') + '18',
                        color: CATEGORY_COLORS[t.enriched_category] || '#94a3b8',
                      }}
                    >
                      {t.enriched_category}
                    </span>
                  </td>
                  <td>{t.card_member}</td>
                  <td style={{ textAlign: 'right' }}>
                    <span className={`amount ${t.amount < 0 ? 'credit' : 'debit'}`}>
                      {t.amount < 0 ? '-' : ''}${Math.abs(t.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
