import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Sparkles,
  Terminal,
  FileCode,
  FolderOpen,
  Cpu,
  RotateCcw,
  ChevronDown,
  ChevronRight,
  Check,
  Copy,
  ArrowUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Search,
  Globe,
  Download,
  Eye,
  X,
  FileText,
  Database,
  BarChart3,
  Maximize2,
  LayoutDashboard,
  Share2,
  Zap,
  Brain
} from 'lucide-react';

interface Step {
  type?: string;
  name?: string;
  arguments?: any;
  result?: string;
  text?: string;
}

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  thoughtText?: string;
  timestamp: string;
  startTimestamp?: number;
  status?: 'submitting' | 'in_progress' | 'completed' | 'error';
  interactionId?: string;
  environmentId?: string;
  elapsed?: number;
  steps?: Step[];
  files?: Record<string, string>;
  usage?: any;
  error?: string;
  isA2A?: boolean;
}

interface A2AMessage {
  id: string;
  timestamp: string;
  traceId: string;
  sender: { agentId: string; name: string; role: string; color: string; avatar: string };
  recipient: { agentId: string; name: string; role: string; color: string; avatar: string };
  intent: 'DELEGATE_SIMULATION' | 'SIMULATION_COMPLETED' | 'CHALLENGE_ASSUMPTION' | 'RECALIBRATE_MODEL' | 'CONSENSUS_REACHED';
  status: 'VERIFIED' | 'DISPUTED' | 'RECALIBRATED' | 'SIGNED';
  summary: string;
  protocol: string;
  sandboxId: string;
  hash: string;
  payload: Record<string, any>;
}

const EBC_DEMO_TRACKS = [
  {
    title: "Live Tech Giants Valuation Dashboard",
    tag: "Search + Live HTML",
    desc: "Fetch live Google Search metrics for GOOGL, AMZN & MSFT and render interactive HTML dashboard.",
    prompt: "Search Google for the latest stock prices, market cap, and revenue for Alphabet (GOOGL), Amazon (AMZN), and Microsoft (MSFT). In 1 single step, use `create_file` to write an interactive dark-mode HTML dashboard at '/workspace/risk_dashboard.html' featuring live price cards, interactive sensitivity sliders, and comparative Chart.js bars."
  },
  {
    title: "10,000-Run Monte Carlo Simulation",
    tag: "Instant Sandbox Compute",
    desc: "Run 10,000 Monte Carlo iterations in Python, export CSV distribution & generate interactive VaR curve.",
    prompt: "Execute a Python script at '/workspace/monte_carlo.py' running a 10,000-iteration Monte Carlo supply chain disruption simulation in Python. Save the distribution dataset to '/workspace/var_distribution.csv' and generate an interactive HTML distribution visualizer at '/workspace/var_simulation.html'."
  },
  {
    title: "Real-Time Anomaly Forensics & Radar",
    tag: "Python Forensics",
    desc: "Generate 500 corporate transactions, detect statistical outliers (>3.0σ), and render interactive radar chart.",
    prompt: "Execute a Python script at '/workspace/detect_anomalies.py' generating 500 expense transactions and detecting statistical anomalies (>3.0σ). Save flagged items to '/workspace/fraud_anomalies.csv' and create an interactive HTML radar visualizer at '/workspace/fraud_radar.html'."
  },
  {
    title: "Algorithmic Order Matcher & Test Suite",
    tag: "Code Execution",
    desc: "Write algorithmic order matching engine with unit tests, execute in Linux sandbox & verify 100% pass.",
    prompt: "Write a high-performance algorithmic order matching engine in '/workspace/order_matcher.py' with automated unit tests in '/workspace/test_matcher.py', execute `python3 test_matcher.py` in the sandbox, and verify 100% test pass status."
  },
  {
    title: "A2A Multi-Agent Forensic Consensus",
    tag: "A2A Wire-Tap",
    desc: "Orchestrate 3 agents (Deal Lead, Quant Worker & Red-Team Auditor) disputing assumptions to reach consensus.",
    prompt: "Execute an Agent-to-Agent (A2A) M&A valuation audit: Deal Lead requests initial 10k Monte Carlo valuation, Red-Team Risk Auditor challenges terminal growth assumptions, Quant Agent recalibrates in Linux sandbox, and CRO signs reconciled Board Memorandum."
  }
];

function parseCsv(csvText: string) {
  const lines = csvText.trim().split('\n').map(l => l.trim()).filter(Boolean);
  if (lines.length === 0) return { headers: [], rows: [] };
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  const rows = lines.slice(1).map(line => line.split(',').map(c => c.trim().replace(/^"|"$/g, '')));
  return { headers, rows };
}

interface ParsedContent {
  thoughts: string[];
  finalAnswer: string;
  isPureThinking: boolean;
}

function segmentThoughts(rawText: string): string[] {
  if (!rawText) return [];
  
  // 1. Separate joined punctuation like "task.I will" or "exists.I will" into "task. I will"
  const clean = rawText
    .replace(/([.?!])([A-Z])/g, '$1 $2')
    .replace(/<thought>|<\/thought>/gi, ' ')
    .trim();

  // 2. Identify sentence splits and thought transition keywords
  const rawSegments = clean
    .split(/(?<=[.?!])\s+(?=[A-Z])|(?=\b(?:I will|Now I will|I need to|Let me|Let's|I am going to|I will now|Next,|First,|Finally,|We will|I should|I shall)\b)/gi)
    .map(s => s.trim())
    .filter(s => s.length > 10);

  // 3. Normalize and deduplicate repeated thoughts while maintaining sequence
  const result: string[] = [];
  const seenNorm = new Set<string>();

  for (const seg of rawSegments) {
    const normalized = seg.toLowerCase().replace(/[^a-z0-9]/g, '').trim();
    if (normalized.length < 8) continue;

    let isDupe = false;
    for (const prev of seenNorm) {
      if (prev === normalized || (normalized.length > 25 && prev.includes(normalized)) || (prev.length > 25 && normalized.includes(prev))) {
        isDupe = true;
        break;
      }
    }

    if (!isDupe) {
      seenNorm.add(normalized);
      const polished = seg.charAt(0).toUpperCase() + seg.slice(1);
      result.push(polished);
    }
  }

  return result;
}

function parseThinkingAndAnswer(rawText: string, streamedThoughtText?: string): ParsedContent {
  const streamedThoughts = streamedThoughtText ? segmentThoughts(streamedThoughtText) : [];

  if (!rawText || !rawText.trim()) {
    return { thoughts: streamedThoughts, finalAnswer: '', isPureThinking: streamedThoughts.length > 0 };
  }

  // 1. Explicit <thought> tags
  const tagMatch = rawText.match(/<thought>([\s\S]*?)<\/thought>/i);
  if (tagMatch) {
    const thoughtText = tagMatch[1].trim();
    const remaining = rawText.replace(/<thought>[\s\S]*?<\/thought>/i, '').trim();
    const thoughtItems = segmentThoughts(thoughtText);
    const mergedThoughts = Array.from(new Set([...streamedThoughts, ...thoughtItems]));
    return {
      thoughts: mergedThoughts.length > 0 ? mergedThoughts : (thoughtText ? [thoughtText] : streamedThoughts),
      finalAnswer: remaining,
      isPureThinking: !remaining && (!!thoughtText || streamedThoughts.length > 0),
    };
  }

  // 2. Multi-step reasoning pattern detection
  const paragraphs = rawText.split(/\n\n+/);
  const rawThinkingParts: string[] = [];
  const answerParts: string[] = [];
  let inThinkingPhase = true;

  for (let i = 0; i < paragraphs.length; i++) {
    const p = paragraphs[i].trim();
    if (!p) continue;

    // Report headers or tables mean thinking phase is concluded
    const isReportHeader = /^#{1,6}\s+/m.test(p) || 
                           /^(Executive Summary|Summary Report|Audit Findings|Conclusion|Key Findings|Consensus Reached|Consolidated|Final Report|M&A Valuation|Analysis|Resolution)/i.test(p) || 
                           /\|.*\|.*\|/m.test(p) ||
                           p.startsWith('```');

    if (isReportHeader) {
      inThinkingPhase = false;
    }

    const isThought = /^(I will|Let me|Let's|First,|Next,|Now I will|I am going to|I need to|Plan:|Thought:|Thinking:)/i.test(p);

    if (inThinkingPhase && isThought) {
      rawThinkingParts.push(p);
    } else {
      inThinkingPhase = false;
      answerParts.push(p);
    }
  }

  if (paragraphs.length === 1 && rawThinkingParts.length === 0) {
    const single = paragraphs[0];
    const segmented = segmentThoughts(single);
    if (segmented.length > 1 && segmented.every(s => /^(I will|I need|I am|Let|Now|First|Next)/i.test(s))) {
      const merged = Array.from(new Set([...streamedThoughts, ...segmented]));
      return {
        thoughts: merged,
        finalAnswer: '',
        isPureThinking: true,
      };
    }
  }

  const combinedThinking = rawThinkingParts.join(' ');
  const textThoughts = segmentThoughts(combinedThinking);
  const allThoughts = Array.from(new Set([...streamedThoughts, ...textThoughts]));
  const finalAnswer = answerParts.join('\n\n').trim();

  return {
    thoughts: allThoughts,
    finalAnswer: finalAnswer,
    isPureThinking: allThoughts.length > 0 && !finalAnswer,
  };
}

function ExecutiveHtmlFrame({ path, content, onExpand }: { path: string; content: string; onExpand: () => void }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const filename = path.split('/').pop() || path;

  return (
    <div className="my-3 rounded-xl border border-amber-300/80 bg-white overflow-hidden shadow-xs">
      <div className="px-4 py-2.5 bg-gradient-to-r from-amber-50 via-amber-50/40 to-white border-b border-amber-200/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-amber-500 text-white shadow-2xs">
            <LayoutDashboard className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-zinc-900 font-mono">{filename}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-bold border border-amber-200">
                LIVE INTERACTIVE ARTIFACT
              </span>
            </div>
            <span className="text-[10px] text-zinc-500">Autonomous Cloud Sandbox HTML/JS Dashboard</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-2.5 py-1 text-[11px] font-medium text-zinc-700 hover:text-zinc-900 bg-white hover:bg-zinc-100 border border-zinc-200 rounded-md transition-colors cursor-pointer shadow-2xs"
          >
            {isExpanded ? 'Collapse' : 'Expand Visual'}
          </button>
          <button
            onClick={onExpand}
            className="p-1.5 text-zinc-700 hover:text-zinc-900 bg-white hover:bg-zinc-100 border border-zinc-200 rounded-md transition-colors cursor-pointer shadow-2xs"
            title="Pop out Full Screen"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-2 bg-zinc-50/60">
          <div className="w-full h-[460px] rounded-lg border border-zinc-200 overflow-hidden bg-white shadow-inner">
            <iframe
              srcDoc={content}
              title={filename}
              className="w-full h-full border-0"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ExecutiveCsvVisualizer({ path, content }: { path: string; content: string }) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const filename = path.split('/').pop() || path;
  const { headers, rows } = parseCsv(content);

  const isComparative = headers.length >= 2 && rows.length > 0;

  return (
    <div className="my-3 rounded-xl border border-emerald-300/80 bg-white overflow-hidden shadow-xs">
      <div className="px-4 py-2.5 bg-gradient-to-r from-emerald-50 via-emerald-50/40 to-white border-b border-emerald-200/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-emerald-600 text-white shadow-2xs">
            <Database className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-zinc-900 font-mono">{filename}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">
                STRUCTURED DATASET ({rows.length} rows)
              </span>
            </div>
            <span className="text-[10px] text-zinc-500">Autonomous Cloud Sandbox Dataset</span>
          </div>
        </div>

        <div className="flex items-center gap-1 bg-zinc-100 p-0.5 rounded-lg border border-zinc-200 text-[11px] font-medium font-sans">
          <button
            onClick={() => setViewMode('chart')}
            className={`px-2.5 py-0.5 rounded-md transition-all cursor-pointer ${
              viewMode === 'chart' ? 'bg-white text-zinc-900 shadow-2xs font-semibold' : 'text-zinc-500 hover:text-zinc-800'
            }`}
          >
            📊 Visual Chart
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`px-2.5 py-0.5 rounded-md transition-all cursor-pointer ${
              viewMode === 'table' ? 'bg-white text-zinc-900 shadow-2xs font-semibold' : 'text-zinc-500 hover:text-zinc-800'
            }`}
          >
            📋 Data Table
          </button>
        </div>
      </div>

      <div className="p-3 bg-zinc-50/60">
        {viewMode === 'chart' && isComparative ? (
          <div className="p-4 bg-white rounded-lg border border-zinc-200 space-y-3.5">
            <div className="space-y-3">
              {rows.slice(0, 10).map((row, idx) => {
                const label = row[0];
                const vals = row.slice(1);
                return (
                  <div key={idx} className="space-y-1.5 text-xs">
                    <div className="flex items-center justify-between font-semibold text-zinc-800">
                      <span>{label}</span>
                      <span className="text-zinc-500 font-mono text-[11px]">{vals.join('  vs  ')}</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {vals.map((v, vIdx) => {
                        const headerName = headers[vIdx + 1] || `Series ${vIdx + 1}`;
                        return (
                          <div key={vIdx} className="p-2.5 rounded-md bg-zinc-50 border border-zinc-200/80 flex items-center justify-between">
                            <span className="text-[11px] font-medium text-zinc-500">{headerName}</span>
                            <span className="font-mono font-bold text-zinc-900 text-xs">{v}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-zinc-200 overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="bg-zinc-100/90 border-b border-zinc-200">
                  {headers.map((h, i) => (
                    <th key={i} className="p-2.5 font-bold text-zinc-900">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, rIdx) => (
                  <tr key={rIdx} className="border-b border-zinc-100 hover:bg-zinc-50">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="p-2.5 text-zinc-700">{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function extractFilesFromSteps(steps: Step[] = []): Record<string, string> {
  const files: Record<string, string> = {};
  for (const st of steps) {
    if (st.name === 'create_file' && st.arguments?.TargetFile && st.arguments?.Content) {
      files[st.arguments.TargetFile] = st.arguments.Content;
    } else if ((st.name === 'view_file' || st.name === 'read_file') && st.result) {
      const target = st.arguments?.AbsolutePath || st.arguments?.path || st.arguments?.TargetFile;
      if (target) {
        files[target] = st.result;
      }
    } else if (st.name === 'run_command' && st.arguments?.CommandLine) {
      const cmd = String(st.arguments.CommandLine);
      const match = cmd.match(/cat\s+<<\s*['"]?([A-Za-z0-9_]+)['"]?\s*>\s*([^\s\n]+)\s*\n([\s\S]*?)\n\1/);
      if (match && match[2] && match[3]) {
        files[match[2].trim()] = match[3];
      }
    }
  }
  return files;
}

const A2A_POD_AGENTS = [
  {
    id: "deal_lead_01",
    name: "Deal Lead Host",
    role: "M&A Orchestrator",
    badgeColor: "bg-blue-500/10 text-blue-400 border-blue-500/30",
    avatar: "👔",
    desc: "Deconstructs board thesis & delegates sub-tasks"
  },
  {
    id: "quant_worker_02",
    name: "Quant Sandbox Worker",
    role: "Heavy Compute (MicroVM)",
    badgeColor: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    avatar: "⚡",
    desc: "Executes 10,000 simulations in isolated Linux container"
  },
  {
    id: "redteam_auditor_03",
    name: "Red-Team Risk Auditor",
    role: "Model Governance (SR 11-7)",
    badgeColor: "bg-rose-500/10 text-rose-400 border-rose-500/30",
    avatar: "🛡️",
    desc: "Interrogates assumptions & flags debt covenants"
  },
  {
    id: "cro_arbitrator_04",
    name: "Chief Risk Officer",
    role: "Consensus Arbitrator",
    badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    avatar: "⚖️",
    desc: "Enforces protocol consensus & signs final memo"
  }
];

const INITIAL_A2A_MESSAGES: A2AMessage[] = [
  {
    id: "a2a-env-101",
    timestamp: "00:01.4s",
    traceId: "a2a-trace-dcf-9901",
    sender: { agentId: "deal_lead_01", name: "Deal Lead Host", role: "Orchestrator", color: "text-blue-600 bg-blue-50 border-blue-200", avatar: "👔" },
    recipient: { agentId: "quant_worker_02", name: "Quant Sandbox Worker", role: "Compute", color: "text-amber-600 bg-amber-50 border-amber-200", avatar: "⚡" },
    intent: "DELEGATE_SIMULATION",
    status: "VERIFIED",
    summary: "Dispatched initial DCF valuation task to isolated sandbox with WACC 7.5% & Growth 4.5%.",
    protocol: "A2A/JSON-RPC 2.0",
    sandboxId: "env-gcp-sandbox-84920",
    hash: "sha256:4a8b1c90ef23d81b490d1f90b9...",
    payload: {
      action: "simulate_dcf",
      target: "Project Alpha (Enterprise SaaS Target)",
      parameters: {
        iterations: 10000,
        baseline_wacc: "7.50%",
        terminal_growth: "4.50%",
        container_script: "/workspace/monte_carlo.py"
      }
    }
  },
  {
    id: "a2a-env-102",
    timestamp: "00:16.8s",
    traceId: "a2a-trace-dcf-9901",
    sender: { agentId: "quant_worker_02", name: "Quant Sandbox Worker", role: "Compute", color: "text-amber-600 bg-amber-50 border-amber-200", avatar: "⚡" },
    recipient: { agentId: "deal_lead_01", name: "Deal Lead Host", role: "Orchestrator", color: "text-blue-600 bg-blue-50 border-blue-200", avatar: "👔" },
    intent: "SIMULATION_COMPLETED",
    status: "DISPUTED",
    summary: "Completed 10k Monte Carlo iterations. Produced initial Target Valuation of $5,821.2B (VaR: $74.5B).",
    protocol: "A2A/JSON-RPC 2.0",
    sandboxId: "env-gcp-sandbox-84920",
    hash: "sha256:e7a9b0c2834d8120fa89c091ad...",
    payload: {
      valuation_mean: "$5,821.2B",
      implied_var_95: "$74.5B",
      irr_expected: "24.8%",
      recommendation: "STRONG BUY (UNHEDGED)",
      sandbox_exit_code: 0
    }
  },
  {
    id: "a2a-env-103",
    timestamp: "00:27.2s",
    traceId: "a2a-trace-dcf-9901",
    sender: { agentId: "redteam_auditor_03", name: "Red-Team Risk Auditor", role: "Model Risk", color: "text-rose-600 bg-rose-50 border-rose-200", avatar: "🛡️" },
    recipient: { agentId: "quant_worker_02", name: "Quant Sandbox Worker", role: "Compute", color: "text-amber-600 bg-amber-50 border-amber-200", avatar: "⚡" },
    intent: "CHALLENGE_ASSUMPTION",
    status: "DISPUTED",
    summary: "⚠️ FORMAL DISSENT FILED: Terminal Growth (4.5%) violates GDP bounds (2.1%). Unmodeled $820M debt covenant in Q3 2027.",
    protocol: "A2A/JSON-RPC 2.0",
    sandboxId: "env-gcp-sandbox-84920",
    hash: "sha256:91f0c439a8204bca9928174e9f...",
    payload: {
      dissent_severity: "CRITICAL_MODEL_RISK",
      violations: [
        "Terminal Growth (4.5%) exceeds long-term nominal GDP trend (2.1%)",
        "WACC (7.5%) neglects Federal Reserve higher-for-longer refinancing spreads (+125 bps)",
        "Omission of $820M revolving credit facility covenant maturity in Q3 2027"
      ],
      mandated_recalibration: {
        wacc_floor: "8.50%",
        terminal_growth_cap: "2.20%",
        synergy_haircut: "25.0%"
      }
    }
  },
  {
    id: "a2a-env-104",
    timestamp: "00:42.5s",
    traceId: "a2a-trace-dcf-9901",
    sender: { agentId: "quant_worker_02", name: "Quant Sandbox Worker", role: "Compute", color: "text-amber-600 bg-amber-50 border-amber-200", avatar: "⚡" },
    recipient: { agentId: "redteam_auditor_03", name: "Red-Team Risk Auditor", role: "Model Risk", color: "text-rose-600 bg-rose-50 border-rose-200", avatar: "🛡️" },
    intent: "RECALIBRATE_MODEL",
    status: "RECALIBRATED",
    summary: "🔄 Recalibrated simulation in sandbox: Imposed WACC 8.5%, capped Growth to 2.2%. Revised Valuation to $4,514.0B, VaR to $184.2B.",
    protocol: "A2A/JSON-RPC 2.0",
    sandboxId: "env-gcp-sandbox-84920",
    hash: "sha256:32c819a0029b4e1837f6a91b2c...",
    payload: {
      prior_valuation: "$5,821.2B",
      revised_valuation: "$4,514.0B",
      prior_var_95: "$74.5B",
      revised_var_95: "$184.2B",
      delta_valuation: "-$1,307.2B (-22.4%)",
      covenants_resolved: true
    }
  },
  {
    id: "a2a-env-105",
    timestamp: "00:54.1s",
    traceId: "a2a-trace-dcf-9901",
    sender: { agentId: "cro_arbitrator_04", name: "CRO Arbitrator", role: "Consensus", color: "text-emerald-600 bg-emerald-50 border-emerald-200", avatar: "⚖️" },
    recipient: { agentId: "all_nodes", name: "Pod Broadcast (All Agents)", role: "Broadcast", color: "text-purple-600 bg-purple-50 border-purple-200", avatar: "🌐" },
    intent: "CONSENSUS_REACHED",
    status: "SIGNED",
    summary: "✅ Cryptographic Multi-Agent Consensus Reached. Boardroom Memorandum signed. SHA-256 sealed.",
    protocol: "A2A/JSON-RPC 2.0",
    sandboxId: "env-gcp-sandbox-84920",
    hash: "sha256:7f83b2a9010481ecbb291a4410...",
    payload: {
      decision: "ACQUIRE (RISK-ADJUSTED OVERWEIGHT)",
      approved_valuation_ceiling: "$4,514.0B",
      required_downside_hedge: "$184.2B",
      governance_compliance: "SR 11-7 / SOC2 TYPE II VERIFIED",
      consensus_signature: "ECDSA_SECP256K1_SIG_0x9920194af890b14c3e"
    }
  }
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [environmentId, setEnvironmentId] = useState<string | null>(null);
  const [lastInteractionId, setLastInteractionId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});
  const [expandedThoughts, setExpandedThoughts] = useState<Record<string, boolean>>({});
  const [now, setNow] = useState<number>(Date.now());
  const [sandboxFiles, setSandboxFiles] = useState<Record<string, string>>({});
  const [activePreviewFile, setActivePreviewFile] = useState<{ path: string; content: string } | null>(null);
  const [showFileExplorer, setShowFileExplorer] = useState(false);
  const [showA2AInspector, setShowA2AInspector] = useState(false);
  const [a2aMessages, setA2aMessages] = useState<A2AMessage[]>(INITIAL_A2A_MESSAGES);
  const [selectedA2APacket, setSelectedA2APacket] = useState<A2AMessage | null>(INITIAL_A2A_MESSAGES[2]);
  const [activeA2ATab, setActiveA2ATab] = useState<'packets' | 'topology' | 'inspect'>('packets');
  const [isReplayingA2A, setIsReplayingA2A] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Live 30ms stopwatch ticker for ultra-smooth sub-second precision
  useEffect(() => {
    if (!isLoading) return;
    const interval = setInterval(() => {
      setNow(Date.now());
    }, 30);
    return () => clearInterval(interval);
  }, [isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Auto-grow textarea height dynamically with multi-line input and newlines
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(Math.max(textareaRef.current.scrollHeight, 24), 220)}px`;
    }
  }, [input]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleReplayA2A = async () => {
    setIsReplayingA2A(true);
    setA2aMessages([]);
    for (let i = 0; i < INITIAL_A2A_MESSAGES.length; i++) {
      await new Promise(r => setTimeout(r, 600));
      setA2aMessages(prev => [...prev, INITIAL_A2A_MESSAGES[i]]);
      setSelectedA2APacket(INITIAL_A2A_MESSAGES[i]);
    }
    setIsReplayingA2A(false);
  };

  const downloadFile = (filename: string, content: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename.split('/').pop() || 'file.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const fetchSandboxFile = async (filename: string, envId?: string) => {
    const targetEnv = envId || environmentId;
    if (!targetEnv) return;
    try {
      const res = await fetch('/api/fetch_file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ environment_id: targetEnv, filename })
      });
      const data = await res.json();
      if (data.content) {
        setSandboxFiles(prev => ({ ...prev, [data.filename]: data.content, [filename]: data.content }));
        return data.content;
      }
    } catch (e) {
      console.error('Error fetching file:', e);
    }
  };

  // Automatically fetch any files mentioned in agent messages that are not yet cached
  useEffect(() => {
    if (!environmentId) return;
    for (const msg of messages) {
      if (msg.sender === 'agent' && msg.text) {
        const matches = msg.text.match(/[\w\-]+\.(?:html|csv|json|png|svg|py|md|txt)/g);
        if (matches) {
          for (const fname of matches) {
            if (!sandboxFiles[fname] && !sandboxFiles[`/workspace/${fname}`]) {
              fetchSandboxFile(fname, msg.environmentId || environmentId);
            }
          }
        }
      }
    }
  }, [messages, environmentId, sandboxFiles]);

  const toggleStepExpand = (msgId: string) => {
    setExpandedSteps(prev => ({
      ...prev,
      [msgId]: prev[msgId] === undefined ? false : !prev[msgId]
    }));
  };

  const toggleThoughtExpand = (msgId: string) => {
    setExpandedThoughts(prev => ({
      ...prev,
      [msgId]: prev[msgId] === undefined ? false : !prev[msgId]
    }));
  };

  const handleResetSession = () => {
    if (confirm("Reset current sandbox environment? The next turn will provision a fresh remote sandbox.")) {
      setEnvironmentId(null);
      setLastInteractionId(null);
      setMessages([]);
      setSandboxFiles({});
      setActivePreviewFile(null);
    }
  };

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsgId = `user-${Date.now()}`;
    const agentMsgId = `agent-${Date.now()}`;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const startMs = Date.now();

    const userMsg: Message = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: timeStr,
    };

    const agentMsg: Message = {
      id: agentMsgId,
      sender: 'agent',
      text: '',
      timestamp: timeStr,
      startTimestamp: startMs,
      status: 'submitting',
      steps: [],
    };

    setMessages(prev => [...prev, userMsg, agentMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          environment_id: environmentId || undefined,
          previous_interaction_id: lastInteractionId || undefined,
        }),
      });

      if (!response.body) {
        throw new Error("No response body received from server.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentEvent = 'message';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.replace('event:', '').trim();
          } else if (line.startsWith('data:')) {
            const dataStr = line.replace('data:', '').trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              setMessages(prev =>
                prev.map(m => {
                  if (m.id !== agentMsgId) return m;

                  if (currentEvent === 'init') {
                    if (data.environment_id) setEnvironmentId(data.environment_id);
                    if (data.interaction_id) setLastInteractionId(data.interaction_id);
                    return {
                      ...m,
                      status: 'in_progress',
                      interactionId: data.interaction_id,
                      environmentId: data.environment_id,
                    };
                  } else if (currentEvent === 'status') {
                    return {
                      ...m,
                      status: 'in_progress',
                    };
                  } else if (currentEvent === 'token') {
                    // Live token-by-token streaming
                    return {
                      ...m,
                      text: (m.text || '') + (data.text || ''),
                      status: 'in_progress',
                    };
                  } else if (currentEvent === 'thought') {
                    // Live thought-by-thought streaming
                    return {
                      ...m,
                      thoughtText: (m.thoughtText || '') + (data.thought || ''),
                      status: 'in_progress',
                    };
                  } else if (currentEvent === 'step') {
                    const existingSteps = m.steps || [];
                    const lastStep = existingSteps[existingSteps.length - 1];
                    let updatedSteps: Step[];

                    // Merge deltas if updating active step
                    if (lastStep && lastStep.name === data.name && (!lastStep.result || !lastStep.arguments) && (data.result || data.arguments)) {
                      updatedSteps = [
                        ...existingSteps.slice(0, -1),
                        { ...lastStep, ...data }
                      ];
                    } else {
                      updatedSteps = [...existingSteps, data];
                    }

                    // Extract created file on the fly
                    if (data.name === 'create_file' && data.arguments?.TargetFile && data.arguments?.Content) {
                      setSandboxFiles(prevFiles => ({
                        ...prevFiles,
                        [data.arguments.TargetFile]: data.arguments.Content
                      }));
                    }
                    return {
                      ...m,
                      steps: updatedSteps,
                    };
                  } else if (currentEvent === 'done') {
                    if (data.environment_id) setEnvironmentId(data.environment_id);
                    if (data.interaction_id) setLastInteractionId(data.interaction_id);
                    if (data.files) {
                      setSandboxFiles(prevFiles => ({ ...prevFiles, ...data.files }));
                    }
                    return {
                      ...m,
                      status: 'completed',
                      text: data.output_text || m.text,
                      elapsed: data.elapsed,
                      usage: data.usage,
                      files: data.files,
                      interactionId: data.interaction_id,
                      environmentId: data.environment_id,
                    };
                  } else if (currentEvent === 'error') {
                    return {
                      ...m,
                      status: 'error',
                      error: data.error || 'Unknown error occurred',
                    };
                  }
                  return m;
                })
              );
            } catch (e) {
              console.error("Failed to parse SSE line:", line, e);
            }
          }
        }
      }

      // Guarantee completed state after stream closes
      setMessages(prev =>
        prev.map(m => (m.id === agentMsgId && m.status === 'in_progress' ? { ...m, status: 'completed' } : m))
      );
    } catch (err: any) {
      setMessages(prev =>
        prev.map(m => (m.id === agentMsgId ? { ...m, status: 'error', error: err.message } : m))
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getDisplayTime = (msg: Message) => {
    if (msg.status === 'completed' && msg.elapsed !== undefined) {
      return `${msg.elapsed.toFixed(1)}s`;
    }
    if ((msg.status === 'in_progress' || msg.status === 'submitting') && msg.startTimestamp) {
      const elapsedSec = (now - msg.startTimestamp) / 1000;
      return `${elapsedSec.toFixed(1)}s`;
    }
    return null;
  };

  // Strict deduplication of sandbox files by base filename
  const deduplicatedSandboxFiles: Record<string, string> = {};
  for (const [key, content] of Object.entries(sandboxFiles)) {
    const baseName = key.split('/').pop() || key;
    const existingKey = Object.keys(deduplicatedSandboxFiles).find(k => (k.split('/').pop() || k) === baseName);
    if (!existingKey) {
      deduplicatedSandboxFiles[key] = content;
    }
  }
  const fileKeys = Object.keys(deduplicatedSandboxFiles);

  return (
    <div className="flex h-screen bg-[#fafafa] text-zinc-900 antialiased font-sans overflow-hidden">
      {/* Main Chat View */}
      <div className="flex flex-col flex-1 h-screen overflow-hidden">
        {/* Clean Executive Header */}
        <header className="h-14 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-20">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-zinc-950 text-white flex items-center justify-center shadow-xs">
              <Sparkles className="w-3.5 h-3.5 text-zinc-100" />
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold tracking-tight text-zinc-900 text-sm">Antigravity Console</span>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-zinc-100 text-zinc-600 border border-zinc-200">
                antigravity-preview-05-2026
              </span>
            </div>
          </div>

          {/* Sandbox Status, File Explorer Trigger & Controls */}
          <div className="flex items-center gap-2.5">
            {environmentId ? (
              <div className="flex items-center gap-2 bg-emerald-50/90 border border-emerald-200 px-2.5 py-1 rounded-md text-xs font-mono">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-emerald-800 font-medium truncate max-w-[140px] md:max-w-[200px]">
                  {environmentId}
                </span>
                <button
                  onClick={() => copyToClipboard(environmentId, 'env-badge')}
                  className="p-0.5 hover:bg-emerald-100 rounded text-emerald-600 transition-colors cursor-pointer"
                  title="Copy Sandbox ID"
                >
                  {copiedId === 'env-badge' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            ) : (
              <div className="hidden sm:flex items-center gap-1.5 bg-zinc-100 border border-zinc-200/60 px-2.5 py-1 rounded-md text-zinc-500 text-xs font-mono">
                <Cpu className="w-3.5 h-3.5 text-zinc-400" />
                <span>Sandbox Standby</span>
              </div>
            )}

            {/* A2A Wire-Tap Forensic Inspector Button */}
            <button
              onClick={() => setShowA2AInspector(!showA2AInspector)}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold border rounded-md transition-all cursor-pointer shadow-xs bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100"
              title="Inspect Live Agent-to-Agent (A2A) Forensic Protocol Wire-Tap"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-600"></span>
              </span>
              <Share2 className="w-3.5 h-3.5" />
              <span>A2A Wire-Tap ({a2aMessages.length})</span>
            </button>

            {/* Sandbox Files Explorer Button */}
            <button
              onClick={() => setShowFileExplorer(!showFileExplorer)}
              className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium border rounded-md transition-all cursor-pointer shadow-xs ${
                fileKeys.length > 0
                  ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 font-semibold'
                  : 'bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-100'
              }`}
              title="View files generated in /workspace"
            >
              <FolderOpen className="w-3.5 h-3.5" />
              <span>Sandbox Disk ({fileKeys.length})</span>
            </button>

            <button
              onClick={handleResetSession}
              disabled={isLoading || (!environmentId && messages.length === 0)}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-zinc-600 hover:text-zinc-900 bg-white hover:bg-zinc-100 border border-zinc-200 rounded-md transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-xs cursor-pointer"
              title="Reset sandbox"
            >
              <RotateCcw className="w-3 h-3" />
              <span className="hidden sm:inline">Reset</span>
            </button>
          </div>
        </header>

        {/* Main Conversation Stream */}
        <main className="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-6 max-w-4xl w-full mx-auto">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col justify-center items-center text-center py-16 px-4 max-w-3xl mx-auto space-y-8">
              <div className="space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 border border-zinc-200 text-xs font-medium text-zinc-700 mb-2 font-mono">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  Google Cloud Vertex AI Managed Agents
                </div>
                <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-zinc-950">
                  Autonomous Cloud Sandbox
                </h2>
                <p className="text-sm text-zinc-500 leading-relaxed max-w-xl mx-auto">
                  Execute live web research, perform heavy mathematical compute, generate data pipelines, and render board-ready artifacts inside an isolated, stateful Linux container.
                </p>
              </div>

              {/* Executive EBC Starter Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 w-full text-left">
                {EBC_DEMO_TRACKS.map((card, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(card.prompt)}
                    className="group p-4 rounded-xl bg-white hover:bg-zinc-50 border border-zinc-200 hover:border-zinc-300 transition-all text-left shadow-xs flex flex-col justify-between cursor-pointer space-y-2"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-600 font-semibold border border-zinc-200">
                          {card.tag}
                        </span>
                        <Sparkles className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-800 transition-colors" />
                      </div>
                      <h3 className="text-xs font-semibold text-zinc-900 group-hover:text-black">
                        {card.title}
                      </h3>
                      <p className="text-[12px] text-zinc-500 mt-1 leading-relaxed">{card.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map(msg => {
              const displayTime = getDisplayTime(msg);
              const toolSteps = (msg.steps || []).filter(
                s => s.type && !s.type.includes('model_output') && !s.type.includes('user_input')
              );

              // Detect created files in this turn and match with cached sandbox files
              const textMentionedFiles: Record<string, string> = {};
              if (msg.text) {
                const matches = msg.text.match(/[\w\-]+\.(?:html|csv|json|png|svg|py|md|txt)/g);
                if (matches) {
                  for (const f of matches) {
                    if (sandboxFiles[f]) {
                      textMentionedFiles[f] = sandboxFiles[f];
                    } else if (sandboxFiles[`/workspace/${f}`]) {
                      textMentionedFiles[f] = sandboxFiles[`/workspace/${f}`];
                    }
                  }
                }
              }

              const rawTurnFiles: Record<string, string> = {
                ...textMentionedFiles,
                ...(msg.files || {}),
                ...extractFilesFromSteps(msg.steps || [])
              };

              // Strict deduplication by base filename to prevent duplicate frames/badges
              const turnFiles: Record<string, string> = {};
              for (const [key, content] of Object.entries(rawTurnFiles)) {
                const baseName = key.split('/').pop() || key;
                const existingKey = Object.keys(turnFiles).find(k => (k.split('/').pop() || k) === baseName);
                if (!existingKey) {
                  turnFiles[key] = content;
                }
              }

              // Parse thinking/planning vs final consolidated answer
              const { thoughts, finalAnswer } = parseThinkingAndAnswer(msg.text || '', msg.thoughtText);

              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'} space-y-1.5 w-full`}
                >
                  {/* Message Bubble Card */}
                  <div
                    className={`max-w-[95%] md:max-w-[90%] rounded-2xl p-5 space-y-4 overflow-hidden break-words transition-all ${
                      msg.sender === 'user'
                        ? 'bg-zinc-900 text-white shadow-xs'
                        : 'bg-white border border-zinc-200 shadow-xs text-zinc-800 w-full'
                    }`}
                  >
                    {/* Agent Bubble Header */}
                    {msg.sender === 'agent' && (
                      <div className="flex items-center justify-between border-b border-zinc-100 pb-2.5 text-xs text-zinc-400">
                        <div className="flex items-center gap-2 font-mono text-[11px]">
                          <span className="font-semibold text-zinc-800">Antigravity Agent</span>

                          {msg.status === 'in_progress' && (
                            <span className="flex items-center gap-1.5 text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200/80">
                              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                              Running in Cloud Sandbox...
                            </span>
                          )}
                          {msg.status === 'completed' && (
                            <span className="flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200/80 font-medium">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              Done
                            </span>
                          )}
                          {msg.status === 'error' && (
                            <span className="flex items-center gap-1 text-rose-700 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200">
                              <AlertCircle className="w-3 h-3 text-rose-600" />
                              Failed
                            </span>
                          )}
                        </div>

                        {/* Live Stopwatch Timer */}
                        {displayTime && (
                          <span className="flex items-center gap-1 font-mono text-[11px] text-zinc-500 bg-zinc-50 border border-zinc-200 px-2 py-0.5 rounded-md">
                            <Clock className="w-3 h-3 text-zinc-400" />
                            <span className="tabular-nums font-semibold">{displayTime}</span>
                          </span>
                        )}
                      </div>
                    )}

                    {/* User Content */}
                    {msg.sender === 'user' ? (
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.text}</p>
                    ) : (
                      <div className="space-y-4">
                        {/* 1. DYNAMIC THINKING & REASONING FLOW (Collapsible / Expandable) */}
                        {thoughts.length > 0 && (
                          <div className="rounded-xl border border-purple-200/80 bg-gradient-to-br from-purple-50/50 via-indigo-50/30 to-white overflow-hidden shadow-2xs">
                            <button
                              onClick={() => toggleThoughtExpand(msg.id)}
                              className="w-full px-3.5 py-2.5 flex items-center justify-between bg-purple-100/60 hover:bg-purple-100/90 transition-colors text-purple-900 font-mono text-[11px] cursor-pointer"
                            >
                              <div className="flex items-center gap-2">
                                <div className="p-1 rounded-md bg-purple-600 text-white shadow-2xs">
                                  <Brain className="w-3.5 h-3.5 animate-pulse" />
                                </div>
                                <span className="font-bold text-purple-950">
                                  Proceso de Razonamiento Agéntico ({thoughts.length} pasos cognitivos secuenciados)
                                </span>
                                {msg.status === 'in_progress' && (
                                  <span className="px-2 py-0.5 rounded-full bg-purple-200 text-purple-800 text-[10px] font-bold animate-pulse flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-purple-600 animate-ping"></span>
                                    Pensando en vivo...
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center gap-1 text-purple-700 font-sans text-xs">
                                <span className="text-[11px] font-medium">
                                  {expandedThoughts[msg.id] !== false ? 'Ocultar' : 'Ver Pasos'}
                                </span>
                                {expandedThoughts[msg.id] !== false ? (
                                  <ChevronDown className="w-3.5 h-3.5" />
                                ) : (
                                  <ChevronRight className="w-3.5 h-3.5" />
                                )}
                              </div>
                            </button>

                            {expandedThoughts[msg.id] !== false && (
                              <div className="p-3.5 space-y-2.5 border-t border-purple-200/60 font-sans">
                                {thoughts.map((th, thIdx) => {
                                  const isLatest = thIdx === thoughts.length - 1 && msg.status === 'in_progress';
                                  return (
                                    <div
                                      key={thIdx}
                                      className={`flex items-start gap-3 p-2.5 rounded-xl transition-all duration-200 ${
                                        isLatest
                                          ? 'bg-purple-100/70 border border-purple-300 shadow-xs ring-1 ring-purple-400/40'
                                          : 'bg-white/90 border border-purple-100/90 shadow-2xs hover:border-purple-200'
                                      }`}
                                    >
                                      {/* Animated Step Badge */}
                                      <div className="flex flex-col items-center shrink-0">
                                        <span
                                          className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 ${
                                            isLatest
                                              ? 'bg-purple-700 text-white shadow-2xs animate-pulse'
                                              : 'bg-purple-100 text-purple-900 border border-purple-200/60'
                                          }`}
                                        >
                                          Step {(thIdx + 1).toString().padStart(2, '0')}
                                        </span>
                                      </div>

                                      {/* Thought Text */}
                                      <div className="flex-1 min-w-0">
                                        <p className="text-zinc-800 leading-relaxed text-[12px] font-normal">
                                          {th}
                                        </p>
                                      </div>

                                      {/* Status icon */}
                                      <div className="shrink-0 pt-0.5">
                                        {isLatest ? (
                                          <div className="w-2 h-2 rounded-full bg-purple-600 animate-ping" />
                                        ) : (
                                          <Check className="w-3.5 h-3.5 text-purple-400" />
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            )}
                          </div>
                        )}

                        {/* 2. VERIFIED SANDBOX OPERATIONS (Tool calls like bash, view_file, etc.) */}
                        {toolSteps.length > 0 && (
                          <div className="rounded-xl border border-zinc-200 bg-zinc-50/70 overflow-hidden text-xs">
                            <button
                              onClick={() => toggleStepExpand(msg.id)}
                              className="w-full px-3.5 py-2.5 flex items-center justify-between bg-zinc-100/80 hover:bg-zinc-100 transition-colors text-zinc-700 font-mono text-[11px] cursor-pointer"
                            >
                              <div className="flex items-center gap-2">
                                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                                <span className="font-semibold text-zinc-800">
                                  Operaciones de Ejecución en Sandbox ({toolSteps.length} acciones)
                                </span>
                              </div>
                              {expandedSteps[msg.id] !== false ? (
                                <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
                              ) : (
                                <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
                              )}
                            </button>

                            {expandedSteps[msg.id] !== false && (
                              <div className="p-3 space-y-2.5 max-h-72 overflow-y-auto border-t border-zinc-200 font-mono text-[11px]">
                                {toolSteps.map((st, idx) => (
                                  <div key={idx} className="p-2.5 rounded-lg bg-white border border-zinc-200 space-y-1.5 shadow-2xs">
                                    <div className="flex items-center justify-between text-zinc-500">
                                      <span className="font-semibold text-zinc-900 flex items-center gap-1.5">
                                        {st.name === 'google_search' && <Search className="w-3.5 h-3.5 text-blue-600" />}
                                        {st.name === 'url_context' && <Globe className="w-3.5 h-3.5 text-teal-600" />}
                                        {st.name === 'provision_sandbox' && <Cpu className="w-3.5 h-3.5 text-sky-600" />}
                                        {st.name === 'create_file' && <FileCode className="w-3.5 h-3.5 text-amber-600" />}
                                        {st.name === 'run_command' && <Terminal className="w-3.5 h-3.5 text-emerald-600" />}
                                        {st.name === 'view_file' && <FolderOpen className="w-3.5 h-3.5 text-indigo-600" />}
                                        {st.name === 'list_dir' && <FolderOpen className="w-3.5 h-3.5 text-indigo-600" />}
                                        <span>
                                          {st.name === 'google_search' ? 'google_search (Live Web Query)' :
                                           st.name === 'url_context' ? 'url_context (Web Scrape)' :
                                           st.name === 'create_file' ? 'create_file (Disk Write)' :
                                           st.name === 'run_command' ? 'run_command (Execution)' :
                                           st.name === 'view_file' ? 'view_file (Disk Read)' :
                                           st.name === 'list_dir' ? 'list_dir (Inspect Workspace)' :
                                           st.name || st.type}
                                        </span>
                                      </span>
                                      <span className="text-[10px] text-zinc-400">action #{idx + 1}</span>
                                    </div>

                                    {st.arguments && (
                                      <div className="text-zinc-800 text-[11px] bg-zinc-50 p-2 rounded-md border border-zinc-200 overflow-x-auto">
                                        {st.name === 'run_command' ? (
                                          <div>
                                            <span className="text-zinc-500 text-[10px] block">Command Executed:</span>
                                            <code className="text-emerald-700 font-bold">$ {st.arguments.CommandLine}</code>
                                          </div>
                                        ) : st.name === 'list_dir' ? (
                                          <div>
                                            <span className="text-zinc-500 text-[10px] block">Ruta Inspeccionada:</span>
                                            <code className="text-indigo-700 font-bold font-mono">{st.arguments?.DirectoryPath || st.arguments?.path || '/workspace (Directorio Raíz)'}</code>
                                          </div>
                                        ) : st.name === 'create_file' ? (
                                          <div className="space-y-1">
                                            <div className="flex items-center justify-between">
                                              <span className="text-amber-800 font-semibold">Saved to: {st.arguments.TargetFile}</span>
                                              {st.arguments.Content && (
                                                <button
                                                  onClick={() => setActivePreviewFile({ path: st.arguments.TargetFile, content: st.arguments.Content })}
                                                  className="text-[10px] text-blue-600 hover:underline flex items-center gap-1 cursor-pointer font-sans"
                                                >
                                                  <Eye className="w-3 h-3" />
                                                  <span>Preview Artifact</span>
                                                </button>
                                              )}
                                            </div>
                                            {st.arguments.Content && (
                                              <pre className="max-h-24 overflow-y-auto text-[10px] text-zinc-600 bg-white p-1.5 rounded border border-zinc-200 font-mono">
                                                {st.arguments.Content}
                                              </pre>
                                            )}
                                          </div>
                                        ) : st.name === 'google_search' ? (
                                          <div>
                                            <span className="text-blue-700 font-semibold">Search Queries:</span>
                                            <pre className="text-zinc-700 font-mono mt-0.5">{JSON.stringify(st.arguments, null, 2)}</pre>
                                          </div>
                                        ) : (
                                          <pre className="text-zinc-600 font-mono">{JSON.stringify(st.arguments, null, 2)}</pre>
                                        )}
                                      </div>
                                    )}

                                    {st.result !== undefined && (
                                      <div className="text-[10px] text-zinc-700 bg-zinc-100/80 p-2 rounded-md max-h-24 overflow-y-auto border-l-2 border-emerald-500">
                                        <span className="text-zinc-500 block mb-0.5 font-sans font-medium">Resultado:</span>
                                        <pre className="whitespace-pre-wrap font-mono">
                                          {st.name === 'list_dir' && (!st.result || st.result === '[]' || st.result === '{}' || st.result.trim() === '')
                                            ? '[ Directorio /workspace limpio y vacío (0 archivos previos) ]'
                                            : st.result}
                                        </pre>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {/* 3. DIRECT INLINE EXECUTIVE ARTIFACTS (Only when created during this turn) */}
                        {Object.entries(turnFiles).map(([filePath, content]) => {
                          if (filePath.endsWith('.html')) {
                            return (
                              <ExecutiveHtmlFrame
                                key={filePath}
                                path={filePath}
                                content={content}
                                onExpand={() => setActivePreviewFile({ path: filePath, content })}
                              />
                            );
                          } else if (filePath.endsWith('.csv')) {
                            return (
                              <ExecutiveCsvVisualizer
                                key={filePath}
                                path={filePath}
                                content={content}
                              />
                            );
                          }
                          return null;
                        })}

                        {/* 4. ARTIFACT BADGES (Only for files generated in this turn) */}
                        {Object.keys(turnFiles).length > 0 && (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 my-2">
                            {Object.entries(turnFiles).map(([filePath, content]) => {
                              const isHtml = filePath.endsWith('.html');
                              const isCsv = filePath.endsWith('.csv');
                              const isSvg = filePath.endsWith('.svg');
                              const filename = filePath.split('/').pop() || filePath;

                              return (
                                <div
                                  key={filePath}
                                  className="flex items-center justify-between p-3 rounded-xl bg-zinc-50 border border-zinc-200 hover:border-zinc-300 transition-all shadow-2xs"
                                >
                                  <div className="flex items-center gap-2.5 overflow-hidden">
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                                      isHtml ? 'bg-amber-100 text-amber-700' :
                                      isCsv ? 'bg-emerald-100 text-emerald-700' :
                                      isSvg ? 'bg-indigo-100 text-indigo-700' : 'bg-zinc-200 text-zinc-700'
                                    }`}>
                                      {isHtml ? <BarChart3 className="w-4 h-4" /> :
                                       isCsv ? <Database className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                                    </div>
                                    <div className="overflow-hidden font-mono">
                                      <span className="text-xs font-semibold text-zinc-900 block truncate">{filename}</span>
                                      <span className="text-[10px] text-zinc-400 font-sans">{content.length} bytes · Generado en Sandbox</span>
                                    </div>
                                  </div>

                                  <div className="flex items-center gap-1 shrink-0">
                                    <button
                                      onClick={() => setActivePreviewFile({ path: filePath, content })}
                                      className="p-1.5 hover:bg-white rounded-md text-zinc-600 hover:text-zinc-900 transition-colors border border-transparent hover:border-zinc-200 cursor-pointer"
                                      title="Open Interactive Preview"
                                    >
                                      <Eye className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                      onClick={() => downloadFile(filename, content)}
                                      className="p-1.5 hover:bg-white rounded-md text-zinc-600 hover:text-zinc-900 transition-colors border border-transparent hover:border-zinc-200 cursor-pointer"
                                      title="Download File"
                                    >
                                      <Download className="w-3.5 h-3.5" />
                                    </button>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {/* 5. CONSOLIDATED FINAL SYNTHESIS / ANSWER */}
                        {finalAnswer ? (
                          <div className="text-zinc-800 leading-relaxed text-[14px] pt-1">
                            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-zinc-100">
                              <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-zinc-900 text-white flex items-center gap-1">
                                <Sparkles className="w-3 h-3 text-amber-300" />
                                Respuesta Ejecutiva Consolidada
                              </span>
                            </div>
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                code({ node, className, children, ...props }: any) {
                                  const match = /language-(\w+)/.exec(className || '');
                                  const isBlock = String(children).includes('\n') || !!match;
                                  const codeStr = String(children).replace(/\n$/, '');

                                  if (isBlock) {
                                    return (
                                      <div className="relative my-3 rounded-xl overflow-hidden border border-zinc-200 bg-zinc-950 text-zinc-100 shadow-2xs">
                                        <div className="flex items-center justify-between px-3.5 py-1.5 bg-zinc-900 border-b border-zinc-800 text-xs text-zinc-400 font-mono">
                                          <span className="text-[11px] text-zinc-300 font-medium">{match ? match[1] : 'code'}</span>
                                          <button
                                            onClick={() => copyToClipboard(codeStr, codeStr.slice(0, 15))}
                                            className="flex items-center gap-1 hover:text-white transition-colors cursor-pointer"
                                          >
                                            {copiedId === codeStr.slice(0, 15) ? (
                                              <>
                                                <Check className="w-3 h-3 text-emerald-400" />
                                                <span className="text-emerald-400 text-[11px]">Copied</span>
                                              </>
                                            ) : (
                                              <>
                                                <Copy className="w-3 h-3" />
                                                <span className="text-[11px]">Copy</span>
                                              </>
                                            )}
                                          </button>
                                        </div>
                                        <pre className="p-3.5 overflow-x-auto text-xs font-mono leading-relaxed bg-zinc-950 text-zinc-100">
                                          <code {...props}>{children}</code>
                                        </pre>
                                      </div>
                                    );
                                  }

                                  return (
                                    <code className="px-1.5 py-0.5 mx-0.5 rounded-md bg-zinc-100 text-zinc-800 font-mono text-[12px] font-medium border border-zinc-200/80" {...props}>
                                      {children}
                                    </code>
                                  );
                                },
                                table({ children }) {
                                  return (
                                    <div className="my-3 overflow-x-auto rounded-xl border border-zinc-200 shadow-2xs">
                                      <table className="w-full text-left text-xs border-collapse">{children}</table>
                                    </div>
                                  );
                                },
                                th({ children }) {
                                  return <th className="border-b border-zinc-200 bg-zinc-50 px-3.5 py-2 font-semibold text-zinc-900">{children}</th>;
                                },
                                td({ children }) {
                                  return <td className="border-b border-zinc-100 px-3.5 py-2 text-zinc-700">{children}</td>;
                                },
                                p({ children }) {
                                  return <p className="mb-2.5 last:mb-0 leading-relaxed">{children}</p>;
                                },
                                ul({ children }) {
                                  return <ul className="list-disc pl-5 my-2 space-y-1 text-zinc-700">{children}</ul>;
                                },
                                ol({ children }) {
                                  return <ol className="list-decimal pl-5 my-2 space-y-1 text-zinc-700">{children}</ol>;
                                },
                                h1({ children }) {
                                  return <h1 className="text-base font-bold text-zinc-950 mt-3 mb-1.5">{children}</h1>;
                                },
                                h2({ children }) {
                                  return <h2 className="text-sm font-semibold text-zinc-950 mt-2.5 mb-1">{children}</h2>;
                                },
                                h3({ children }) {
                                  return <h3 className="text-xs font-semibold text-zinc-900 mt-2 mb-0.5 uppercase tracking-wider">{children}</h3>;
                                }
                              }}
                            >
                              {finalAnswer}
                            </ReactMarkdown>
                          </div>
                        ) : msg.status === 'in_progress' ? (
                          <div className="rounded-xl border border-amber-200/80 bg-gradient-to-br from-amber-50/40 via-white to-zinc-50/60 p-4 space-y-3 shadow-2xs">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2.5">
                                <div className="relative flex h-2.5 w-2.5">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
                                </div>
                                <span className="font-semibold text-xs text-zinc-900 font-mono">
                                  Pipeline de Ejecución Agéntica en Vivo
                                </span>
                              </div>
                              <span className="text-[11px] font-mono text-zinc-500 bg-white border border-zinc-200 px-2 py-0.5 rounded-md">
                                {displayTime || '0.0s'}
                              </span>
                            </div>

                            {/* Dynamic Step Pipeline Status */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px] font-mono pt-1">
                              <div className="p-2 rounded-lg bg-white border border-zinc-200 flex items-center gap-2 shadow-2xs">
                                <Cpu className="w-3.5 h-3.5 text-sky-600 shrink-0" />
                                <div className="min-w-0">
                                  <div className="text-[10px] text-zinc-400 font-bold uppercase">Entorno</div>
                                  <div className="text-zinc-800 truncate font-semibold">Linux MicroVM Activo</div>
                                </div>
                              </div>
                              <div className="p-2 rounded-lg bg-white border border-zinc-200 flex items-center gap-2 shadow-2xs">
                                <Search className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                                <div className="min-w-0">
                                  <div className="text-[10px] text-zinc-400 font-bold uppercase">Grounding</div>
                                  <div className="text-zinc-800 truncate font-semibold">Google Search Engine</div>
                                </div>
                              </div>
                              <div className="p-2 rounded-lg bg-white border border-zinc-200 flex items-center gap-2 shadow-2xs">
                                <Terminal className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                                <div className="min-w-0">
                                  <div className="text-[10px] text-zinc-400 font-bold uppercase">Sandbox Compute</div>
                                  <div className="text-zinc-800 truncate font-semibold">
                                    {toolSteps.length > 0 ? `${toolSteps.length} acción(es) ejecutadas` : 'Invocando Operaciones...'}
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center gap-2 text-xs text-zinc-600 font-sans pt-0.5">
                              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                              <span>
                                {toolSteps.length > 0
                                  ? `Ejecutando ${toolSteps[toolSteps.length - 1].name || 'operación'} en /workspace y compilando artefactos...`
                                  : 'Conectando herramientas nativas y extrayendo datos en tiempo real...'}
                              </span>
                            </div>
                          </div>
                        ) : null}

                        {/* Error Box */}
                        {msg.error && (
                          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs font-mono space-y-1">
                            <div className="font-semibold flex items-center gap-1.5 text-rose-900">
                              <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                              Interaction Error
                            </div>
                            <p className="whitespace-pre-wrap">{msg.error}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Floating Minimalist Input Bar */}
        <footer className="p-4 md:p-5 bg-white/80 border-t border-zinc-200/80 backdrop-blur-md shrink-0">
          <div className="max-w-4xl mx-auto flex items-center gap-2.5">
            <div className="flex-1 bg-white rounded-xl border border-zinc-300 focus-within:border-zinc-800 focus-within:ring-1 focus-within:ring-zinc-800 transition-all px-3.5 py-2.5 shadow-xs flex items-center">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  environmentId
                    ? "Instruct agent inside active sandbox (e.g. 'Generate interactive risk_dashboard.html')..."
                    : "Type an instruction (e.g. 'Create a python script to analyze Google, Amazon and Microsoft stocks and generate interactive HTML chart')..."
                }
                rows={1}
                disabled={isLoading}
                className="w-full bg-transparent border-0 resize-none text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none max-h-56 min-h-[24px] overflow-y-auto leading-relaxed block"
              />
            </div>

            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="h-10 w-10 rounded-xl bg-zinc-900 hover:bg-black text-white flex items-center justify-center shadow-xs disabled:opacity-30 disabled:cursor-not-allowed transition-all shrink-0 cursor-pointer"
            >
              {isLoading ? (
                <RotateCcw className="w-4 h-4 animate-spin text-zinc-300" />
              ) : (
                <ArrowUp className="w-4.5 h-4.5" />
              )}
            </button>
          </div>
          <div className="max-w-4xl mx-auto mt-2 flex items-center justify-between text-[11px] text-zinc-400 px-1">
            <span>Enter to send · Shift+Enter for newline</span>
            <span className="font-mono">Project: vtxdemos · Live Sandbox Compute</span>
          </div>
        </footer>
      </div>

      {/* Right-Side Live Sandbox File Explorer Drawer */}
      {showFileExplorer && (
        <aside className="w-80 border-l border-zinc-200 bg-white flex flex-col h-screen shrink-0 shadow-lg z-30 transition-all">
          <div className="p-4 border-b border-zinc-200 flex items-center justify-between bg-zinc-50/70">
            <div className="flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-semibold text-zinc-900 font-mono">/workspace Files ({fileKeys.length})</span>
            </div>
            <button
              onClick={() => setShowFileExplorer(false)}
              className="p-1 hover:bg-zinc-200 rounded text-zinc-500 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="p-3 border-b border-zinc-200 bg-zinc-50/50 space-y-2">
            <div className="text-[11px] font-medium text-zinc-600">Fetch / Sync File from Sandbox:</div>
            <div className="flex items-center gap-1.5">
              <input
                id="sandbox-fetch-input"
                type="text"
                placeholder="e.g. stock_dashboard.html"
                className="flex-1 px-2.5 py-1.5 text-xs font-mono border border-zinc-200 rounded-lg bg-white focus:outline-none focus:border-blue-500"
                defaultValue="stock_dashboard.html"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const val = (e.target as HTMLInputElement).value.trim();
                    if (val) fetchSandboxFile(val);
                  }
                }}
              />
              <button
                onClick={() => {
                  const inputEl = document.getElementById('sandbox-fetch-input') as HTMLInputElement;
                  if (inputEl && inputEl.value.trim()) {
                    fetchSandboxFile(inputEl.value.trim());
                  }
                }}
                className="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium cursor-pointer shadow-2xs"
              >
                Sync
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {fileKeys.length === 0 ? (
              <div className="text-center py-12 text-zinc-400 text-xs font-sans">
                <Cpu className="w-8 h-8 mx-auto mb-2 text-zinc-300 stroke-[1.5]" />
                <p>No files generated yet.</p>
                <p className="text-[11px] text-zinc-400 mt-1">Files created in /workspace will appear here live.</p>
              </div>
            ) : (
              fileKeys.map(filePath => {
                const filename = filePath.split('/').pop() || filePath;
                const content = sandboxFiles[filePath];
                const isHtml = filename.endsWith('.html');
                const isCsv = filename.endsWith('.csv');

                return (
                  <div
                    key={filePath}
                    className="p-3 rounded-xl bg-zinc-50 hover:bg-zinc-100/80 border border-zinc-200 transition-all text-xs font-mono space-y-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="overflow-hidden">
                        <span className="font-semibold text-zinc-900 block truncate text-xs">{filename}</span>
                        <span className="text-[10px] text-zinc-400 block truncate font-sans">{filePath}</span>
                      </div>
                      <span className={`text-[9px] uppercase px-1.5 py-0.5 rounded font-bold ${
                        isHtml ? 'bg-amber-100 text-amber-800' :
                        isCsv ? 'bg-emerald-100 text-emerald-800' : 'bg-zinc-200 text-zinc-700'
                      }`}>
                        {filename.split('.').pop()}
                      </span>
                    </div>

                    <div className="flex items-center justify-between pt-1 border-t border-zinc-200/60 font-sans">
                      <span className="text-[10px] text-zinc-400">{content.length} bytes</span>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => setActivePreviewFile({ path: filePath, content })}
                          className="px-2 py-0.5 rounded bg-white hover:bg-zinc-200 text-zinc-700 border border-zinc-200 text-[11px] flex items-center gap-1 cursor-pointer"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </button>
                        <button
                          onClick={() => downloadFile(filename, content)}
                          className="p-1 hover:bg-zinc-200 rounded text-zinc-600 cursor-pointer"
                          title="Download"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>
      )}

      {/* Interactive Live Artifact Modal / Viewer */}
      {activePreviewFile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 md:p-8 z-50 animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl border border-zinc-200 shadow-2xl w-full max-w-4xl max-h-[88vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-5 py-3.5 border-b border-zinc-200 flex items-center justify-between bg-zinc-50">
              <div className="flex items-center gap-2.5 font-mono">
                <div className="w-6 h-6 rounded-md bg-zinc-900 text-white flex items-center justify-center text-xs">
                  <BarChart3 className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-zinc-900">{activePreviewFile.path.split('/').pop()}</h3>
                  <span className="text-[10px] text-zinc-400 font-sans">Live Cloud Sandbox Artifact</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => downloadFile(activePreviewFile.path, activePreviewFile.content)}
                  className="px-2.5 py-1 rounded-md bg-white hover:bg-zinc-100 border border-zinc-200 text-xs text-zinc-700 flex items-center gap-1.5 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </button>
                <button
                  onClick={() => setActivePreviewFile(null)}
                  className="p-1.5 hover:bg-zinc-200 rounded-md text-zinc-500 cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modal Content / Iframe or Code */}
            <div className="flex-1 overflow-auto p-4 bg-zinc-50/50">
              {activePreviewFile.path.endsWith('.html') ? (
                <div className="w-full h-[65vh] rounded-xl border border-zinc-200 overflow-hidden bg-white shadow-inner">
                  <iframe
                    srcDoc={activePreviewFile.content}
                    title="Live Artifact Preview"
                    className="w-full h-full border-0"
                    sandbox="allow-scripts"
                  />
                </div>
              ) : activePreviewFile.path.endsWith('.csv') ? (
                <div className="bg-white rounded-xl border border-zinc-200 overflow-x-auto shadow-2xs">
                  <table className="w-full text-left text-xs border-collapse font-mono">
                    <tbody>
                      {activePreviewFile.content.trim().split('\n').map((row, rIdx) => {
                        const cols = row.split(',');
                        if (rIdx === 0) {
                          return (
                            <tr key={rIdx} className="bg-zinc-100/80 border-b border-zinc-200">
                              {cols.map((c, cIdx) => (
                                <th key={cIdx} className="p-2.5 font-bold text-zinc-900">{c.trim()}</th>
                              ))}
                            </tr>
                          );
                        }
                        return (
                          <tr key={rIdx} className="border-b border-zinc-100 hover:bg-zinc-50/80">
                            {cols.map((c, cIdx) => (
                              <td key={cIdx} className="p-2.5 text-zinc-700">{c.trim()}</td>
                            ))}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : activePreviewFile.path.endsWith('.md') ? (
                <div className="p-6 rounded-xl bg-white text-zinc-800 text-sm font-sans overflow-auto max-h-[65vh] leading-relaxed border border-zinc-200 shadow-inner">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table({ children }) {
                        return (
                          <div className="my-3 overflow-x-auto rounded-xl border border-zinc-200 shadow-2xs">
                            <table className="w-full text-left text-xs border-collapse">{children}</table>
                          </div>
                        );
                      },
                      th({ children }) {
                        return <th className="border-b border-zinc-200 bg-zinc-50 px-3.5 py-2 font-semibold text-zinc-900">{children}</th>;
                      },
                      td({ children }) {
                        return <td className="border-b border-zinc-100 px-3.5 py-2 text-zinc-700">{children}</td>;
                      },
                      p({ children }) {
                        return <p className="mb-2.5 last:mb-0 leading-relaxed">{children}</p>;
                      },
                      h1({ children }) {
                        return <h1 className="text-lg font-bold text-zinc-950 mt-4 mb-2 pb-1 border-b border-zinc-200">{children}</h1>;
                      },
                      h2({ children }) {
                        return <h2 className="text-base font-semibold text-zinc-950 mt-3 mb-1.5">{children}</h2>;
                      }
                    }}
                  >
                    {activePreviewFile.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <pre className="p-4 rounded-xl bg-zinc-950 text-zinc-100 text-xs font-mono overflow-auto max-h-[65vh] leading-relaxed">
                  <code>{activePreviewFile.content}</code>
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* A2A Forensic Protocol Wire-Tap Modal */}
      {showA2AInspector && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 md:p-6 z-50 animate-in fade-in duration-150">
          <div className="bg-zinc-950 border border-zinc-800 text-zinc-100 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/90">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
                  <Share2 className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-sm font-bold text-white tracking-tight">Agent-to-Agent (A2A) Forensic Wire-Tap</h2>
                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] font-mono font-semibold">
                      A2A-RPC v1.2
                    </span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono font-semibold">
                      VPC-SC Enforced
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-0.5">Live Cryptographic Message Mesh, Adversarial Risk Audit & Multi-Agent Consensus</p>
                </div>
              </div>

              <div className="flex items-center gap-2.5">
                <button
                  onClick={handleReplayA2A}
                  disabled={isReplayingA2A}
                  className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-1.5 cursor-pointer disabled:opacity-50 transition-all shadow-xs"
                >
                  {isReplayingA2A ? (
                    <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Zap className="w-3.5 h-3.5" />
                  )}
                  <span>{isReplayingA2A ? 'Streaming Packets...' : 'Replay Adversarial Audit'}</span>
                </button>
                <button
                  onClick={() => setShowA2AInspector(false)}
                  className="p-1.5 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* 4-Node Agent Pod Ribbon */}
            <div className="px-6 py-3 bg-zinc-900/40 border-b border-zinc-800/80">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {A2A_POD_AGENTS.map(agent => (
                  <div key={agent.id} className="p-2.5 rounded-xl bg-zinc-900/90 border border-zinc-800 flex items-start gap-2.5">
                    <span className="text-lg">{agent.avatar}</span>
                    <div className="overflow-hidden">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-zinc-200 truncate">{agent.name}</span>
                      </div>
                      <span className="text-[10px] text-zinc-400 block truncate">{agent.role}</span>
                      <span className={`inline-block mt-1 px-1.5 py-0.2 rounded text-[9px] font-mono border ${agent.badgeColor}`}>
                        {agent.id}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Tabs Navigation */}
            <div className="px-6 py-2 border-b border-zinc-800 flex items-center gap-4 bg-zinc-950 text-xs font-mono">
              <button
                onClick={() => setActiveA2ATab('packets')}
                className={`pb-1 border-b-2 transition-all cursor-pointer ${
                  activeA2ATab === 'packets'
                    ? 'border-purple-500 text-purple-400 font-bold'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Forensic Wire-Tap Feed ({a2aMessages.length})
              </button>
              <button
                onClick={() => setActiveA2ATab('inspect')}
                className={`pb-1 border-b-2 transition-all cursor-pointer ${
                  activeA2ATab === 'inspect'
                    ? 'border-purple-500 text-purple-400 font-bold'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Envelope Inspector {selectedA2APacket ? `(${selectedA2APacket.id})` : ''}
              </button>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-hidden flex flex-col md:flex-row min-h-[420px]">
              {/* Left Side: Timeline Feed */}
              <div className="w-full md:w-1/2 border-r border-zinc-800 overflow-y-auto p-4 space-y-3 bg-zinc-950">
                <div className="text-[11px] font-mono text-zinc-400 flex items-center justify-between px-1">
                  <span>INTERCEPTED ENVELOPES</span>
                  <span>TRACE: a2a-trace-dcf-9901</span>
                </div>

                {a2aMessages.map((msg, idx) => {
                  const isSelected = selectedA2APacket?.id === msg.id;
                  const isDissent = msg.intent === 'CHALLENGE_ASSUMPTION';
                  const isConsensus = msg.intent === 'CONSENSUS_REACHED';
                  const isRecalibration = msg.intent === 'RECALIBRATE_MODEL';

                  return (
                    <div
                      key={msg.id}
                      onClick={() => {
                        setSelectedA2APacket(msg);
                        setActiveA2ATab('inspect');
                      }}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-2 ${
                        isSelected
                          ? 'bg-purple-950/30 border-purple-500/80 shadow-md ring-1 ring-purple-500/50'
                          : isDissent
                          ? 'bg-rose-950/20 border-rose-800/60 hover:bg-rose-950/30'
                          : isConsensus
                          ? 'bg-emerald-950/20 border-emerald-800/60 hover:bg-emerald-950/30'
                          : isRecalibration
                          ? 'bg-amber-950/20 border-amber-800/60 hover:bg-amber-950/30'
                          : 'bg-zinc-900/60 border-zinc-800 hover:bg-zinc-900'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <div className="flex items-center gap-1.5">
                          <span className="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">#{idx + 1}</span>
                          <span className="text-zinc-400">{msg.timestamp}</span>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wide ${
                          isDissent ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                          isConsensus ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                          isRecalibration ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                          'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                        }`}>
                          {msg.intent}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-xs">
                        <span className="font-semibold text-zinc-200">{msg.sender.name}</span>
                        <span className="text-zinc-400">➔</span>
                        <span className="font-semibold text-zinc-300">{msg.recipient.name}</span>
                      </div>

                      <p className="text-xs text-zinc-300 leading-relaxed font-sans">{msg.summary}</p>

                      <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400 pt-1 border-t border-zinc-800/60">
                        <span className="truncate max-w-[200px]">{msg.hash}</span>
                        <span className="text-purple-400 font-semibold">Inspect ➔</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Right Side: Detailed Forensic Inspector */}
              <div className="w-full md:w-1/2 overflow-y-auto p-5 space-y-4 bg-zinc-900/30">
                {selectedA2APacket ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-white font-mono">{selectedA2APacket.id}</h3>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-zinc-800 text-zinc-300">
                            {selectedA2APacket.protocol}
                          </span>
                        </div>
                        <span className="text-xs text-zinc-400 font-sans">Trace: {selectedA2APacket.traceId}</span>
                      </div>

                      <button
                        onClick={() => copyToClipboard(JSON.stringify(selectedA2APacket, null, 2), selectedA2APacket.id)}
                        className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 cursor-pointer font-mono border border-zinc-700"
                      >
                        {copiedId === selectedA2APacket.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copiedId === selectedA2APacket.id ? 'Copied' : 'Copy Envelope'}</span>
                      </button>
                    </div>

                    {/* Handshake Details */}
                    <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                      <div className="p-3 rounded-xl bg-zinc-900 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 block uppercase">Sender Node</span>
                        <div className="font-bold text-zinc-100 mt-0.5">{selectedA2APacket.sender.name}</div>
                        <span className="text-[10px] text-zinc-400">{selectedA2APacket.sender.role}</span>
                      </div>
                      <div className="p-3 rounded-xl bg-zinc-900 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 block uppercase">Recipient Node</span>
                        <div className="font-bold text-zinc-100 mt-0.5">{selectedA2APacket.recipient.name}</div>
                        <span className="text-[10px] text-zinc-400">{selectedA2APacket.recipient.role}</span>
                      </div>
                    </div>

                    {/* Structured Payload Breakdown */}
                    <div className="p-4 rounded-xl bg-zinc-900/90 border border-zinc-800 space-y-2.5">
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-zinc-400 uppercase font-bold text-[11px]">Decoded A2A Payload</span>
                        <span className="text-emerald-400 font-semibold">Integrity Verified (SHA-256)</span>
                      </div>

                      <pre className="p-3 rounded-lg bg-black text-purple-300 text-xs font-mono overflow-x-auto leading-relaxed border border-zinc-800">
                        <code>{JSON.stringify(selectedA2APacket.payload, null, 2)}</code>
                      </pre>
                    </div>

                    {/* Sandbox Container Context */}
                    <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 text-xs font-mono space-y-1.5">
                      <div className="text-[11px] text-zinc-400 uppercase font-bold">Execution Provenance</div>
                      <div className="flex justify-between text-zinc-300">
                        <span>Sandbox MicroVM:</span>
                        <span className="text-zinc-100 font-bold">{selectedA2APacket.sandboxId}</span>
                      </div>
                      <div className="flex justify-between text-zinc-300 truncate">
                        <span>Cryptographic Hash:</span>
                        <span className="text-purple-400 font-bold">{selectedA2APacket.hash}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-zinc-500 text-xs font-mono">
                    Select a packet from the feed to inspect payload.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
