import React, { useState, useEffect } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Play, 
  Presentation, 
  FileText, 
  ShieldAlert, 
  Terminal, 
  Layers, 
  Maximize2, 
  Minimize2,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Scale,
  Cpu,
  Lock,
  ArrowRight,
  Sliders,
  Check
} from 'lucide-react';

interface SlideData {
  id: number;
  section: string;
  badge: string;
  title: string;
  subtitle: string;
  content: React.ReactNode;
  speakerNotes: string;
  demoTarget: 'adk' | 'antigravity' | 'privacy_pro' | 'vault';
  demoPrompt: string;
}

interface SlidesDeckViewProps {
  onNavigateToDemo: (tab: string, prompt?: string) => void;
}

export const SlidesDeckView: React.FC<SlidesDeckViewProps> = ({ onNavigateToDemo }) => {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [showNotes, setShowNotes] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Interactive state for Slide 2 (Subagent inspector)
  const [selectedAgentTab, setSelectedAgentTab] = useState<'assembly' | 'citation' | 'wall' | 'redline'>('assembly');

  // Interactive state for Slide 5 (Live Slide Slider)
  const [slideClaim, setSlideClaim] = useState<number>(45);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        if (currentSlideIndex < slides.length - 1) {
          setCurrentSlideIndex(prev => prev + 1);
        }
      } else if (e.key === 'ArrowLeft') {
        if (currentSlideIndex > 0) {
          setCurrentSlideIndex(prev => prev - 1);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentSlideIndex]);

  const slides: SlideData[] = [
    // --- SLIDE 1 ---
    {
      id: 1,
      section: "PART 1: MULTI-AGENT ORCHESTRATION",
      badge: "Architecture Comparison",
      title: "The Monolithic Chatbot Trap vs. Multi-Agent Specialization",
      subtitle: "Why a single general-purpose prompt fails in high-stakes corporate law",
      speakerNotes: "Andrew and Ian: In high-stakes M&A or litigation, a single monolithic prompt cannot reliably research Delaware case law, assemble modular clauses, and enforce ethical walls simultaneously without severe context drift and hallucination. In Google ADK, we decouple these roles into independent, auditable cognitive lanes.",
      demoTarget: "adk",
      demoPrompt: "Assemble GDPR + Schrems II compliant AI governance addendum with zero data retention and 30-day audit rights",
      content: (
        <div className="bg-white border border-slate-200/80 rounded-2xl p-8 shadow-card flex flex-col justify-between h-full">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 md:divide-x divide-slate-100">
            {/* Left: Monolithic Challenges */}
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 text-rose-700 text-sm font-semibold mb-1">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  <h4>Monolithic Generalist Prompts</h4>
                </div>
                <p className="text-xs text-slate-500">Traditional single-session LLMs without deterministic architectural boundaries</p>
              </div>

              <div className="space-y-4">
                <div className="space-y-1">
                  <h5 className="text-sm font-medium text-slate-900">1. Context Drift & Loss Across Deals</h5>
                  <p className="text-xs text-slate-600 leading-relaxed">Multi-turn conversations lose track of covenants across 100+ page transactional agreements and exhibits.</p>
                </div>

                <div className="space-y-1">
                  <h5 className="text-sm font-medium text-slate-900">2. Phantom Precedent Citations</h5>
                  <p className="text-xs text-slate-600 leading-relaxed">Generates plausible-sounding but fictitious Delaware Chancery or federal court opinions without verification.</p>
                </div>

                <div className="space-y-1">
                  <h5 className="text-sm font-medium text-slate-900">3. Zero Ethical Wall Enforcement</h5>
                  <p className="text-xs text-slate-600 leading-relaxed">Unsanitized session memory risks cross-contaminating confidential adverse client terms into active drafting.</p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 text-xs text-rose-700 font-medium">
                Risk: Malpractice liability, ethical wall breach, and ungrounded court submissions.
              </div>
            </div>

            {/* Right: ADK Solution */}
            <div className="space-y-6 md:pl-10">
              <div>
                <div className="flex items-center gap-2 text-blue-700 text-sm font-semibold mb-1">
                  <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                  <h4>Google ADK Autonomous Orchestration</h4>
                </div>
                <p className="text-xs text-slate-500">Modular subagent lanes with deterministic state verification</p>
              </div>

              <div className="space-y-4">
                <div className="space-y-1">
                  <h5 className="text-sm font-medium text-slate-900">1. Cognitive Division of Labor</h5>
                  <p className="text-xs text-slate-600 leading-relaxed">Specialized Coordinator dispatches parallel tasks to Assembly, Citation, Screening, and Redline agents.</p>
                </div>

                <div className="space-y-1">
                  <h5 className="text-sm font-medium text-slate-900">2. Deterministic State Transitions</h5>
                  <p className="text-xs text-slate-600 leading-relaxed">Tracks clause dependencies and approval gates outside the probabilistic LLM via auditable state machines.</p>
                </div>

                <div className="space-y-1">
                  <h5 className="text-sm font-medium text-slate-900">3. Model Context Protocol (MCP) Boundary</h5>
                  <p className="text-xs text-slate-600 leading-relaxed">Standard tool connectors sanitize adverse client data and verify primary case law before drafting begins.</p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 text-xs text-blue-700 font-medium">
                Outcome: Verifiable, auditable legal deliverables with 0 hallucinations.
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Weil Practice Standard: Corporate, M&A, and Regulatory Compliance</span>
            <span className="font-mono text-slate-600">Architecture: Google ADK + MCP Gateway</span>
          </div>
        </div>
      )
    },

    // --- SLIDE 2 ---
    {
      id: 2,
      section: "PART 1: MULTI-AGENT ORCHESTRATION",
      badge: "Cognitive Lanes",
      title: "The Legal Multi-Agent Division of Labor",
      subtitle: "Click any subagent below to inspect its cognitive role and MCP tool RPC",
      speakerNotes: "Here is the exact topology running live in our demo: The Coordinator breaks down the attorney's instruction. Lane 1 (Assembly) pulls approved Lego clauses. Lane 2 (Citation) checks court reporters. Lane 3 (Ethical Wall) verifies conflicts. Lane 4 (Redline) scores deviation risk against Weil standards.",
      demoTarget: "adk",
      demoPrompt: "Assemble GDPR + Schrems II compliant AI governance addendum with zero data retention and 30-day audit rights",
      content: (
        <div className="bg-white border border-slate-200/80 rounded-2xl p-8 shadow-card flex flex-col justify-between h-full">
          <div className="space-y-6">
            <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-4 text-center max-w-xl mx-auto w-full">
              <span className="text-[11px] font-semibold text-blue-700 uppercase tracking-wider">Cognitive Router</span>
              <h4 className="text-base font-semibold text-slate-900 mt-0.5">Google ADK Coordinator Agent</h4>
              <p className="text-xs text-slate-500">Decomposes mandates • Dispatches parallel tasks • Synthesizes final deliverables</p>
            </div>

            {/* Subagent Selector */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { id: 'assembly', name: 'Assembly Agent', role: 'Privacy Pro Legos' },
                { id: 'citation', name: 'Citation Agent', role: 'Precedent Grounding' },
                { id: 'wall', name: 'Ethical Wall Guard', role: 'Chinese Wall Barrier' },
                { id: 'redline', name: 'Redline Agent', role: 'Risk & Cap Scorer' },
              ].map(agent => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgentTab(agent.id as any)}
                  className={`p-4 rounded-xl border text-left transition cursor-pointer ${
                    selectedAgentTab === agent.id 
                      ? 'bg-blue-50/50 border-blue-500/80 shadow-xs' 
                      : 'bg-white border-slate-200/70 hover:bg-slate-50'
                  }`}
                >
                  <h5 className="font-semibold text-sm text-slate-900">{agent.name}</h5>
                  <p className="text-xs text-slate-500 mt-1">{agent.role}</p>
                </button>
              ))}
            </div>

            {/* Subagent Details */}
            <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-4 text-xs flex items-center justify-between">
              {selectedAgentTab === 'assembly' && (
                <div className="space-y-1">
                  <span className="font-semibold text-slate-900 block">Assembly Agent Specification:</span>
                  <p className="text-slate-600">Retrieves approved modular clauses via <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 font-mono text-blue-700">fetch_lego_clause(clause_id)</code>. Enforces prerequisite dependency graphs before contract drafting.</p>
                </div>
              )}
              {selectedAgentTab === 'citation' && (
                <div className="space-y-1">
                  <span className="font-semibold text-slate-900 block">Citation Agent Specification:</span>
                  <p className="text-slate-600">Executes deterministic primary authority checks via <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 font-mono text-emerald-700">verify_case_citation(citation)</code> against Delaware Chancery, SDNY, and CJEU court reporters.</p>
                </div>
              )}
              {selectedAgentTab === 'wall' && (
                <div className="space-y-1">
                  <span className="font-semibold text-slate-900 block">Ethical Wall Guard Specification:</span>
                  <p className="text-slate-600">Intercepts queries at the tool boundary. Evaluates adverse client conflicts under ABA Model Rule 1.10 and redacts proprietary terms before model ingestion.</p>
                </div>
              )}
              {selectedAgentTab === 'redline' && (
                <div className="space-y-1">
                  <span className="font-semibold text-slate-900 block">Redline Agent Specification:</span>
                  <p className="text-slate-600">Calculates structured diffs and scores indemnity cap variance against Weil master market baselines (standard 15% cap vs. counterparty drafts).</p>
                </div>
              )}
              <span className="px-2.5 py-1 bg-white border border-slate-200 rounded font-mono text-[11px] text-slate-500 shrink-0 ml-4">
                Latency: &lt;180ms
              </span>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between">
            <span>Model Independence: Decoupled via Model Context Protocol (MCP)</span>
            <span className="font-mono text-slate-600">RPC Gateway v1.0</span>
          </div>
        </div>
      )
    },

    // --- SLIDE 3 ---
    {
      id: 3,
      section: "PART 1: MULTI-AGENT ORCHESTRATION",
      badge: "Deterministic Safeguards",
      title: "The Deterministic Harness: Guardrails General Counsel Can Trust",
      subtitle: "Bridging generative LLM flexibility with deterministic legal safeguards",
      speakerNotes: "General Counsel offices are rightfully terrified of black-box AI. Our deterministic harness sits outside the LLM: it enforces regex and primary-database checks on every citation, cryptographically logs every tool invocation, and holds all final actions in an attorney-in-the-loop review queue.",
      demoTarget: "adk",
      demoPrompt: "Retrieve merger indemnification precedent from the BioGen acquisition to use in drafting for Apex Pharma",
      content: (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full items-stretch">
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 flex flex-col justify-between shadow-card">
            <div>
              <span className="text-xs font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded font-medium">Pillar 1</span>
              <h4 className="font-semibold text-slate-900 text-base mt-3 mb-2">Citation Grounding</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Zero tolerance for phantom citations. The Citation Agent executes deterministic lookups against official state and federal court reporters before drafting completes.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-slate-100 text-xs text-slate-700">
              Pass Standard: Primary authority validated in court reporter.
            </div>
          </div>

          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 flex flex-col justify-between shadow-card">
            <div>
              <span className="text-xs font-mono text-amber-800 bg-amber-50 px-2 py-0.5 rounded font-medium">Pillar 2</span>
              <h4 className="font-semibold text-slate-900 text-base mt-3 mb-2">Ethical Wall Screening</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Evaluates adverse parties under ABA Model Rule 1.10. Confidential schedules are scrubbed at the MCP tool boundary so the model never ingests adverse client data.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-slate-100 text-xs text-slate-700">
              Active Action: Block & substitute sanitized Weil benchmark.
            </div>
          </div>

          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 flex flex-col justify-between shadow-card">
            <div>
              <span className="text-xs font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium">Pillar 3</span>
              <h4 className="font-semibold text-slate-900 text-base mt-3 mb-2">Attorney-in-the-Loop</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Agents propose; attorneys dispose. All multi-agent deliberations output into an interactive redline diff viewer where supervising counsel signs off with one click.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-slate-100 text-xs text-slate-700">
              Auditability: Complete timestamped provenance log.
            </div>
          </div>
        </div>
      )
    },

    // --- SLIDE 4 ---
    {
      id: 4,
      section: "PART 2: ANTIGRAVITY MANAGED AGENTS",
      badge: "Computational Runtime",
      title: "Why Elite Law Firms Need a Sandboxed Linux MicroVM",
      subtitle: "Moving from pure text prediction to computational legal modeling in an isolated container",
      speakerNotes: "Why do we offer Antigravity Managed Agents alongside ADK? Because real law involves heavy quantitative modeling. When negotiating a $500M buyout or litigating damages, you don't want an LLM guessing numbers in natural language. You want the agent to write a deterministic Python script, execute it in an air-gapped sandbox, and produce defensible numbers.",
      demoTarget: "antigravity",
      demoPrompt: "Calculate 10,000-trial Monte Carlo settlement risk distribution for pending Delaware patent dispute",
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full items-center">
          <div className="space-y-4">
            <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-card">
              <h4 className="font-semibold text-slate-900 text-sm mb-1">1. True Code Execution (`/workspace`)</h4>
              <p className="text-xs text-slate-600 leading-relaxed">Dedicated ephemeral Linux MicroVM running Python, NumPy, SciPy, and Pandas inside Weil's Google Cloud perimeter.</p>
            </div>
            <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-card">
              <h4 className="font-semibold text-slate-900 text-sm mb-1">2. Persistent Virtual Disk Drawer</h4>
              <p className="text-xs text-slate-600 leading-relaxed">Retains generated contracts, CSV calculation sheets, and SVG charts across multi-turn attorney sessions.</p>
            </div>
            <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-card">
              <h4 className="font-semibold text-slate-900 text-sm mb-1">3. Air-Gapped Zero-Egress Security</h4>
              <p className="text-xs text-slate-600 leading-relaxed">Enforced by VPC Service Controls: no public internet egress, complete cryptographic isolation.</p>
            </div>
          </div>

          <div className="bg-slate-100 border border-slate-200 rounded-2xl p-6 shadow-card font-mono text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 text-slate-600">
              <span className="flex items-center gap-2 font-sans font-medium text-slate-800">
                <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block animate-ping"></span>
                MicroVM: sandbox-weil-8820
              </span>
              <span className="text-[11px] text-slate-500">Linux 6.6 (gVisor)</span>
            </div>
            <div className="mt-4 space-y-2 text-slate-800">
              <p className="text-slate-400 font-sans"># Computational Execution Stream</p>
              <p><span className="text-blue-600 font-semibold">$</span> python3 /workspace/settlement_sim.py</p>
              <p className="text-slate-600">[STDOUT] 10,000 trials evaluated in 184ms</p>
              <p className="text-emerald-700 font-medium">[STDOUT] P10 (Best Case):   $14.2M</p>
              <p className="text-slate-800 font-medium">[STDOUT] P50 (Expected):    $28.5M</p>
              <p className="text-rose-700 font-medium">[STDOUT] P90 (Max Risk):    $44.1M</p>
              <p className="text-blue-700">[DISK] Generated `/workspace/distribution.svg`</p>
            </div>
          </div>
        </div>
      )
    },

    // --- SLIDE 5 (Interactive Live Claim Slider) ---
    {
      id: 5,
      section: "PART 2: ANTIGRAVITY MANAGED AGENTS",
      badge: "Computational Case Study",
      title: "Computational Law: The Monte Carlo Dispute Settlement Model",
      subtitle: "Drag the claim slider below to see exposure curves calculate dynamically",
      speakerNotes: "Notice how the agent generated this exact probability curve live in our demo. It runs a 10,000-iteration triangular distribution accounting for liability variance and legal defense costs, providing partners with empirical corridors like '$25M - $29M' rather than subjective guesses.",
      demoTarget: "antigravity",
      demoPrompt: "Calculate 10,000-trial Monte Carlo settlement risk distribution for pending Delaware patent dispute",
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full items-center">
          <div className="space-y-4">
            <h4 className="font-semibold text-slate-900 text-base">Delaware Patent Litigation Case Study</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Plaintiff claims damages. Move the interactive slider to simulate trial outcomes across 10,000 Monte Carlo trials in real time:
            </p>

            {/* Interactive Live Slider on Slide */}
            <div className="p-4 bg-white border border-slate-200/80 rounded-xl space-y-2 shadow-card">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 font-medium">Dispute Claim Amount:</span>
                <span className="text-blue-700 font-mono font-semibold text-sm">${slideClaim}M USD</span>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={slideClaim}
                onChange={(e) => setSlideClaim(parseInt(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="grid grid-cols-3 gap-3 pt-1">
              <div className="bg-white border border-slate-200/80 rounded-xl p-3 text-center shadow-xs">
                <span className="text-[11px] text-slate-500 uppercase font-medium">P10 Best Case</span>
                <p className="text-xl font-semibold text-emerald-700 mt-1 font-mono">${(slideClaim * 0.38 + 2.1).toFixed(1)}M</p>
              </div>
              <div className="bg-white border border-slate-200/80 rounded-xl p-3 text-center shadow-xs">
                <span className="text-[11px] text-slate-500 uppercase font-medium">P50 Expected</span>
                <p className="text-xl font-semibold text-slate-900 mt-1 font-mono">${(slideClaim * 0.64 + 2.5).toFixed(1)}M</p>
              </div>
              <div className="bg-white border border-slate-200/80 rounded-xl p-3 text-center shadow-xs">
                <span className="text-[11px] text-slate-500 uppercase font-medium">P90 Exposure</span>
                <p className="text-xl font-semibold text-rose-700 mt-1 font-mono">${(slideClaim * 0.98 + 3.2).toFixed(1)}M</p>
              </div>
            </div>
            <div className="p-3 bg-slate-50 border border-slate-200/60 rounded-xl text-xs text-slate-700">
              Target Acceptance Corridor: <span className="text-blue-700 font-mono font-semibold">${(slideClaim * 0.38 * 1.05 + 2.1).toFixed(1)}M – ${(slideClaim * 0.64 * 1.05 + 2.5).toFixed(1)}M</span>
            </div>
          </div>

          <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-card flex flex-col items-center justify-center">
            <span className="text-xs text-slate-500 mb-2 font-medium">Live Rendered Sandbox SVG Output</span>
            <div className="w-full bg-slate-50 rounded-xl p-3 border border-slate-200/60">
              <svg viewBox="0 0 400 180" className="w-full h-auto">
                <path d="M 30 150 C 90 145, 140 100, 200 40 C 260 40, 310 110, 370 150 Z" fill="rgba(37, 99, 235, 0.12)" stroke="#2563EB" strokeWidth="2" />
                <line x1="140" y1="110" x2="140" y2="150" stroke="#059669" strokeWidth="1.5" strokeDasharray="3,3" />
                <line x1="200" y1="40" x2="200" y2="150" stroke="#475569" strokeWidth="1.5" strokeDasharray="3,3" />
                <line x1="280" y1="120" x2="280" y2="150" stroke="#DC2626" strokeWidth="1.5" strokeDasharray="3,3" />
                <text x="110" y="105" fill="#059669" fontSize="10" fontWeight="600">P10: ${(slideClaim * 0.38 + 2.1).toFixed(0)}M</text>
                <text x="180" y="32" fill="#0F172A" fontSize="11" fontWeight="600">P50: ${(slideClaim * 0.64 + 2.5).toFixed(0)}M</text>
                <text x="260" y="115" fill="#DC2626" fontSize="10" fontWeight="600">P90: ${(slideClaim * 0.98 + 3.2).toFixed(0)}M</text>
                <line x1="20" y1="150" x2="380" y2="150" stroke="#CBD5E1" strokeWidth="1" />
              </svg>
            </div>
          </div>
        </div>
      )
    },

    // --- SLIDE 6 ---
    {
      id: 6,
      section: "PART 2: ANTIGRAVITY MANAGED AGENTS",
      badge: "Auditability & Forensics",
      title: "Forensic Wire-Tap: Complete Visibility Under the Hood",
      subtitle: "Inspecting stdout, stderr, tool calls, and disk mutations in real time",
      speakerNotes: "Our forensic wire-tap solves the 'black-box AI' dilemma. An attorney can view every command executed in the MicroVM, every file touched, and every parameter passed. It delivers absolute defensibility for client billing and liability insurance.",
      demoTarget: "antigravity",
      demoPrompt: "Calculate 10,000-trial Monte Carlo settlement risk distribution for pending Delaware patent dispute",
      content: (
        <div className="space-y-5 flex flex-col justify-center h-full">
          <div className="grid grid-cols-3 gap-5">
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 text-center shadow-card">
              <h5 className="font-semibold text-sm text-slate-900">Live Terminal Stream</h5>
              <p className="text-xs text-slate-500 mt-1">Real-time bash execution, compiler outputs, and stderr traps.</p>
            </div>
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 text-center shadow-card">
              <h5 className="font-semibold text-sm text-slate-900">Disk Mutation Traces</h5>
              <p className="text-xs text-slate-500 mt-1">Every created or modified file in `/workspace` is versioned.</p>
            </div>
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 text-center shadow-card">
              <h5 className="font-semibold text-sm text-slate-900">Zero Internet Egress</h5>
              <p className="text-xs text-slate-500 mt-1">VPC-SC prevents unauthorized external network requests.</p>
            </div>
          </div>

          <div className="bg-slate-100 border border-slate-200 rounded-xl p-5 text-xs font-mono text-slate-800 space-y-1.5 shadow-card">
            <p className="text-slate-400">[14:02:11] [INIT] Spawning ephemeral MicroVM container (ID: sandbox-weil-8820)</p>
            <p className="text-blue-700 font-medium">[14:02:12] [TOOL] Invoking iManage MCP: `search_precedents(matter="9042-M&A")`</p>
            <p className="text-emerald-700 font-medium">[14:02:13] [AUTH] Verified ethical wall token: No conflict on Apex Pharma matter</p>
            <p className="text-indigo-700 font-medium">[14:02:14] [CODE] Writing `/workspace/indemnity_audit.py` (142 lines)</p>
            <p className="text-slate-800 font-medium">[14:02:16] [STDOUT] Evaluated 42 clauses. 3 deviations flagged against standard index.</p>
            <p className="text-slate-600">[14:02:17] [DISK] Created `/workspace/weil_redline_v2.docx` (1.4 MB)</p>
          </div>
        </div>
      )
    },

    // --- SLIDE 7 ---
    {
      id: 7,
      section: "PART 3: SINGLE-PANE COCKPIT & PRIVACY PRO",
      badge: "Interface Consolidation",
      title: "Consolidating 45,000 Legal Surfaces into 1 Cockpit",
      subtitle: "Ending tool fragmentation: unifying iManage, Harvey, Thomson Reuters & custom models",
      speakerNotes: "Andrew made a compelling statement in our sync: 'My hope is that we can go from having 45,000 surfaces that our lawyers have to go to to do something to something close to one.' That is what this Single-Pane-of-Glass cockpit delivers. Attorneys don't switch between 5 browser tabs—research, clause assembly, redlining, and sandbox math all happen in one unified flow.",
      demoTarget: "privacy_pro",
      demoPrompt: "Assemble GDPR + Schrems II compliant AI governance addendum",
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full items-center">
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 space-y-4 shadow-card">
            <h4 className="font-semibold text-slate-900 text-sm">Today: Fractured Context Across Tools</h4>
            <div className="space-y-2 text-xs text-slate-600">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60">Window 1: iManage DMS (searching old precedent)</div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60">Window 2: Westlaw / Lexis (checking case citations)</div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60">Window 3: Microsoft Word (manual redlining)</div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60">Window 4: Excel (calculating liability caps)</div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60">Window 5: Email (checking ethical wall conflict list)</div>
            </div>
            <p className="text-xs text-slate-500 italic">Result: 45 minutes of manual context switching and human copy-paste risks.</p>
          </div>

          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 space-y-4 shadow-card">
            <h4 className="font-semibold text-slate-900 text-sm">Tomorrow: Weil Unified Cockpit</h4>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/60 space-y-2.5 text-xs text-slate-700">
              <div className="flex items-center justify-between font-medium border-b border-slate-200/60 pb-2">
                <span className="text-slate-900">Weil Executive Portal</span>
                <span className="text-blue-700 font-mono text-[11px]">1 Single Pane of Glass</span>
              </div>
              <p>• Precedent search via iManage MCP connector</p>
              <p>• Modular clause assembly via Privacy Pro Studio</p>
              <p>• Live judicial case law citation verification</p>
              <p>• Sandboxed damage simulation via Antigravity MicroVM</p>
            </div>
            <p className="text-xs text-blue-700 font-medium">Result: Frictionless execution with zero context loss.</p>
          </div>
        </div>
      )
    },

    // --- SLIDE 8 ---
    {
      id: 8,
      section: "PART 3: SINGLE-PANE COCKPIT & PRIVACY PRO",
      badge: "Modular Clause Engine",
      title: "Privacy Pro in Action: The Modular Clause Engine",
      subtitle: "Treating contracts as validated structural building blocks with deterministic dependency checks",
      speakerNotes: "Andrew described Privacy Pro as assembling documents out of Legos. In our interactive Lego Studio tab, you can drag and drop standardized clauses. If you add Clause 4 (AI Training Prohibition) without Clause 3 (Audit Rights), the system immediately halts you with a dependency violation.",
      demoTarget: "privacy_pro",
      demoPrompt: "Assemble GDPR + Schrems II compliant AI governance addendum",
      content: (
        <div className="space-y-5 flex flex-col justify-center h-full">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-white border border-slate-200/80 rounded-xl shadow-card text-xs">
              <span className="text-blue-700 font-medium block mb-1">Clause 01</span>
              <p className="font-semibold text-slate-900">Definitions & Scope</p>
              <p className="text-slate-500 text-xs mt-1">Foundation block</p>
            </div>
            <div className="p-4 bg-white border border-slate-200/80 rounded-xl shadow-card text-xs">
              <span className="text-blue-700 font-medium block mb-1">Clause 02</span>
              <p className="font-semibold text-slate-900">Schrems II SCCs</p>
              <p className="text-slate-500 text-xs mt-1">Cross-border EU-US</p>
            </div>
            <div className="p-4 bg-white border border-slate-200/80 rounded-xl shadow-card text-xs">
              <span className="text-blue-700 font-medium block mb-1">Clause 03</span>
              <p className="font-semibold text-slate-900">Sub-processor Audit</p>
              <p className="text-slate-500 text-xs mt-1">30-day notice right</p>
            </div>
            <div className="p-4 bg-white border border-slate-200/80 rounded-xl shadow-card text-xs">
              <span className="text-blue-700 font-medium block mb-1">Clause 04</span>
              <p className="font-semibold text-slate-900">AI Model Prohibit</p>
              <p className="text-slate-500 text-xs mt-1">Zero data retention</p>
            </div>
          </div>

          <div className="bg-white border border-slate-200/80 rounded-xl p-5 text-xs space-y-2.5 shadow-card">
            <h5 className="font-semibold text-slate-900 text-xs">Intelligent Dependency Validation:</h5>
            <div className="p-2.5 bg-slate-50 border border-slate-200/60 rounded-lg flex items-center gap-2 text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span><span className="font-semibold text-slate-900">Dependency Verified:</span> Clause 04 (AI Training Prohibition) requires Clause 03 (Audit Rights) — <span className="italic text-emerald-700 font-medium">Satisfied</span>.</span>
            </div>
            <div className="p-2.5 bg-slate-50 border border-slate-200/60 rounded-lg flex items-center gap-2 text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
              <span><span className="font-semibold text-slate-900">Jurisdictional Fit:</span> Clause 02 (Schrems II) triggers mandatory Transfer Impact Assessment (TIA) — <span className="italic text-blue-700 font-medium">Auto-attached</span>.</span>
            </div>
          </div>
        </div>
      )
    },

    // --- SLIDE 9 ---
    {
      id: 9,
      section: "PART 3: SINGLE-PANE COCKPIT & PRIVACY PRO",
      badge: "Standardized Interoperability",
      title: "Model Context Protocol (MCP): The Universal Legal Bridge",
      subtitle: "Connecting Weil's proprietary data to Google AI without monolithic vendor lock-in",
      speakerNotes: "Ian, you emphasized in our meeting that you want a multi-provider stack with no monolithic lock-in. MCP is the open standard that makes this possible. Your iManage DMS, Relativity, and court databases become standard MCP tool endpoints that any Google agent can call securely over encrypted RPC.",
      demoTarget: "vault",
      demoPrompt: "",
      content: (
        <div className="space-y-6 flex flex-col justify-center h-full">
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 text-center shadow-card max-w-xl mx-auto w-full">
            <span className="text-[11px] font-semibold text-blue-700 uppercase tracking-wider">Universal Legal Bridge</span>
            <h4 className="text-xl font-semibold text-slate-900 mt-1">Open Model Context Protocol (MCP)</h4>
            <p className="text-xs text-slate-500 max-w-lg mx-auto mt-2 leading-relaxed">
              Decouples AI reasoning from document storage. Allows Weil to swap underlying models (Gemini 2.5, Gemma open-weight) while preserving your core document repositories.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-5">
            <div className="p-5 bg-white border border-slate-200/80 rounded-xl text-center shadow-card hover:border-slate-300 transition">
              <h5 className="font-semibold text-sm text-slate-900">iManage DMS MCP</h5>
              <p className="text-xs text-slate-500 mt-1">Searches matters & precedent files securely.</p>
            </div>
            <div className="p-5 bg-white border border-slate-200/80 rounded-xl text-center shadow-card hover:border-slate-300 transition">
              <h5 className="font-semibold text-sm text-slate-900">Ethical Wall MCP</h5>
              <p className="text-xs text-slate-500 mt-1">Screens conflict registries dynamically.</p>
            </div>
            <div className="p-5 bg-white border border-slate-200/80 rounded-xl text-center shadow-card hover:border-slate-300 transition">
              <h5 className="font-semibold text-sm text-slate-900">Citation Authority MCP</h5>
              <p className="text-xs text-slate-500 mt-1">Checks Delaware Chancery & SDNY records.</p>
            </div>
          </div>
        </div>
      )
    }
  ];

  const currentSlide = slides[currentSlideIndex];

  const handleNext = () => {
    if (currentSlideIndex < slides.length - 1) {
      setCurrentSlideIndex(currentSlideIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
    }
  };

  return (
    <div className={`flex flex-col h-full ${isFullscreen ? 'fixed inset-0 z-50 bg-slate-50 p-8' : ''}`}>
      {/* Slide Controls Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200/80 mb-2">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-50 text-blue-700 rounded-lg border border-blue-100">
            <Presentation className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 text-xs">
              <span className="font-medium text-slate-500">{currentSlide.section}</span>
              <span className="text-slate-300">•</span>
              <span className="text-slate-400">Slide {currentSlide.id} of {slides.length}</span>
            </div>
            <h2 className="text-xl font-semibold text-slate-900 tracking-tight">{currentSlide.title}</h2>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigateToDemo(currentSlide.demoTarget, currentSlide.demoPrompt)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl text-xs transition shadow-xs cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Launch Live Demo for This Slide</span>
          </button>

          <button
            onClick={() => setShowNotes(!showNotes)}
            className={`px-3 py-2 rounded-xl text-xs font-medium border transition cursor-pointer ${
              showNotes ? 'bg-amber-50 text-amber-900 border-amber-300' : 'bg-white text-slate-600 border-slate-200 hover:text-slate-900'
            }`}
          >
            Speaker Script
          </button>

          <div className="flex items-center gap-1 bg-white p-1 rounded-xl border border-slate-200 shadow-xs">
            <button
              onClick={handlePrev}
              disabled={currentSlideIndex === 0}
              className="p-1.5 text-slate-500 hover:text-slate-900 disabled:opacity-30 rounded-lg hover:bg-slate-100 transition cursor-pointer"
              title="Previous Slide (←)"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleNext}
              disabled={currentSlideIndex === slides.length - 1}
              className="p-1.5 text-slate-500 hover:text-slate-900 disabled:opacity-30 rounded-lg hover:bg-slate-100 transition cursor-pointer"
              title="Next Slide (→)"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 text-slate-500 hover:text-slate-900 bg-white border border-slate-200 rounded-xl transition cursor-pointer"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main Slide Stage */}
      <div className="flex-1 py-4 flex flex-col justify-between overflow-y-auto">
        <div className="mb-3">
          <span className="inline-block px-2.5 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200/60 mb-2">
            {currentSlide.badge}
          </span>
          <p className="text-sm text-slate-500 font-normal">{currentSlide.subtitle}</p>
        </div>

        <div className="flex-1 my-auto">
          {currentSlide.content}
        </div>

        {/* Slide Footer */}
        <div className="pt-4 mt-2 border-t border-slate-200/80 flex items-center justify-between text-xs text-slate-500 font-normal">
          <span>Weil, Gotshal & Manges LLP • Executive Briefing Center</span>
          <div className="flex items-center gap-1.5">
            {slides.map((s, idx) => (
              <button
                key={s.id}
                onClick={() => setCurrentSlideIndex(idx)}
                className={`h-2 rounded-full transition cursor-pointer ${
                  idx === currentSlideIndex ? 'bg-blue-600 w-6' : 'bg-slate-200 hover:bg-slate-300 w-2'
                }`}
                title={`Go to slide ${idx + 1}`}
              />
            ))}
          </div>
          <span>Google Cloud Vertex AI</span>
        </div>
      </div>

      {/* Speaker Notes Drawer */}
      {showNotes && (
        <div className="mt-3 p-4 bg-amber-50/80 border border-amber-200 rounded-xl text-xs text-amber-900 animate-fadeIn shadow-xs">
          <div className="flex items-center gap-2 font-medium mb-1 text-amber-950">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>Speaker Script for Jesus Chavez:</span>
          </div>
          <p className="leading-relaxed italic">{currentSlide.speakerNotes}</p>
        </div>
      )}
    </div>
  );
};
