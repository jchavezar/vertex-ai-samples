import React, { useState } from 'react';
import { X, Mail, ShieldCheck, CheckCircle2, Lock, ExternalLink, Loader2, Sparkles, AlertCircle } from 'lucide-react';

export default function GmailAuthModal({ authStatus, onConnect, onDisconnect, onClose }) {
  const [emailInput, setEmailInput] = useState(authStatus?.email && authStatus.email !== 'Not connected' ? authStatus.email : 'jesusarguelles@google.com');
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = async () => {
    setIsLoading(true);
    try {
      await onConnect(emailInput);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setIsLoading(true);
    try {
      await onDisconnect();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-xl animate-fadeIn">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-red-500 to-amber-500 text-white shadow-lg shadow-red-500/20">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Google Workspace & Gmail</h3>
              <p className="text-[11px] text-slate-400">Google ADK Agentic E-Receipt Connector</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {authStatus?.connected ? (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h4 className="text-xs font-bold text-emerald-200">Gmail Agent Integration Active</h4>
                  <p className="text-[11px] text-emerald-300/80">Connected account: <span className="font-mono font-bold text-white">{authStatus.email}</span></p>
                  <p className="text-[10px] text-slate-400">Tokens synced via Google Secret Manager (<span className="font-mono">gworkspace-mcp-tokens</span>).</p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center gap-2 text-slate-300 font-semibold">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" /> Active Security Scopes:
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-300 font-mono">https://www.googleapis.com/auth/gmail.readonly</span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-300 font-mono">https://www.googleapis.com/auth/gmail.labels</span>
                </div>
              </div>

              <button
                onClick={handleDisconnect}
                disabled={isLoading}
                className="w-full py-2.5 rounded-xl bg-red-950/40 hover:bg-red-900/60 text-red-300 border border-red-500/30 font-semibold text-xs transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Disconnect Gmail Account'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-indigo-300">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  Unlock Deep E-Receipt Itemization
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Connecting your Gmail permits the Google ADK Agent to securely match bank transactions against digital order confirmations, parse PDF invoices, and extract SKU line-items in real time.
                </p>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 block">Google Account Email</label>
                <input
                  type="email"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  placeholder="name@google.com or name@gmail.com"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50"
                />
              </div>

              <div className="flex items-center gap-2 text-[11px] text-slate-400">
                <Lock className="w-3.5 h-3.5 text-emerald-400" />
                <span>Read-only access. Zero credentials stored in plaintext.</span>
              </div>

              <button
                onClick={handleConnect}
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-red-500 via-indigo-600 to-violet-600 hover:opacity-95 text-white font-bold text-xs shadow-lg shadow-indigo-600/25 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                ) : (
                  <Mail className="w-4 h-4" />
                )}
                {isLoading ? 'Authorizing Workspace...' : 'Connect Google Workspace / Gmail'}
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
