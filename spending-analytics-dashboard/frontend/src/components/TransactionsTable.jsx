import React, { useState, useMemo } from 'react';
import { Search, ArrowUpDown, Filter, Eye, Tag, AlertCircle, Sparkles, Receipt, CheckCircle2, RotateCcw } from 'lucide-react';
import DeepReceiptModal from './DeepReceiptModal';
import { GmailLogo } from './SpendGalaxyModal';
import { getUserConfig, ALL_EXECUTIVE_USERS_LIST } from '../utils/userConfig';

const GMAIL_GROUNDED_KEYWORDS = ['amazon', 'alo yoga', 'delta', 'whole foods', 'sephora', 'grubhub', 'doordash', 'target', 'google', 'macy'];

const isGmailGroundedMerchant = (merchantName = '', desc = '') => {
  const m = (merchantName + ' ' + desc).toLowerCase();
  return GMAIL_GROUNDED_KEYWORDS.some(k => m.includes(k));
};

export default function TransactionsTable({ transactions = [], onOpenGmailAuth, onOpenTraceConsole }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [memberFilter, setMemberFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [sortField, setSortField] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedTx, setSelectedTx] = useState(null);
  const [selectedReceiptTx, setSelectedReceiptTx] = useState(null);
  const [gmailOnlyFilter, setGmailOnlyFilter] = useState(false);

  // Extract unique categories & expense types
  const categories = useMemo(() => {
    const set = new Set(transactions.map(t => t.primary_category).filter(Boolean));
    return ['ALL', ...Array.from(set)];
  }, [transactions]);

  const expenseTypes = useMemo(() => {
    const set = new Set(transactions.map(t => t.expense_type).filter(Boolean));
    return ['ALL', ...Array.from(set)];
  }, [transactions]);

  // Filter and sort transactions
  const filteredTransactions = useMemo(() => {
    return transactions
      .filter(tx => {
        const matchesSearch =
          tx.clean_merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tx.raw_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tx.primary_category.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesMember = memberFilter === 'ALL' || tx.card_member === memberFilter;
        const matchesCategory = categoryFilter === 'ALL' || tx.primary_category === categoryFilter;
        const matchesType = typeFilter === 'ALL' || tx.expense_type === typeFilter;
        const matchesGmail = !gmailOnlyFilter || isGmailGroundedMerchant(tx.clean_merchant, tx.raw_description);

        return matchesSearch && matchesMember && matchesCategory && matchesType && matchesGmail;
      })
      .sort((a, b) => {
        let aVal = a[sortField];
        let bVal = b[sortField];

        if (sortField === 'amount') {
          aVal = a.amount;
          bVal = b.amount;
        }

        if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
  }, [transactions, searchTerm, memberFilter, categoryFilter, typeFilter, gmailOnlyFilter, sortField, sortOrder]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls / Filter Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
        
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search merchant, description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 text-xs text-slate-200 pl-10 pr-4 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        {/* Filter Dropdowns & Gmail Grounded Pill */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
          {/* Gmail Grounded Toggle */}
          <button
            onClick={() => setGmailOnlyFilter(!gmailOnlyFilter)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              gmailOnlyFilter
                ? 'bg-red-500/20 text-red-200 border border-red-500/60 shadow-md shadow-red-500/20'
                : 'bg-slate-950/80 text-slate-300 border border-slate-800 hover:text-white'
            }`}
            title="Filter by transactions with verified Gmail E-Receipts"
          >
            <GmailLogo className="w-3.5 h-3.5" />
            <span>Gmail Grounded</span>
          </button>

          {/* Cardholder */}
          <select
            value={memberFilter}
            onChange={(e) => setMemberFilter(e.target.value)}
            className="bg-slate-950/80 text-xs text-slate-300 px-3 py-2 rounded-xl border border-slate-800 focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Cardholders</option>
            {ALL_EXECUTIVE_USERS_LIST.map(u => (
              <option key={u.name} value={u.name}>{u.name} ({u.short})</option>
            ))}
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
                <th className="py-3.5 px-4">Merchant & Description</th>
                <th className="py-3.5 px-4">Card Member</th>
                <th className="py-3.5 px-4">Category</th>
                <th className="py-3.5 px-4">Tags & Type</th>
                <th className="py-3.5 px-4 text-right cursor-pointer hover:text-slate-200" onClick={() => handleSort('amount')}>
                  <div className="flex items-center justify-end gap-1">
                    Amount <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3.5 px-4 text-center">Receipt Intelligence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredTransactions.map((tx) => {
                const isGmailGrounded = isGmailGroundedMerchant(tx.clean_merchant, tx.raw_description);
                const userCfg = getUserConfig(tx.card_member);
                return (
                  <tr key={tx.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">{tx.date}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {isGmailGrounded ? (
                          <span className="p-1 rounded-md bg-slate-950 border border-slate-700 shadow-sm" title="Verified with Gmail Grounding">
                            <GmailLogo className="w-3.5 h-3.5" />
                          </span>
                        ) : (
                          <span className="p-1 rounded-md bg-slate-950 border border-violet-500/30 text-violet-400" title="Synthesized by Google ADK LLM">
                            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
                          </span>
                        )}
                        <div>
                          <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                            <span>{tx.clean_merchant}</span>
                            {tx.has_return && (
                              <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.2 rounded font-bold">
                                ↩️ Returned
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-500 truncate max-w-xs">{tx.raw_description}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${userCfg.badgeClass}`}>
                        {userCfg.short} ({userCfg.tag})
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-slate-300">{tx.primary_category}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                          {tx.expense_type}
                        </span>
                        {tx.tags?.slice(0, 1).map((t, i) => (
                          <span key={i} className="text-[10px] bg-indigo-500/10 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-500/20">
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
                        onClick={() => setSelectedReceiptTx(tx)}
                        className={`px-2.5 py-1 rounded-lg border text-[11px] font-semibold transition-all flex items-center gap-1.5 mx-auto cursor-pointer ${
                          isGmailGrounded
                            ? 'bg-slate-950 hover:bg-slate-900 text-slate-200 border-slate-700 shadow-sm'
                            : 'bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border-indigo-500/30'
                        }`}
                        title={isGmailGrounded ? "View Grounded Gmail E-Receipt" : "View ADK Synthesized Receipt"}
                      >
                        {isGmailGrounded ? <GmailLogo className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5 text-violet-400" />}
                        <span>{isGmailGrounded ? 'Gmail Receipt' : 'ADK Receipt'}</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Deep Receipt Intelligence Modal */}
      {selectedReceiptTx && (
        <DeepReceiptModal
          transaction={selectedReceiptTx}
          onClose={() => setSelectedReceiptTx(null)}
          onOpenGmailAuth={onOpenGmailAuth}
          onOpenTraceConsole={onOpenTraceConsole}
        />
      )}
    </div>
  );
}
