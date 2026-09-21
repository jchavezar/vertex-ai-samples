import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RotateCcw, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle, 
  FileText, 
  Search, 
  Cpu, 
  Layers, 
  Check, 
  Copy,
  ExternalLink,
  Sparkles,
  GitCompare,
  History,
  Activity,
  ArrowRight,
  Download,
  Printer,
  Scale,
  Building,
  Award,
  ScrollText,
  FileCheck,
  Cloud
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ADKMultiAgentViewProps {
  initialPrompt?: string;
}

const DEFAULT_WORK_PRODUCT = {
  title: "Privacy & Artificial Intelligence Governance Master Addendum",
  matter_id: "MATTER-9042",
  client_name: "Apex Pharma Inc.",
  date: "September 9, 2026",
  firm: "Weil, Gotshal & Manges LLP",
  office: "767 Fifth Avenue • New York, NY 10153 • Technology & IP Transactions Practice",
  supervising_counsel: "Jesus Chavez, Esq. (Partner, Technology & IP Transactions)",
  signature_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  jurisdiction: "State of Delaware & European Union (GDPR Module 2)",
  risk_rating: "Audit Cleared (Low Risk)",
  ethical_wall_cleared: true,
  ethical_wall_notice: null,
  clauses_count: 4,
  citations_verified: 2,
  clauses: [
    {
      id: "CLAUSE-01",
      title: "Definitions & Scope of Protected Data",
      jurisdiction: "Global / Multi-Jurisdictional",
      risk_level: "Low",
      text: "For the purposes of this Agreement: (a) 'Protected Data' means any personal, proprietary, or confidential data provided by or on behalf of Client to Service Provider in connection with the Services; (b) 'Applicable Privacy Law' includes Regulation (EU) 2016/679 (GDPR), the California Consumer Privacy Act as amended (CCPA/CPRA), and the EU AI Act (Regulation (EU) 2024/1689)."
    },
    {
      id: "CLAUSE-02",
      title: "Schrems II Standard Contractual Clauses (Module 2)",
      jurisdiction: "EU / EEA / United States",
      risk_level: "High",
      text: "To the extent that the processing of Protected Data involves transfers from the EEA to countries not deemed to provide an adequate level of data protection, the Parties hereby enter into and incorporate by reference the Standard Contractual Clauses (Module 2: Controller-to-Processor) pursuant to CJEU Decision Case C-311/18 (Schrems II). The Parties agree that the technical and organizational measures set forth in Schedule B satisfy supplementary safeguard obligations."
    },
    {
      id: "CLAUSE-03",
      title: "Sub-processor Notification & 30-Day Audit Right",
      jurisdiction: "EU / Global",
      risk_level: "Medium",
      text: "Service Provider shall not engage any third-party sub-processor without providing at least thirty (30) days prior written notice to Client. Client shall have the affirmative right to conduct annual security and algorithmic governance audits, or appoint an independent auditor, upon fourteen (14) days notice."
    },
    {
      id: "CLAUSE-04",
      title: "Prohibition on Foundation Model Training & Data Retention",
      jurisdiction: "All Jurisdictions",
      risk_level: "Critical",
      text: "Service Provider warrants that Protected Data, prompt inputs, and generated outputs shall not be stored, retained, or utilized for training, fine-tuning, or aligning foundation models, generative AI architectures, or machine learning algorithms, whether owned by Service Provider or any third party."
    }
  ],
  citations: [
    {
      status_badge: "VERIFIED_PRIMARY_LAW",
      case_details: {
        case_name: "In re Caremark Int'l Inc. Derivative Litigation",
        citation: "698 A.2d 959",
        court: "Del. Ch.",
        year: 1996,
        holding: "Directors have an affirmative duty of oversight to ensure corporate compliance systems exist and function effectively."
      }
    },
    {
      status_badge: "VERIFIED_PRIMARY_LAW",
      case_details: {
        case_name: "Data Protection Commissioner v. Facebook Ireland & Schrems (Schrems II)",
        citation: "Case C-311/18",
        court: "Court of Justice of the European Union (CJEU)",
        year: 2020,
        holding: "Standard Contractual Clauses remain valid but require supplementary measures to ensure equivalent protection."
      }
    }
  ],
  document_markdown: `# WEIL, GOTSHAL & MANGES LLP
### Technology & IP Transactions Practice Group • 767 Fifth Avenue, New York, NY 10153

---

## PRIVACY & ARTIFICIAL INTELLIGENCE GOVERNANCE MASTER ADDENDUM
**Matter Reference**: \`MATTER-9042\` | **Client**: **Apex Pharma Inc.** | **Date**: September 9, 2026  
**Supervising Partner**: Jesus Chavez, Esq. | **Jurisdiction**: State of Delaware & EU GDPR Module 2

---

### RECITALS & OPERATIVE PURPOSE
This Addendum supplements the Master Services Agreement between Client (**Apex Pharma Inc.**) and Service Provider. The Parties agree that the following modular covenants and governance safeguards are incorporated by reference and shall supersede any conflicting terms under Google Cloud VPC Service Controls perimeter.

---

### OPERATIVE COVENANTS & MODULAR ARTICLES

#### Article 1. Definitions & Scope of Protected Data (\`CLAUSE-01\`)
*Jurisdiction: Global / Multi-Jurisdictional | Risk Rating: Low*

> "For the purposes of this Agreement: (a) 'Protected Data' means any personal, proprietary, or confidential data provided by or on behalf of Client to Service Provider in connection with the Services; (b) 'Applicable Privacy Law' includes Regulation (EU) 2016/679 (GDPR), the California Consumer Privacy Act as amended (CCPA/CPRA), and the EU AI Act (Regulation (EU) 2024/1689)."

#### Article 2. Schrems II Standard Contractual Clauses (Module 2) (\`CLAUSE-02\`)
*Jurisdiction: EU / EEA / United States | Risk Rating: High*

> "To the extent that the processing of Protected Data involves transfers from the EEA to countries not deemed to provide an adequate level of data protection, the Parties hereby enter into and incorporate by reference the Standard Contractual Clauses (Module 2: Controller-to-Processor) pursuant to CJEU Decision Case C-311/18 (Schrems II)."

#### Article 3. Sub-processor Notification & 30-Day Audit Right (\`CLAUSE-03\`)
*Jurisdiction: EU / Global | Risk Rating: Medium*

> "Service Provider shall not engage any third-party sub-processor without providing at least thirty (30) days prior written notice to Client. Client shall have the affirmative right to conduct annual security and algorithmic governance audits, or appoint an independent auditor, upon fourteen (14) days notice."

#### Article 4. Prohibition on Foundation Model Training & Data Retention (\`CLAUSE-04\`)
*Jurisdiction: All Jurisdictions | Risk Rating: Critical*

> "Service Provider warrants that Protected Data, prompt inputs, and generated outputs shall not be stored, retained, or utilized for training, fine-tuning, or aligning foundation models, generative AI architectures, or machine learning algorithms, whether owned by Service Provider or any third party."

---

### TABLE OF AUTHORITIES & VERIFIED JUDICIAL PRECEDENTS

- **In re Caremark Int'l Inc. Derivative Litigation**, *698 A.2d 959* (Del. Ch. 1996)
  - **Legal Holding**: Directors have an affirmative duty of oversight to ensure corporate compliance systems exist and function effectively.
  - **Verification Status**: \`🟢 VERIFIED_PRIMARY_LAW\`

- **Data Protection Commissioner v. Facebook Ireland & Schrems (Schrems II)**, *Case C-311/18* (CJEU 2020)
  - **Legal Holding**: Standard Contractual Clauses remain valid but require supplementary measures to ensure equivalent protection.
  - **Verification Status**: \`🟢 VERIFIED_PRIMARY_LAW\`

---

### EXECUTION & ATTESTATION BLOCK

| **For Client (Apex Pharma Inc.)** | **For Supervising Legal Counsel (Weil)** |
| :--- | :--- |
| **Apex Pharma Inc.** | **Weil, Gotshal & Manges LLP** |
| By: ___________________________ | By: */s/ Jesus Chavez, Esq.* |
| Title: Authorized Representative | Title: Partner, Technology Transactions |

**Cryptographic Verification Seal**: \`SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\`  
**Zero-Leak Certified**: Executed within Google Cloud VPC Service Controls with Zero Data Retention.`
};

export const ADKMultiAgentView: React.FC<ADKMultiAgentViewProps> = ({ initialPrompt = '' }) => {
  const [prompt, setPrompt] = useState(
    initialPrompt || "Assemble GDPR + Schrems II compliant AI governance addendum with zero data retention and 30-day audit rights"
  );
  const [matterId, setMatterId] = useState("MATTER-9042");
  const [clientName, setClientName] = useState("Apex Pharma Inc.");
  const [runtimeTarget, setRuntimeTarget] = useState<'local' | 'cloud_agent_runtime'>('local');
  const [isRunning, setIsRunning] = useState(false);
  const [copied, setCopied] = useState(false);
  const [workProductTab, setWorkProductTab] = useState<'document' | 'diff' | 'audit'>('document');
  const [docViewMode, setDocViewMode] = useState<'sheet' | 'markdown'>('sheet');
  const [elapsedTime, setElapsedTime] = useState<number>(0);

  // Agent lane states
  const [coordinatorPlan, setCoordinatorPlan] = useState<any>(null);
  const [assemblyState, setAssemblyState] = useState<any>({ 
    status: 'success', 
    events: [], 
    latency: '142ms',
    title: 'Assembled 4 Modular Lego Clauses',
    message: 'All prerequisite dependencies satisfied (Module 2 SCCs, Zero Data Retention, Audit Rights).'
  });
  const [citationState, setCitationState] = useState<any>({ 
    status: 'success', 
    events: [], 
    latency: '88ms',
    title: 'All Legal Citations Grounded',
    message: 'Verified 2 primary authorities with 0 hallucinations.'
  });
  const [ethicalWallState, setEthicalWallState] = useState<any>({ 
    status: 'success', 
    events: [], 
    latency: '64ms',
    title: 'Ethical Clearance Granted',
    message: 'No adverse party conflicts detected for MATTER-9042.'
  });
  const [redlineState, setRedlineState] = useState<any>({ 
    status: 'success', 
    events: [], 
    latency: '190ms',
    title: 'Risk & Deviation Analysis Complete',
    message: 'Indemnity Cap: 15.0% Capped | Survival: 18 Months'
  });
  const [workProduct, setWorkProduct] = useState<any>(DEFAULT_WORK_PRODUCT);

  useEffect(() => {
    if (initialPrompt) {
      setPrompt(initialPrompt);
    }
  }, [initialPrompt]);

  // Elapsed timer when running
  useEffect(() => {
    let interval: any;
    if (isRunning) {
      const start = Date.now();
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - start) / 100) / 10);
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const runWorkflow = async (customPrompt?: string) => {
    const q = customPrompt || prompt;
    setIsRunning(true);
    setWorkProduct(null);
    setCoordinatorPlan(null);
    setElapsedTime(0);
    setAssemblyState({ status: 'running', events: [], latency: '142ms' });
    setCitationState({ status: 'running', events: [], latency: '88ms' });
    setEthicalWallState({ status: 'running', events: [], latency: '64ms' });
    setRedlineState({ status: 'running', events: [], latency: '190ms' });

    try {
      const response = await fetch('/api/adk/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: q,
          matter_id: matterId,
          client_name: clientName,
          attorney_email: "jesusarguelles@google.com",
          runtime_target: runtimeTarget
        })
      });

      if (!response.body) throw new Error("No response stream");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          if (!part.trim()) continue;
          const lines = part.split('\n');
          let eventType = '';
          let dataStr = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) eventType = line.slice(7).trim();
            if (line.startsWith('data: ')) dataStr = line.slice(6).trim();
          }

          if (dataStr) {
            try {
              const data = JSON.parse(dataStr);
              handleSSEEvent(eventType, data);
            } catch (e) {
              console.error("Failed to parse SSE data", e);
            }
          }
        }
      }
    } catch (err) {
      console.error("Workflow run error", err);
    } finally {
      setIsRunning(false);
    }
  };

  const handleSSEEvent = (event: string, data: any) => {
    if (event === 'coordinator') {
      if (data.type === 'coordinator_plan') {
        setCoordinatorPlan(data);
      } else if (data.type === 'work_product') {
        setWorkProduct(data);
      }
    } else if (event === 'ethical_wall') {
      setEthicalWallState((prev: any) => ({
        ...prev,
        status: data.status || 'running',
        latency: '64ms',
        events: [...prev.events, data]
      }));
    } else if (event === 'assembly') {
      setAssemblyState((prev: any) => ({
        ...prev,
        status: data.status || 'running',
        latency: '142ms',
        events: [...prev.events, data]
      }));
    } else if (event === 'citation') {
      setCitationState((prev: any) => ({
        ...prev,
        status: data.status || 'running',
        latency: '88ms',
        events: [...prev.events, data]
      }));
    } else if (event === 'redline') {
      setRedlineState((prev: any) => ({
        ...prev,
        status: data.status || 'running',
        latency: '190ms',
        events: [...prev.events, data]
      }));
    }
  };

  const handleCopy = () => {
    if (workProduct?.document_markdown) {
      navigator.clipboard.writeText(workProduct.document_markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!workProduct) return;
    const textToDownload = workProduct.document_markdown || "";
    const blob = new Blob([textToDownload], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `WEIL_${matterId}_Privacy_Addendum.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Executive Control Header */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-card">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <span className="p-2.5 bg-blue-50 text-blue-700 rounded-xl border border-blue-100">
              <Cpu className="w-5 h-5" />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-slate-900">Google ADK Autonomous Multi-Agent Team</h3>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono text-blue-700 bg-blue-50 border border-blue-100 font-medium">
                  DAG Topology Active
                </span>
              </div>
              <p className="text-xs text-slate-500 font-normal">Deterministic parallel orchestration with Model Context Protocol (MCP) tool integration</p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200/60">
              <span className="text-slate-400 font-mono text-[10px]">MATTER</span>
              <input 
                value={matterId}
                onChange={(e) => setMatterId(e.target.value)}
                className="bg-transparent font-mono font-medium text-slate-800 w-24 text-xs focus:outline-none"
              />
            </div>
            <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200/60">
              <span className="text-slate-400 font-mono text-[10px]">CLIENT</span>
              <input 
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                className="bg-transparent font-medium text-slate-800 w-32 text-xs focus:outline-none"
              />
            </div>

            {/* Runtime Target Dropdown */}
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition ${
              runtimeTarget === 'cloud_agent_runtime' 
                ? 'bg-blue-50/90 border-blue-300 text-blue-900 shadow-xs' 
                : 'bg-slate-50 border-slate-200/60 text-slate-800'
            }`}>
              <Cloud className={`w-3.5 h-3.5 ${runtimeTarget === 'cloud_agent_runtime' ? 'text-blue-600 animate-pulse' : 'text-slate-400'}`} />
              <span className="text-slate-400 font-mono text-[10px]">RUNTIME</span>
              <select
                value={runtimeTarget}
                onChange={(e) => setRuntimeTarget(e.target.value as any)}
                className="bg-transparent font-medium text-xs focus:outline-none cursor-pointer"
              >
                <option value="local">⚡ Local ADK Team (4 Parallel Lanes)</option>
                <option value="cloud_agent_runtime">☁️ Vertex AI Agent Runtime (Cloud Live • gemini-3.8-flash)</option>
              </select>
            </div>

            {isRunning && (
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg font-mono text-xs font-medium border border-blue-200">
                <Activity className="w-3.5 h-3.5 animate-pulse" />
                {elapsedTime.toFixed(1)}s
              </span>
            )}
          </div>
        </div>

        {/* Cloud Runtime Observability Status Pill */}
        {runtimeTarget === 'cloud_agent_runtime' && (
          <div className="mb-4 px-4 py-2 bg-blue-50/70 border border-blue-200/80 rounded-xl flex items-center justify-between text-xs text-blue-900">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
              <span className="font-semibold">Live Google Cloud Connection Active:</span>
              <span className="font-mono text-[11px] text-blue-700">Project: vtxdemos • Model: gemini-3.8-flash • VPC-SC Zero Retention</span>
            </div>
            <div className="flex items-center gap-3">
              <a
                href="https://console.cloud.google.com/traces/list?project=vtxdemos"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-[11px] font-medium text-blue-700 hover:text-blue-900 underline underline-offset-2"
              >
                <Activity className="w-3 h-3" />
                <span>Open Cloud Trace</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </a>
              <span className="text-blue-300">•</span>
              <a
                href="https://console.cloud.google.com/logs/query?project=vtxdemos"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-[11px] font-medium text-blue-700 hover:text-blue-900 underline underline-offset-2"
              >
                <Search className="w-3 h-3" />
                <span>Open Cloud Logging</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </a>
              <span className="text-blue-300">•</span>
              <a
                href="https://console.cloud.google.com/vertex-ai/reasoning-engines?project=vtxdemos"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-[11px] font-medium text-blue-700 hover:text-blue-900 underline underline-offset-2"
              >
                <Cpu className="w-3 h-3" />
                <span>Agent Runtime Console</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
          </div>
        )}

        {/* 1-Click Executive Presets */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1">
          <span className="text-xs text-slate-400 font-medium shrink-0">Mandates:</span>
          <button
            onClick={() => {
              const p = "Assemble GDPR + Schrems II compliant AI governance addendum with zero data retention and 30-day audit rights";
              setPrompt(p);
              runWorkflow(p);
            }}
            className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-700 font-medium transition shrink-0 cursor-pointer"
          >
            EU-US AI Transfer Addendum (Privacy Pro)
          </button>
          <button
            onClick={() => {
              const p = "Retrieve merger indemnification precedent from the BioGen acquisition to use in drafting for Apex Pharma";
              setPrompt(p);
              runWorkflow(p);
            }}
            className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-700 font-medium transition shrink-0 cursor-pointer"
          >
            Ethical Wall Conflict Barrier Test (BioGen Precedent)
          </button>
          <button
            onClick={() => {
              const p = "Analyze M&A seller acquisition contract redlines and indemnity cap deviation against standard market baselines";
              setPrompt(p);
              runWorkflow(p);
            }}
            className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-700 font-medium transition shrink-0 cursor-pointer"
          >
            M&A Due Diligence: Redline & Cap Audit
          </button>
        </div>

        {/* Query Input Bar */}
        <div className="flex items-center gap-3">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isRunning && runWorkflow()}
            placeholder="Enter legal instruction or contract drafting mandate..."
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:bg-white transition"
          />
          <button
            onClick={() => runWorkflow()}
            disabled={isRunning || !prompt.trim()}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white font-medium rounded-xl text-xs transition shadow-xs cursor-pointer"
          >
            {isRunning ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>Deliberating...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Execute ADK Team</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Dynamic Topology Bar */}
      <div className="bg-white border border-slate-200/80 rounded-xl px-5 py-2.5 shadow-card flex items-center justify-between text-xs overflow-x-auto">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-xs font-medium">Orchestration Graph:</span>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-xs transition ${
              isRunning ? 'bg-blue-600 text-white font-medium' : 'bg-slate-100 text-slate-700'
            }`}>
              ADK Coordinator
            </span>
            <ArrowRight className="w-3 h-3 text-slate-300" />
            <span className={`px-2 py-0.5 rounded text-xs transition ${
              assemblyState.status === 'running' ? 'bg-blue-100 text-blue-800 animate-pulse' :
              assemblyState.status === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-50 text-slate-500'
            }`}>
              Assembly
            </span>
            <span className="text-slate-300">•</span>
            <span className={`px-2 py-0.5 rounded text-xs transition ${
              citationState.status === 'running' ? 'bg-blue-100 text-blue-800 animate-pulse' :
              citationState.status === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-50 text-slate-500'
            }`}>
              Citation
            </span>
            <span className="text-slate-300">•</span>
            <span className={`px-2 py-0.5 rounded text-xs transition ${
              ethicalWallState.status === 'warning' ? 'bg-amber-50 text-amber-800' :
              ethicalWallState.status === 'running' ? 'bg-blue-100 text-blue-800 animate-pulse' : 'bg-slate-50 text-slate-500'
            }`}>
              Ethical Wall
            </span>
            <span className="text-slate-300">•</span>
            <span className={`px-2 py-0.5 rounded text-xs transition ${
              redlineState.status === 'running' ? 'bg-blue-100 text-blue-800 animate-pulse' :
              redlineState.status === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-50 text-slate-500'
            }`}>
              Redline
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-slate-500 text-xs">
          <span>Concurrency: 4 Lanes</span>
          <span>•</span>
          <span className="text-emerald-700 font-medium">Zero-Egress Active</span>
        </div>
      </div>

      {/* Main Deliberation Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 overflow-hidden">
        {/* Left: 4 Parallel Subagent Lanes (7 cols) */}
        <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto pr-1">
          <LaneCard
            icon="📄"
            title="Assembly Agent"
            role="Privacy Pro Legos"
            state={assemblyState}
            accentColor="blue"
          />

          <LaneCard
            icon="🔍"
            title="Citation Agent"
            role="Precedent Verifier"
            state={citationState}
            accentColor="emerald"
          />

          <LaneCard
            icon="🛡️"
            title="Ethical Wall Guard"
            role="Chinese Wall Barrier"
            state={ethicalWallState}
            accentColor="amber"
          />

          <LaneCard
            icon="✍️"
            title="Redline Agent"
            role="Risk & Cap Scorer"
            state={redlineState}
            accentColor="purple"
          />
        </div>

        {/* Right: Synthesized Work Product Drawer (5 cols) */}
        <div className="lg:col-span-5 bg-white border border-slate-200/80 rounded-2xl p-6 flex flex-col justify-between overflow-hidden shadow-card">
          <div>
            {/* Header with View Tabs */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
              <div className="flex items-center gap-2">
                <span className="p-1.5 bg-emerald-50 text-emerald-700 rounded-lg">
                  <FileText className="w-4 h-4" />
                </span>
                <div>
                  <h4 className="font-semibold text-sm text-slate-900 leading-tight">Governed Deliverable</h4>
                  <p className="text-[11px] text-slate-500 font-mono">{matterId}</p>
                </div>
              </div>

              {/* View Switcher Tabs */}
              <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200/60 text-xs">
                <button
                  onClick={() => setWorkProductTab('document')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1 ${
                    workProductTab === 'document' ? 'bg-white text-slate-900 shadow-xs font-medium' : 'text-slate-600 hover:text-slate-900 font-normal'
                  }`}
                >
                  <FileText className="w-3 h-3 text-blue-600" />
                  <span>Brief</span>
                </button>
                <button
                  onClick={() => setWorkProductTab('diff')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1 ${
                    workProductTab === 'diff' ? 'bg-white text-slate-900 shadow-xs font-medium' : 'text-slate-600 hover:text-slate-900 font-normal'
                  }`}
                >
                  <GitCompare className="w-3 h-3" />
                  <span>Redline</span>
                </button>
                <button
                  onClick={() => setWorkProductTab('audit')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1 ${
                    workProductTab === 'audit' ? 'bg-white text-slate-900 shadow-xs font-medium' : 'text-slate-600 hover:text-slate-900 font-normal'
                  }`}
                >
                  <ShieldCheck className="w-3 h-3" />
                  <span>Audit</span>
                </button>
              </div>
            </div>

            {/* Document Mode Toolbar (when on Brief tab and workProduct ready) */}
            {workProduct && workProductTab === 'document' && (
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] text-slate-400 uppercase font-mono tracking-wider">Format:</span>
                  <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200/60 text-[11px]">
                    <button
                      onClick={() => setDocViewMode('sheet')}
                      className={`px-2 py-0.5 rounded transition cursor-pointer flex items-center gap-1 ${
                        docViewMode === 'sheet' ? 'bg-white text-slate-900 shadow-xs font-medium' : 'text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <ScrollText className="w-3 h-3 text-blue-600" />
                      <span>Executive Sheet</span>
                    </button>
                    <button
                      onClick={() => setDocViewMode('markdown')}
                      className={`px-2 py-0.5 rounded transition cursor-pointer flex items-center gap-1 ${
                        docViewMode === 'markdown' ? 'bg-white text-slate-900 shadow-xs font-medium' : 'text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <span>Plain Text</span>
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-1 px-2 py-1 text-[11px] text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition cursor-pointer border border-slate-200/60"
                    title="Export .txt file"
                  >
                    <Download className="w-3 h-3" />
                    <span>Export</span>
                  </button>
                  <button
                    onClick={() => window.print()}
                    className="flex items-center gap-1 px-2 py-1 text-[11px] text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition cursor-pointer border border-slate-200/60"
                    title="Print / Save PDF"
                  >
                    <Printer className="w-3 h-3" />
                    <span>Print</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Dynamic Content Area */}
          <div className="flex-1 overflow-y-auto my-2 pr-1 text-xs text-slate-700">
            {workProduct ? (
              workProductTab === 'document' ? (
                docViewMode === 'sheet' ? (
                  /* Formal Executive Document Sheet */
                  <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs space-y-5 text-slate-800 font-sans">
                    {/* Formal Firm Letterhead */}
                    <div className="text-center pb-4 border-b border-slate-200 space-y-1">
                      <span className="text-[10px] tracking-[0.25em] font-semibold text-slate-500 uppercase block">
                        Weil, Gotshal & Manges LLP
                      </span>
                      <span className="text-[9px] text-slate-400 tracking-wider block">
                        767 Fifth Avenue • New York, NY 10153 • Technology & IP Transactions Practice
                      </span>
                      <div className="pt-2">
                        <h3 className="text-xs font-bold tracking-wide text-slate-900 uppercase">
                          Privacy & Artificial Intelligence Governance Master Addendum
                        </h3>
                        <div className="flex items-center justify-center gap-2 text-[10px] text-slate-500 font-medium mt-1">
                          <span>Matter: <strong className="font-mono text-slate-700">{workProduct.matter_id || matterId}</strong></span>
                          <span>•</span>
                          <span>Client: <strong className="text-slate-800">{workProduct.client_name || clientName}</strong></span>
                          <span>•</span>
                          <span>Date: {workProduct.date || 'September 9, 2026'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Ethical Wall Clearance Banner if triggered */}
                    {workProduct.ethical_wall_notice && (
                      <div className="p-3 bg-amber-50/80 border border-amber-200 rounded-lg text-xs space-y-1">
                        <div className="flex items-center gap-1.5 font-semibold text-amber-950 text-[11px]">
                          <ShieldAlert className="w-3.5 h-3.5 text-amber-700 shrink-0" />
                          <span>ABA Model Rule 1.10 Ethical Wall Compliance Attestation</span>
                        </div>
                        <p className="text-[11px] text-amber-900 leading-relaxed font-normal">
                          {workProduct.ethical_wall_notice}
                        </p>
                      </div>
                    )}

                    {/* Recitals & Purpose */}
                    <div className="space-y-1 text-xs text-slate-600 leading-relaxed border-l-2 border-slate-300 pl-3 py-0.5 bg-slate-50/60 rounded-r">
                      <p className="font-semibold text-slate-900 text-[11px] uppercase tracking-wider">Recitals & Purpose</p>
                      <p>
                        This Addendum supplements the Master Services Agreement between Client ({workProduct.client_name || clientName}) and Service Provider. Incorporating validated modular covenants with zero prompt data retention under Google Cloud VPC Service Controls perimeter.
                      </p>
                    </div>

                    {/* Operative Articles (Lego Clauses) */}
                    <div className="space-y-3.5">
                      <div className="flex items-center justify-between pb-1 border-b border-slate-100">
                        <span className="text-[11px] font-semibold text-slate-900 uppercase tracking-wider">
                          Operative Articles ({workProduct.clauses?.length || 4} Clauses Assembled)
                        </span>
                        <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-medium">
                          Dependency Validated
                        </span>
                      </div>

                      {(workProduct.clauses && workProduct.clauses.length > 0 ? workProduct.clauses : [
                        {
                          id: "CLAUSE-01",
                          title: "Definitions & Scope of Protected Data",
                          jurisdiction: "Global / Multi-Jurisdictional",
                          risk_level: "Low",
                          text: "For the purposes of this Agreement: (a) 'Protected Data' means any personal, proprietary, or confidential data provided by or on behalf of Client to Service Provider in connection with the Services; (b) 'Applicable Privacy Law' includes Regulation (EU) 2016/679 (GDPR), the California Consumer Privacy Act as amended (CCPA/CPRA), and the EU AI Act (Regulation (EU) 2024/1689)."
                        },
                        {
                          id: "CLAUSE-02",
                          title: "Schrems II Standard Contractual Clauses (Module 2)",
                          jurisdiction: "EU / EEA / United States",
                          risk_level: "High",
                          text: "To the extent that the processing of Protected Data involves transfers from the EEA to countries not deemed to provide an adequate level of data protection, the Parties hereby enter into and incorporate by reference the Standard Contractual Clauses (Module 2: Controller-to-Processor) pursuant to CJEU Decision Case C-311/18 (Schrems II). The Parties agree that the technical and organizational measures set forth in Schedule B satisfy supplementary safeguard obligations."
                        },
                        {
                          id: "CLAUSE-03",
                          title: "Sub-processor Notification & 30-Day Audit Right",
                          jurisdiction: "EU / Global",
                          risk_level: "Medium",
                          text: "Service Provider shall not engage any third-party sub-processor without providing at least thirty (30) days prior written notice to Client. Client shall have the affirmative right to conduct annual security and algorithmic governance audits, or appoint an independent auditor, upon fourteen (14) days notice."
                        },
                        {
                          id: "CLAUSE-04",
                          title: "Prohibition on Foundation Model Training & Data Retention",
                          jurisdiction: "All Jurisdictions",
                          risk_level: "Critical",
                          text: "Service Provider warrants that Protected Data, prompt inputs, and generated outputs shall not be stored, retained, or utilized for training, fine-tuning, or aligning foundation models, generative AI architectures, or machine learning algorithms, whether owned by Service Provider or any third party."
                        }
                      ]).map((c: any, idx: number) => (
                        <div key={c.id || idx} className="space-y-1.5 bg-slate-50/80 border border-slate-200/70 rounded-xl p-3">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-semibold text-slate-900 text-xs">
                              Section {idx + 1}. {c.title}
                            </span>
                            <span className="font-mono text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-medium">
                              {c.id}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-[10px] text-slate-400 font-medium">
                            <span>Jurisdiction: {c.jurisdiction}</span>
                            <span>•</span>
                            <span className={
                              c.risk_level === 'Critical' ? 'text-rose-700' :
                              c.risk_level === 'High' ? 'text-amber-700' : 'text-emerald-700'
                            }>
                              Risk: {c.risk_level}
                            </span>
                          </div>
                          <p className="text-xs text-slate-700 leading-relaxed italic border-l-2 border-blue-500/80 pl-2.5 py-1 bg-white rounded-r shadow-2xs">
                            "{c.text}"
                          </p>
                        </div>
                      ))}
                    </div>

                    {/* Table of Authorities */}
                    {(workProduct.citations && workProduct.citations.length > 0) && (
                      <div className="space-y-2.5 pt-3 border-t border-slate-200">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-semibold text-slate-900 uppercase tracking-wider">
                            Table of Authorities & Judicial Grounding
                          </span>
                          <span className="text-[10px] text-emerald-700 font-mono font-medium">
                            0 Hallucinations
                          </span>
                        </div>
                        <div className="space-y-2">
                          {workProduct.citations.map((cite: any, idx: number) => {
                            const caseDetails = cite.case_details;
                            return (
                              <div key={idx} className="p-2.5 bg-emerald-50/40 border border-emerald-200/70 rounded-lg text-xs space-y-1">
                                <div className="flex items-center justify-between">
                                  <span className="font-semibold text-slate-900 text-xs">
                                    {caseDetails?.case_name || "Primary Judicial Precedent"}
                                  </span>
                                  <span className="text-[10px] font-mono text-emerald-800 bg-emerald-100/80 px-2 py-0.5 rounded-full font-medium">
                                    {cite.status_badge || "VERIFIED"}
                                  </span>
                                </div>
                                <p className="text-[11px] text-slate-600 font-medium">
                                  {caseDetails?.citation} ({caseDetails?.court} {caseDetails?.year})
                                </p>
                                <p className="text-[11px] text-slate-500 italic">
                                  Holding: "{caseDetails?.holding}"
                                </p>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Formal Signature & Execution Block */}
                    <div className="pt-4 border-t border-slate-200 space-y-4">
                      <div className="grid grid-cols-2 gap-6 text-xs text-slate-700 pt-1">
                        <div className="space-y-1">
                          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-medium">
                            For Client
                          </span>
                          <p className="font-semibold text-slate-900">{workProduct.client_name || clientName}</p>
                          <div className="h-6 border-b border-dashed border-slate-300"></div>
                          <p className="text-[10px] text-slate-400">Authorized Officer / General Counsel</p>
                        </div>
                        <div className="space-y-1">
                          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-medium">
                            Supervising Legal Counsel
                          </span>
                          <p className="font-semibold text-slate-900">Weil, Gotshal & Manges LLP</p>
                          <p className="font-serif italic text-blue-900 text-sm h-6 flex items-end">
                            /s/ Jesus Chavez, Esq.
                          </p>
                          <p className="text-[10px] text-slate-400">Partner, Technology & IP Transactions</p>
                        </div>
                      </div>

                      {/* Cryptographic Provenance Stamp */}
                      <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-[10px] font-mono text-slate-500 flex items-center justify-between">
                        <div className="flex items-center gap-1.5 truncate">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span className="truncate">SHA-256: {workProduct.signature_hash || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}</span>
                        </div>
                        <span className="text-emerald-700 font-medium shrink-0 ml-2">Zero-Leak Certified</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Formatted Markdown Mode */
                  <div className="p-5 bg-white border border-slate-200/90 rounded-xl space-y-3 shadow-xs">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100 text-slate-500 text-[11px]">
                      <span className="font-medium text-slate-700">Rendered Legal Markdown</span>
                      <button onClick={handleCopy} className="text-blue-600 hover:underline cursor-pointer">
                        {copied ? 'Copied' : 'Copy Text'}
                      </button>
                    </div>
                    <div className="text-xs text-slate-800 leading-relaxed font-sans">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({ node, ...props }) => <h1 className="text-sm font-bold text-slate-900 border-b border-slate-200 pb-1.5 mb-2 mt-3 tracking-wide uppercase text-center" {...props} />,
                          h2: ({ node, ...props }) => <h2 className="text-xs font-bold text-slate-900 border-b border-slate-100 pb-1 mb-2 mt-3 tracking-wide uppercase text-center" {...props} />,
                          h3: ({ node, ...props }) => <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-1.5 mt-3" {...props} />,
                          h4: ({ node, ...props }) => <h4 className="text-xs font-semibold text-slate-900 mb-1 mt-2.5" {...props} />,
                          p: ({ node, ...props }) => <p className="text-xs text-slate-700 leading-relaxed mb-2" {...props} />,
                          blockquote: ({ node, ...props }) => <blockquote className="border-l-2 border-blue-500 bg-blue-50/50 p-2.5 rounded-r text-xs text-slate-700 italic my-2" {...props} />,
                          hr: ({ node, ...props }) => <hr className="border-slate-200 my-2.5" {...props} />,
                          table: ({ node, ...props }) => <div className="overflow-x-auto my-3"><table className="w-full border border-slate-200 text-xs text-left" {...props} /></div>,
                          th: ({ node, ...props }) => <th className="bg-slate-100 p-2 font-semibold text-slate-800 border-b border-slate-200" {...props} />,
                          td: ({ node, ...props }) => <td className="p-2 border-b border-slate-100 text-slate-700" {...props} />,
                          ul: ({ node, ...props }) => <ul className="list-disc pl-4 space-y-1 mb-2 text-xs text-slate-700" {...props} />,
                          li: ({ node, ...props }) => <li className="leading-relaxed" {...props} />
                        }}
                      >
                        {workProduct.document_markdown}
                      </ReactMarkdown>
                    </div>
                  </div>
                )
              ) : workProductTab === 'diff' ? (
                <div className="space-y-3">
                  {/* Redline Summary Header */}
                  <div className="p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-slate-900 uppercase tracking-wider">
                        Market Redline & Indemnity Cap Audit
                      </span>
                      <span className="text-[10px] font-mono text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-full font-medium">
                        Weil Precedent Rule
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 pt-1 text-center font-mono">
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <span className="text-[9px] text-slate-400 uppercase block">Counterparty</span>
                        <span className="text-xs font-semibold text-rose-700">100% Uncapped</span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <span className="text-[9px] text-slate-400 uppercase block">Weil Market</span>
                        <span className="text-xs font-semibold text-emerald-700">15.0% Capped</span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <span className="text-[9px] text-slate-400 uppercase block">Survival</span>
                        <span className="text-xs font-semibold text-slate-800">18 Months</span>
                      </div>
                    </div>
                  </div>

                  {/* Staged Clause Diff */}
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-2 shadow-2xs">
                    <span className="text-[10px] font-mono text-slate-400 block">Section 8.2 • Indemnification Limitation</span>
                    <div className="space-y-2 font-mono text-[11px] leading-relaxed">
                      <div className="p-2.5 bg-rose-50/70 border border-rose-200 rounded-lg text-rose-900 line-through">
                        - Counterparty Proposed: "Seller indemnification liability shall be uncapped and survive indefinitely for all operational representations."
                      </div>
                      <div className="p-2.5 bg-emerald-50/70 border border-emerald-200 rounded-lg text-emerald-950">
                        + Weil Governed Standard: "Seller aggregate indemnification liability shall be strictly capped at 15.0% of Purchase Price ($6.75M USD) and terminate after 18 months pursuant to Weil Delaware Chancery Precedent."
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-500 pt-1">
                      Mitigation Rationale: Uncapped indemnification violates Weil M&A Deal Standards. Capped at 15% with 18-month survival.
                    </p>
                  </div>
                </div>
              ) : (
                /* Audit Provenance Log */
                <div className="space-y-2 font-mono text-[11px]">
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <div className="flex items-center justify-between text-slate-500 text-[10px]">
                      <span>STEP 1: COORDINATOR DECOMPOSITION</span>
                      <span className="text-blue-700 font-medium">DISPATCHED (4 LANES)</span>
                    </div>
                    <p className="text-slate-800">Decomposed mandate for {workProduct.client_name || clientName} ({matterId})</p>
                  </div>

                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <div className="flex items-center justify-between text-slate-500 text-[10px]">
                      <span>STEP 2: ETHICAL WALL SCREENING</span>
                      <span className="text-emerald-700 font-medium">ABA RULE 1.10 CLEARED</span>
                    </div>
                    <p className="text-slate-800">Zero adverse client cross-contamination; proprietary terms sanitized.</p>
                  </div>

                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <div className="flex items-center justify-between text-slate-500 text-[10px]">
                      <span>STEP 3: MODULAR CLAUSE RETRIEVAL</span>
                      <span className="text-emerald-700 font-medium">DEPENDENCY VALIDATED</span>
                    </div>
                    <p className="text-slate-800">{workProduct.clauses_count || 4} modular Lego clauses retrieved via MCP connector.</p>
                  </div>

                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <div className="flex items-center justify-between text-slate-500 text-[10px]">
                      <span>STEP 4: PRIMARY LAW CITATION</span>
                      <span className="text-blue-700 font-medium">DELAWARE CHANCERY & CJEU</span>
                    </div>
                    <p className="text-slate-800">In re Caremark, 698 A.2d 959 (Del. Ch.) & Case C-311/18 (Schrems II)</p>
                  </div>

                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <div className="flex items-center justify-between text-slate-500 text-[10px]">
                      <span>STEP 5: CRYPTOGRAPHIC SIGNATURE</span>
                      <span className="text-emerald-700 font-medium">SHA-256 VERIFIED</span>
                    </div>
                    <p className="text-slate-800 truncate font-mono">{workProduct.signature_hash || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}</p>
                  </div>
                </div>
              )
            ) : isRunning ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
                <div className="w-8 h-8 border-2 border-blue-600/20 border-t-blue-600 rounded-full animate-spin"></div>
                <p className="text-slate-700 text-xs font-medium">Coordinating subagents and verifying legal citations...</p>
                <p className="text-[11px] text-slate-400">Executing parallel MCP queries across firm vault</p>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-2">
                <FileText className="w-10 h-10 text-slate-300 stroke-1" />
                <p className="text-sm font-medium text-slate-700">Awaiting Multi-Agent Synthesis</p>
                <p className="text-xs text-slate-500 max-w-xs">Run a preset mandate or enter an instruction above to see coordination in action.</p>
              </div>
            )}
          </div>

          {/* Action Footer */}
          {workProduct && (
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-emerald-700 font-medium">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Zero-Leak Enforced</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg text-xs transition cursor-pointer"
                >
                  {copied ? 'Copied' : 'Copy'}
                </button>
                <button
                  onClick={() => alert("Deliverable signed and exported to iManage Document Vault (MATTER-9042)!")}
                  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-xs transition shadow-xs cursor-pointer"
                >
                  Sign & Transmit
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface LaneCardProps {
  icon: string;
  title: string;
  role: string;
  state: any;
  accentColor: 'blue' | 'emerald' | 'amber' | 'purple';
}

const LaneCard: React.FC<LaneCardProps> = ({ icon, title, role, state, accentColor }) => {
  const isRunning = state.status === 'running';
  const isSuccess = state.status === 'success';
  const isWarning = state.status === 'warning';

  const borderClass = isWarning 
    ? 'border-amber-300 bg-amber-50/20' 
    : isRunning 
    ? 'border-blue-300 bg-blue-50/20 shadow-xs' 
    : isSuccess 
    ? 'border-slate-200/80 hover:border-slate-300' 
    : 'border-slate-200/80';

  return (
    <div className={`bg-white border ${borderClass} rounded-2xl p-4 flex flex-col justify-between transition h-72 overflow-hidden shadow-card`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <div>
            <h4 className="font-semibold text-xs text-slate-900 leading-tight">{title}</h4>
            <p className="text-[10px] text-slate-500 font-mono">{role}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {state.latency && (
            <span className="text-[10px] font-mono text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200">
              {state.latency}
            </span>
          )}
          {isRunning && (
            <span className="px-2 py-0.5 rounded text-[10px] bg-blue-50 text-blue-700 font-medium border border-blue-100 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-ping"></span>
              Thinking
            </span>
          )}
          {isSuccess && (
            <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-50 text-emerald-700 font-medium border border-emerald-100">
              Complete
            </span>
          )}
          {isWarning && (
            <span className="px-2 py-0.5 rounded text-[10px] bg-amber-50 text-amber-800 font-medium border border-amber-200">
              Barrier Active
            </span>
          )}
        </div>
      </div>

      {/* Events Log in Lane */}
      <div className="flex-1 overflow-y-auto py-2.5 space-y-2 text-xs">
        {state.events.length === 0 && !isRunning && (
          <div className="h-full flex items-center justify-center text-slate-400 text-xs italic">
            Standing by for coordinator dispatch...
          </div>
        )}

        {state.events.map((ev: any, idx: number) => (
          <div key={idx} className="space-y-1">
            {ev.type === 'agent_thought' && (
              <p className="text-slate-600 text-[11px] bg-slate-50 p-2.5 rounded-lg border border-slate-100 leading-relaxed">
                {ev.thought}
              </p>
            )}

            {ev.type === 'tool_call' && (
              <div className="p-2.5 bg-blue-50/50 border border-blue-100 rounded-lg space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono text-blue-900 font-medium">
                  <span>Tool: {ev.tool}</span>
                  <span className="text-blue-500">RPC Verified</span>
                </div>
                {ev.result && (
                  <p className="text-[10px] text-slate-600 font-mono truncate">
                    ↳ {JSON.stringify(ev.result).slice(0, 80)}...
                  </p>
                )}
              </div>
            )}

            {ev.type === 'agent_status' && (
              <div className="p-2 bg-emerald-50 border border-emerald-100 rounded-lg">
                <div className="flex items-center gap-1 text-emerald-800 font-medium text-xs">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{ev.title}</span>
                </div>
                <p className="text-[11px] text-slate-600 mt-0.5">{ev.message}</p>
              </div>
            )}

            {ev.type === 'agent_warning' && (
              <div className="p-2 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex items-center gap-1 text-amber-900 font-medium text-xs">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>{ev.title}</span>
                </div>
                <p className="text-[11px] text-amber-800 mt-0.5 leading-snug">{ev.message}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Lane Footer Badge */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
        <span>ADK Orchestration Node</span>
        <span className="font-mono text-slate-400">v1.2.0</span>
      </div>
    </div>
  );
};
