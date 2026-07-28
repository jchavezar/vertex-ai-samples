import React, { useState } from 'react';
import { GcpErrorItem } from '../../types';
import {
  Zap,
  Code,
  Terminal,
  Globe,
  Flame,
  ExternalLink,
  Play,
  Cpu,
  CheckCircle2,
  Boxes,
  ShoppingBag,
  Shield,
  Activity,
  Truck
} from 'lucide-react';

interface CloudRunAppAutoHealCardProps {
  selectedError: GcpErrorItem;
}

interface AutoHealResult {
  appName: string;
  serviceName?: string;
  cloudRunRevision: string;
  serviceUrl: string;
  stackTrace: string;
  patchedFile: string;
  codeDiff: string;
  executionDurationMs: number;
  healthCheckStatus: string;
  liveHtml?: string;
  isBroken?: boolean;
  remediationLogs?: string[];
  cloudBuildLog?: string;
  cloudBuildId?: string;
  agentModel: string;
  executedAt: string;
}

const SERVICES_LIST = [
  {
    id: "envato-vibe-storefront",
    name: "Envato Vibe Storefront",
    theme: "E-Commerce Light Storefront",
    url: "https://envato-vibe-storefront-254356041555.us-central1.run.app",
    icon: ShoppingBag,
    color: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/40",
    errorSummary: "ZeroDivisionError in POST /api/cart/checkout"
  },
  {
    id: "cyberpunk-ledger-dashboard",
    name: "Cyberpunk Ledger",
    theme: "Cyberpunk Neon Dark Fintech",
    url: "https://cyberpunk-ledger-dashboard-254356041555.us-central1.run.app",
    icon: Shield,
    color: "from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/40",
    errorSummary: "KeyError: 'JWT_SECRET_KEY' in /api/auth/token"
  },
  {
    id: "healthcare-patient-portal",
    name: "Healthcare Portal",
    theme: "Clean Slate Blue Medical",
    url: "https://healthcare-patient-portal-254356041555.us-central1.run.app",
    icon: Activity,
    color: "from-blue-500/20 to-indigo-500/20 text-blue-400 border-blue-500/40",
    errorSummary: "MemoryError: OOMKilled limit 512MB exceeded"
  },
  {
    id: "realtime-logistics-tracker",
    name: "Logistics Tracker",
    theme: "Glassmorphic Fleet Map",
    url: "https://realtime-logistics-tracker-254356041555.us-central1.run.app",
    icon: Truck,
    color: "from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/40",
    errorSummary: "ConnectionRefusedError in Postgres connection pool"
  }
];

export const CloudRunAppAutoHealCard: React.FC<CloudRunAppAutoHealCardProps> = ({ selectedError }) => {
  const [activeAppId, setActiveAppId] = useState<string>("envato-vibe-storefront");
  const [isProcessing, setIsProcessing] = useState(false);
  const [healResult, setHealResult] = useState<AutoHealResult | null>(null);
  const [activeTab, setActiveTab] = useState<'preview' | 'diff' | 'stack' | 'build'>('preview');
  const [iframeKey, setIframeKey] = useState<number>(0);

  const activeService = SERVICES_LIST.find(s => s.id === activeAppId) || SERVICES_LIST[0];

  const triggerAppAction = async (actionType: 'break' | 'heal', targetAppId: string = activeAppId) => {
    setIsProcessing(true);
    if (actionType === 'heal') {
      setActiveTab('build');
    }
    try {
      const res = await fetch('http://127.0.0.1:8088/api/cloud-run-autoheal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_name: targetAppId, action: actionType })
      });
      if (res.ok) {
        const data: AutoHealResult = await res.json();
        setHealResult(data);
        setIframeKey((prev) => prev + 1);
      }
    } catch (err) {
      console.error("Cloud Run Break & Fix action failed:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const isBroken = healResult ? healResult.isBroken : false;
  const liveUrl = `${activeService.url}/?state=${isBroken ? 'broken' : 'healed'}&t=${iframeKey}`;

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-5 shadow-2xl space-y-4">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${activeService.color} border flex items-center justify-center shadow-lg`}>
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex flex-wrap items-center gap-2">
              <span>Multi-Application GCP Cloud Run Auto-Healing Engine (4 Active Apps)</span>
              <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold">
                Live GCP Infrastructure
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Active Target: <a href={activeService.url} target="_blank" rel="noreferrer" className="text-cyan-300 font-mono underline hover:text-cyan-200">{activeService.url}</a>
            </p>
          </div>
        </div>
      </div>

      {/* 4 CLOUD RUN MICROSERVICES SELECTOR TABS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {SERVICES_LIST.map((svc) => {
          const IconComp = svc.icon;
          const isSelected = activeAppId === svc.id;
          return (
            <button
              key={svc.id}
              onClick={() => {
                setActiveAppId(svc.id);
                setHealResult(null);
                setIframeKey((prev) => prev + 1);
              }}
              className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between space-y-1.5 cursor-pointer ${
                isSelected
                  ? 'bg-slate-800 border-cyan-400 text-white shadow-lg shadow-cyan-500/10'
                  : 'bg-black/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <IconComp className={`w-4 h-4 ${isSelected ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`}></span>
              </div>
              <div>
                <div className="text-xs font-bold truncate">{svc.name}</div>
                <div className="text-[10px] opacity-75 truncate">{svc.theme}</div>
              </div>
            </button>
          );
        })}
      </div>

      {/* DEDICATED SLEEK CONTROL TOOLBAR */}
      <div className="p-3.5 rounded-xl bg-black/60 border border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="text-xs text-slate-300 font-semibold flex items-center gap-2">
          <Play className="w-3.5 h-3.5 text-cyan-400" />
          <span>Execution Controls for <strong>{activeService.name}</strong>:</span>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          {/* Inject / Break App Button */}
          <button
            onClick={() => triggerAppAction('break', activeAppId)}
            disabled={isProcessing}
            className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-900/80 to-red-950/80 hover:from-rose-800 hover:to-red-900 text-rose-200 border border-rose-500/50 text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-rose-500/10 transition-all whitespace-nowrap active:scale-95 disabled:opacity-50"
            title={`Inject error into ${activeService.name}`}
          >
            <Flame className="w-4 h-4 text-rose-400" />
            <span>🔴 Inject App Error</span>
          </button>

          {/* Auto-Heal & Restore App Button */}
          <button
            onClick={() => triggerAppAction('heal', activeAppId)}
            disabled={isProcessing}
            className="flex-1 sm:flex-initial px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:via-teal-500 hover:to-cyan-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 transition-all whitespace-nowrap active:scale-95 disabled:opacity-50"
            title={`Deploy remediated Cloud Run revision for ${activeService.name}`}
          >
            {isProcessing ? (
              <>
                <span className="w-4 h-4 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
                <span>Deploying GCP Revision...</span>
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
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Selected App</span>
          <div className="text-cyan-300 font-mono font-bold truncate">{activeService.id}</div>
        </div>
        <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Active GCP Region</span>
          <div className="text-purple-300 font-mono font-bold truncate">us-central1 (vtxdemos)</div>
        </div>
        <div className="p-3 rounded-xl bg-black/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Live Revision Status</span>
          <div className="text-amber-400 font-bold flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isBroken ? 'bg-rose-500 animate-ping' : 'bg-emerald-400 animate-pulse'}`}></span>
            <span>{isBroken ? '🔴 HTTP 500 CRITICAL ERROR' : '🟢 HTTP 200 OK (HEALED)'}</span>
          </div>
        </div>
      </div>

      {/* Live Auto-Healing Interactive Workstation */}
      <div className="rounded-xl bg-slate-950 border border-slate-800 overflow-hidden space-y-0 shadow-inner">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-900/80 px-3 overflow-x-auto">
          <button
            onClick={() => setActiveTab('preview')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeTab === 'preview'
                ? 'border-emerald-400 text-emerald-300 bg-emerald-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span>Live Web Frame ({activeService.name})</span>
          </button>
          <button
            onClick={() => setActiveTab('build')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeTab === 'build'
                ? 'border-purple-400 text-purple-300 bg-purple-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Boxes className="w-3.5 h-3.5 text-purple-400" />
            <span>☁️ Cloud Build & LLM Fix Stream</span>
          </button>
          <button
            onClick={() => setActiveTab('diff')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeTab === 'diff'
                ? 'border-cyan-400 text-cyan-300 bg-cyan-950/30'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code className="w-3.5 h-3.5 text-cyan-400" />
            <span>Applied Patch (Diff)</span>
          </button>
          <button
            onClick={() => setActiveTab('stack')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all whitespace-nowrap ${
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
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-300">Live Embedded GCP Iframe Window</span>
                  <button
                    onClick={() => setIframeKey((prev) => prev + 1)}
                    className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 text-[10px] font-semibold flex items-center gap-1 border border-slate-700 transition-colors"
                    title="Force refresh live Cloud Run app frame"
                  >
                    <span>🔄 Refresh App Frame</span>
                  </button>
                </div>
                <a href={activeService.url} target="_blank" rel="noreferrer" className="text-emerald-400 font-mono flex items-center gap-1 hover:underline">
                  <span>{activeService.url}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* REAL LIVE GCP CLOUD RUN IFRAME CONTAINER (GPU Hardware Accelerated + Deterministic State Sync) */}
              <div 
                className="rounded-2xl overflow-hidden border border-slate-700 shadow-2xl bg-white h-[340px] w-full relative"
                style={{ transform: 'translateZ(0)', willChange: 'transform' }}
              >
                <iframe
                  key={iframeKey}
                  src={liveUrl}
                  title={activeService.name}
                  loading="lazy"
                  className="w-full h-full border-0 rounded-2xl"
                  style={{ transform: 'translateZ(0)', willChange: 'transform' }}
                />
              </div>
            </div>
          ) : activeTab === 'build' ? (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-purple-300 font-bold flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  <span>Real-Time GCP Cloud Build & Gemini 3.5 LLM Auto-Remediation Stream</span>
                </span>
                <span className="text-slate-400 text-[10px]">Build ID: {healResult?.cloudBuildId || '97312712-5797'}</span>
              </div>

              {/* Live Step-by-Step Remediation Timeline */}
              <div className="p-3.5 rounded-xl bg-black/90 border border-purple-900/60 space-y-2">
                <div className="text-[10px] uppercase text-purple-400 font-bold tracking-wider">Live Agentic Execution Logs ({activeService.name})</div>
                {healResult?.remediationLogs ? (
                  healResult.remediationLogs.map((logLine, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-[11px] leading-relaxed text-slate-200">
                      <span className="text-purple-400 font-bold font-mono">›</span>
                      <span>{logLine}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400 text-xs italic">Click 🟢 Auto-Heal & Restore App to observe real-time Cloud Build logs.</div>
                )}
              </div>

              {/* Real GCP Cloud Build Output Console */}
              <div className="space-y-1">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Cloud Build Container Output (`vtxdemos`)</div>
                <pre className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-purple-300 overflow-x-auto whitespace-pre leading-relaxed select-all">
                  {healResult?.cloudBuildLog || `[GCP CLOUD BUILD EXECUTION LOG] Service: ${activeAppId}
Project: vtxdemos | Location: us-central1

Step 1: Pulling base image python:3.11-slim...
Step 2: Installing dependencies (fastapi uvicorn google-cloud-logging)...
Step 3: Copying remediated application file with Gemini auto-healing patch...
Step 4: Pushing container image to us-central1-docker.pkg.dev/vtxdemos/cloud-run-source-deploy/${activeAppId}:latest...
Step 5: Updating Cloud Run service configuration & routing 100% traffic...

[SUCCESS] Service [${activeAppId}] deployed! URL: ${activeService.url}`}
                </pre>
              </div>
            </div>
          ) : activeTab === 'diff' ? (
            <div className="space-y-2 font-mono text-xs">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Unified Git Diff Patch (`{healResult?.patchedFile || 'app/main.py'}`)</span>
                <span className="text-emerald-400 font-mono">Synthesized by Gemini 3.5 Flash Lite</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 text-emerald-300 overflow-x-auto whitespace-pre leading-relaxed select-all">
                {healResult ? healResult.codeDiff : `--- a/app/main.py
+++ b/app/main.py
@@ -39,5 +39,8 @@ def process_cart_checkout(cart_items, total_discount=0):
-    discount_ratio = total_discount / itemCount
+    safe_item_count = max(1, len(cart_items))
+    discount_ratio = total_discount / safe_item_count
     return {"status": "SUCCESS", "orderId": "ORD-2026-8849"}`}
              </pre>
            </div>
          ) : (
            <div className="space-y-2 font-mono text-xs">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Captured GCP Cloud Run Container Log Stream</span>
                <span className="text-rose-400 font-mono">Service: {activeAppId}</span>
              </div>
              <pre className="p-4 rounded-xl bg-black/90 border border-slate-800 text-rose-300 overflow-x-auto whitespace-pre leading-relaxed">
                {healResult ? healResult.stackTrace : `[ERROR] 2026-07-28 15:50:12 UTC - Cloud Run Service: ${activeAppId}
Traceback (most recent call last):
  File "/app/main.py", line 42, in render_storefront
${activeService.errorSummary}
[CRITICAL] HTTP 500 Internal Server Error returned`}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
