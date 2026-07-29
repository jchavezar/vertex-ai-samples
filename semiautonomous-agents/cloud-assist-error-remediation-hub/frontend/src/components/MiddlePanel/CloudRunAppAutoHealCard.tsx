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
  Truck,
  Maximize2,
  Minimize2,
  X
} from 'lucide-react';

interface CloudRunAppAutoHealCardProps {
  selectedError: GcpErrorItem;
  isLightMode?: boolean;
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
    color: "from-blue-500/20 to-cyan-500/20 text-cyan-400 border-cyan-500/40",
    errorSummary: "ZeroDivisionError: division by zero in /api/cart/checkout"
  },
  {
    id: "cyberpunk-ledger-dashboard",
    name: "Cyberpunk Ledger",
    theme: "Cyberpunk Neon Dark Fintech",
    url: "https://cyberpunk-ledger-dashboard-254356041555.us-central1.run.app",
    icon: Shield,
    color: "from-amber-500/20 to-rose-500/20 text-amber-400 border-amber-500/40",
    errorSummary: "KeyError: 'JWT_SECRET_KEY' in /api/auth/token"
  },
  {
    id: "healthcare-patient-portal",
    name: "Healthcare Portal",
    theme: "Clean Slate Blue Medical",
    url: "https://healthcare-patient-portal-254356041555.us-central1.run.app",
    icon: Activity,
    color: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/40",
    errorSummary: "MemoryError: OOMKilled 512MB heap limit exceeded"
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

export const CloudRunAppAutoHealCard: React.FC<CloudRunAppAutoHealCardProps> = ({ selectedError, isLightMode = false }) => {
  const [activeAppId, setActiveAppId] = useState<string>("envato-vibe-storefront");
  const [isProcessing, setIsProcessing] = useState(false);
  const [healResult, setHealResult] = useState<AutoHealResult | null>(null);
  const [appStateOverride, setAppStateOverride] = useState<'broken' | 'healed' | null>('broken');
  const [activeTab, setActiveTab] = useState<'preview' | 'diff' | 'stack' | 'build'>('preview');
  const [iframeKey, setIframeKey] = useState<number>(0);
  const [isFullscreenView, setIsFullscreenView] = useState<boolean>(false);

  const [streamedLogs, setStreamedLogs] = useState<string[]>([]);

  // Sync with selected error from Cloud Logging panel
  React.useEffect(() => {
    if (selectedError) {
      const summaryText = (selectedError.serviceName + " " + selectedError.summary + " " + selectedError.fullText + " " + selectedError.id).toLowerCase();

      let matchedSvc = SERVICES_LIST.find(s => {
        if (s.id === "cyberpunk-ledger-dashboard" && (summaryText.includes("cyberpunk") || summaryText.includes("keyerror") || summaryText.includes("jwt"))) return true;
        if (s.id === "healthcare-patient-portal" && (summaryText.includes("healthcare") || summaryText.includes("memoryerror") || summaryText.includes("oom"))) return true;
        if (s.id === "envato-vibe-storefront" && (summaryText.includes("storefront") || summaryText.includes("envato") || summaryText.includes("zerodivision"))) return true;
        if (s.id === "realtime-logistics-tracker" && (summaryText.includes("logistics") || summaryText.includes("postgres") || summaryText.includes("conn"))) return true;
        return summaryText.includes(s.id);
      });

      if (matchedSvc) {
        setActiveAppId(matchedSvc.id);
      }
      setHealResult(null);
      setStreamedLogs([]);
      setAppStateOverride('broken'); // Default to broken HTTP 500 state for active incidents
      setIframeKey((prev) => prev + 1);
    }
  }, [selectedError]);

  const activeService = SERVICES_LIST.find(s => s.id === activeAppId) || SERVICES_LIST[0];

  const triggerAppAction = async (actionType: 'break' | 'heal', targetAppId: string = activeAppId) => {
    setIsProcessing(true);
    setStreamedLogs([]);
    if (actionType === 'heal') {
      setActiveTab('build');
    } else {
      setAppStateOverride('broken');
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
        
        if (actionType === 'heal' && data.remediationLogs) {
          // Stream build logs sequentially to reflect real Cloud Build container deployment progression
          const logs = data.remediationLogs;
          logs.forEach((logLine, index) => {
            setTimeout(() => {
              setStreamedLogs((prev) => [...prev, logLine]);
              if (index === logs.length - 1) {
                setAppStateOverride('healed');
                setIframeKey((prev) => prev + 1);
                setIsProcessing(false);
              }
            }, (index + 1) * 1100);
          });
        } else {
          setStreamedLogs(data.remediationLogs || []);
          setIframeKey((prev) => prev + 1);
          setIsProcessing(false);
        }
      } else {
        setIsProcessing(false);
      }
    } catch (err) {
      console.error("Cloud Run Break & Fix action failed:", err);
      setIsProcessing(false);
    }
  };

  const isBroken = healResult ? healResult.isBroken : (appStateOverride ? appStateOverride === 'broken' : true);
  const liveUrl = `${activeService.url}/?state=${isBroken ? 'broken' : 'healed'}&t=${iframeKey}`;

  return (
    <div className={`rounded-2xl p-5 shadow-sm space-y-4 border ${
      isLightMode
        ? 'bg-white border-slate-300 text-slate-950 font-sans'
        : 'bg-slate-900 border-slate-800 text-white shadow-2xl'
    }`}>
      {/* Top Banner Header */}
      <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 ${
        isLightMode ? 'border-slate-200' : 'border-slate-800/80'
      }`}>
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-md border ${
            isLightMode
              ? 'bg-slate-950 text-white border-slate-900'
              : `bg-gradient-to-br ${activeService.color}`
          }`}>
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <h2 className={`text-sm font-bold tracking-tight flex flex-wrap items-center gap-2 ${
              isLightMode ? 'text-slate-950 font-mono' : 'text-white'
            }`}>
              <span>Multi-Application GCP Cloud Run Auto-Healing Engine (4 Active Apps)</span>
              <span className={`text-[10px] uppercase font-mono px-2.5 py-0.5 rounded-full font-semibold border ${
                isLightMode
                  ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                  : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
              }`}>
                Live GCP Infrastructure
              </span>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                🏷️ Source: Subagent Sandbox Harness
              </span>
            </h2>
            <p className={`text-[11px] ${isLightMode ? 'text-slate-600 font-mono' : 'text-slate-400'}`}>
              Active Target: <a href={activeService.url} target="_blank" rel="noreferrer" className={`font-mono underline ${isLightMode ? 'text-slate-950 font-bold hover:text-slate-700' : 'text-cyan-300 hover:text-cyan-200'}`}>{activeService.url}</a>
            </p>
          </div>
        </div>
      </div>

      {/* 4 CLOUD RUN MICROSERVICES SELECTOR TABS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
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
                  ? isLightMode
                    ? 'bg-slate-950 border-slate-950 text-white shadow-md font-mono'
                    : 'bg-slate-800 border-cyan-400 text-white shadow-lg shadow-cyan-500/10'
                  : isLightMode
                    ? 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'
                    : 'bg-black/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <IconComp className={`w-4 h-4 ${isSelected ? (isLightMode ? 'text-white' : 'text-cyan-400') : (isLightMode ? 'text-slate-600' : 'text-slate-500')}`} />
                <span className={`w-2 h-2 rounded-full ${isSelected ? (isLightMode ? 'bg-white animate-pulse' : 'bg-cyan-400 animate-pulse') : (isLightMode ? 'bg-slate-400' : 'bg-slate-600')}`}></span>
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
      <div className={`p-3.5 rounded-xl border flex flex-col sm:flex-row items-center justify-between gap-3 ${
        isLightMode
          ? 'bg-slate-50 border-slate-200 text-slate-900'
          : 'bg-black/60 border-slate-800/80 text-slate-300'
      }`}>
        <div className={`text-xs font-semibold flex items-center gap-2 ${isLightMode ? 'text-slate-900 font-mono' : 'text-slate-300'}`}>
          <Play className={`w-3.5 h-3.5 ${isLightMode ? 'text-slate-950' : 'text-cyan-400'}`} />
          <span>Execution Controls for <strong>{activeService.name}</strong>:</span>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          {/* Inject / Break App Button */}
          <button
            onClick={() => triggerAppAction('break', activeAppId)}
            disabled={isProcessing}
            className={`flex-1 sm:flex-initial px-5 py-2.5 rounded-xl border text-xs font-bold font-mono flex items-center justify-center gap-2 transition-all whitespace-nowrap active:scale-95 disabled:opacity-50 cursor-pointer ${
              isLightMode
                ? 'bg-rose-50 hover:bg-rose-100 border-rose-300 text-rose-800 shadow-sm'
                : 'bg-gradient-to-r from-rose-900/80 to-red-950/80 hover:from-rose-800 hover:to-red-900 text-rose-200 border-rose-500/50 shadow-lg shadow-rose-500/10'
            }`}
            title={`Inject error into ${activeService.name}`}
          >
            <Flame className="w-4 h-4 text-rose-600" />
            <span>🔴 Inject App Error</span>
          </button>

          {/* Auto-Heal & Restore App Button */}
          <button
            onClick={() => triggerAppAction('heal', activeAppId)}
            disabled={isProcessing}
            className={`flex-1 sm:flex-initial px-6 py-2.5 rounded-xl text-white font-bold font-mono text-xs flex items-center justify-center gap-2 shadow-md transition-all whitespace-nowrap active:scale-95 disabled:opacity-50 cursor-pointer ${
              isLightMode
                ? 'bg-slate-950 hover:bg-slate-800 border border-slate-900'
                : 'bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:via-teal-500 hover:to-cyan-500 shadow-lg shadow-emerald-500/20'
            }`}
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
        <div className={`p-3 rounded-xl border space-y-1 ${
          isLightMode
            ? 'bg-[#f8fafc] border-slate-200 text-slate-900 font-mono'
            : 'bg-black/60 border-slate-800'
        }`}>
          <span className={`text-[10px] uppercase font-semibold ${isLightMode ? 'text-slate-500' : 'text-slate-400'}`}>Selected App</span>
          <div className={`font-mono font-bold truncate ${isLightMode ? 'text-slate-950' : 'text-cyan-300'}`}>{activeService.id}</div>
        </div>

        <div className={`p-3 rounded-xl border space-y-1 ${
          isLightMode
            ? 'bg-[#f8fafc] border-slate-200 text-slate-900 font-mono'
            : 'bg-black/60 border-slate-800'
        }`}>
          <span className={`text-[10px] uppercase font-semibold ${isLightMode ? 'text-slate-500' : 'text-slate-400'}`}>Active GCP Region</span>
          <div className={`font-mono font-bold truncate ${isLightMode ? 'text-slate-950' : 'text-purple-300'}`}>us-central1 (vtxdemos)</div>
        </div>

        <div className={`p-3 rounded-xl border space-y-1 ${
          isLightMode
            ? 'bg-[#f8fafc] border-slate-200 text-slate-900 font-mono'
            : 'bg-black/60 border-slate-800'
        }`}>
          <span className={`text-[10px] uppercase font-semibold ${isLightMode ? 'text-slate-500' : 'text-slate-400'}`}>Live Revision Status</span>
          <div className="flex items-center space-x-2 font-mono font-bold">
            <span className={`w-2.5 h-2.5 rounded-full ${isBroken ? 'bg-rose-500 animate-ping' : 'bg-emerald-500'}`}></span>
            <span className={isBroken ? 'text-rose-700 font-bold' : 'text-emerald-700 font-bold'}>
              {isBroken ? 'HTTP 500 ERROR (BROKEN)' : 'HTTP 200 OK (HEALED)'}
            </span>
          </div>
        </div>
      </div>

      {/* WORKSTATION TAB CONTROL BAR */}
      <div className={`rounded-xl border overflow-hidden ${
        isLightMode ? 'bg-[#f8fafc] border-slate-300' : 'bg-black/80 border-slate-800'
      }`}>
        <div className={`flex items-center justify-between border-b px-4 py-2 ${
          isLightMode ? 'bg-slate-100 border-slate-300' : 'bg-slate-950 border-slate-800'
        }`}>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'preview'
                  ? isLightMode
                    ? 'bg-white text-slate-950 border border-slate-300 shadow-sm font-mono'
                    : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md'
                  : isLightMode
                    ? 'text-slate-700 hover:text-slate-950'
                    : 'text-slate-400 hover:text-white'
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              <span>Live Web Frame ({activeService.name})</span>
            </button>

            <button
              onClick={() => setActiveTab('build')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'build'
                  ? isLightMode
                    ? 'bg-white text-slate-950 border border-slate-300 shadow-sm font-mono'
                    : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
                  : isLightMode
                    ? 'text-slate-700 hover:text-slate-950'
                    : 'text-slate-400 hover:text-white'
              }`}
            >
              <Boxes className="w-3.5 h-3.5" />
              <span>Cloud Build & LLM Fix Stream</span>
            </button>

            <button
              onClick={() => setActiveTab('diff')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'diff'
                  ? isLightMode
                    ? 'bg-white text-slate-950 border border-slate-300 shadow-sm font-mono'
                    : 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md'
                  : isLightMode
                    ? 'text-slate-700 hover:text-slate-950'
                    : 'text-slate-400 hover:text-white'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Applied Code Patch Diff</span>
            </button>

            <button
              onClick={() => setActiveTab('stack')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'stack'
                  ? isLightMode
                    ? 'bg-white text-slate-950 border border-slate-300 shadow-sm font-mono'
                    : 'bg-slate-800 text-white'
                  : isLightMode
                    ? 'text-slate-700 hover:text-slate-950'
                    : 'text-slate-400 hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>Runtime Stack Trace</span>
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href={liveUrl}
              target="_blank"
              rel="noreferrer"
              className={`text-xs font-mono underline flex items-center gap-1 ${
                isLightMode ? 'text-slate-900 font-bold hover:text-slate-700' : 'text-cyan-300 hover:text-cyan-200'
              }`}
            >
              <span>{activeService.url}</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        {/* WORKSTATION CONTENT BODIES */}
        <div className="p-4">
          {/* TAB 1: LIVE IFRAME PREVIEW */}
          {activeTab === 'preview' && (
            <div className="space-y-3">
              <div className={`flex items-center justify-between text-xs px-2 ${isLightMode ? 'text-slate-700 font-mono' : 'text-slate-400'}`}>
                <span>Live Embedded GCP Iframe Window</span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setIframeKey((prev) => prev + 1)}
                    className={`px-2.5 py-1 rounded border text-[11px] font-mono flex items-center gap-1 transition-colors cursor-pointer ${
                      isLightMode
                        ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-950 font-bold'
                        : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200'
                    }`}
                    title="Force refresh iframe element"
                  >
                    <span>🔄 Refresh App Frame</span>
                  </button>

                  <button
                    onClick={() => setIsFullscreenView(true)}
                    className={`px-3 py-1 rounded border text-[11px] font-mono font-bold flex items-center gap-1 transition-all cursor-pointer ${
                      isLightMode
                        ? 'bg-slate-950 hover:bg-slate-800 text-white border-slate-900 shadow-sm'
                        : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white border-purple-500/50 shadow-md'
                    }`}
                    title="Expand Live Cloud Run App to Fullscreen Window"
                  >
                    <Maximize2 className="w-3 h-3" />
                    <span>Expand Fullscreen</span>
                  </button>
                </div>
              </div>

              <div className={`w-full h-[460px] rounded-xl overflow-hidden border shadow-inner ${
                isLightMode ? 'bg-white border-slate-300' : 'bg-white border-slate-800'
              }`}>
                <iframe
                  key={`${activeAppId}-${iframeKey}`}
                  src={liveUrl}
                  title={`${activeService.name} Live Frame`}
                  className="w-full h-full border-0 rounded-xl"
                />
              </div>
            </div>
          )}

          {/* TAB 2: CLOUD BUILD & LLM FIX STREAM */}
          {activeTab === 'build' && (
            <div className="space-y-3 font-mono text-xs">
              <div className={`flex items-center justify-between p-3 rounded-xl border ${
                isLightMode ? 'bg-white border-slate-300 text-slate-900' : 'bg-slate-900/90 border-slate-800 text-slate-200'
              }`}>
                <div className="flex items-center space-x-2">
                  <Cpu className={`w-4 h-4 ${isProcessing ? 'text-amber-500 animate-spin' : 'text-purple-400'}`} />
                  <span className="font-bold">Engine: Gemini 3.5 Flash Lite + GCP Cloud Build</span>
                </div>
                {isProcessing ? (
                  <span className="text-amber-600 font-bold flex items-center gap-2 animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
                    <span>BUILDING CONTAINER & DEPLOYING REVISION...</span>
                  </span>
                ) : (
                  <span className="text-emerald-600 font-bold">STATUS: 200 REVISION DEPLOYED</span>
                )}
              </div>

              <div className={`p-4 rounded-xl border h-72 overflow-y-auto space-y-2 ${
                isLightMode
                  ? 'bg-slate-950 text-emerald-400 border-slate-900 shadow-inner'
                  : 'bg-black/90 text-emerald-400 border-slate-800'
              }`}>
                {(streamedLogs.length > 0
                  ? streamedLogs
                  : (healResult?.remediationLogs || [
                      `[INFO] Target Microservice: ${activeService.id}`,
                      `[INFO] Active GCP Region: us-central1 (Project: vtxdemos)`,
                      `[ANALYSIS] Ready to execute Cloud Build container compilation...`
                    ])
                ).map((logLine, idx) => (
                  <div key={idx} className="flex items-start space-x-2 animate-fadeIn">
                    <span className="text-slate-500 select-none">&gt;</span>
                    <span className="leading-relaxed">{logLine}</span>
                  </div>
                ))}
                {isProcessing && (
                  <div className="flex items-center space-x-2 text-amber-400 pt-1 font-bold animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                    <span>Compiling container layers & deploying Cloud Run revision...</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: APPLIED CODE PATCH DIFF */}
          {activeTab === 'diff' && (
            <div className="space-y-3 font-mono text-xs">
              <div className={`flex items-center justify-between p-2.5 rounded-xl border ${
                isLightMode ? 'bg-white border-slate-300 text-slate-900' : 'bg-slate-900/90 border-slate-800 text-slate-300'
              }`}>
                <span>File: <code>main.py</code></span>
                <span className="text-emerald-500 font-bold">+ Code Fix Applied</span>
              </div>

              <pre className={`p-4 rounded-xl border overflow-x-auto whitespace-pre-wrap ${
                isLightMode
                  ? 'bg-slate-950 text-slate-100 border-slate-900 shadow-inner'
                  : 'bg-black/90 text-slate-200 border-slate-800'
              }`}>
                {healResult?.codeDiff || `# Patch generated for ${activeService.name}:\n- discount_ratio = total_discount / itemCount\n+ discount_ratio = total_discount / itemCount if itemCount > 0 else 0.0`}
              </pre>
            </div>
          )}

          {/* TAB 4: RUNTIME STACK TRACE */}
          {activeTab === 'stack' && (
            <div className="space-y-3 font-mono text-xs">
              <div className={`p-4 rounded-xl border overflow-x-auto ${
                isLightMode
                  ? 'bg-slate-950 text-rose-400 border-slate-900 shadow-inner'
                  : 'bg-black/90 text-rose-400 border-slate-800'
              }`}>
                {healResult?.stackTrace || activeService.errorSummary}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* FULLSCREEN LIVE WEB FRAME MODAL */}
      {isFullscreenView && (
        <div className="fixed inset-0 z-50 flex flex-col bg-slate-950/95 backdrop-blur-md p-6 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${activeService.color} border flex items-center justify-center`}>
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>{activeService.name} (Full-Screen Live Cloud Run Web Frame)</span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    GCP Live Revision
                  </span>
                </h2>
                <a href={liveUrl} target="_blank" rel="noreferrer" className="text-xs text-cyan-300 font-mono underline hover:text-cyan-200 flex items-center gap-1">
                  <span>{liveUrl}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <a
                href={liveUrl}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-500/20"
              >
                <span>↗ Open in New Browser Tab</span>
              </a>

              <button
                onClick={() => setIsFullscreenView(false)}
                className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-all cursor-pointer"
                title="Exit Full Screen"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="flex-1 w-full h-full rounded-2xl overflow-hidden border border-slate-700 bg-white shadow-2xl">
            <iframe
              key={`fs-${iframeKey}`}
              src={liveUrl}
              title={`${activeService.name} Fullscreen`}
              className="w-full h-full border-0 rounded-2xl"
            />
          </div>
        </div>
      )}
    </div>
  );
};
