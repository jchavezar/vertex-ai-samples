import React, { useState } from 'react';
import { GcpErrorItem } from '../../types';
import {
  Sparkles,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Code,
  Terminal,
  Globe,
  RefreshCw,
  MessageSquare,
  Bot,
  Layers,
  ArrowRight,
  ExternalLink
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
  agentModel: string;
  executedAt: string;
}

export const CloudRunAppAutoHealCard: React.FC<CloudRunAppAutoHealCardProps> = ({ selectedError }) => {
  const [isHealing, setIsHealing] = useState(false);
  const [healResult, setHealResult] = useState<AutoHealResult | null>(null);
  const [activeTab, setActiveTab] = useState<'preview' | 'diff' | 'stack'>('preview');

  const handleTriggerAutoHeal = async () => {
    setIsHealing(true);
    try {
      const res = await fetch('http://127.0.0.1:8088/api/cloud-run-autoheal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        const data: AutoHealResult = await res.json();
        setHealResult(data);
      }
    } catch (err) {
      console.error("Cloud Run auto-heal failed:", err);
    } finally {
      setIsHealing(false);
    }
  };

  return (
    <div className="rounded-2xl bg-gradient-to-br from-[#0c101a] via-[#111728] to-[#0c101a] border border-cyan-500/50 p-5 shadow-2xl space-y-4">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/40 flex items-center justify-center shadow-lg shadow-cyan-500/10">
            <Globe className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <span>Cloud Run Application-Level Auto-Healing Engine</span>
              <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold">
                Gemini 3.5 Flash Lite Powered
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Detects application-level stack traces in Cloud Run logs, applies live code patches & renders visual frontend restoration
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleTriggerAutoHeal}
            disabled={isHealing}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 via-cyan-600 to-blue-600 hover:from-emerald-500 hover:via-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all"
          >
            {isHealing ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
                <span>Applying Code Patch & Re-deploying...</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5 fill-amber-300 text-amber-300" />
                <span>Auto-Heal Cloud Run App</span>
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
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Detected Stack Trace</span>
          <div className="text-rose-400 font-mono font-bold truncate">ZeroDivisionError: /api/cart/checkout</div>
        </div>
        <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Current State</span>
          <div className="text-amber-400 font-bold flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
            <span>{healResult ? '🟢 HEALED & OPERATIONAL' : '🔴 HTTP 500 CRITICAL ERROR'}</span>
          </div>
        </div>
      </div>

      {/* Live Auto-Healing Interactive Workstation */}
      <div className="rounded-xl bg-slate-950 border border-slate-800 overflow-hidden space-y-0">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-900/80 px-3">
          <button
            onClick={() => setActiveTab('preview')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
              activeTab === 'preview'
                ? 'border-cyan-400 text-cyan-300 bg-cyan-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            <span>Live Visual App Preview</span>
          </button>
          <button
            onClick={() => setActiveTab('diff')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
              activeTab === 'diff'
                ? 'border-emerald-400 text-emerald-300 bg-emerald-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code className="w-3.5 h-3.5 text-emerald-400" />
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
            <span>Application Stack Trace</span>
          </button>
        </div>

        {/* Tab Content Display Area */}
        <div className="p-4 bg-slate-950">
          {activeTab === 'preview' ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-[11px] text-slate-400">
                <span>Real-time Embedded Browser Renderer</span>
                <span className="text-cyan-400 font-mono">https://envato-vibe-storefront.run.app</span>
              </div>

              {/* Visual App State Morphing Window */}
              {healResult ? (
                <div
                  className="rounded-xl overflow-hidden border border-emerald-500/40 shadow-2xl transition-all animate-fadeIn"
                  dangerouslySetInnerHTML={{ __html: healResult.healedHtml }}
                />
              ) : (
                <div
                  className="rounded-xl overflow-hidden border border-rose-500/40 shadow-2xl"
                  dangerouslySetInnerHTML={{
                    __html: `
    <div style="font-family: system-ui; padding: 24px; background: #0f172a; color: #f8fafc; border-radius: 12px; border: 1px solid #e11d48;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-b: 1px solid #334155; padding-bottom: 12px;">
        <span style="font-weight: bold; color: #f43f5e;">🔴 Envato Vibe Storefront (CRITICAL 500 ERROR)</span>
        <span style="font-size: 11px; background: #e11d4822; color: #fda4af; padding: 2px 8px; border-radius: 99px;">HTTP 500</span>
      </div>
      <div style="margin-top: 16px; background: #000; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 12px; color: #f43f5e;">
        <div>ZeroDivisionError: division by zero in /api/cart/checkout</div>
        <div style="color: #64748b; margin-top: 8px;">Line 42: discount_ratio = total_discount / itemCount</div>
      </div>
      <div style="margin-top: 14px; color: #94a3b8; font-size: 12px; font-style: italic;">
        Click <strong>⚡ Auto-Heal Cloud Run App</strong> above to synthesize real-time code patch and restore application state.
      </div>
    </div>`
                  }}
                />
              )}
            </div>
          ) : activeTab === 'diff' ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Unified Git Diff Patch (`app/routes/checkout.py`)</span>
                <span className="text-emerald-400 font-mono">Synthesized by Gemini 3.5 Flash Lite</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-emerald-300 overflow-x-auto whitespace-pre leading-relaxed select-all">
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
            <div className="space-y-2">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Captured Cloud Run Container Log Stream</span>
                <span className="text-rose-400 font-mono">Revision: envato-vibe-storefront-00042</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-rose-300 overflow-x-auto whitespace-pre leading-relaxed">
                {healResult ? healResult.stackTrace : `[ERROR] 2026-07-28 15:08:12.402 UTC - Cloud Run Revision: envato-vibe-storefront-00042-v3x
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
