import React, { useState } from 'react';
import { GcpErrorItem } from '../../types';
import {
  Zap,
  Code,
  Terminal,
  Globe,
  Flame,
  CheckCircle2,
  AlertTriangle,
  Play
} from 'lucide-react';

interface CloudRunAppAutoHealCardProps {
  selectedError: GcpErrorItem;
}

interface AutoHealResult {
  appName: string;
  cloudRunRevision: string;
  serviceUrl: string;
  stackTrace: string;
  patchedFile: string;
  codeDiff: string;
  executionDurationMs: number;
  healthCheckStatus: string;
  brokenHtml: string;
  healedHtml: string;
  isBroken?: boolean;
  agentModel: string;
  executedAt: string;
}

export const CloudRunAppAutoHealCard: React.FC<CloudRunAppAutoHealCardProps> = ({ selectedError }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [healResult, setHealResult] = useState<AutoHealResult | null>(null);
  const [activeTab, setActiveTab] = useState<'preview' | 'diff' | 'stack'>('preview');

  const triggerAppAction = async (actionType: 'break' | 'heal') => {
    setIsProcessing(true);
    try {
      const res = await fetch('http://127.0.0.1:8088/api/cloud-run-autoheal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionType })
      });
      if (res.ok) {
        const data: AutoHealResult = await res.json();
        setHealResult(data);
      }
    } catch (err) {
      console.error("Cloud Run Break & Fix action failed:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const isBroken = healResult ? healResult.isBroken : true;

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-5 shadow-2xl space-y-4">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 flex items-center justify-center shadow-lg shadow-emerald-500/10">
            <Globe className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex flex-wrap items-center gap-2">
              <span>Next-Gen Cloud Run Application "Break & Fix" Engine</span>
              <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold">
                Gemini 3.5 Flash Lite Powered
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Interactive application-level error injection & real-time light-theme UI auto-patching
            </p>
          </div>
        </div>
      </div>

      {/* DEDICATED SLEEK CONTROL TOOLBAR (No Piling / Crisp Spacing) */}
      <div className="p-3 rounded-xl bg-black/60 border border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="text-xs text-slate-300 font-semibold flex items-center gap-2">
          <Play className="w-3.5 h-3.5 text-cyan-400" />
          <span>Interactive Execution Controls:</span>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          {/* Inject / Break App Button */}
          <button
            onClick={() => triggerAppAction('break')}
            disabled={isProcessing}
            className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-900/80 to-red-950/80 hover:from-rose-800 hover:to-red-900 text-rose-200 border border-rose-500/50 text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-rose-500/10 transition-all whitespace-nowrap active:scale-95 disabled:opacity-50"
            title="Simulate Cloud Run ZeroDivisionError app crash"
          >
            <Flame className="w-4 h-4 text-rose-400" />
            <span>🔴 Inject App Error</span>
          </button>

          {/* Auto-Heal & Restore App Button */}
          <button
            onClick={() => triggerAppAction('heal')}
            disabled={isProcessing}
            className="flex-1 sm:flex-initial px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:via-teal-500 hover:to-cyan-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 transition-all whitespace-nowrap active:scale-95 disabled:opacity-50"
            title="Synthesize python patch and restore Light-Theme App UI"
          >
            {isProcessing ? (
              <>
                <span className="w-4 h-4 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
                <span>Applying Code Patch...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 fill-amber-300 text-amber-300" />
                <span>🟢 Auto-Heal & Restore App</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Target Application & Incident Summary Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Target Service</span>
          <div className="text-cyan-300 font-mono font-bold truncate">envato-vibe-storefront</div>
        </div>
        <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Application Stack Trace</span>
          <div className="text-rose-400 font-mono font-bold truncate">ZeroDivisionError: /api/cart/checkout</div>
        </div>
        <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Live App Status</span>
          <div className="text-amber-400 font-bold flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isBroken ? 'bg-rose-500 animate-ping' : 'bg-emerald-400 animate-pulse'}`}></span>
            <span>{isBroken ? '🔴 HTTP 500 CRITICAL ERROR' : '🟢 HTTP 200 OK (HEALED)'}</span>
          </div>
        </div>
      </div>

      {/* Live Auto-Healing Interactive Workstation */}
      <div className="rounded-xl bg-slate-950 border border-slate-800 overflow-hidden space-y-0 shadow-inner">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-900/80 px-3">
          <button
            onClick={() => setActiveTab('preview')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
              activeTab === 'preview'
                ? 'border-emerald-400 text-emerald-300 bg-emerald-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span>Next-Gen Light Theme UI Preview</span>
          </button>
          <button
            onClick={() => setActiveTab('diff')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
              activeTab === 'diff'
                ? 'border-cyan-400 text-cyan-300 bg-cyan-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code className="w-3.5 h-3.5 text-cyan-400" />
            <span>Applied Code Patch (Diff)</span>
          </button>
          <button
            onClick={() => setActiveTab('stack')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
              activeTab === 'stack'
                ? 'border-rose-400 text-rose-300 bg-rose-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-rose-400" />
            <span>Container Log Stream</span>
          </button>
        </div>

        {/* Tab Content Display Area */}
        <div className="p-4 bg-slate-950">
          {activeTab === 'preview' ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-[11px] text-slate-400">
                <span className="font-semibold text-slate-300">Live Embedded Application View (Next-Gen Light Mode)</span>
                <span className="text-emerald-400 font-mono">https://envato-vibe-storefront.run.app</span>
              </div>

              {/* NEXT-GEN LIGHT THEME APP UI RENDERER */}
              <div
                className="rounded-2xl overflow-hidden border border-slate-200 shadow-2xl transition-all duration-300 bg-white"
                dangerouslySetInnerHTML={{
                  __html: healResult
                    ? healResult.healedHtml
                    : `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 24px; background: #ffffff; color: #0f172a; border-radius: 16px; border: 1px solid #fecdd3; box-shadow: 0 10px 25px -5px rgba(244, 63, 94, 0.08);">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ffe4e6; padding-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 10px; height: 10px; border-radius: 50%; background: #f43f5e; box-shadow: 0 0 10px #f43f5e;"></div>
          <span style="font-weight: 800; font-size: 15px; color: #e11d48;">Envato Vibe Storefront</span>
          <span style="font-size: 11px; background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; padding: 2px 8px; border-radius: 99px; font-weight: 700;">🔴 APP BROKEN</span>
        </div>
        <span style="font-size: 11px; background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 4px 12px; border-radius: 99px; font-weight: 700;">HTTP 500 CRITICAL</span>
      </div>
      <div style="margin-top: 18px; background: #0f172a; padding: 18px; border-radius: 12px; font-family: monospace; font-size: 12px; color: #fda4af;">
        <div style="color: #f43f5e; font-weight: 700;">ZeroDivisionError: division by zero in /api/cart/checkout</div>
        <div style="color: #94a3b8; margin-top: 4px;">File "/app/routes/checkout.py", line 42, in process_cart_checkout</div>
      </div>
      <div style="margin-top: 14px; color: #64748b; font-size: 12px;">
        Click <strong>🟢 Auto-Heal & Restore App</strong> above to synthesize real-time code patch and restore Next-Gen Light UI.
      </div>
    </div>`
                }}
              />
            </div>
          ) : activeTab === 'diff' ? (
            <div className="space-y-2 font-mono text-xs">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Unified Git Diff Patch (`app/routes/checkout.py`)</span>
                <span className="text-emerald-400 font-mono">Synthesized by Gemini 3.5 Flash Lite</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 text-emerald-300 overflow-x-auto whitespace-pre leading-relaxed select-all">
                {healResult ? healResult.codeDiff : `--- a/app/routes/checkout.py
+++ b/app/routes/checkout.py
@@ -39,5 +39,8 @@ def process_cart_checkout(cart_items, total_discount=0):
-    discount_ratio = total_discount / itemCount
-    final_price = subtotal - discount_ratio
+    # Antigravity Agent Auto-Healing Patch: Zero-Division Protection
+    safe_item_count = max(1, len(cart_items))
+    discount_ratio = total_discount / safe_item_count
+    final_price = max(0.0, subtotal - discount_ratio)
+    
+    return {"status": "SUCCESS", "orderId": "ORD-2026-8849", "finalPrice": final_price}`}
              </pre>
            </div>
          ) : (
            <div className="space-y-2 font-mono text-xs">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Captured Cloud Run Container Log Stream</span>
                <span className="text-rose-400 font-mono">Revision: envato-vibe-storefront-00042</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 text-rose-300 overflow-x-auto whitespace-pre leading-relaxed">
                {healResult ? healResult.stackTrace : `[ERROR] 2026-07-28 15:12:05.102 UTC - Cloud Run Revision: envato-vibe-storefront-00042-v3x
Traceback (most recent call last):
  File "/app/routes/checkout.py", line 42, in process_cart_checkout
    discount_ratio = total_discount / itemCount
ZeroDivisionError: division by zero
[CRITICAL] HTTP 500 Internal Server Error returned on POST /api/cart/checkout`}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
