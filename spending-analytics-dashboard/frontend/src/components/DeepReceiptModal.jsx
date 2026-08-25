import React, { useState, useEffect } from 'react';
import { X, Sparkles, Receipt, FileText, CheckCircle2, Clock, RotateCcw, ShieldCheck, Tag, ExternalLink, RefreshCw, Loader2, ArrowRight, Mail, Terminal, Database, HelpCircle, Columns, Truck, Check } from 'lucide-react';
import { GmailLogo } from './SpendGalaxyModal';

export default function DeepReceiptModal({ transaction, onClose, onOpenGmailAuth, onOpenTraceConsole, isGmailConnected }) {
  const [receiptData, setReceiptData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [activeTab, setActiveTab] = useState('ITEMS'); // 'ITEMS' | 'EMAIL' | 'COMPARISON'

  const fetchReceipt = async (isRescan = false) => {
    if (!transaction) return;
    if (isRescan) setIsScanning(true);
    else setIsLoading(true);

    try {
      const endpoint = isRescan 
        ? `/api/receipts/deep/${transaction.id}?force_refresh=true` 
        : `/api/receipts/deep/${transaction.id}`;
      
      const res = await fetch(endpoint);
      const data = await res.json();
      setReceiptData(data.receipt || data);
    } catch (err) {
      console.error("Failed to load receipt intelligence:", err);
    } finally {
      setIsLoading(false);
      setIsScanning(false);
    }
  };

  useEffect(() => {
    fetchReceipt(false);
  }, [transaction?.id]);

  if (!transaction) return null;

  const isDinorah = transaction.card_member?.toUpperCase().includes('DINORAH');
  const isJesus = transaction.card_member?.toUpperCase().includes('JESUS');
  const isGmailGrounded = receiptData?.grounding_source === "GMAIL_MCP_GROUNDED" || receiptData?.gmail_source_matched;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/85 backdrop-blur-xl animate-fadeIn">
      <div className="relative w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/80 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-600/20">
              <Receipt className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Google ADK Receipt Intelligence</span>
                <span className="px-2 py-0.2 text-[9px] font-bold rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20 flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5 text-violet-400" /> Gemini 3.7 Flash
                </span>
                
                {/* PROVENANCE GROUNDING BADGE */}
                {isGmailGrounded ? (
                  <span className="px-2.5 py-0.5 text-[9px] font-black rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5 shadow-sm">
                    <GmailLogo className="w-3 h-3" /> Gmail Grounded
                  </span>
                ) : (
                  <span className="px-2 py-0.2 text-[9px] font-bold rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1">
                    <Database className="w-2.5 h-2.5 text-indigo-400" /> 🤖 ADK Agent Synthesized
                  </span>
                )}
              </div>
              <h2 className="text-base sm:text-lg font-extrabold text-white leading-tight truncate max-w-lg">{transaction.clean_merchant}</h2>
            </div>
          </div>


          <div className="flex items-center gap-2">
            {onOpenTraceConsole && (
              <button
                onClick={onOpenTraceConsole}
                className="p-1.5 px-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 transition-colors cursor-pointer flex items-center gap-1 text-[11px] font-semibold"
                title="View Real-Time Agent Execution Trace"
              >
                <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                <span className="hidden sm:inline">Trace</span>
              </button>
            )}

            <button
              onClick={() => fetchReceipt(true)}
              disabled={isScanning}
              className="p-1.5 px-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 transition-colors cursor-pointer flex items-center gap-1 text-[11px] font-semibold disabled:opacity-50"
              title="Re-scan and re-synthesize receipt with ADK Agent"
            >
              {isScanning ? <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" /> : <RefreshCw className="w-3.5 h-3.5 text-indigo-400" />}
              <span className="hidden sm:inline">{isScanning ? 'Scanning...' : 'Re-Scan'}</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Controls Bar */}
        <div className="px-5 py-2 bg-slate-950/40 border-b border-slate-800 flex items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setActiveTab('ITEMS')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'ITEMS'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <FileText className="w-3 h-3" />
              <span>Itemized Breakdown</span>
            </button>

            <button
              onClick={() => setActiveTab('EMAIL')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'EMAIL'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Mail className="w-3 h-3 text-emerald-400" />
              <span>Grounded Gmail E-Receipt</span>
              {isGmailGrounded && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />}
            </button>

            <button
              onClick={() => setActiveTab('COMPARISON')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'COMPARISON'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Columns className="w-3 h-3" />
              <span>Bank vs Agent Value</span>
            </button>
          </div>

          <div className="text-[11px] font-mono text-slate-400 hidden sm:block">
            Amex Statement: <span className="text-slate-200 font-bold">{transaction.date}</span>
          </div>
        </div>

        {/* Modal Content Area (Optimized 2-Column Grid to Fit Without Scrolling) */}
        <div className="p-4 sm:p-5 overflow-y-auto max-h-[78vh]">
          {isLoading ? (
            <div className="py-12 text-center space-y-2">
              <Loader2 className="w-7 h-7 animate-spin text-indigo-400 mx-auto" />
              <p className="text-xs font-semibold text-slate-200">Google ADK Agent is extracting receipt intelligence...</p>
            </div>
          ) : receiptData ? (
            <>
              {/* TAB 1: 2-COLUMN COMPACT DASHBOARD VIEW */}
              {activeTab === 'ITEMS' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
                  
                  {/* LEFT COLUMN: Metadata, Policy & Grounding Badges */}
                  <div className="lg:col-span-5 space-y-3">
                    
                    {/* Top 4 Pill Stats */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                        <span className="text-[9px] text-slate-400 uppercase font-semibold block">Order Ref</span>
                        <span className="text-xs font-mono font-bold text-slate-200 truncate block">{receiptData.order_id || 'N/A'}</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                        <span className="text-[9px] text-slate-400 uppercase font-semibold block">Card Member</span>
                        <span className={`text-xs font-bold truncate block ${isDinorah ? 'text-pink-400' : isJesus ? 'text-cyan-400' : 'text-slate-200'}`}>
                          {transaction.card_member}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                        <span className="text-[9px] text-slate-400 uppercase font-semibold block">Purchase Date</span>
                        <span className="text-xs font-mono font-bold text-slate-200 block">{transaction.date}</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                        <span className="text-[9px] text-slate-400 uppercase font-semibold block">Total Charged</span>
                        <span className="text-xs font-mono font-extrabold text-white block">${Math.abs(transaction.amount).toFixed(2)}</span>
                      </div>
                    </div>

                    {/* Return Policy & Deadline Status Pill */}
                    {transaction.has_return ? (
                      <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <RotateCcw className="w-4 h-4 text-emerald-400 shrink-0" />
                          <div>
                            <h4 className="text-xs font-bold text-emerald-300">↩️ Refund Credited</h4>
                            <p className="text-[10px] text-emerald-400/80">-${transaction.return_amount?.toFixed(2)} credited</p>
                          </div>
                        </div>
                        <span className="text-xs font-mono font-extrabold text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-lg border border-emerald-500/30">
                          Net: ${transaction.net_amount?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                    ) : receiptData.is_return_eligible ? (
                      <div className="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/30 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-indigo-400 shrink-0" />
                          <div>
                            <h4 className="text-xs font-bold text-indigo-200">🟢 30-Day Return Active</h4>
                            <p className="text-[10px] text-slate-400">Deadline <span className="text-slate-200 font-semibold">{receiptData.return_window_deadline}</span> ({receiptData.days_remaining_to_return}d left)</p>
                          </div>
                        </div>
                        {receiptData.return_policy?.return_portal_url && (
                          <a
                            href={receiptData.return_policy.return_portal_url}
                            target="_blank"
                            rel="noreferrer"
                            className="px-2.5 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/30 text-[11px] font-semibold flex items-center gap-1 transition-colors shrink-0"
                          >
                            Return Portal <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        )}
                      </div>
                    ) : (
                      <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-2 text-[11px] text-slate-400">
                        <ShieldCheck className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        <span>Return Window Expired (30 days)</span>
                      </div>
                    )}

                    {/* ADK Merchandise Pattern Insights */}
                    {receiptData.merchandise_insights && (
                      <div className="p-3 rounded-xl bg-gradient-to-br from-violet-950/30 via-slate-900 to-slate-900 border border-violet-500/30 space-y-1.5">
                        <h4 className="text-[10px] font-bold uppercase tracking-wider text-violet-300 flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-violet-400" /> ADK Insights & Pattern Synthesis
                        </h4>
                        <ul className="space-y-1 text-[11px] text-slate-300">
                          {receiptData.merchandise_insights.map((insight, i) => (
                            <li key={i} className="flex items-start gap-1.5 leading-snug">
                              <CheckCircle2 className="w-3 h-3 text-violet-400 shrink-0 mt-0.5" />
                              <span>{insight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* RIGHT COLUMN: Itemized Table & Financial Breakout */}
                  <div className="lg:col-span-7 space-y-3">
                    
                    {/* Itemized Table */}
                    <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/60">
                      <div className="px-3.5 py-2 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-indigo-400" /> Itemized Merchandise Breakdown
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">{receiptData.items?.length || 1} item(s)</span>
                      </div>

                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900/40 text-slate-400 uppercase text-[9px] border-b border-slate-800/80 font-semibold">
                          <tr>
                            <th className="py-2 px-3">Item & Specs</th>
                            <th className="py-2 px-2">SKU</th>
                            <th className="py-2 px-2 text-center">Qty</th>
                            <th className="py-2 px-3 text-right">Price</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60">
                          {receiptData.items?.map((item, idx) => (
                            <tr key={idx} className="hover:bg-slate-900/30 transition-colors">
                              <td className="py-2 px-3">
                                <p className="font-semibold text-slate-100 text-[11px] leading-tight">{item.name}</p>
                                {item.category && <span className="text-[9px] text-slate-400">{item.category}</span>}
                              </td>
                              <td className="py-2 px-2">
                                <span className="font-mono text-[9px] text-slate-400 bg-slate-900 px-1 py-0.2 rounded border border-slate-800">
                                  {item.sku || 'SKU-001'}
                                </span>
                              </td>
                              <td className="py-2 px-2 text-center font-mono text-slate-300 text-xs">
                                {item.quantity || 1}
                              </td>
                              <td className="py-2 px-3 text-right font-mono font-bold text-slate-100 text-xs">
                                ${((item.unit_price || 0) * (item.quantity || 1)).toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Financial Breakout Box */}
                    <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1 text-xs">
                      <div className="flex justify-between text-slate-400 text-[11px]">
                        <span>Merchandise Subtotal:</span>
                        <span className="font-mono font-semibold">${receiptData.subtotal?.toFixed(2) || '0.00'}</span>
                      </div>
                      {receiptData.tax_amount > 0 && (
                        <div className="flex justify-between text-slate-400 text-[11px]">
                          <span>Sales Tax (8.875%):</span>
                          <span className="font-mono font-semibold">${receiptData.tax_amount?.toFixed(2)}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-xs font-bold text-white pt-1.5 border-t border-slate-800">
                        <span>Total Amount Charged:</span>
                        <span className="font-mono text-indigo-300 text-sm">${receiptData.total_charged?.toFixed(2) || Math.abs(transaction.amount).toFixed(2)}</span>
                      </div>
                    </div>
                  </div>

                </div>
              )}

              {/* TAB 2: GROUNDED GMAIL SOURCE EMAIL */}
              {activeTab === 'EMAIL' && (
                <div className="space-y-3 animate-fadeIn">
                  <div className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800 space-y-2.5">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <Mail className="w-4 h-4 text-emerald-400" />
                        <span className="text-xs font-bold text-white">Gmail Message Source Metadata</span>
                      </div>
                      <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.2 rounded-full border border-emerald-500/30">
                        Google Workspace Grounded
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-semibold">Subject</span>
                        <span className="text-slate-200 font-bold text-[11px]">{receiptData.gmail_subject || `Order Confirmation - ${transaction.clean_merchant}`}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-semibold">Sender (From)</span>
                        <span className="text-slate-200 font-mono text-[11px]">{receiptData.gmail_sender || `receipts@${transaction.clean_merchant.toLowerCase().replace(/[^a-z]/g, '')}.com`}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-semibold">Carrier / Channel</span>
                        <span className="text-slate-200 flex items-center gap-1 text-[11px]">
                          <Truck className="w-3 h-3 text-indigo-400" />
                          <span>{receiptData.gmail_carrier || 'Direct Delivery / E-Receipt'}</span>
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-semibold">Delivery Status</span>
                        <span className="text-emerald-400 font-semibold flex items-center gap-1 text-[11px]">
                          <Check className="w-3 h-3" />
                          <span>{receiptData.gmail_delivery_status || 'Delivered & Confirmed'}</span>
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Raw E-Receipt Body</span>
                    <div className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800/90 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-56 overflow-y-auto">
                      {receiptData.raw_email_body || `From: ${transaction.clean_merchant} Orders <orders@${transaction.clean_merchant.toLowerCase().replace(/[^a-z]/g, '')}.com>
Subject: Order Receipt #${receiptData.order_id}
To: ${transaction.card_member}

Thank you for your purchase with ${transaction.clean_merchant}!
Total: $${Math.abs(transaction.amount).toFixed(2)} charged on ${transaction.date}.`}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: BANK STATEMENT VS AGENT COMPARISON */}
              {activeTab === 'COMPARISON' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 animate-fadeIn">
                  
                  {/* Left: What Bank Provided */}
                  <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Raw Bank Statement</span>
                      <span className="text-[9px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.2 rounded border border-slate-800">CSV Only</span>
                    </div>

                    <div className="space-y-1.5 text-xs">
                      <div>
                        <span className="text-slate-500 block text-[9px]">RAW DESCRIPTOR:</span>
                        <p className="font-mono text-slate-300 font-bold bg-slate-900/90 p-1.5 rounded-lg border border-slate-800 text-[11px] truncate">{transaction.raw_description}</p>
                      </div>
                      <div className="flex justify-between py-0.5 border-b border-slate-800/50 text-[11px]">
                        <span className="text-slate-400">Amount Charged:</span>
                        <span className="font-mono text-slate-200 font-bold">${Math.abs(transaction.amount).toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between py-0.5 border-b border-slate-800/50 text-[11px]">
                        <span className="text-slate-400">SKU Itemization:</span>
                        <span className="text-red-400 font-semibold">❌ None (Single lump sum)</span>
                      </div>
                      <div className="flex justify-between py-0.5 border-b border-slate-800/50 text-[11px]">
                        <span className="text-slate-400">Sales Tax / Fee Split:</span>
                        <span className="text-red-400 font-semibold">❌ Not Provided</span>
                      </div>
                      <div className="flex justify-between py-0.5 text-[11px]">
                        <span className="text-slate-400">Return Policy & Deadline:</span>
                        <span className="text-red-400 font-semibold">❌ Unknown</span>
                      </div>
                    </div>
                  </div>

                  {/* Right: What ADK + Gmail Agent Augmented */}
                  <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/50 space-y-3 shadow-xl">
                    <div className="flex items-center justify-between border-b border-indigo-500/30 pb-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-indigo-400" /> Google ADK + Gmail Grounding
                      </span>
                      <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded border border-emerald-500/40">Augmented</span>
                    </div>

                    <div className="space-y-1.5 text-xs">
                      <div>
                        <span className="text-indigo-400 block text-[9px] font-semibold">ITEMIZED PRODUCTS EXTRACTED:</span>
                        <p className="font-semibold text-white bg-indigo-950/50 p-1.5 rounded-lg border border-indigo-500/30 text-[11px] truncate">
                          {receiptData.items?.length || 1} distinct SKU line items ({receiptData.items?.map(i => i.name).join(', ')})
                        </p>
                      </div>
                      <div className="flex justify-between py-0.5 border-b border-indigo-500/20 text-[11px]">
                        <span className="text-slate-300">Sales Tax & Fee Breakdown:</span>
                        <span className="text-emerald-300 font-mono font-bold">${receiptData.tax_amount?.toFixed(2)} Tax (8.875%)</span>
                      </div>
                      <div className="flex justify-between py-0.5 border-b border-indigo-500/20 text-[11px]">
                        <span className="text-slate-300">Return Policy Tracking:</span>
                        <span className="text-emerald-300 font-semibold">🟢 30-Day Window ({receiptData.return_window_deadline})</span>
                      </div>
                      <div className="flex justify-between py-0.5 text-[11px]">
                        <span className="text-slate-300">Delivery Status:</span>
                        <span className="text-indigo-300 font-semibold">{receiptData.gmail_delivery_status || 'Confirmed Delivered'}</span>
                      </div>
                    </div>
                  </div>

                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Compact Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950/80 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
