import { useState, useEffect, useMemo } from 'react';
import { Search } from 'lucide-react';
import type { Transaction } from '../types';
import { CATEGORY_COLORS } from '../types';
import { fetchTransactions } from '../api';

interface Props {
  period: string;
}

const ALL_CATEGORIES = Object.keys(CATEGORY_COLORS);

export function Transactions({ period }: Props) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [memberFilter, setMemberFilter] = useState('');

  useEffect(() => {
    setLoading(true);
    fetchTransactions({ period }).then(data => {
      setTransactions(data.sort((a, b) => b.date.localeCompare(a.date)));
      setLoading(false);
    });
  }, [period]);

  const members = useMemo(() => {
    const set = new Set(transactions.map(t => t.card_member).filter(Boolean));
    return Array.from(set).sort();
  }, [transactions]);

  const filtered = useMemo(() => {
    return transactions.filter(t => {
      if (categoryFilter && t.enriched_category !== categoryFilter) return false;
      if (memberFilter && t.card_member !== memberFilter) return false;
      if (search) {
        const q = search.toLowerCase();
        const matchDesc = (t.description || '').toLowerCase().includes(q);
        const matchMerchant = (t.merchant_clean || '').toLowerCase().includes(q);
        const matchCat = (t.enriched_category || '').toLowerCase().includes(q);
        if (!matchDesc && !matchMerchant && !matchCat) return false;
      }
      return true;
    });
  }, [transactions, categoryFilter, memberFilter, search]);

  const totalFiltered = filtered.reduce((s, t) => s + t.amount, 0);

  if (loading) return <div className="loading"><div className="spinner" />Loading transactions...</div>;

  return (
    <div>
      <div className="filter-bar">
        <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', pointerEvents: 'none' }} />
          <input
            type="text"
            placeholder="Search transactions..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: 36, width: '100%' }}
          />
        </div>
        <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
          <option value="">All Categories</option>
          {ALL_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={memberFilter} onChange={e => setMemberFilter(e.target.value)}>
          <option value="">All Members</option>
          {members.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>{filtered.length} transactions</h3>
          <span className="amount" style={{ fontSize: 16 }}>
            Total: ${totalFiltered.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </span>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Merchant</th>
                <th>Category</th>
                <th>Subcategory</th>
                <th>Card Member</th>
                <th>Channel</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t, i) => (
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
                  <td style={{ color: '#64748b', fontSize: 13 }}>{t.subcategory}</td>
                  <td>{t.card_member}</td>
                  <td style={{ color: '#64748b', fontSize: 13 }}>{t.purchase_channel}</td>
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
