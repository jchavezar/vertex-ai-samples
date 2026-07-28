import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MetricCard from './components/MetricCard';
import SpendTimelineChart from './components/SpendTimelineChart';
import CategoryBreakdownChart from './components/CategoryBreakdownChart';
import ExpenseTypeChart from './components/ExpenseTypeChart';
import AIAuditDrawer from './components/AIAuditDrawer';
import CardholderComparison from './components/CardholderComparison';
import TransactionsTable from './components/TransactionsTable';
import AskAIAssistant from './components/AskAIAssistant';
import SpendGalaxyModal from './components/SpendGalaxyModal';

import { DollarSign, RefreshCw, ShoppingBag, CreditCard, Sparkles, TrendingUp, Tag, Store, Orbit } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [cardholder, setCardholder] = useState('ALL');
  const [galaxyCategory, setGalaxyCategory] = useState(null);
  
  // Data state
  const [kpis, setKpis] = useState(null);
  const [categories, setCategories] = useState([]);
  const [expenseTypes, setExpenseTypes] = useState([]);
  const [cardholdersData, setCardholdersData] = useState({});
  const [merchants, setMerchants] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [tags, setTags] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [auditReport, setAuditReport] = useState(null);
  
  // Loading states
  const [loading, setLoading] = useState(true);
  const [auditLoading, setAuditLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const API_BASE = '/api';

  const fetchData = async () => {
    setLoading(true);
    try {
      const [
        kpiRes,
        catRes,
        expRes,
        cardRes,
        merchRes,
        timeRes,
        tagsRes,
        txRes
      ] = await Promise.all([
        fetch(`${API_BASE}/kpis`),
        fetch(`${API_BASE}/analytics/categories`),
        fetch(`${API_BASE}/analytics/expense-types`),
        fetch(`${API_BASE}/analytics/cardholders`),
        fetch(`${API_BASE}/analytics/merchants`),
        fetch(`${API_BASE}/analytics/timeline`),
        fetch(`${API_BASE}/analytics/tags`),
        fetch(`${API_BASE}/transactions`)
      ]);

      const [
        kpiData,
        catData,
        expData,
        cardData,
        merchData,
        timeData,
        tagsData,
        txData
      ] = await Promise.all([
        kpiRes.json(),
        catRes.json(),
        expRes.json(),
        cardRes.json(),
        merchRes.json(),
        timeRes.json(),
        tagsRes.json(),
        txRes.json()
      ]);

      setKpis(kpiData);
      setCategories(catData);
      setExpenseTypes(expData);
      setCardholdersData(cardData);
      setMerchants(merchData);
      setTimeline(timeData);
      setTags(tagsData);
      setTransactions(txData);
    } catch (err) {
      console.error("Failed to load backend analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIAudit = async (force = false) => {
    setAuditLoading(true);
    try {
      const res = await fetch(`${API_BASE}/ai/audit-report?force_refresh=${force}`);
      const data = await res.json();
      setAuditReport(data);
    } catch (err) {
      console.error("Failed to load AI Audit Report:", err);
    } finally {
      setAuditLoading(false);
    }
  };

  const handleUploadCSV = async (file) => {
    if (!file) return;
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/upload-csv`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        alert(`CSV Upload Error: ${err.detail || 'Failed to process CSV'}`);
        return;
      }

      const data = await res.json();
      alert(`🎉 ${data.message}`);

      // Refresh all analytics & dataset
      await fetchData();
      fetchAIAudit(true);
    } catch (err) {
      console.error("Upload error:", err);
      alert("Failed to upload CSV file.");
    } finally {
      setIsUploading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchAIAudit(false);
  }, []);

  // Filter transactions when cardholder filter changes
  const displayTransactions = cardholder === 'ALL'
    ? transactions
    : transactions.filter(t => t.card_member.toLowerCase() === cardholder.toLowerCase());

  // Transactions belonging to selected galaxy category
  const galaxyTransactions = galaxyCategory
    ? transactions.filter(t => 
        t.primary_category.toLowerCase() === galaxyCategory.toLowerCase() ||
        t.expense_type.toLowerCase() === galaxyCategory.toLowerCase()
      )
    : [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans relative selection:bg-indigo-500 selection:text-white">
      {/* Background ambient glows */}
      <div className="bg-glow-purple" />
      <div className="bg-glow-cyan" />

      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        cardholder={cardholder}
        setCardholder={setCardholder}
        dateRange={kpis?.date_range || {}}
        onTriggerAIAudit={() => {
          setActiveTab('audit');
          fetchAIAudit(true);
        }}
        onUploadCSV={handleUploadCSV}
        isUploading={isUploading}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-8 relative z-10 space-y-8">
        {loading ? (
          <div className="h-96 flex flex-col items-center justify-center text-center">
            <Sparkles className="w-10 h-10 text-indigo-400 animate-spin mb-4" />
            <p className="text-sm text-slate-300 font-semibold">Loading PulseSpend Analytics Engine...</p>
            <p className="text-xs text-slate-500 mt-1">Connecting to FastAPI backend on port 8001</p>
          </div>
        ) : (
          <>
            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
              <div className="space-y-8 animate-fadeIn">
                {/* Metric Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                  <MetricCard
                    title="Gross Expenses"
                    amount={kpis?.total_gross || 0}
                    subtitle={`Across ${kpis?.total_count || 0} total transactions`}
                    icon={DollarSign}
                    color="indigo"
                    trend="+100%"
                    trendType="positive"
                  />
                  <MetricCard
                    title="Refunds & Credits"
                    amount={kpis?.total_refunds || 0}
                    subtitle="11 returned items / credits"
                    icon={RefreshCw}
                    color="emerald"
                    trend="Savings"
                    trendType="positive"
                  />
                  <MetricCard
                    title="Net Outflow"
                    amount={kpis?.total_net || 0}
                    subtitle={`Avg $${kpis?.avg_transaction} per purchase`}
                    icon={TrendingUp}
                    color="cyan"
                  />
                  <MetricCard
                    title="Top Category"
                    amount={kpis?.top_category || 'Dining'}
                    subtitle={`$${kpis?.top_category_amount?.toLocaleString()} spent`}
                    icon={ShoppingBag}
                    color="violet"
                  />
                </div>

                {/* Charts Section: Timeline & Category Doughnut */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2">
                    <SpendTimelineChart data={timeline} />
                  </div>
                  <div className="lg:col-span-1">
                    <CategoryBreakdownChart
                      data={categories}
                      onSelectCategory={(cat) => setGalaxyCategory(cat)}
                    />
                  </div>
                </div>

                {/* Charts Section: Expense Intent Bar & Merchant Leaderboard */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <ExpenseTypeChart
                    data={expenseTypes}
                    onSelectCategory={(cat) => setGalaxyCategory(cat)}
                  />

                  {/* Top Merchants Leaderboard */}
                  <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-base font-bold text-slate-100">Top 10 Merchants Leaderboard</h3>
                        <p className="text-xs text-slate-400">Highest individual merchant gross spending</p>
                      </div>
                      <Store className="w-5 h-5 text-indigo-400" />
                    </div>

                    <div className="space-y-3">
                      {merchants.slice(0, 6).map((m, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 hover:border-indigo-500/30 transition-all">
                          <div className="flex items-center gap-3">
                            <span className="w-6 h-6 rounded-lg bg-indigo-500/10 text-indigo-400 font-bold text-xs flex items-center justify-center border border-indigo-500/20">
                              #{idx + 1}
                            </span>
                            <div>
                              <p className="text-xs font-bold text-slate-200">{m.clean_merchant}</p>
                              <span className="text-[10px] text-slate-400">{m.primary_category} • {m.transaction_count} txs</span>
                            </div>
                          </div>
                          <span className="text-xs font-mono font-bold text-slate-100">${m.total_spent?.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Popular AI Hashtags Cloud */}
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <Tag className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-sm font-bold text-slate-100">AI Intelligent Micro-Tag Cloud</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((t, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                        <span className="font-semibold text-cyan-400">{t.tag}</span>
                        <span className="text-[10px] text-slate-400">({t.count} txs • ${t.total_spent.toLocaleString()})</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* AI AUDIT TAB */}
            {activeTab === 'audit' && (
              <div className="animate-fadeIn">
                <AIAuditDrawer
                  auditData={auditReport}
                  isLoading={auditLoading}
                  onRefresh={() => fetchAIAudit(true)}
                />
              </div>
            )}

            {/* CARDHOLDERS TAB */}
            {activeTab === 'cardholders' && (
              <div className="animate-fadeIn">
                <CardholderComparison cardholders={cardholdersData} />
              </div>
            )}

            {/* TRANSACTIONS LEDGER TAB */}
            {activeTab === 'transactions' && (
              <div className="animate-fadeIn space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-slate-100">Enriched Transaction Ledger</h2>
                    <p className="text-xs text-slate-400">Displaying {displayTransactions.length} transactions enriched with Gemini AI labels and necessity scores</p>
                  </div>
                </div>
                <TransactionsTable transactions={displayTransactions} />
              </div>
            )}

            {/* ASK AI CHAT TAB */}
            {activeTab === 'chat' && (
              <div className="animate-fadeIn">
                <AskAIAssistant />
              </div>
            )}
          </>
        )}
      </main>

      {/* Spend Galaxy Constellation Modal */}
      {galaxyCategory && (
        <SpendGalaxyModal
          categoryName={galaxyCategory}
          transactions={galaxyTransactions.length > 0 ? galaxyTransactions : transactions}
          onClose={() => setGalaxyCategory(null)}
        />
      )}

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 relative z-10">
        <p>PulseSpend AI • Engineered with FastAPI, React, Chart.js & Gemini 2.5 Flash</p>
      </footer>
    </div>
  );
}
