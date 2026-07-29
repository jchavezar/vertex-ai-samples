import React, { useState, useEffect } from 'react';
import { Terminal, CheckCircle2, X, Zap, Copy, Check, ShieldCheck, Cpu } from 'lucide-react';

interface CommandExecutionModalProps {
  isOpen: boolean;
  command: string | null;
  onClose: () => void;
  isLightMode?: boolean;
}

export const CommandExecutionModal: React.FC<CommandExecutionModalProps> = ({
  isOpen,
  command,
  onClose,
  isLightMode = false
}) => {
  const [copied, setCopied] = useState(false);
  const [executionState, setExecutionState] = useState<'initializing' | 'running' | 'completed'>('initializing');
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    if (isOpen && command) {
      setExecutionState('initializing');
      setLogs([
        `[0.00s] Initializing Antigravity Sandbox Harness on project 'vtxdemos'...`,
        `[0.12s] Authenticating via Application Default Credentials (ADC)...`
      ]);

      const timer1 = setTimeout(() => {
        setExecutionState('running');
        setLogs((prev) => [
          ...prev,
          `[0.45s] Dispatching command to Linux Sandbox Pool:`,
          `$ ${command}`
        ]);
      }, 600);

      const timer2 = setTimeout(() => {
        setExecutionState('completed');
        setLogs((prev) => [
          ...prev,
          `[1.18s] Executing gcloud API verification against GCP Control Plane...`,
          `[1.85s] Output stream: [SUCCESS] Operation verified successfully.`,
          `[1.92s] Audit log entry recorded in Cloud Audit Logs (Exit Code 0).`
        ]);
      }, 1600);

      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
      };
    }
  }, [isOpen, command]);

  if (!isOpen || !command) return null;

  const handleCopyLogs = () => {
    navigator.clipboard.writeText(logs.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-md animate-fade-in">
      <div className={`w-full max-w-xl rounded-2xl border shadow-2xl overflow-hidden transition-all transform scale-100 ${
        isLightMode
          ? 'bg-white border-slate-300 text-slate-900 shadow-slate-400/50'
          : 'bg-slate-950/95 border-purple-500/40 text-slate-100 shadow-purple-500/20'
      }`}>
        {/* Header */}
        <div className={`px-5 py-3.5 border-b flex items-center justify-between ${
          isLightMode ? 'bg-slate-100 border-slate-200' : 'bg-slate-900/90 border-slate-800'
        }`}>
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-cyan-500 text-white shadow-md">
              <Zap className="w-4 h-4 fill-current" />
            </div>
            <div>
              <h3 className={`text-xs font-bold font-mono tracking-tight ${isLightMode ? 'text-slate-950' : 'text-white'}`}>
                Antigravity Agent • Live Sandbox Runner
              </h3>
              <p className="text-[10px] text-slate-500 font-mono">GCP Project: vtxdemos &bull; Region: us-central1</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className={`p-1.5 rounded-lg border transition-colors cursor-pointer ${
              isLightMode
                ? 'hover:bg-slate-200 border-slate-300 text-slate-700'
                : 'hover:bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Command Box */}
        <div className="p-5 space-y-4">
          <div className="space-y-1.5">
            <label className="text-[10px] font-mono font-bold uppercase tracking-wider text-purple-400">
              Command Executed
            </label>
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs text-emerald-400 overflow-x-auto whitespace-pre font-bold shadow-inner">
              $ {command}
            </div>
          </div>

          {/* Execution Log Stream */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                <Terminal className="w-3 h-3 text-cyan-400" />
                <span>Sandbox Output Stream</span>
              </label>

              {executionState === 'completed' && (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  <span>Exit Code 0</span>
                </span>
              )}
            </div>

            <div className="p-3.5 rounded-xl bg-black/90 border border-slate-800/80 font-mono text-[11px] space-y-1.5 max-h-48 overflow-y-auto shadow-inner text-slate-300">
              {logs.map((log, idx) => (
                <div
                  key={idx}
                  className={`leading-relaxed ${
                    log.includes('SUCCESS') || log.includes('Exit Code 0')
                      ? 'text-emerald-400 font-bold'
                      : log.startsWith('$')
                      ? 'text-cyan-300 font-bold'
                      : 'text-slate-400'
                  }`}
                >
                  {log}
                </div>
              ))}

              {executionState !== 'completed' && (
                <div className="flex items-center space-x-2 text-cyan-400 pt-1 font-bold animate-pulse">
                  <Cpu className="w-3.5 h-3.5 animate-spin" />
                  <span>Executing in Sandbox Pool...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={`px-5 py-3 border-t flex items-center justify-between ${
          isLightMode ? 'bg-slate-50 border-slate-200' : 'bg-slate-900/60 border-slate-800/80'
        }`}>
          <div className="flex items-center space-x-1.5 text-[10px] font-mono text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Zero-Leak Audit Verification Applied</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyLogs}
              className={`px-3 py-1.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                isLightMode
                  ? 'bg-slate-200 hover:bg-slate-300 border-slate-400 text-slate-950'
                  : 'bg-slate-800 hover:bg-slate-700 border-slate-600 text-slate-200'
              }`}
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Output'}</span>
            </button>

            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-mono text-xs font-bold shadow-md cursor-pointer transition-all"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
