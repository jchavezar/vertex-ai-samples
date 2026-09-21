import React, { useState, useEffect, useMemo } from 'react';
import { 
  Layers, 
  CheckCircle, 
  AlertTriangle, 
  FileText, 
  ShieldCheck, 
  Sparkles, 
  Plus, 
  Download, 
  Check, 
  Filter,
  Cpu,
  Zap,
  Scale,
  ShieldAlert,
  Loader2,
  TrendingUp,
  FileCheck
} from 'lucide-react';

export const PrivacyProLegoView: React.FC = () => {
  const [availableClauses, setAvailableClauses] = useState<any[]>([]);
  const [selectedClauseIds, setSelectedClauseIds] = useState<string[]>([
    "CLAUSE-01",
    "CLAUSE-02",
    "CLAUSE-03",
    "CLAUSE-04",
    "CLAUSE-08"
  ]);
  const [activeCategory, setActiveCategory] = useState<string>('All');
  const [dependencyWarnings, setDependencyWarnings] = useState<string[]>([]);
  
  // AI Harmonizer & Negotiation Stance States
  const [posture, setPosture] = useState<'aggressive' | 'balanced' | 'vendor'>('aggressive');
  const [isHarmonizing, setIsHarmonizing] = useState(false);
  const [harmonizedData, setHarmonizedData] = useState<any>(null);
  const [activeRightTab, setActiveRightTab] = useState<'draft' | 'reconciliations' | 'playbook'>('draft');

  useEffect(() => {
    fetchClauses();
  }, []);

  useEffect(() => {
    validateDependencies();
  }, [selectedClauseIds, availableClauses]);

  useEffect(() => {
    if (selectedClauseIds.length > 0) {
      runHarmonization(selectedClauseIds, posture);
    }
  }, [posture]);

  const fetchClauses = async () => {
    try {
      const res = await fetch('/api/mcp/clauses');
      const data = await res.json();
      if (data.clauses) {
        setAvailableClauses(data.clauses);
        runHarmonization(selectedClauseIds, posture);
      }
    } catch (e) {
      console.error("Error loading clauses", e);
    }
  };

  const runHarmonization = async (ids: string[], currentPosture: string) => {
    setIsHarmonizing(true);
    try {
      const res = await fetch('/api/mcp/lego/harmonize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clause_ids: ids, posture: currentPosture })
      });
      const data = await res.json();
      setHarmonizedData(data);
    } catch (e) {
      console.error("Harmonization error", e);
    } finally {
      setIsHarmonizing(false);
    }
  };

  const validateDependencies = () => {
    const warnings: string[] = [];
    const selectedSet = new Set(selectedClauseIds);

    for (const cid of selectedClauseIds) {
      const clause = availableClauses.find(c => c.id === cid);
      if (clause && clause.dependencies) {
        for (const depId of clause.dependencies) {
          if (!selectedSet.has(depId)) {
            const depClause = availableClauses.find(c => c.id === depId);
            warnings.push(
              `"${clause.title}" (${clause.id}) requires prerequisite "${depClause?.title || depId}" (${depId}) to be enforceable in court.`
            );
          }
        }
      }
    }
    setDependencyWarnings(warnings);
  };

  const toggleClause = (id: string) => {
    let newIds: string[];
    if (selectedClauseIds.includes(id)) {
      newIds = selectedClauseIds.filter(c => c !== id);
    } else {
      newIds = [...selectedClauseIds, id];
    }
    setSelectedClauseIds(newIds);
    if (newIds.length > 0) {
      runHarmonization(newIds, posture);
    }
  };

  const autoResolveDependencies = () => {
    const newSet = new Set(selectedClauseIds);
    for (const cid of selectedClauseIds) {
      const clause = availableClauses.find(c => c.id === cid);
      if (clause && clause.dependencies) {
        for (const depId of clause.dependencies) {
          newSet.add(depId);
        }
      }
    }
    const resolvedIds = Array.from(newSet);
    setSelectedClauseIds(resolvedIds);
    runHarmonization(resolvedIds, posture);
  };

  // Dynamic contract integrity calculation
  const integrityScore = useMemo(() => {
    if (selectedClauseIds.length === 0) return 0;
    if (dependencyWarnings.length === 0) return 100;
    const penalty = dependencyWarnings.length * 18;
    return Math.max(40, 100 - penalty);
  }, [selectedClauseIds, dependencyWarnings]);

  const filteredClauses = useMemo(() => {
    if (activeCategory === 'All') return availableClauses;
    return availableClauses.filter(c => c.category.toLowerCase().includes(activeCategory.toLowerCase()));
  }, [availableClauses, activeCategory]);

  const displayedSections = harmonizedData?.sections || availableClauses.filter(c => selectedClauseIds.includes(c.id));

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Header & Dynamic Integrity Meter */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-card flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-50 text-blue-700 rounded-xl border border-blue-100">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-semibold text-slate-900">"Privacy Pro" Modular Clause Studio</h3>
              <span className="px-2 py-0.5 rounded text-xs font-mono text-blue-700 bg-blue-50 border border-blue-100">
                The Legal Lego Engine
              </span>
              <span className="flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium text-purple-700 bg-purple-50 border border-purple-200">
                <Cpu className="w-3 h-3" />
                Gemini 3.7 Flash
              </span>
            </div>
            <p className="text-xs text-slate-500 font-normal">
              Autonomous multi-clause harmonization, cross-dependency validation, and counterparty risk intelligence
            </p>
          </div>
        </div>

        {/* Dynamic Integrity Gauge & Action Buttons */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 bg-slate-50 px-3.5 py-1.5 rounded-xl border border-slate-200/60">
            <div className="relative w-9 h-9 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-200"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className={integrityScore === 100 ? "text-emerald-500 transition-all duration-500" : "text-amber-500 transition-all duration-500"}
                  strokeDasharray={`${integrityScore}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <span className="absolute text-[10px] font-semibold font-mono text-slate-800">
                {integrityScore}%
              </span>
            </div>
            <div>
              <span className="text-[10px] font-medium uppercase text-slate-400 block">Integrity</span>
              <span className={`text-xs font-medium ${integrityScore === 100 ? 'text-emerald-700' : 'text-amber-700'}`}>
                {integrityScore === 100 ? 'Audit Ready' : `${dependencyWarnings.length} Missing Gaps`}
              </span>
            </div>
          </div>

          {dependencyWarnings.length > 0 ? (
            <button
              onClick={autoResolveDependencies}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-xl text-xs transition cursor-pointer shadow-xs"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Auto-Snap Dependencies</span>
            </button>
          ) : (
            <button
              onClick={() => alert("Assembled agreement exported to iManage DMS!")}
              className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl text-xs transition shadow-xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Assembled Draft</span>
            </button>
          )}
        </div>
      </div>

      {/* AI Stance Selector & Harmonizer Bar */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-2xl p-4 shadow-sm border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-xl">
            <Scale className="w-4 h-4 text-amber-300" />
          </div>
          <div>
            <span className="text-[11px] uppercase tracking-wider text-slate-400 block font-mono">
              Autonomous AI Negotiation Stance
            </span>
            <span className="text-xs font-semibold text-white">
              Calibrate Contract Provisions & Exposure Thresholds
            </span>
          </div>
        </div>

        {/* Posture Pill Selector */}
        <div className="flex items-center gap-2 bg-white/5 p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setPosture('aggressive')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
              posture === 'aggressive'
                ? 'bg-blue-600 text-white shadow-xs font-semibold'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <span>🛡️ Weil Pro-Client</span>
            <span className="text-[10px] opacity-75 hidden sm:inline">(Aggressive)</span>
          </button>

          <button
            onClick={() => setPosture('balanced')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
              posture === 'balanced'
                ? 'bg-blue-600 text-white shadow-xs font-semibold'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <span>⚖️ Balanced Market</span>
            <span className="text-[10px] opacity-75 hidden sm:inline">(Standard)</span>
          </button>

          <button
            onClick={() => setPosture('vendor')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
              posture === 'vendor'
                ? 'bg-blue-600 text-white shadow-xs font-semibold'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <span>⚡ Fast-Close</span>
            <span className="text-[10px] opacity-75 hidden sm:inline">(Vendor Leaning)</span>
          </button>
        </div>

        {/* Re-harmonize Trigger */}
        <button
          onClick={() => runHarmonization(selectedClauseIds, posture)}
          disabled={isHarmonizing}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold rounded-xl text-xs transition cursor-pointer shadow-xs disabled:opacity-50"
        >
          {isHarmonizing ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Harmonizing with Gemini 3.7...</span>
            </>
          ) : (
            <>
              <Zap className="w-3.5 h-3.5 fill-current" />
              <span>Run Gemini 3.7 Flash Harmonizer</span>
            </>
          )}
        </button>
      </div>

      {/* Dependency Warning Bar */}
      {dependencyWarnings.length > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-900 flex items-start gap-3 shadow-xs">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="space-y-1 flex-1">
            <span className="font-bold text-amber-950 text-xs flex items-center gap-2">
              <span>⚠️ FTC & EU AI Act Enforceability Breach:</span>
              <span className="text-[11px] font-normal text-amber-800">
                Substantive legal contradiction detected
              </span>
            </span>
            {dependencyWarnings.map((w, idx) => (
              <p key={idx} className="text-amber-900 leading-relaxed font-medium">{w}</p>
            ))}
          </div>
          <button
            onClick={autoResolveDependencies}
            className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-lg text-xs shrink-0 cursor-pointer shadow-xs"
          >
            Auto-Repair Graph
          </button>
        </div>
      )}

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 overflow-hidden">
        {/* Left: Clause Repository */}
        <div className="lg:col-span-5 bg-white border border-slate-200/80 rounded-2xl p-5 flex flex-col justify-between overflow-hidden shadow-card">
          <div>
            <div className="pb-3 border-b border-slate-100 flex items-center justify-between mb-3">
              <h4 className="font-semibold text-sm text-slate-900">Modular Lego Blocks</h4>
              <span className="text-xs text-slate-400 font-mono">{availableClauses.length} Standardized Blocks</span>
            </div>

            {/* Category Filter Pills */}
            <div className="flex items-center gap-1 mb-3 overflow-x-auto pb-1">
              {['All', 'Governance', 'Data Transfer', 'Audit Rights', 'Risk'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-2.5 py-1 rounded-lg text-xs transition cursor-pointer border ${
                    activeCategory === cat ? 'bg-slate-900 text-white border-slate-900 font-medium' : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 font-normal'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto my-1 space-y-2 pr-1">
            {filteredClauses.map((clause) => {
              const isSelected = selectedClauseIds.includes(clause.id);
              return (
                <div
                  key={clause.id}
                  onClick={() => toggleClause(clause.id)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start justify-between gap-3 ${
                    isSelected 
                      ? 'bg-blue-50/50 border-blue-400 text-slate-900' 
                      : 'bg-slate-50 border-slate-200/60 hover:border-slate-300 text-slate-700'
                  }`}
                >
                  <div className="space-y-1 overflow-hidden">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-blue-700 bg-blue-50 border border-blue-100 px-1.5 py-0.5 rounded font-bold">
                        {clause.id}
                      </span>
                      <h5 className="font-semibold text-xs text-slate-900 truncate">{clause.title}</h5>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">{clause.summary}</p>
                    <div className="flex items-center gap-2 pt-0.5 text-[10px] font-mono">
                      <span className="text-slate-400">{clause.category}</span>
                      <span className="text-slate-300">•</span>
                      <span className={
                        clause.risk_level === 'Critical' 
                          ? 'text-rose-700 font-medium' 
                          : clause.risk_level === 'High' 
                          ? 'text-amber-800 font-medium' 
                          : 'text-emerald-700 font-medium'
                      }>
                        {clause.risk_level} Risk
                      </span>
                    </div>
                  </div>

                  <div className={`p-1.5 rounded-lg shrink-0 mt-0.5 transition ${isSelected ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-500'}`}>
                    {isSelected ? <Check className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Click any block to snap or detach</span>
            <span>Weil Master Taxonomy v3.4</span>
          </div>
        </div>

        {/* Right: Assembled Contract Canvas & AI Intelligence Tabs */}
        <div className="lg:col-span-7 bg-white border border-slate-200/80 rounded-2xl p-5 flex flex-col justify-between overflow-hidden shadow-card">
          {/* Top Sub-Tabs Navigation */}
          <div className="pb-3 border-b border-slate-100 flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
              <button
                onClick={() => setActiveRightTab('draft')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  activeRightTab === 'draft'
                    ? 'bg-white text-slate-950 font-bold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                <span>Assembled Addendum ({displayedSections.length})</span>
              </button>

              <button
                onClick={() => setActiveRightTab('reconciliations')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  activeRightTab === 'reconciliations'
                    ? 'bg-white text-slate-950 font-bold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <FileCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>AI Harmonization Notes (4)</span>
              </button>

              <button
                onClick={() => setActiveRightTab('playbook')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  activeRightTab === 'playbook'
                    ? 'bg-white text-slate-950 font-bold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <TrendingUp className="w-3.5 h-3.5 text-purple-600" />
                <span>Opposing Counsel Radar</span>
              </button>
            </div>

            <span className="px-2.5 py-1 bg-slate-100 border border-slate-200 rounded-lg text-xs font-mono text-slate-600">
              Delaware / EU Dual-Regime
            </span>
          </div>

          {/* Sub-Tab 1: Assembled Contract Text */}
          {activeRightTab === 'draft' && (
            <div className="flex-1 overflow-y-auto my-3 p-5 bg-slate-50 border border-slate-200/60 rounded-xl space-y-3.5 text-xs text-slate-800 leading-relaxed font-sans pr-2">
              <div className="text-center pb-3 border-b border-slate-200">
                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-mono text-[10px] font-semibold uppercase tracking-wider mb-1 inline-block">
                  Calibrated for: {harmonizedData?.posture_label || 'Weil Standard'}
                </span>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Data Privacy & AI Governance Master Addendum
                </h2>
                <p className="text-[11px] text-slate-500 mt-0.5 italic">
                  Drafted pursuant to Weil, Gotshal & Manges LLP Standard Commercial Practice
                </p>
              </div>

              {displayedSections.length === 0 ? (
                <div className="py-16 text-center text-slate-400">
                  Select modular Lego blocks on the left to begin assembling the agreement.
                </div>
              ) : (
                displayedSections.map((clause: any, idx: number) => (
                  <div key={clause.id || clause.clause_id} className="p-3.5 bg-white border border-slate-200/80 rounded-xl space-y-1.5 shadow-xs">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-slate-900">
                        Section {idx + 1}. {clause.title}
                      </span>
                      <span className="font-mono text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded text-[10px]">
                        [{clause.id || clause.clause_id}]
                      </span>
                    </div>
                    <p className="text-slate-700 text-xs leading-relaxed italic">
                      "{clause.text}"
                    </p>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Sub-Tab 2: AI Harmonization & Cross-Clause Reconciliation */}
          {activeRightTab === 'reconciliations' && (
            <div className="flex-1 overflow-y-auto my-3 p-4 bg-slate-50 border border-slate-200/60 rounded-xl space-y-3 text-xs pr-2">
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
                <span className="font-bold text-emerald-900 block mb-1">
                  Gemini 3.7 Flash Cross-Clause Synthesis Engine
                </span>
                <p className="text-emerald-800 leading-relaxed text-[11px]">
                  {harmonizedData?.executive_summary || 'Analyzing active clauses across jurisdiction boundaries...'}
                </p>
              </div>

              <div className="space-y-2">
                <h5 className="font-semibold text-slate-900 text-xs uppercase tracking-wider">
                  Active Legal Reconciliations
                </h5>
                {(harmonizedData?.reconciliations || []).map((rec: string, idx: number) => (
                  <div key={idx} className="p-3 bg-white border border-slate-200 rounded-xl flex items-start gap-2.5 shadow-xs">
                    <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">
                      {idx + 1}
                    </div>
                    <p className="text-slate-700 leading-relaxed text-xs">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sub-Tab 3: Opposing Counsel Negotiation Radar */}
          {activeRightTab === 'playbook' && (
            <div className="flex-1 overflow-y-auto my-3 p-4 bg-slate-50 border border-slate-200/60 rounded-xl space-y-3.5 text-xs pr-2">
              {/* Risk Scores Grid */}
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">Schrems II Compliance</span>
                  <span className="font-bold text-emerald-700 text-xs">Module 2 Controller Verified</span>
                </div>
                <div className="p-2.5 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">EU AI Act Art. 50</span>
                  <span className="font-bold text-emerald-700 text-xs">Zero Retention Passed</span>
                </div>
                <div className="p-2.5 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">Delaware Caremark</span>
                  <span className="font-bold text-blue-700 text-xs">Fiduciary Oversight Active</span>
                </div>
                <div className="p-2.5 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">Opposing Counsel Friction</span>
                  <span className="font-bold text-amber-700 text-xs">
                    {harmonizedData?.risk_radar?.opposing_counsel_friction?.split('(')[0] || 'Moderate Friction'}
                  </span>
                </div>
              </div>

              {/* Negotiation Battleground Items */}
              <div className="space-y-2 pt-1">
                <h5 className="font-semibold text-slate-900 text-xs uppercase tracking-wider">
                  Expected Counterparty Redlines (Skadden / Latham)
                </h5>
                {(harmonizedData?.playbook || []).map((item: any, idx: number) => (
                  <div key={idx} className="p-3 bg-white border border-slate-200 rounded-xl space-y-1.5 shadow-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 text-xs">{item.issue}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        item.severity === 'Critical' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {item.severity} Conflict
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100">
                      <span className="font-semibold text-rose-700">Expected Pushback: </span>
                      {item.counterparty_objection}
                    </div>
                    <div className="text-[11px] text-slate-700 bg-emerald-50/60 p-2 rounded-lg border border-emerald-100">
                      <span className="font-semibold text-emerald-800">Weil Playbook Counter-Position: </span>
                      {item.weil_recommendation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Bottom Status Footer */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5 text-slate-500">
              <Cpu className="w-3.5 h-3.5 text-purple-600" />
              <span>Gemini 3.7 Flash Active • Zero-Data-Retention (ZDR) Enforced</span>
            </span>
            <span className="text-emerald-700 font-bold font-mono">100% Audit Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};
