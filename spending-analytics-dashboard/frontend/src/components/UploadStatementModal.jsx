import React, { useState } from 'react';
import { X, Upload, Sparkles, Mail, CheckCircle2, FileText, ArrowRight, Loader2, ShieldCheck, Orbit, Database, RefreshCw } from 'lucide-react';

export default function UploadStatementModal({ isOpen, files, isUploading, gmailStatus, onConfirmUpload, onCancel, onOpenGmailAuth, cachedCount = 0 }) {
  const [pipelineMode, setPipelineMode] = useState('FULL_RERUN'); // Default to full parallel live stream on statement upload

  if (!isOpen || !files || files.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-xl animate-fadeIn">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-lg shadow-indigo-600/20">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Statement Ingestion & Transformation</h3>
              <p className="text-[11px] text-slate-400">Piping {files.length} statement file(s) into PulseSpend AI</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {/* Selected Files List */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Selected Statements</span>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5 max-h-32 overflow-y-auto">
              {Array.from(files).map((f, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs text-slate-200">
                  <div className="flex items-center gap-2 truncate">
                    <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span className="truncate font-mono">{f.name}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{(f.size / 1024).toFixed(1)} KB</span>
                </div>
              ))}
            </div>
          </div>

          {/* Persisted Cache Status & Pipeline Options */}
          <div className="space-y-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Agent Intelligence Pipeline Execution</span>

            {/* Option A: Keep & Merge Existing Extraction */}
            <div
              onClick={() => setPipelineMode('REUSE_CACHE')}
              className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                pipelineMode === 'REUSE_CACHE'
                  ? 'bg-indigo-950/40 border-indigo-500/50 shadow-md shadow-indigo-500/10'
                  : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-xl border shrink-0 mt-0.5 ${
                  pipelineMode === 'REUSE_CACHE' ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' : 'bg-slate-900 text-slate-500 border-slate-800'
                }`}>
                  <Database className="w-4 h-4" />
                </div>
                <div className="space-y-1 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-white">Keep Existing Agent Extractions (Fast & Persistent)</h4>
                    <input
                      type="radio"
                      name="pipelineMode"
                      checked={pipelineMode === 'REUSE_CACHE'}
                      onChange={() => setPipelineMode('REUSE_CACHE')}
                      className="text-indigo-600 cursor-pointer"
                    />
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Instantly preserves all previously parsed receipts, Gmail groundings, and SKU itemizations without re-running the full cluster.
                  </p>
                </div>
              </div>
            </div>

            {/* Option B: Re-run Full Parallel Cluster */}
            <div
              onClick={() => setPipelineMode('FULL_RERUN')}
              className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                pipelineMode === 'FULL_RERUN'
                  ? 'bg-indigo-950/40 border-indigo-500/50 shadow-md shadow-indigo-500/10'
                  : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-xl border shrink-0 mt-0.5 ${
                  pipelineMode === 'FULL_RERUN' ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' : 'bg-slate-900 text-slate-500 border-slate-800'
                }`}>
                  <RefreshCw className="w-4 h-4" />
                </div>
                <div className="space-y-1 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-white">Re-Run 8x Parallel ADK Cluster (Full Re-Scan)</h4>
                    <input
                      type="radio"
                      name="pipelineMode"
                      checked={pipelineMode === 'FULL_RERUN'}
                      onChange={() => setPipelineMode('FULL_RERUN')}
                      className="text-indigo-600 cursor-pointer"
                    />
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Spawns 8 parallel subagents with Gemini 3.7 Flash and queries Gmail in real-time for updated receipts and return policies.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Includes cross-statement deduplication and automatic negative return linking.</span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <button
            onClick={onCancel}
            disabled={isUploading}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-colors cursor-pointer"
          >
            Cancel
          </button>

          <button
            onClick={() => onConfirmUpload(files, pipelineMode === 'FULL_RERUN')}
            disabled={isUploading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-violet-600 hover:opacity-95 text-white font-bold text-xs shadow-lg shadow-indigo-600/25 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {isUploading ? (
              <Loader2 className="w-4 h-4 animate-spin text-white" />
            ) : (
              <Orbit className="w-4 h-4" />
            )}
            {isUploading ? 'Executing Pipeline...' : pipelineMode === 'FULL_RERUN' ? 'Re-Run Parallel Pipeline' : 'Ingest & Keep Extractions'}
          </button>
        </div>
      </div>
    </div>
  );
}
