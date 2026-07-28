import React, { useRef } from 'react';
import { Sparkles, CreditCard, Calendar, UserCheck, Upload, DollarSign, MessageSquareText, LayoutDashboard, BrainCircuit, Loader2 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, cardholder, setCardholder, dateRange, onTriggerAIAudit, onUploadCSV, isUploading, availableCardholders = [] }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onUploadCSV) {
      onUploadCSV(file);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-slate-950/75 border-b border-slate-800/80 px-6 py-4 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-indigo-500/25">
            <BrainCircuit className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                PulseSpend AI
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> Gemini 2.5
              </span>
            </div>
            <p className="text-xs text-slate-400">Intelligent Expense Intelligence & Spend Galaxy Constellations</p>
          </div>
        </div>

        {/* Global Controls: Date Range, Cardholder Filter, Upload CSV, AI Audit */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-indigo-400" />
            <span>{dateRange.start || '07/02/2026'} - {dateRange.end || '07/26/2026'}</span>
          </div>

          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-lg border border-slate-800">
            <UserCheck className="w-3.5 h-3.5 text-slate-400 ml-2" />
            <select
              value={cardholder}
              onChange={(e) => setCardholder(e.target.value)}
              className="bg-transparent text-xs text-slate-200 font-medium px-2 py-1 focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-slate-900">All Members</option>
              {availableCardholders.length > 0 ? (
                availableCardholders.map(name => (
                  <option key={name} value={name} className="bg-slate-900">{name}</option>
                ))
              ) : (
                <>
                  <option value="ALEX MORGAN" className="bg-slate-900">Alex Morgan</option>
                  <option value="JORDAN TAYLOR" className="bg-slate-900">Jordan Taylor</option>
                </>
              )}
            </select>
          </div>

          {/* Hidden File Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv"
            className="hidden"
          />

          {/* Upload Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 shadow-sm transition-all cursor-pointer disabled:opacity-50"
            title="Import Amex CSV statement"
          >
            {isUploading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            ) : (
              <Upload className="w-3.5 h-3.5 text-cyan-400" />
            )}
            {isUploading ? 'Enriching CSV...' : 'Import Amex CSV'}
          </button>

          <button
            onClick={onTriggerAIAudit}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-md shadow-violet-600/20 transition-all cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            AI Audit Report
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto mt-4 pt-3 border-t border-slate-800/60 flex items-center gap-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg transition-all ${
            activeTab === 'overview'
              ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <LayoutDashboard className="w-4 h-4" />
          Dashboard Overview
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg transition-all ${
            activeTab === 'audit'
              ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          AI Patterns & Anomalies
        </button>

        <button
          onClick={() => setActiveTab('cardholders')}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg transition-all ${
            activeTab === 'cardholders'
              ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <CreditCard className="w-4 h-4" />
          Cardholder Breakdown
        </button>

        <button
          onClick={() => setActiveTab('transactions')}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg transition-all ${
            activeTab === 'transactions'
              ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <DollarSign className="w-4 h-4" />
          Spending Ledger
        </button>

        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg transition-all ${
            activeTab === 'chat'
              ? 'bg-amber-600/20 text-amber-300 border border-amber-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
          }`}
        >
          <MessageSquareText className="w-4 h-4" />
          Ask AI Assistant
        </button>
      </div>
    </header>
  );
}
