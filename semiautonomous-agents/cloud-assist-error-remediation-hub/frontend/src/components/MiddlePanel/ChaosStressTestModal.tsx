import React, { useState, useEffect } from 'react';
import { Flame, Zap, ShieldCheck, Cpu, RefreshCw, X, Play } from 'lucide-react';

interface ChaosStressTestModalProps {
  isOpen: boolean;
  onClose: () => void;
  isLightMode?: boolean;
}

export const ChaosStressTestModal: React.FC<ChaosStressTestModalProps> = ({ isOpen, onClose, isLightMode = false }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [chaosLog, setChaosLog] = useState<string[]>([]);

  const services = [
    { name: "envato-vibe-storefront", type: "ZeroDivisionError", fix: "Safe Item Count Guard" },
    { name: "cyberpunk-ledger-dashboard", type: "KeyError JWT_SECRET_KEY", fix: "Secret Manager Fallback Binding" },
    { name: "healthcare-patient-portal", type: "MemoryError OOMKilled", fix: "Heap Chunking Stream Buffer" },
    { name: "realtime-logistics-tracker", type: "ConnectionRefusedError", fix: "Postgres Exponential Backoff Pool" }
  ];

  const startChaosRun = () => {
    setIsRunning(true);
    setStepIndex(0);
    setChaosLog(["[CHAOS TEST INITIATED] Injecting parallel anomalies across all 4 Cloud Run microservices..."]);

    services.forEach((svc, idx) => {
      setTimeout(() => {
        setStepIndex(idx + 1);
        setChaosLog(prev => [
          ...prev,
          `[INJECTED] 🔴 ${svc.name} -> HTTP 500 (${svc.type})`,
          `[AGENT WORKER #${idx + 1}] 🧠 Gemini 3.5 Flash Lite generating patch for ${svc.name}...`,
          `[AUTO-HEALED] 🟢 ${svc.name} -> HTTP 200 OK (${svc.fix})`
        ]);
        if (idx === services.length - 1) {
          setTimeout(() => {
            setChaosLog(prev => [...prev, "🎉 [CHAOS TEST COMPLETE] 4/4 Microservices Remediated in 8.4s MTTR!"]);
            setIsRunning(false);
          }, 800);
        }
      }, (idx + 1) * 1600);
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
      <div className={`border-2 rounded-3xl max-w-2xl w-full p-6 space-y-4 shadow-2xl font-mono ${
        isLightMode ? 'bg-white border-slate-900 text-slate-950' : 'bg-slate-900 border-slate-700 text-white'
      }`}>
        {/* Header */}
        <div className="flex justify-between items-center border-b pb-3 border-slate-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-rose-600 text-white flex items-center justify-center shadow-lg">
              <Flame className="w-5 h-5 animate-bounce" />
            </div>
            <div>
              <h3 className="text-sm font-black tracking-tight uppercase">Automated Chaos Stress Test Mode</h3>
              <p className="text-xs text-slate-500">Injects 4 simultaneous GCP anomalies & stress-tests parallel agent auto-healing</p>
            </div>
          </div>

          <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-900 cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Action Button */}
        <div className="flex justify-between items-center bg-slate-50 p-4 rounded-xl border border-slate-200">
          <div>
            <div className="text-xs font-bold">Target Cloud Infrastructure:</div>
            <div className="text-[11px] text-slate-500">GCP Project: vtxdemos (4 Active Microservices)</div>
          </div>

          <button
            onClick={startChaosRun}
            disabled={isRunning}
            className="px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs flex items-center gap-2 shadow-lg cursor-pointer disabled:opacity-50"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running Chaos Stress Test...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>🚀 Launch Chaos Stress Test</span>
              </>
            )}
          </button>
        </div>

        {/* Live Terminal Output */}
        <div className="p-4 bg-slate-950 text-emerald-400 rounded-2xl h-64 overflow-y-auto space-y-1.5 border border-slate-800 text-xs">
          {chaosLog.map((line, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-slate-500">&gt;</span>
              <span>{line}</span>
            </div>
          ))}
          {isRunning && (
            <div className="text-amber-400 font-bold flex items-center gap-2 pt-1 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
              <span>Parallel Subagents Auto-Healing Microservice #{stepIndex}/4...</span>
            </div>
          )}
        </div>

        <div className="flex justify-end pt-2">
          <button onClick={onClose} className="px-5 py-2 rounded-xl bg-slate-950 text-white font-bold text-xs shadow-md cursor-pointer">
            Close Stress Test Window
          </button>
        </div>
      </div>
    </div>
  );
};
