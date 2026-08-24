import React, { useState } from 'react';
import {
  CheckCircle2,
  Copy,
  Printer,
  X,
  ShieldCheck,
  Building,
} from 'lucide-react';
import { BoardMemoResponse } from '../types';

interface ExecutiveMemoModalProps {
  memo: BoardMemoResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ExecutiveMemoModal: React.FC<ExecutiveMemoModalProps> = ({
  memo,
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !memo) return null;

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(memo.full_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 md:p-8">
      <div className="bg-[#0f172a] border border-cyan-500/40 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl shadow-cyan-950/60 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <div className="h-full w-full bg-slate-900 rounded-[10px] flex items-center justify-center">
                <Building className="h-4 w-4 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-extrabold text-slate-100 text-sm tracking-wide">
                  EXECUTIVE BOARDROOM DECISION MEMORANDUM
                </h2>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800 rounded font-bold">
                  BOARD READY
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                {memo.memo_id} &bull; Generated in {memo.generation_time_ms.toFixed(0)} ms
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyMarkdown}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              {copied ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy Markdown</span>
                </>
              )}
            </button>

            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              <Printer className="h-3.5 w-3.5" />
              <span>Print / PDF</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* Key Metrics Badges */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {memo.key_metrics_table.map((m, idx) => (
              <div
                key={idx}
                className="bg-slate-950/80 p-3 rounded-xl border border-slate-800"
              >
                <span className="text-[10px] font-mono text-slate-400 uppercase block">
                  {m.metric}
                </span>
                <span className="text-base font-extrabold text-slate-100 font-mono mt-0.5 block">
                  {m.value}
                </span>
                <span
                  className={`text-[9px] font-mono font-bold mt-1 inline-block px-1.5 py-0.5 rounded ${
                    m.status === 'ELEVATED' || m.status === 'ACTION REQUIRED'
                      ? 'bg-rose-950 text-rose-300 border border-rose-800'
                      : m.status === 'WARNING'
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}
                >
                  {m.status}
                </span>
              </div>
            ))}
          </div>

          {/* Formatted Markdown Content */}
          <div className="bg-slate-950/90 rounded-xl p-6 border border-slate-800 text-slate-200 text-xs font-sans leading-relaxed space-y-4">
            <div className="whitespace-pre-wrap font-mono text-[11px] leading-relaxed text-slate-300">
              {memo.full_markdown}
            </div>
          </div>

          {/* Governance Sign-offs */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-3 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              Governance & Attestation Record
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
              {memo.governance_signoffs.map((sig, idx) => (
                <div
                  key={idx}
                  className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 flex items-center justify-between"
                >
                  <div>
                    <span className="font-bold text-slate-200 block">{sig.role}</span>
                    <span className="text-[10px] text-slate-500">{sig.timestamp}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-800/80 rounded text-[10px] font-bold">
                    {sig.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-slate-900/90 flex items-center justify-between">
          <span className="text-xs text-slate-500 font-mono">
            Attestation: Gemini 2.5/3 Enterprise Engine &bull; Zero-Leak Protocol Enforced
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-lg transition-all"
          >
            Close Memorandum
          </button>
        </div>
      </div>
    </div>
  );
};
