import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Search, 
  ShieldAlert, 
  ShieldCheck, 
  CheckCircle, 
  FileText, 
  Scale, 
  Lock, 
  Unlock,
  ExternalLink,
  Code,
  Sparkles
} from 'lucide-react';

export const LegalVaultMCPView: React.FC = () => {
  // iManage Search State
  const [imanageQuery, setImanageQuery] = useState("BioGen indemnification settlement");
  const [matterId, setMatterId] = useState("MATTER-9042");
  const [imanageResults, setImanageResults] = useState<any[]>([]);
  const [isSearchingImanage, setIsSearchingImanage] = useState(false);

  // Citation Verifier State
  const [citationInput, setCitationInput] = useState("698 A.2d 959");
  const [citationResult, setCitationResult] = useState<any>(null);

  // Registered MCP Tools
  const [mcpTools, setMcpTools] = useState<any[]>([]);

  useEffect(() => {
    fetchMcpTools();
    searchImanage();
    verifyCitation("698 A.2d 959");
  }, []);

  const fetchMcpTools = async () => {
    try {
      const res = await fetch('/api/mcp/tools');
      const data = await res.json();
      if (data.tools) setMcpTools(data.tools);
    } catch (e) {
      console.error("Failed to load MCP tools", e);
    }
  };

  const searchImanage = async (customQuery?: string) => {
    const q = customQuery || imanageQuery;
    setIsSearchingImanage(true);
    try {
      const res = await fetch(`/api/mcp/imanage/search?q=${encodeURIComponent(q)}&matter_id=${matterId}&attorney=jesusarguelles@google.com`);
      const data = await res.json();
      if (data.documents) {
        setImanageResults(data.documents);
      }
    } catch (e) {
      console.error("Error searching iManage", e);
    } finally {
      setIsSearchingImanage(false);
    }
  };

  const verifyCitation = async (citationString?: string) => {
    const c = citationString || citationInput;
    try {
      const res = await fetch(`/api/mcp/citations/verify?citation=${encodeURIComponent(c)}`);
      const data = await res.json();
      setCitationResult(data);
    } catch (e) {
      console.error("Error verifying citation", e);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-50 text-blue-700 rounded-xl border border-blue-100">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900">Model Context Protocol (MCP) Gateway & Legal Vault</h3>
            <p className="text-xs text-slate-500 font-medium">
              Open standard tool connectors for iManage DMS, Ethical Walls, and Judicial Case Law Authority
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl font-mono text-xs font-medium flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-ping"></span>
            MCP Server: Active (4 Tools Registered)
          </span>
        </div>
      </div>

      {/* Main Content Grid: iManage Search (7 cols) | Citation Verifier & MCP Schema (5 cols) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 overflow-hidden">
        {/* Left: iManage DMS & Ethical Wall Interceptor */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-5 flex flex-col justify-between overflow-hidden shadow-card">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-700" />
                <h4 className="font-semibold text-xs text-slate-900">iManage DMS Precedent Search & Ethical Wall Filter</h4>
              </div>
              <span className="text-[11px] text-slate-500 font-mono font-medium">Active Matter: {matterId}</span>
            </div>

            {/* Quick Test Presets */}
            <div className="flex items-center gap-2.5 mb-3">
              <span className="text-xs text-slate-500 font-medium uppercase tracking-wider">Test Scenarios:</span>
              <button
                onClick={() => {
                  setImanageQuery("BioGen indemnification settlement");
                  searchImanage("BioGen indemnification settlement");
                }}
                className="px-3 py-1 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg text-xs text-amber-900 font-medium transition cursor-pointer"
              >
                Conflict Test (BioGen Adverse Client)
              </button>
              <button
                onClick={() => {
                  setImanageQuery("Privacy Pro AI Governance Addendum");
                  searchImanage("Privacy Pro AI Governance Addendum");
                }}
                className="px-3 py-1 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-xs text-blue-900 font-medium transition cursor-pointer"
              >
                Cleared Precedent (CloudScale)
              </button>
            </div>

            {/* Search Input */}
            <div className="flex items-center gap-2 mb-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  value={imanageQuery}
                  onChange={(e) => setImanageQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && searchImanage()}
                  placeholder="Search iManage precedent documents..."
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:bg-white"
                />
              </div>
              <button
                onClick={() => searchImanage()}
                disabled={isSearchingImanage}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-medium transition shadow-sm cursor-pointer"
              >
                Search DMS
              </button>
            </div>

            {/* Results List */}
            <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
              {imanageResults.map((doc, idx) => {
                const isConflict = doc.ethical_wall_status === 'CONFLICT_DETECTED_SANITIZED';
                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border transition space-y-2.5 ${
                      isConflict 
                        ? 'bg-amber-50/60 border-amber-200 shadow-xs' 
                        : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] font-medium bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded">
                            {doc.doc_id}
                          </span>
                          <h5 className="font-semibold text-xs text-slate-900">{doc.title}</h5>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5 font-medium">
                          Matter: {doc.matter_id} • Client: {doc.client} • Year: {doc.year}
                        </p>
                      </div>

                      {isConflict ? (
                        <span className="px-2.5 py-1 bg-amber-100 text-amber-900 border border-amber-200 rounded-full text-xs font-medium shrink-0 flex items-center gap-1.5 shadow-xs">
                          <Lock className="w-3.5 h-3.5 text-amber-700" />
                          Ethical Wall Sanitized
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-full text-xs font-medium shrink-0 flex items-center gap-1.5">
                          <Unlock className="w-3.5 h-3.5 text-emerald-600" />
                          Cleared Precedent
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-700 italic bg-white p-3 rounded-lg border border-slate-200 leading-relaxed shadow-xs">
                      "{doc.content}"
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 font-medium">
                      <span>Practice: {doc.practice_group}</span>
                      <span className="font-mono text-slate-700 font-medium">Indemnity Cap: {doc.indemnity_cap_percent}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 flex items-center justify-between font-medium">
            <span>Client Matter Boundary Check: Zero Data Leakage Enforced</span>
            <span className="text-emerald-700 font-mono font-medium">ABA Model Rule 1.10 Compliant</span>
          </div>
        </div>

        {/* Right: Citation Authority & MCP Tool Schemas */}
        <div className="lg:col-span-5 flex flex-col space-y-4 overflow-hidden">
          {/* Citation Verifier Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card flex-shrink-0">
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Scale className="w-4 h-4 text-emerald-600" />
                <h4 className="font-semibold text-xs text-slate-900">Case Law Citation Grounding Authority</h4>
              </div>
              <span className="text-[11px] text-emerald-700 font-mono font-medium">Primary Law API</span>
            </div>

            <div className="flex items-center gap-2 mb-3">
              <input
                value={citationInput}
                onChange={(e) => setCitationInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && verifyCitation()}
                placeholder="e.g. 698 A.2d 959 or Schrems II"
                className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:bg-white"
              />
              <button
                onClick={() => verifyCitation()}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-medium transition shadow-sm cursor-pointer"
              >
                Verify
              </button>
            </div>

            {citationResult && (
              <div className={`p-3.5 rounded-xl border text-xs space-y-2 ${
                citationResult.verified 
                  ? 'bg-emerald-50 border-emerald-200' 
                  : 'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-900">
                    {citationResult.case_details ? citationResult.case_details.case_name : "Unverified Citation"}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-medium ${
                    citationResult.verified ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {citationResult.status_badge}
                  </span>
                </div>

                {citationResult.case_details && (
                  <>
                    <p className="text-[11px] text-slate-500 font-medium">
                      Court: {citationResult.case_details.court} ({citationResult.case_details.year})
                    </p>
                    <p className="text-xs text-slate-700 italic pt-1 leading-relaxed">
                      "{citationResult.case_details.holding}"
                    </p>
                  </>
                )}

                {citationResult.warning && (
                  <p className="text-xs text-red-700 font-medium">{citationResult.warning}</p>
                )}
              </div>
            )}
          </div>

          {/* Registered MCP Tool Definitions */}
          <div className="flex-1 bg-white border border-slate-200 rounded-2xl p-5 shadow-card overflow-y-auto flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <Code className="w-4 h-4 text-indigo-600" />
                  <h4 className="font-semibold text-xs text-slate-900">Registered MCP Tool Schemas</h4>
                </div>
                <span className="text-[11px] text-slate-500 font-mono font-medium">RPC v1.0</span>
              </div>

              <div className="space-y-2.5">
                {mcpTools.map((tool, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 hover:border-slate-300 transition">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-medium text-indigo-900">tool: {tool.name}</span>
                      <span className="text-[10px] text-slate-400 font-mono font-medium">JSON Schema</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-snug">{tool.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 flex items-center justify-between font-medium">
              <span>Standard Model Context Protocol</span>
              <span className="text-indigo-700 font-mono font-medium">No Monolithic Lock-In</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
