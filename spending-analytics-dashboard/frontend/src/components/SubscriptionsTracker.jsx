import React, { useState } from 'react';
import { Repeat, Sparkles, DollarSign, Calendar, AlertCircle, CheckCircle, ShieldAlert, ArrowUpRight, Filter } from 'lucide-react';
import { getUserConfig } from '../utils/userConfig';

export default function SubscriptionsTracker({ subscriptionData, cardholderFilter = 'ALL' }) {
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  
  if (!subscriptionData || !subscriptionData.subscriptions) {
    return null;
  }

  const {
    subscription_count,
    total_monthly_recurring,
    total_annual_projected,
    potential_annual_savings,
    subscriptions = []
  } = subscriptionData;

  // Filter subscriptions by cardholder and category
  const filteredSubs = subscriptions.filter(sub => {
    if (cardholderFilter !== 'ALL' && sub.card_member && !sub.card_member.toLowerCase().includes(cardholderFilter.toLowerCase())) {
      return false;
    }
    if (selectedCategory !== 'ALL' && sub.category !== selectedCategory) {
      return false;
    }
    return true;
  });

  const categories = ['ALL', ...Array.from(new Set(subscriptions.map(s => s.category).filter(Boolean)))];

  const getMemberTag = (memberName) => {
    if (!memberName) return null;
    const userCfg = getUserConfig(memberName);
    return (
      <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border inline-flex items-center gap-1 ${userCfg.badgeClass}`}>
        <span>{userCfg.iconEmoji}</span>
        <span>{userCfg.short} ({userCfg.tag})</span>
      </span>
    );
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl space-y-6">
      {/* Header & KPI Summary */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Repeat className="w-4 h-4" />
            </div>
            <h3 className="text-base font-bold text-white tracking-tight">Recurring Subscriptions & Fixed Costs</h3>
            <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
              {filteredSubs.length} Active Services
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Automated recurring charge detection and AI cost-optimization across statements
          </p>
        </div>

        {/* Quick KPI Stats */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Monthly Burn</span>
            <span className="text-sm font-extrabold font-mono text-white">${total_monthly_recurring.toLocaleString()}/mo</span>
          </div>
          <div className="px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Annual Projected</span>
            <span className="text-sm font-extrabold font-mono text-indigo-300">${total_annual_projected.toLocaleString()}/yr</span>
          </div>
          <div className="px-3.5 py-2 rounded-xl bg-emerald-950/30 border border-emerald-500/30">
            <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider block">AI Potential Savings</span>
            <span className="text-sm font-extrabold font-mono text-emerald-300">~${potential_annual_savings.toLocaleString()}/yr</span>
          </div>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`text-xs px-3 py-1 rounded-xl font-medium whitespace-nowrap transition-all cursor-pointer ${
              selectedCategory === cat
                ? 'bg-indigo-600 text-white font-bold shadow-md shadow-indigo-600/20'
                : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {cat === 'ALL' ? 'All Categories' : cat}
          </button>
        ))}
      </div>

      {/* Subscription Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSubs.map((sub) => (
          <div
            key={sub.id}
            className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/90 hover:border-indigo-500/40 transition-all flex flex-col justify-between space-y-3 group"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                    {sub.name}
                  </h4>
                  <span className="text-[11px] text-slate-400">{sub.category}</span>
                </div>
                {getMemberTag(sub.card_member)}
              </div>

              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-lg font-extrabold font-mono text-indigo-300">
                  ${sub.monthly_amount.toFixed(2)}
                </span>
                <span className="text-[10px] text-slate-400 font-semibold uppercase">
                  / {sub.billing_frequency.toLowerCase()}
                </span>
                <span className="text-[11px] text-slate-400 font-mono ml-auto">
                  ${sub.annual_projected.toFixed(0)}/yr
                </span>
              </div>
            </div>

            {/* AI Optimization Tip */}
            {sub.optimization_tip && (
              <div className="p-2.5 rounded-lg bg-indigo-950/30 border border-indigo-500/20 flex items-start gap-2">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                <p className="text-[10px] text-indigo-200 leading-snug">{sub.optimization_tip}</p>
              </div>
            )}

            <div className="flex items-center justify-between text-[10px] text-slate-400 pt-2 border-t border-slate-800/60">
              <span>Last Billed: {sub.last_billed_date || 'Current Month'}</span>
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Active
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
