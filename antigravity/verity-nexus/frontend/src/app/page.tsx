"use client";

import React, { useEffect, useState, useRef } from 'react';
import { useChat } from 'ai/react';
import { useVerityStore } from '@/store/verityStore';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  Activity,
  FileCheck,
  Terminal,
  BarChart3,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Globe,
  Layers,
  Search,
  ChevronRight,
  Maximize2,
  X
} from 'lucide-react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';

// --- Sub-Components ---

const CyberCard = ({ children, className = "", glowColor = "orange" }: { children: React.ReactNode, className?: string, glowColor?: string }) => (
  <div className={`relative group ${className}`}>
    <div className={`absolute -inset-1 bg-gradient-to-r ${glowColor === 'orange' ? 'from-orange-600/20 via-orange-500/10 to-transparent' : 'from-emerald-600/20 via-emerald-500/10 to-transparent'} rounded-[24px] blur-xl opacity-0 group-hover:opacity-100 transition-all duration-700`}></div>
    <div className="relative bg-[#080808] border border-white/5 rounded-2xl p-6 h-full overflow-hidden transition-all group-hover:border-white/10 shadow-2xl">
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      {children}
    </div>
  </div>
);

const DataShardBadge = ({ count }: { count: number }) => {
  const handleJump = () => {
    const el = document.getElementById('neural-shard-layer');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Trigger a visual confirmation pulse on the target panel
      el.style.borderColor = 'rgba(249, 115, 22, 0.5)';
      el.style.boxShadow = '0 0 50px rgba(249, 115, 22, 0.15)';
      setTimeout(() => {
        el.style.borderColor = '';
        el.style.boxShadow = '';
      }, 2000);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, backgroundColor: 'rgba(249, 115, 22, 0.15)' }}
      whileTap={{ scale: 0.98 }}
      onClick={handleJump}
      className="bg-orange-500/10 border border-orange-500/20 rounded-2xl p-4 flex items-center gap-4 group transition-all cursor-pointer select-none"
    >
      <div className="w-10 h-10 rounded-xl bg-orange-600/20 flex items-center justify-center border border-orange-500/30 group-hover:scale-110 group-hover:border-orange-500/50 transition-all">
        <Layers className="w-5 h-5 text-orange-500" />
      </div>
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
          <p className="text-[10px] font-black text-orange-500 uppercase tracking-[0.2em]">Forensic Shard Detected</p>
        </div>
        <p className="text-[11px] text-slate-300 font-medium">
          Synchronized <span className="text-white font-black">{count} analytical findings</span> to the neural discovery layer.
        </p>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <span className="text-[7px] font-black text-orange-500/0 group-hover:text-orange-500/40 uppercase tracking-widest transition-all">Jump to Shard</span>
        <ChevronRight className="w-4 h-4 text-orange-500/50 group-hover:translate-x-1 group-hover:text-orange-500 transition-all" />
      </div>
    </motion.div>
  );
};

const AuditFindings = () => {
  const { findings } = useVerityStore();
  const items = Array.isArray(findings) ? findings : [];

  if (!items || items.length === 0) return (
    <div className="h-full flex flex-col items-center justify-center text-center py-20 opacity-30">
      <div className="relative mb-8">
        <Activity className="w-16 h-16 text-slate-500" />
        <motion.div
          animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-0 bg-orange-500/30 rounded-full blur-[40px]"
        />
      </div>
      <p className="text-[10px] uppercase tracking-[0.4em] font-black text-slate-400">Neural Sync Pending</p>
      <p className="text-[8px] uppercase tracking-[0.2em] text-slate-600 mt-2 font-bold select-none cursor-default">Synchronizing Swarm Intelligence Findsets</p>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4 px-2">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center">
            <Layers className="w-4 h-4 text-orange-500 z-10" />
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 10, repeat: Infinity, ease: "linear" }} className="absolute inset-0 border border-orange-500/30 rounded-full scale-150" />
          </div>
          <h3 className="text-[11px] font-black text-white uppercase tracking-[0.4em]">Neural Discovery Shards</h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[8px] font-bold text-slate-500 tracking-widest uppercase animate-pulse">Live Uplink</span>
          <span className="text-[10px] font-mono text-white bg-orange-600 px-3 py-1 rounded-full border border-orange-400/50 shadow-lg shadow-orange-500/20">
            {items.length} FINDINGS
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5">
        <AnimatePresence mode="popLayout">
          {items.map((finding: any, idx: number) => {
            const riskLevel = finding.risk_score >= 0.8 ? 'CRITICAL' : finding.risk_score >= 0.5 ? 'MATERIAL' : 'ELEVATED';
            const riskColor = riskLevel === 'CRITICAL' ? 'text-red-500' : riskLevel === 'MATERIAL' ? 'text-orange-500' : 'text-yellow-500';
            const riskBg = riskLevel === 'CRITICAL' ? 'bg-red-500/10' : riskLevel === 'MATERIAL' ? 'bg-orange-500/10' : 'bg-yellow-500/10';
            const riskBorder = riskLevel === 'CRITICAL' ? 'border-red-500/20' : riskLevel === 'MATERIAL' ? 'border-orange-500/20' : 'border-yellow-500/20';

            return (
              <motion.div
                key={finding.trans_id || idx}
                initial={{ opacity: 0, scale: 0.95, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ type: "spring", stiffness: 100, damping: 15 }}
                className="relative group"
              >
                {/* Glow Background */}
                <div className={`absolute -inset-0.5 ${riskBg} rounded-2xl blur opacity-20 group-hover:opacity-100 transition duration-500`} />

                <div className={`relative bg-[#0A0A0A] border ${riskBorder} rounded-2xl p-6 hover:bg-[#0D0D0D] transition-all cursor-crosshair overflow-hidden shadow-2xl`}>
                  {/* Subtle Grid Background */}
                  <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:20px_20px]" />

                  <div className="relative z-10">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex gap-4">
                        <div className={`w-12 h-12 rounded-xl ${riskBg} flex items-center justify-center border ${riskBorder} shadow-inner`}>
                          <Zap className={`w-6 h-6 ${riskColor}`} />
                        </div>
                        <div>
                          <p className={`text-[8px] font-black uppercase tracking-[0.3em] mb-1 ${riskColor}`}>{riskLevel} Finding</p>
                          <h4 className="text-lg font-black text-white group-hover:text-orange-400 transition-colors uppercase tracking-tight leading-none mb-2">
                            {finding.vendor || finding.category || "Unknown Entity"}
                          </h4>
                          <div className="flex items-center gap-3">
                            <motion.span
                              whileHover={{ scale: 1.05, backgroundColor: 'rgba(255,255,255,0.1)' }}
                              whileTap={{ scale: 0.95 }}
                              onClick={(e) => {
                                e.stopPropagation();
                                const shardId = `SHARD_${finding.trans_id?.split('-').pop() || 'IDX'}`;
                                navigator.clipboard.writeText(shardId);
                                // Brief visual confirmation on the element itself could go here
                              }}
                              title="Click to copy Shard ID"
                              className="text-[10px] font-mono text-slate-500 bg-white/5 px-2 py-0.5 border border-white/5 rounded cursor-pointer transition-colors hover:text-orange-400 hover:border-orange-500/30"
                            >
                              SHARD_{finding.trans_id?.split('-').pop() || 'IDX'}
                            </motion.span>
                            <span className="text-[11px] font-black text-white">
                              EXP: ${finding.amount?.toLocaleString() || '---'}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-black text-white leading-none tracking-tighter shadow-orange-500/20 drop-shadow-lg">
                          {(finding.risk_score * 10).toFixed(1)}
                        </div>
                        <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600 font-black mt-2">
                          RISK INDEX
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {/* Risk Factors */}
                      <div className="flex flex-wrap gap-2">
                        {(finding.risk_factors || [finding.risk_level || 'General Anomaly']).map((factor: string, i: number) => (
                          <span key={i} className="text-[8px] bg-white/[0.04] border border-white/10 text-slate-300 px-3 py-1.5 rounded-lg uppercase tracking-[0.15em] font-bold shadow-sm">
                            {factor}
                          </span>
                        ))}
                      </div>

                      {/* Intelligence Insight */}
                      <motion.div
                        whileHover={{ backgroundColor: 'rgba(255,255,255,0.04)', borderColor: 'rgba(249, 115, 22, 0.2)' }}
                        className="relative p-4 bg-white/[0.02] border border-white/5 rounded-xl group/insight cursor-help transition-all"
                      >
                        <div className="absolute left-0 top-3 bottom-3 w-0.5 bg-orange-500 rounded-full group-hover/insight:h-full transition-all" />
                        <p className="text-[11px] text-slate-400 leading-relaxed font-medium pl-2 italic">
                          "{finding.recommendation || finding.impact_assessment || "Awaiting secondary agent validation."}"
                        </p>
                        <div className="absolute right-3 bottom-2 opacity-0 group-hover/insight:opacity-40 transition-opacity">
                          <p className="text-[7px] font-black text-orange-500 uppercase tracking-widest">Deep Dive Available</p>
                        </div>
                      </motion.div>

                      {/* Bottom Visual Bar */}
                      <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${finding.risk_score * 100}%` }}
                          className={`h-full ${riskColor.replace('text', 'bg')} opacity-40`}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};

const MaterialityGauge = () => {
  const { stats } = useVerityStore();
  const percentage = Math.min(stats.materiality_reached, 100);

  return (
    <CyberCard>
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]" />
            <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-[0.4em]">Exposure Index</h3>
          </div>
          <p className="text-3xl font-black text-white tracking-tighter drop-shadow-2xl">
            ${stats.total_exposure.toLocaleString()}
          </p>
        </div>
        <motion.div
          animate={{
            scale: percentage > 80 ? [1, 1.1, 1] : 1,
            boxShadow: percentage > 80 ? ["0 0 0px rgba(239,68,68,0)", "0 0 20px rgba(239,68,68,0.4)", "0 0 0px rgba(239,68,68,0)"] : "none"
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className={`w-14 h-14 rounded-2xl flex items-center justify-center border transition-all duration-500 ${percentage > 70 ? 'bg-red-500/10 border-red-500/40 text-red-500 shadow-lg' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500'}`}
        >
          <ShieldAlert className="w-7 h-7" />
        </motion.div>
      </div>

      <div className="space-y-5">
        <div className="flex justify-between items-end mb-1">
          <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.3em]">Materiality Load</span>
          <span className={`text-base font-mono font-black ${percentage > 80 ? 'text-red-500' : 'text-emerald-500'}`}>
            {percentage.toFixed(1)}%
          </span>
        </div>
        <div className="relative h-3 bg-white/[0.03] rounded-full overflow-hidden border border-white/5 p-[1px]">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            className={`h-full relative rounded-full ${percentage > 75 ? 'bg-gradient-to-r from-orange-600 to-red-600' : 'bg-gradient-to-r from-emerald-600 to-teal-600'}`}
          >
            <div className="absolute inset-0 bg-white/30 animate-pulse" />
            <motion.div
              animate={{ x: ['-100%', '100%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent w-20"
            />
          </motion.div>
        </div>
        <div className="flex justify-between pt-1">
          <span className="text-[7px] font-black text-slate-700 uppercase tracking-widest">Floor: Nominal</span>
          <span className="text-[7px] font-black text-slate-700 uppercase tracking-widest text-right">Limit: $1.5M Shard</span>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4">
        <div className="bg-white/[0.03] rounded-2xl p-4 border border-white/5 group hover:border-orange-500/20 transition-all">
          <span className="block text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1.5">Anomalies</span>
          <div className="flex items-center gap-2">
            <div className="w-1 h-4 bg-orange-500/50 rounded-full" />
            <span className="text-2xl font-black text-white">{stats.anomalies_found}</span>
          </div>
        </div>
        <div className="bg-white/[0.03] rounded-2xl p-4 border border-white/5 group hover:border-emerald-500/20 transition-all">
          <span className="block text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1.5">Status</span>
          <span className={`text-[10px] font-black uppercase tracking-widest ${percentage > 50 ? 'text-orange-500 animate-pulse' : 'text-emerald-500'}`}>
            {percentage > 50 ? 'Critical' : 'Nominal'}
          </span>
        </div>
      </div>
    </CyberCard>
  );
};

const EvidenceLedgerModal = () => {
  const { findings, setEvidenceMaximized } = useVerityStore();
  const [ledgerData, setLedgerData] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    fetch('http://localhost:8005/api/ledger')
      .then(res => res.json())
      .then(data => {
        if (data.transactions) {
          setLedgerData(data.transactions);
        }
      })
      .catch(err => console.error("Error fetching ledger:", err))
      .finally(() => setIsLoading(false));
  }, []);

  const items = React.useMemo(() => {
    if (ledgerData.length === 0) return findings;

    const anomalyMap = new Map();
    (findings || []).forEach((f: any) => {
      if (f.trans_id) {
        anomalyMap.set(f.trans_id, f);
        const numPart = f.trans_id.split('-').pop();
        if (numPart) anomalyMap.set(numPart, f);
      }
    });

    const combined = ledgerData.map(row => {
      const f = anomalyMap.get(row.trans_id) || anomalyMap.get(row.trans_id?.split('-').pop());

      if (f) {
        return {
          ...row,
          vendor: row.vendor_name,
          amount: row.amount_usd,
          risk_score: f.risk_score || 0,
          risk_factors: f.risk_factors || [],
          recommendation: f.recommendation || "",
          hasFinding: true
        };
      }
      return {
        ...row,
        vendor: row.vendor_name,
        amount: row.amount_usd,
        risk_score: 0,
        risk_factors: [],
        recommendation: "Standard operating procedure. No anomalies detected.",
        hasFinding: false
      };
    });

    combined.sort((a, b) => {
      if (a.hasFinding && !b.hasFinding) return -1;
      if (!a.hasFinding && b.hasFinding) return 1;
      return (b.risk_score || 0) - (a.risk_score || 0);
    });

    return combined;
  }, [ledgerData, findings]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-2xl flex flex-col p-12 overflow-hidden"
    >
      <div className="flex justify-between items-center mb-8 shrink-0">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-600/20 flex items-center justify-center border border-cyan-500/30">
            <Search className="w-5 h-5 text-cyan-500" />
          </div>
          <div>
            <h2 className="text-xl font-black text-white uppercase tracking-tighter">Forensic Evidence Ledger</h2>
            <p className="text-[10px] font-bold text-cyan-500/50 uppercase tracking-[0.4em]">Cross-Verification Data Grid</p>
          </div>
        </div>
        <button
          onClick={() => setEvidenceMaximized(false)}
          className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors group"
        >
          <X className="w-6 h-6 text-slate-400 group-hover:scale-110 group-hover:text-white transition-all" />
        </button>
      </div>

      <div className="flex-1 overflow-auto border border-white/10 rounded-2xl bg-[#080808] relative custom-scrollbar">
        <div className="absolute inset-0 bg-cyan-500/5 pointer-events-none" />
        <table className="w-full text-left text-[11px] text-slate-300 relative z-10">
          <thead className="sticky top-0 bg-[#0A0A0A] uppercase tracking-widest text-[9px] font-black border-b border-white/10 z-20">
            <tr>
              <th className="p-4 px-6 text-cyan-500/80">Trans_ID</th>
              <th className="p-4 px-6">Date</th>
              <th className="p-4 px-6">Entity/Vendor</th>
              <th className="p-4 px-6 text-right">Exposure</th>
              <th className="p-4 px-6">Risk Profile</th>
              <th className="p-4 px-6 text-right">Index</th>
              <th className="p-4 px-6 w-1/3">Agent Justification</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono">
            {items.map((f, i) => (
              <tr key={f.trans_id || i} className="hover:bg-white/[0.02] transition-colors group cursor-crosshair">
                <td className="p-4 px-6 whitespace-nowrap">
                  <span className="bg-white/5 border border-white/10 px-2 py-1 rounded text-slate-400 group-hover:text-cyan-400 transition-colors">
                    {f.trans_id?.split('-')[0] || `TR-${i}`}
                  </span>
                </td>
                <td className="p-4 px-6 whitespace-nowrap">{f.date || '---'}</td>
                <td className="p-4 px-6 font-bold text-white uppercase tracking-tight">{f.vendor || f.category || 'Unknown'}</td>
                <td className="p-4 px-6 text-right text-orange-400 font-bold whitespace-nowrap">${f.amount?.toLocaleString() || '---'}</td>
                <td className="p-4 px-6">
                  <div className="flex flex-wrap gap-1">
                    {(f.risk_factors || [f.risk_level || 'Anomaly']).map((factor: string, i: number) => (
                      <span key={i} className="text-[8px] bg-red-500/10 text-red-400 px-2 py-0.5 rounded uppercase tracking-wider border border-red-500/20">
                        {factor}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="p-4 px-6 text-right font-black shadow-lg">
                  <span className={f.risk_score > 0.8 ? 'text-red-500' : 'text-orange-500'}>
                    {(f.risk_score * 10).toFixed(1)}
                  </span>
                </td>
                <td className="p-4 px-6 text-slate-400 italic font-sans text-[10px] leading-relaxed">
                  "{f.recommendation || f.impact_assessment || "No detailed assessment provided."}"
                </td>
              </tr>
            ))}
            {isLoading ? (
              <tr>
                <td colSpan={7} className="p-12 text-center text-slate-600 uppercase tracking-widest font-bold animate-pulse">
                  Querying Quantum Ledger...
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-12 text-center text-slate-600 uppercase tracking-widest font-bold">
                  No forensic shards synchronized. Process queries via terminal to populate matrix.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

const ReasoningStream = () => {
  const { reasoning } = useVerityStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [reasoning]);

  return (
    <div className="bg-black/40 border border-white/10 rounded-2xl p-6 h-[350px] flex flex-col backdrop-blur-md">
      <div className="flex items-center gap-3 mb-6 border-b border-white/5 pb-4">
        <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
        <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.3em]">Agentic Reasoning Swarm</h3>
      </div>
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto font-mono text-[10px] space-y-3 custom-scrollbar pr-2"
      >
        <AnimatePresence initial={false}>
          {reasoning.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`p-3 rounded-lg border leading-relaxed ${msg.includes('[SYSTEM]')
                ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400/80'
                : 'bg-white/5 border-white/5 text-slate-400'
                }`}
            >
              <div className="flex gap-3">
                <span className="text-orange-500/50 shrink-0 select-none">{'>'}</span>
                <span>{msg}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {reasoning.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-600 italic opacity-50">
            <div className="animate-spin mb-4">
              <Globe className="w-8 h-8" />
            </div>
            <p className="uppercase tracking-widest text-[8px] font-bold">Initializing Swarm Bridge...</p>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Main Assistant Hook ---

const nodes = [
  {
    id: 'orchestrator',
    position: { x: 250, y: 0 },
    data: { label: 'Orchestrator' },
    style: {
      background: '#111',
      color: '#fff',
      borderRadius: '12px',
      border: '1px solid #D4A373',
      fontSize: '10px',
      fontWeight: 'bold',
      padding: '10px'
    }
  },
  {
    id: 'audit_agent',
    position: { x: 0, y: 150 },
    data: { label: 'Audit Agent' },
    style: {
      background: '#0a0a0a',
      color: '#fff',
      borderRadius: '12px',
      border: '1px solid #1B262C',
      fontSize: '10px',
      fontWeight: 'bold',
      padding: '10px'
    }
  },
  {
    id: 'tax_agent',
    position: { x: 500, y: 150 },
    data: { label: 'Tax Agent' },
    style: {
      background: '#0a0a0a',
      color: '#fff',
      borderRadius: '12px',
      border: '1px solid #1B262C',
      fontSize: '10px',
      fontWeight: 'bold',
      padding: '10px'
    }
  },
  {
    id: 'mcp_server',
    position: { x: 0, y: 300 },
    data: { label: <div>MCP Server (Cloud Run)<br /><span style={{ fontSize: '8px', opacity: 0.7 }}>mcp-database-toolbox</span></div> },
    style: {
      background: '#0a0a0a',
      color: '#0ea5e9', // cyan-500
      borderRadius: '12px',
      border: '1px dashed #0ea5e9',
      fontSize: '10px',
      fontWeight: 'bold',
      padding: '10px'
    }
  },
  {
    id: 'cloud_sql',
    position: { x: 0, y: 450 },
    data: { label: <div>Cloud SQL (PostgreSQL)<br /><span style={{ fontSize: '8px', opacity: 0.7 }}>'ledger' Database</span></div> },
    style: {
      background: '#0a0a0a',
      color: '#3b82f6', // blue-500
      borderRadius: '12px',
      border: '1px solid #3b82f6',
      fontSize: '10px',
      fontWeight: 'bold',
      padding: '10px'
    }
  },
  {
    id: 'gemini',
    position: { x: 500, y: 300 },
    data: { label: <div>Vertex AI<br /><span style={{ fontSize: '8px', opacity: 0.7 }}>Gemini 2.5 Flash</span></div> },
    style: {
      background: '#0a0a0a',
      color: '#a855f7', // purple-500
      borderRadius: '12px',
      border: '1px solid #a855f7',
      fontSize: '10px',
      fontWeight: 'bold',
      padding: '10px'
    }
  }
];

const edges = [
  { id: 'o-a', source: 'orchestrator', target: 'audit_agent', animated: true, style: { stroke: '#444' } },
  { id: 'o-t', source: 'orchestrator', target: 'tax_agent', animated: true, style: { stroke: '#444' } },
  { id: 'a-t', source: 'audit_agent', target: 'tax_agent', label: 'Findings Transfer', animated: true, style: { stroke: '#D4A373', fontSize: '8px' } },
  { id: 'a-mcp', source: 'audit_agent', target: 'mcp_server', label: 'SSE Connection', animated: true, style: { stroke: '#0ea5e9', fontSize: '8px' } },
  { id: 'mcp-db', source: 'mcp_server', target: 'cloud_sql', label: 'SQL Tunnel', animated: true, style: { stroke: '#3b82f6', fontSize: '8px' } },
  { id: 'o-g', source: 'orchestrator', target: 'gemini', animated: true, style: { stroke: '#a855f7', opacity: 0.3 } },
  { id: 'a-g', source: 'audit_agent', target: 'gemini', animated: true, style: { stroke: '#a855f7', opacity: 0.3 } },
  { id: 't-g', source: 'tax_agent', target: 'gemini', animated: true, style: { stroke: '#a855f7', opacity: 0.3 } },
];

export default function VerityNexus() {
  const [mounted, setMounted] = useState(false);
  const [isDiagramMaximized, setIsDiagramMaximized] = useState(false);
  const { addReasoning, updateStats, updateAgentStatus, setSignOffVisible, isSignOffVisible, findings, setFindings, isEvidenceMaximized, setEvidenceMaximized } = useVerityStore();

  useEffect(() => {
    setMounted(true);
  }, []);

  const { messages, input, handleInputChange, handleSubmit, data } = useChat({
    api: 'http://localhost:8005/api/chat',
    onFinish: () => {
      setSignOffVisible(true);
      addReasoning("Execution cycle complete. Finalizing output shards.");
    }
  });

  const onChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Reset analytical context for new run
    setFindings([]);
    updateStats({
      total_exposure: 0,
      materiality_reached: 0,
      anomalies_found: 0
    });
    setSignOffVisible(false);
    processedIndex.current = 0;
    handleSubmit(e);
  };

  const processedIndex = useRef(0);

  const lastFindingsCommited = useRef("");

  // Handle Streamed Data and Text-based Discoveries
  useEffect(() => {
    let updateFound = false;
    let newFindings: any[] = [];

    // 1. Process Structured Data Channel
    if (data && data.length > processedIndex.current) {
      for (let i = processedIndex.current; i < data.length; i++) {
        const item = data[i] as any;
        if (item.type === 'agent_transition') {
          addReasoning(`[SYSTEM] Handoff confirmed: Switching context to ${item.agent.toUpperCase()}`);
          updateAgentStatus(item.agent, 'active');
        } else if (item.type === 'reasoning_stream') {
          addReasoning(item.content);
        } else if (item.type === 'workflow_complete') {
          let payload = item.data;
          if (typeof payload === 'string') try { payload = JSON.parse(payload); } catch (e) { }

          if (payload) {
            const raw = payload.findings || payload.audit_results || (Array.isArray(payload) ? payload : []);
            const arr = Array.isArray(raw) ? raw : [raw];
            if (arr.length > 0 && (arr[0]?.trans_id || arr[0]?.amount)) {
              newFindings = arr;
              updateFound = true;
            }
          }
        }
      }
      processedIndex.current = data.length;
    }

    // 2. Heavy Fallback: Real-time Text Buffer Parsing
    if (!updateFound && messages.length > 0) {
      const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant');
      if (lastAssistant) {
        const content = lastAssistant.content.trim();
        if (content.includes('"findings"') || content.includes('"trans_id"')) {
          const jsonMatches = content.match(/\{[\s\S]*\}/g);
          if (jsonMatches) {
            for (const match of jsonMatches) {
              try {
                const parsed = JSON.parse(match);
                const raw = parsed.findings || parsed.audit_results || (Array.isArray(parsed) ? parsed : []);
                const arr = Array.isArray(raw) ? raw : [raw];
                if (arr.length > 0 && (arr[0]?.trans_id || arr[0]?.amount)) {
                  newFindings = arr;
                  updateFound = true;
                  break;
                }
              } catch (e) { }
            }
          }
        }
      }
    }

    // 3. Commit Updates with Deep Fingerprint
    if (updateFound && newFindings.length > 0) {
      const fingerprint = JSON.stringify(newFindings);
      if (fingerprint !== lastFindingsCommited.current) {
        console.log("--- [SYNC] Synchronizing Shards:", newFindings.length);
        lastFindingsCommited.current = fingerprint;
        setFindings(newFindings);

        const total = newFindings.reduce((acc: number, f: any) => acc + (f.amount || 0), 0);
        updateStats({
          total_exposure: total,
          materiality_reached: Math.min(100, (total / 1500000) * 100),
          anomalies_found: newFindings.length
        });
      }
    }
  }, [data, messages, setFindings, updateStats, addReasoning, updateAgentStatus]);

  if (!mounted) return <div className="min-h-screen bg-black" />;

  return (
    <div className="min-h-screen bg-[#020202] text-slate-200 font-sans selection:bg-orange-500/30 overflow-hidden flex flex-col">
      {/* Background Decor */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-orange-500/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/5 rounded-full blur-[120px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] mix-blend-overlay" />
      </div>

      {/* Top Navbar */}
      <div className="z-20 border-b border-white/5 bg-black/50 backdrop-blur-xl px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-600 to-red-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-black tracking-[0.2em] text-white">VERITY NEXUS <span className="text-orange-500 font-light opacity-50 ml-1">V2.0</span></h1>
              <p className="text-[8px] font-bold text-slate-500 uppercase tracking-widest mt-0.5">Quantum Ledger Compliance</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-8">
          <div className="flex flex-col items-end">
            <span className="text-[8px] text-slate-500 uppercase font-black tracking-[0.2em] mb-1.5 flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_emerald]" />
              Swarm Status: Active
            </span>
            <div className="flex gap-1.5">
              {[1, 2, 3, 4, 5, 6, 7].map(i => <div key={i} className={`w-3 h-0.5 rounded-full ${i <= 5 ? 'bg-emerald-500/50' : 'bg-white/10'}`} />)}
            </div>
          </div>
          <div className="h-8 w-px bg-white/5" />
          <button className="text-[10px] font-bold bg-white/5 border border-white/10 px-4 py-2 rounded-xl hover:bg-white/10 transition-colors uppercase tracking-widest">
            Terminal View
          </button>
        </div>
      </div>

      <main className="flex-1 max-w-[1600px] mx-auto w-full grid grid-cols-12 gap-8 p-8 relative z-10 overflow-hidden">

        {/* Sidebar Left: Swarm Intelligence */}
        <div className="col-span-3 flex flex-col gap-8">
          <MaterialityGauge />

          <div className="flex-1 flex flex-col bg-white/[0.02] border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm relative group">
            <div className="p-6 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-orange-500" />
                <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Live Inspection</h3>
              </div>
            </div>
            <div
              onClick={() => setIsDiagramMaximized(true)}
              className="flex-1 relative cursor-zoom-in overflow-hidden"
            >
              <div className="absolute inset-0 z-10 bg-orange-500/0 group-hover:bg-orange-500/5 transition-colors flex items-center justify-center">
                <Maximize2 className="w-8 h-8 text-orange-500 opacity-0 group-hover:opacity-100 transition-all scale-50 group-hover:scale-100" />
                <p className="absolute bottom-4 text-[7px] font-black text-orange-500/40 uppercase tracking-[0.3em] opacity-0 group-hover:opacity-100 transition-all">Click to Expand Inspection</p>
              </div>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                className="grayscale brightness-[1.5] opacity-40 group-hover:opacity-60 transition-opacity pointer-events-none"
              >
                <Background color="#222" gap={20} size={1} />
              </ReactFlow>
            </div>
            <div className="p-4 bg-orange-500/5 border-t border-orange-500/10">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[8px] font-bold text-orange-500/50 uppercase">Analysis Confidence</span>
                <span className="text-[10px] font-mono text-orange-500">98.4%</span>
              </div>
              <div className="h-1 w-full bg-orange-500/10 rounded-full overflow-hidden">
                <motion.div initial={{ width: 0 }} animate={{ width: '98.4%' }} className="h-full bg-orange-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Center: Discoveries & Findings */}
        <div className="col-span-5 space-y-8 flex flex-col h-full">
          <div id="neural-shard-layer" className="bg-[#080808] border border-white/5 rounded-3xl p-8 flex-1 overflow-y-auto custom-scrollbar relative scroll-mt-8 transition-all duration-1000">
            <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 rounded-full blur-[60px] pointer-events-none" />
            <AuditFindings />
          </div>

          {/* Bottom Insight Panel */}
          <div className="bg-gradient-to-r from-orange-500/10 to-transparent border border-orange-500/10 rounded-2xl p-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center border border-orange-500/20">
                <Activity className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <p className="text-[8px] font-bold text-orange-500 uppercase tracking-[0.2em] mb-1">Global Risk Signal</p>
                <h4 className="text-xl font-black text-white tracking-tight italic uppercase">High Anomaly Threshold Reached</h4>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setEvidenceMaximized(true)}
                className="bg-transparent border border-cyan-500/30 text-cyan-500 text-[10px] font-black px-6 py-3 rounded-xl hover:bg-cyan-500/10 hover:border-cyan-500/50 transition-all transform active:scale-95 shadow-xl relative overflow-hidden group uppercase tracking-widest"
              >
                <div className="absolute inset-0 bg-cyan-500/10 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                Table Data
              </button>
              <button className="bg-white text-black text-[10px] font-black px-6 py-3 rounded-xl hover:bg-orange-500 hover:text-white transition-all transform active:scale-95 shadow-xl shadow-white/5">
                GENERATE REPORT
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Communication Terminal */}
        <div className="col-span-4 flex flex-col gap-8">
          <ReasoningStream />

          <div className="flex-1 flex flex-col bg-[#050505] border border-white/5 rounded-3xl overflow-hidden shadow-2xl relative">
            <div className="p-6 border-b border-white/5 flex items-center gap-3">
              <Terminal className="w-4 h-4 text-orange-500" />
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Swarm Input Base</span>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-slate-700 select-none">
                  <Search className="w-12 h-12 mb-4 opacity-20" />
                  <p className="text-[10px] uppercase tracking-[0.3em] text-center font-bold">Awaiting Instructions...</p>
                </div>
              )}
              {messages
                .map(m => {
                  const content = m.content.trim();
                  // Detection for pure data payloads (raw or markdown)
                  const containsDataKeys = content.includes('"trans_id"') || content.includes('"findings"');
                  const isDataLikely = containsDataKeys && (
                    content.startsWith('{') ||
                    content.startsWith('[') ||
                    content.includes('```json') ||
                    content.includes('```JSON')
                  );

                  // Hide technical shards from text bubbles but show a "Nice Representation" if it's purely data
                  if (m.role === 'assistant' && isDataLikely) {
                    try {
                      // Extract JSON even if wrapped in markdown
                      const jsonPattern = /\{[\s\S]*\}|\[[\s\S]*\]/;
                      const match = content.match(jsonPattern);
                      const rawJson = match ? match[0] : content;
                      const parsed = JSON.parse(rawJson);
                      const findings = parsed.findings || parsed.audit_results || (Array.isArray(parsed) ? parsed : []);
                      return (
                        <motion.div
                          key={m.id}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="flex justify-start w-full my-4"
                        >
                          <div className="max-w-[100%] w-full">
                            <DataShardBadge count={Array.isArray(findings) ? findings.length : 1} />
                          </div>
                        </motion.div>
                      );
                    } catch (e) {
                      // If parsing fails for a json-looking shard, still hide it as it's debris
                      console.warn("[UI] Debris capture failed to parse:", e);
                      return null;
                    }
                  }

                  // Standard narrative filtering for smaller fragments
                  const isTechnicalShard = (content.includes('"trans_id"') || content.includes('"findings"') || content.includes('"workflow_id"'));
                  if (m.role === 'assistant' && isTechnicalShard && content.length > 50) return null;

                  return (
                    <motion.div
                      key={m.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[90%] group relative px-5 py-3 rounded-2xl text-[13px] leading-relaxed transition-all ${m.role === 'user'
                        ? 'bg-orange-600 text-white font-medium shadow-lg shadow-orange-500/10'
                        : 'bg-white/5 text-slate-300 border border-white/5 hover:border-white/10'
                        }`}>
                        {m.content}
                        {m.role === 'user' && <div className="absolute -right-1 top-2 w-2 h-2 bg-orange-600 rotate-45" />}
                      </div>
                    </motion.div>
                  );
                })}
            </div>

            <div className="p-6 bg-black/40 border-t border-white/5 backdrop-blur-md">
              <AnimatePresence>
                {isSignOffVisible && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mb-4"
                  >
                    <button className="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-black py-4 rounded-xl flex items-center justify-center gap-3 transition-all relative overflow-hidden group shadow-lg shadow-emerald-500/10">
                      <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                      <CheckCircle2 className="w-4 h-4" />
                      EXECUTIVE SIGN-OFF REQD
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={onChatSubmit} className="relative flex items-center gap-3">
                <div className="relative flex-1 group">
                  <div className="absolute inset-0 bg-orange-500/10 rounded-xl blur-lg opacity-0 group-focus-within:opacity-100 transition-opacity" />
                  <input
                    className="w-full bg-[#0A0A0A] border border-white/10 rounded-xl px-5 py-4 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-orange-500/50 transition-all relative z-10"
                    value={input}
                    onChange={handleInputChange}
                    placeholder="Instruct the swarm intelligence..."
                  />
                </div>
                <button
                  type="submit"
                  className="bg-white text-black font-black px-6 py-4 rounded-xl text-[10px] hover:bg-orange-500 hover:text-white transition-all transform active:scale-95 shadow-xl relative z-10 uppercase tracking-widest"
                >
                  EXECUTE
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>

      {/* Footer Stats Bar */}
      <div className="z-20 border-t border-white/5 bg-black/80 backdrop-blur-xl px-8 py-2 flex items-center gap-12 overflow-x-auto">
        {[
          { label: "Active Nodes", value: "3", icon: Cpu },
          { label: "Memory Load", value: "1.2 GB", icon: Activity },
          { label: "Throughput", value: "240 tx/s", icon: Zap },
          { label: "Security Protocol", value: "TLS 1.3", icon: ShieldAlert },
          { label: "Jurisdiction", value: "Global-Cloud", icon: Globe },
        ].map((stat, i) => (
          <div key={i} className="flex items-center gap-3 shrink-0">
            <stat.icon className="w-3 h-3 text-slate-500" />
            <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest">{stat.label}:</span>
            <span className="text-[10px] font-mono text-white/80">{stat.value}</span>
          </div>
        ))}
        <div className="flex-1" />
        <div className="flex items-center gap-2">
          <span className="text-[8px] font-bold text-slate-500 uppercase tracking-[0.3em]">Latency</span>
          <div className="flex items-end gap-0.5 h-3">
            {[4, 7, 5, 8, 4, 3, 6].map((h, i) => (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                animate={{ height: `${h * 10}%` }}
                transition={{ repeat: Infinity, duration: 2, delay: i * 0.1 }}
                className="w-1 bg-orange-500/30 rounded-t-sm"
              />
            ))}
          </div>
        </div>
      </div>
      {/* Diagram Maximization Overlay */}
      <AnimatePresence>
        {isDiagramMaximized && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-2xl flex flex-col p-12"
          >
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-orange-600/20 flex items-center justify-center border border-orange-500/30">
                  <Search className="w-5 h-5 text-orange-500" />
                </div>
                <div>
                  <h2 className="text-xl font-black text-white uppercase tracking-tighter">Swarm Intelligence Architecture</h2>
                  <p className="text-[10px] font-bold text-orange-500/50 uppercase tracking-[0.4em]">Live Multi-Agent Inspection Layer</p>
                </div>
              </div>
              <button
                onClick={() => setIsDiagramMaximized(false)}
                className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors group"
              >
                <X className="w-6 h-6 text-slate-400 group-hover:scale-110 group-hover:text-white transition-all" />
              </button>
            </div>

            <div className="flex-1 bg-black/40 border border-white/5 rounded-[40px] overflow-hidden relative shadow-2xl backdrop-blur-sm">
              {/* Overlay Grid */}
              <div className="absolute inset-0 opacity-[0.05] pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:40px_40px] z-10" />

              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                className="brightness-[1.2] grayscale-[0.5]"
              >
                <Background color="#111" gap={30} size={1} />
              </ReactFlow>

              {/* Status Indicators */}
              <div className="absolute bottom-10 left-10 z-20 flex gap-6">
                <div className="bg-black/60 border border-white/10 rounded-2xl p-4 backdrop-blur-xl">
                  <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Architecture State</p>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <p className="text-xs font-bold text-white uppercase">Operational Shifting</p>
                  </div>
                </div>
                <div className="bg-black/60 border border-white/10 rounded-2xl p-4 backdrop-blur-xl">
                  <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">Orchestration Cycle</p>
                  <p className="text-xs font-mono text-orange-500 tracking-tighter">0.002s LATENCY</p>
                </div>
              </div>
            </div>

            <motion.div
              initial={{ y: 20 }}
              animate={{ y: 0 }}
              className="mt-8 text-center"
            >
              <p className="text-[9px] font-bold text-slate-600 uppercase tracking-[0.8em] select-none">Esc to close inspection view</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Evidence Ledger Maximization Overlay */}
      <AnimatePresence>
        {isEvidenceMaximized && <EvidenceLedgerModal />}
      </AnimatePresence>
    </div>
  );
}
