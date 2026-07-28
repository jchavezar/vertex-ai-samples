import React, { useState, useMemo } from 'react';
import { Search, Filter, ArrowUpDown, Tag, Star, Eye, X, Check, Calendar, CreditCard, MapPin } from 'lucide-react';

export default function TransactionsTable({ transactions = [] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [memberFilter, setMemberFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [sortField, setSortField] = useState('date');
  const [sortAsc, setSortAsc] = useState(false);
  const [selectedTx, setSelectedTx] = useState(null);

  // Categories list
  const categories = useMemo(() => {
    const set = new Set(transactions.map(t => t.primary_category));
    return ['ALL', ...Array.from(set)];
  }, [transactions]);

  // Expense types
  const expenseTypes = useMemo(() => {
    const set = new Set(transactions.map(t => t.expense_type));
    return ['ALL', ...Array.from(set)];
  }, [transactions]);

  // Filtered & Sorted transactions
  const filteredTxs = useMemo(() => {
    return transactions.filter(t => {
      if (memberFilter !== 'ALL' && t.card_member.toLowerCase() !== memberFilter.toLowerCase()) return false;
      if (categoryFilter !== 'ALL' && t.primary_category !== categoryFilter) return false;
      if (typeFilter !== 'ALL' && t.expense_type !== typeFilter) return false;
      if (searchTerm) {
        const s = searchTerm.toLowerCase();
        const m = t.clean_merchant.toLowerCase();
        const r = t.raw_description.toLowerCase();
        const c = t.primary_category.toLowerCase();
        if (!m.includes(s) && !r.includes(s) && !c.includes(s)) return false;
      }
      return true;
    }).sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];
      if (sortField === 'amount') {
        valA = Math.abs(valA);
        valB = Math.abs(valB);
      }
      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });
  }, [transactions, memberFilter, categoryFilter, typeFilter, searchTerm, sortField, sortAsc]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const renderNecessityStars = (score) => {
    return (
      <div className="flex items-center gap-0.5" title={`Necessity Rating: ${score}/5`}>
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-3 h-3 ${star <= score ? 'text-amber-400 fill-amber-400' : 'text-slate-700'}`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Filters Header Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search merchant, statement..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950/80 text-xs text-slate-200 pl-9 pr-4 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        {/* Filter Dropdowns */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
          {/* Cardholder */}
          <select
            value={memberFilter}
            onChange={(e) => setMemberFilter(e.target.value)}
            className="bg-slate-950/80 text-xs text-slate-300 px-3 py-2 rounded-xl border border-slate-800 focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Cardholders</option>
            <option value="DINORAH GUERRA">Dinorah Guerra</option>
            <option value="JESUS CHAVEZ">Jesus Chavez</option>
          </select>

          {/* Category */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-950/80 text-xs text-slate-300 px-3 py-2 rounded-xl border border-slate-800 focus:outline-none cursor-pointer"
          >
            {categories.map(c => (
              <option key={c} value={c}>{c === 'ALL' ? 'All Categories' : c}</option>
            ))}
          </select>

          {/* Expense Type */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-950/80 text-xs text-slate-300 px-3 py-2 rounded-xl border border-slate-800 focus:outline-none cursor-pointer"
          >
            {expenseTypes.map(t => (
              <option key={t} value={t}>{t === 'ALL' ? 'All Expense Types' : t}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3.5 px-4 cursor-pointer hover:text-slate-200" onClick={() => handleSort('date')}>
                  <div className="flex items-center gap-1">
                    Date <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3.5 px-4 cursor-pointer hover:text-slate-200" onClick={() => handleSort('clean_merchant')}>
                  <div className="flex items-center gap-1">
                    Merchant <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3.5 px-4">AI Category</th>
                <th className="py-3.5 px-4">Behavior</th>
                <th className="py-3.5 px-4">Card Member</th>
                <th className="py-3.5 px-4">Tags</th>
                <th className="py-3.5 px-4 text-right cursor-pointer hover:text-slate-200" onClick={() => handleSort('amount')}>
                  <div className="flex items-center justify-end gap-1">
                    Amount <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3.5 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {filteredTxs.map((tx) => (
                <tr key={tx.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">{tx.date}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-100">{tx.clean_merchant}</div>
                    <div className="text-[11px] text-slate-500 truncate max-w-xs">{tx.raw_description}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-medium">
                      {tx.primary_category}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                      tx.is_refund ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      tx.expense_type === 'Lifestyle & Luxury' ? 'bg-violet-500/10 text-violet-300 border border-violet-500/20' :
                      tx.expense_type === 'Food & Dining' ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20' :
                      'bg-slate-800 text-slate-300'
                    }`}>
                      {tx.expense_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className={`text-[11px] font-medium ${tx.card_member.includes('DINORAH') ? 'text-violet-300' : 'text-cyan-300'}`}>
                      {tx.card_member.split(' ')[0]}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {tx.tags?.map((t, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-950 px-1.5 py-0.5 rounded text-slate-400 border border-slate-800">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className={`py-3 px-4 text-right font-mono font-bold whitespace-nowrap ${tx.is_refund ? 'text-emerald-400' : 'text-slate-100'}`}>
                    {tx.is_refund ? `+$${Math.abs(tx.amount).toFixed(2)}` : `$${tx.amount.toFixed(2)}`}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <button
                      onClick={() => setSelectedTx(tx)}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transaction Detail Modal */}
      {selectedTx && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="max-w-lg w-full p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-slate-100">Transaction Details</h3>
              <button onClick={() => setSelectedTx(null)} className="p-1 text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">Clean Merchant:</span>
                <span className="font-bold text-white text-sm">{selectedTx.clean_merchant}</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Amount</span>
                  <span className={`text-base font-bold font-mono ${selectedTx.is_refund ? 'text-emerald-400' : 'text-white'}`}>
                    ${selectedTx.amount.toFixed(2)}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Transaction Date</span>
                  <span className="font-semibold text-slate-200">{selectedTx.date}</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-slate-400 block">Raw Statement Line</span>
                <p className="font-mono text-slate-300 break-words">{selectedTx.raw_description}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Cardholder</span>
                  <span className="font-semibold text-slate-200">{selectedTx.card_member}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Necessity Score</span>
                  {renderNecessityStars(selectedTx.necessity_score)}
                </div>
              </div>

              {selectedTx.extended_details && (
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-slate-400 block mb-1">Extended Bank Details</span>
                  <p className="text-slate-300 whitespace-pre-line font-mono">{selectedTx.extended_details}</p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedTx(null)}
                className="px-4 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white cursor-pointer"
              >
                Close Window
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
