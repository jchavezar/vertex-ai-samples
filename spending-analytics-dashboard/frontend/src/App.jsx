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
import SubscriptionsTracker from './components/SubscriptionsTracker';
import GmailAuthModal from './components/GmailAuthModal';
import PipelineTraceConsole from './components/PipelineTraceConsole';
import UploadStatementModal from './components/UploadStatementModal';

import { DollarSign, RefreshCw, ShoppingBag, CreditCard, Sparkles, TrendingUp, Tag, Store, Orbit, Repeat, Terminal } from 'lucide-react';

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
  const [subscriptionsData, setSubscriptionsData] = useState(null);
  const [auditReport, setAuditReport] = useState(null);
  const [gmailStatus, setGmailStatus] = useState({ connected: false, email: '' });
  
  // Modal / Drawer state
  const [isGmailAuthOpen, setIsGmailAuthOpen] = useState(false);
  const [isTraceConsoleOpen, setIsTraceConsoleOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [pendingUploadFiles, setPendingUploadFiles] = useState([]);
  const [toastNotification, setToastNotification] = useState(null); // { message, type: 'success'|'error'|'info' }

  // Loading states
  const [loading, setLoading] = useState(true);
  const [auditLoading, setAuditLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const showToast = (message, type = 'success') => {
    setToastNotification({ message, type });
    setTimeout(() => setToastNotification(null), 5000);
  };

  const API_BASE = '/api';

  const fetchGmailStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/gmail/status`);
      if (res.ok) {
        const data = await res.json();
        setGmailStatus(data);
      }
    } catch (err) {
      console.error("Failed to fetch Gmail status:", err);
    }
  };

  const handleConnectGmail = async (email) => {
    try {
      const res = await fetch(`${API_BASE}/auth/gmail/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (res.ok) {
        const data = await res.json();
        setGmailStatus(data);
        setIsGmailAuthOpen(false);
      }
    } catch (err) {
      console.error("Failed to connect Gmail:", err);
    }
  };

  const handleDisconnectGmail = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/gmail/disconnect`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        setGmailStatus(data);
      }
    } catch (err) {
      console.error("Failed to disconnect Gmail:", err);
    }
  };

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
        txRes,
        subRes
      ] = await Promise.all([
        fetch(`${API_BASE}/kpis`).catch(() => null),
        fetch(`${API_BASE}/analytics/categories`).catch(() => null),
        fetch(`${API_BASE}/analytics/expense-types`).catch(() => null),
        fetch(`${API_BASE}/analytics/cardholders`).catch(() => null),
        fetch(`${API_BASE}/analytics/merchants`).catch(() => null),
        fetch(`${API_BASE}/analytics/timeline`).catch(() => null),
        fetch(`${API_BASE}/analytics/tags`).catch(() => null),
        fetch(`${API_BASE}/transactions`).catch(() => null),
        fetch(`${API_BASE}/analytics/subscriptions`).catch(() => null)
      ]);

      const kpiData = kpiRes && kpiRes.ok ? await kpiRes.json() : null;
      const catData = catRes && catRes.ok ? await catRes.json() : [];
      const expData = expRes && expRes.ok ? await expRes.json() : [];
      const cardData = cardRes && cardRes.ok ? await cardRes.json() : {};
      const merchData = merchRes && merchRes.ok ? await merchRes.json() : [];
      const timeData = timeRes && timeRes.ok ? await timeRes.json() : [];
      const tagsData = tagsRes && tagsRes.ok ? await tagsRes.json() : [];
      const txData = txRes && txRes.ok ? await txRes.json() : [];
      const subData = subRes && subRes.ok ? await subRes.json() : null;

      if (kpiData) setKpis(kpiData);
      if (catData) setCategories(catData);
      if (expData) setExpenseTypes(expData);
      if (cardData) setCardholdersData(cardData);
      if (merchData) setMerchants(merchData);
      if (timeData) setTimeline(timeData);
      if (tagsData) setTags(tagsData);
      if (txData) setTransactions(txData);
      if (subData) setSubscriptionsData(subData);
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

  const handleExecuteUpload = async (files, isFullRerun) => {
    if (!files || (Array.isArray(files) && files.length === 0)) return;
    setIsUploading(true);
    if (isFullRerun) {
      setIsTraceConsoleOpen(true); // Open live trace console to watch pipeline execution
    }
    try {
      const fileList = Array.isArray(files) ? files : [files];
      const formData = new FormData();
      
      fileList.forEach(f => {
        formData.append('files', f);
      });
      formData.append('run_pipeline', isFullRerun ? 'true' : 'false');

      const res = await fetch(`${API_BASE}/upload-csv`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        showToast(`Statement Ingestion Error: ${err.detail || 'Failed to process statement files'}`, 'error');
        return;
      }

      const data = await res.json();
      setIsUploadModalOpen(false);
      showToast(`🎉 ${data.message}`, 'success');

      // Refresh all analytics, transactions, subscriptions & dataset
      await fetchData();
      fetchAIAudit(true);
    } catch (err) {
      console.error("Upload error:", err);
      showToast("Failed to upload statement files.", 'error');
    } finally {
      setIsUploading(false);
    }
  };


  useEffect(() => {
    fetchData();
    fetchAIAudit(false);
    fetchGmailStatus();
  }, []);

  // Available cardholders list
  const availableCardholders = Object.keys(cardholdersData);

  // Filter transactions when cardholder filter changes
  const displayTransactions = cardholder === 'ALL'
    ? transactions
    : transactions.filter(t => t.card_member.toLowerCase().includes(cardholder.toLowerCase()));

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
        availableCardholders={availableCardholders}
        gmailStatus={gmailStatus}
        onOpenGmailAuth={() => setIsGmailAuthOpen(true)}
        onOpenTraceConsole={() => setIsTraceConsoleOpen(true)}
        onTriggerAIAudit={() => {
          setActiveTab('audit');
          fetchAIAudit(true);
        }}
        onUploadCSV={(files) => {
          setPendingUploadFiles(files);
          setIsUploadModalOpen(true);
        }}
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
                {/* Metric Cards Grid: Clear Separation of Purchases, Real Returns, and Statement Payments */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  <MetricCard
                    title="Gross Purchases"
                    amount={kpis?.total_gross || 0}
                    subtitle={`${kpis?.purchases_count || 0} purchase charges`}
                    icon={DollarSign}
                    color="indigo"
                    trendType="positive"
                  />
                  <MetricCard
                    title="Real Merchant Returns"
                    amount={kpis?.total_merchant_returns || kpis?.total_refunds || 0}
                    subtitle={`${kpis?.returns_count || 0} merchandise refunds`}
                    icon={RefreshCw}
                    color="emerald"
                    trend="Refunded"
                    trendType="positive"
                  />
                  <MetricCard
                    title="Net Actual Spend"
                    amount={kpis?.total_net || 0}
                    subtitle="Purchases minus Returns"
                    icon={TrendingUp}
                    color="cyan"
                  />
                  <MetricCard
                    title="Statement Payments"
                    amount={kpis?.total_statement_payments || 0}
                    subtitle={`${kpis?.payments_count || 0} autopay/bank payouts`}
                    icon={CreditCard}
                    color="amber"
                  />
                  <MetricCard
                    title="Top Spend Category"
                    amount={kpis?.top_category || 'Dining'}
                    subtitle={`$${kpis?.top_category_amount?.toLocaleString()} spent`}
                    icon={ShoppingBag}
                    color="violet"
                  />
                </div>

                {/* Recurring Subscriptions Tracker Banner */}
                {subscriptionsData && (
                  <SubscriptionsTracker
                    subscriptionData={subscriptionsData}
                    cardholderFilter={cardholder}
                  />
                )}

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
                        <h3 className="text-base font-bold text-slate-100">Top Merchants Leaderboard</h3>
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

            {/* AI AUDIT & RECOMMENDATIONS TAB */}
            {activeTab === 'audit' && (
              <div className="animate-fadeIn">
                <AIAuditDrawer
                  auditData={auditReport}
                  isLoading={auditLoading}
                  onRefresh={() => fetchAIAudit(true)}
                />
              </div>
            )}

            {/* SUBSCRIPTIONS TAB */}
            {activeTab === 'subscriptions' && (
              <div className="animate-fadeIn">
                {subscriptionsData ? (
                  <SubscriptionsTracker
                    subscriptionData={subscriptionsData}
                    cardholderFilter={cardholder}
                  />
                ) : (
                  <div className="p-12 text-center text-slate-400">Loading recurring subscriptions...</div>
                )}
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
                    <p className="text-xs text-slate-400">Displaying {displayTransactions.length} transactions with cross-statement returns & AI necessity scores</p>
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

      {/* Upload Statement Modal with Agentic Pipeline Option */}
      <UploadStatementModal
        isOpen={isUploadModalOpen}
        files={pendingUploadFiles}
        isUploading={isUploading}
        gmailStatus={gmailStatus}
        onConfirmUpload={handleExecuteUpload}
        onCancel={() => setIsUploadModalOpen(false)}
        onOpenGmailAuth={() => {
          setIsUploadModalOpen(false);
          setIsGmailAuthOpen(true);
        }}
      />

      {/* Gmail OAuth Connection Modal */}
      {isGmailAuthOpen && (
        <GmailAuthModal
          authStatus={gmailStatus}
          onConnect={handleConnectGmail}
          onDisconnect={handleDisconnectGmail}
          onClose={() => setIsGmailAuthOpen(false)}
        />
      )}

      {/* Real-Time ADK Pipeline Trace & Debug Console */}
      <PipelineTraceConsole
        isOpen={isTraceConsoleOpen}
        onClose={() => setIsTraceConsoleOpen(false)}
      />

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 relative z-10">
        <p>PulseSpend AI • Powered by FastAPI, React, Chart.js & Gemini 3.7 Flash</p>
      </footer>

      {/* Floating Glass Toast Notification */}
      {toastNotification && (
        <div className="fixed top-6 right-6 z-50 animate-bounce transition-all">
          <div className={`px-5 py-3.5 rounded-2xl border backdrop-blur-2xl shadow-2xl flex items-center gap-3 text-xs font-semibold ${
            toastNotification.type === 'error'
              ? 'bg-red-950/90 border-red-500/50 text-red-200 shadow-red-500/20'
              : 'bg-slate-900/90 border-indigo-500/50 text-slate-100 shadow-indigo-500/20'
          }`}>
            <Sparkles className={`w-4 h-4 shrink-0 ${toastNotification.type === 'error' ? 'text-red-400' : 'text-cyan-400 animate-spin'}`} />
            <span>{toastNotification.message}</span>
            <button
              onClick={() => setToastNotification(null)}
              className="ml-2 text-slate-400 hover:text-white cursor-pointer"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
