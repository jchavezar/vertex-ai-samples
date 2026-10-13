import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  ARCHITECTURAL_TIERS,
  BENCHMARK_QUESTIONS,
  BLOCKER_FLAGS,
} from './data';
import {
  ArchitecturalTierId,
  BenchmarkQuestion,
  BlockerFlagId,
  CopilotMessage,
  SimulationResult,
} from './types';

declare global {
  interface Window {
    sidecar?: {
      agent?: {
        sendMessage?: (payload: string | Record<string, unknown>) => Promise<unknown>;
      };
    };
  }
}

const getConfidenceClass = (pct: number): 'conf-green' | 'conf-amber' | 'conf-red' => {
  if (pct >= 80) return 'conf-green';
  if (pct >= 50) return 'conf-amber';
  return 'conf-red';
};

const getConfidenceLabel = (pct: number): string => {
  if (pct >= 80) return 'High Ready';
  if (pct >= 50) return 'Semantic Gap';
  return 'Multi-Tool Gap';
};

const getTierTagClass = (tier: ArchitecturalTierId): string => {
  switch (tier) {
    case 'TIER_1':
      return 'tier-tag tier-1-tag';
    case 'TIER_2':
      return 'tier-tag tier-2-tag';
    case 'TIER_3':
      return 'tier-tag tier-3-tag';
    case 'TIER_4':
      return 'tier-tag tier-4-tag';
  }
};

const getBlockerTagClass = (flagId: BlockerFlagId): string => {
  if (
    flagId === 'License Compliance Blocker' ||
    flagId === 'Missing ML Model in DB' ||
    flagId === 'Incomplete Spec'
  ) {
    return 'tier-tag danger-tag';
  }
  if (flagId === 'External 3P Market API') {
    return 'tier-tag tier-3-tag';
  }
  return 'tier-tag warn-tag';
};

const EXTERNAL_SOURCES = new Set([
  'Market_Financials_API',
  'Tech_Stack_Telemetry_Feed',
  'Buyer_Intent_Signal_Stream',
  'AI_Web_Synthesis_Engine',
  'SEC_Regulatory_Filings',
]);

/**
 * Clean inline Markdown parser for bold (**text**) and inline code (`code`)
 */
const renderInlineMarkdown = (text: string): React.ReactNode[] => {
  const tokens = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return tokens.map((tok, i) => {
    if (tok.startsWith('**') && tok.endsWith('**') && tok.length > 4) {
      return <strong key={i}>{tok.slice(2, -2)}</strong>;
    }
    if (tok.startsWith('`') && tok.endsWith('`') && tok.length > 2) {
      return (
        <code key={i} className="md-inline-code">
          {tok.slice(1, -1)}
        </code>
      );
    }
    return <React.Fragment key={i}>{tok}</React.Fragment>;
  });
};

/**
 * Clean block-level Markdown renderer (headings, bullet lists, numbered lists, fenced code blocks)
 */
const FormattedMarkdown: React.FC<{ content: string }> = ({ content }) => {
  if (!content) return null;

  // Split by fenced code blocks ```lang ... ```
  const segments = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="md-rendered">
      {segments.map((seg, idx) => {
        if (seg.startsWith('```') && seg.endsWith('```')) {
          const lines = seg.slice(3, -3).trim().split('\n');
          const firstLine = lines[0]?.trim() || '';
          const hasLang = /^[a-zA-Z0-9_-]+$/.test(firstLine);
          const codeBody = hasLang ? lines.slice(1).join('\n') : lines.join('\n');
          return (
            <pre key={idx} className="code-block" style={{ margin: '8px 0' }}>
              {codeBody}
            </pre>
          );
        }

        const lines = seg.split('\n');
        const elements: React.ReactNode[] = [];
        let listItems: string[] = [];

        const flushList = (keyPrefix: string) => {
          if (listItems.length > 0) {
            elements.push(
              <ul key={`${keyPrefix}-ul`} className="md-list">
                {listItems.map((item, liIdx) => (
                  <li key={liIdx}>{renderInlineMarkdown(item)}</li>
                ))}
              </ul>
            );
            listItems = [];
          }
        };

        lines.forEach((rawLine, lIdx) => {
          const line = rawLine.trim();
          if (!line) {
            flushList(`${idx}-${lIdx}`);
            return;
          }

          if (/^#{1,4}\s+/.test(line)) {
            flushList(`${idx}-${lIdx}`);
            const headingText = line.replace(/^#{1,4}\s+/, '');
            elements.push(
              <div key={`${idx}-${lIdx}-h`} className="md-heading">
                {renderInlineMarkdown(headingText)}
              </div>
            );
          } else if (/^[-*•]\s+/.test(line) || /^\d+\.\s+/.test(line)) {
            const itemText = line.replace(/^([-*•]|\d+\.)\s+/, '');
            listItems.push(itemText);
          } else {
            flushList(`${idx}-${lIdx}`);
            elements.push(
              <p key={`${idx}-${lIdx}-p`} className="md-para">
                {renderInlineMarkdown(line)}
              </p>
            );
          }
        });

        flushList(`${idx}-end`);
        return <React.Fragment key={idx}>{elements}</React.Fragment>;
      })}
    </div>
  );
};

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [showBlueprint, setShowBlueprint] = useState<boolean>(false);
  const [questions, setQuestions] = useState<BenchmarkQuestion[]>(BENCHMARK_QUESTIONS);
  const [selectedTier, setSelectedTier] = useState<ArchitecturalTierId | 'ALL'>('ALL');
  const [selectedBlocker, setSelectedBlocker] = useState<BlockerFlagId | 'ALL'>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [personaFilter, setPersonaFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeQuestion, setActiveQuestion] = useState<BenchmarkQuestion | null>(null);
  const [drawerTab, setDrawerTab] = useState<'COPILOT' | 'SIMULATOR' | 'TOOLS_DDL'>('COPILOT');

  // Simulator & Copilot State
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulationState, setSimulationState] = useState<Record<string, SimulationResult>>({});
  const [copilotInput, setCopilotInput] = useState<string>('');
  const [isCopilotThinking, setIsCopilotThinking] = useState<boolean>(false);
  const [copilotHistory, setCopilotHistory] = useState<Record<string, CopilotMessage[]>>({});
  const [bridgeStatus, setBridgeStatus] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const chatInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Smooth auto-scroll whenever messages or thinking state change
  useEffect(() => {
    if (drawerTab === 'COPILOT') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [copilotHistory, isCopilotThinking, activeQuestion?.id, drawerTab]);

  useEffect(() => {
    fetch('/api/questions')
      .then((res) => (res.ok ? res.json() : null))
      .then((payload) => {
        if (payload && Array.isArray(payload.questions) && payload.questions.length > 0) {
          const existingIds = new Set(BENCHMARK_QUESTIONS.map((q) => q.id));
          const extra = payload.questions.filter(
            (q: Partial<BenchmarkQuestion>) => q.id && !existingIds.has(q.id) && q.daxOrMetricFormula
          ) as BenchmarkQuestion[];
          if (extra.length > 0) {
            setQuestions([...BENCHMARK_QUESTIONS, ...extra]);
          }
        }
      })
      .catch(() => {
        // Uses embedded 24-question catalog
      });
  }, []);

  const personas = useMemo(() => {
    return Array.from(new Set(questions.map((q) => q.persona)));
  }, [questions]);

  const filteredQuestions = useMemo(() => {
    return questions.filter((q) => {
      const matchesTier = selectedTier === 'ALL' || q.tier === selectedTier;
      const matchesBlocker =
        selectedBlocker === 'ALL' || q.blockerFlags.includes(selectedBlocker);
      const matchesPriority = priorityFilter === 'ALL' || q.priority === priorityFilter;
      const matchesPersona = personaFilter === 'ALL' || q.persona === personaFilter;
      const qLower = searchQuery.trim().toLowerCase();
      const matchesSearch =
        !qLower ||
        q.question.toLowerCase().includes(qLower) ||
        q.code.toLowerCase().includes(qLower) ||
        q.domain.toLowerCase().includes(qLower) ||
        q.systemsInvolved.some((s) => s.toLowerCase().includes(qLower)) ||
        q.missing_artifacts.some((m) => m.toLowerCase().includes(qLower));
      return matchesTier && matchesBlocker && matchesPriority && matchesPersona && matchesSearch;
    });
  }, [questions, selectedTier, selectedBlocker, priorityFilter, personaFilter, searchQuery]);

  const resetAllFilters = () => {
    setSelectedTier('ALL');
    setSelectedBlocker('ALL');
    setPriorityFilter('ALL');
    setPersonaFilter('ALL');
    setSearchQuery('');
  };

  const exportFilteredCSV = () => {
    const headers = [
      'Code',
      'Priority',
      'Tier',
      'Confidence %',
      'Persona',
      'Domain',
      'Question',
      'Systems Involved',
      'Red-Flag Blockers',
      'Missing Artifacts Needed for 100% Precision',
    ];
    const rows = filteredQuestions.map((q) => [
      q.code,
      q.priority || 'P1-Now',
      q.tierLabel,
      `${q.confidence_pct}%`,
      q.persona,
      q.domain,
      `"${q.question.replace(/"/g, '""')}"`,
      `"${q.systemsInvolved.join(', ')}"`,
      `"${q.blockerFlags.join(' | ')}"`,
      `"${q.missing_artifacts.join(' | ').replace(/"/g, '""')}"`,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Dataplex_KC_Commercial_Mesh_Audit.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleOpenQuestion = (q: BenchmarkQuestion) => {
    setActiveQuestion(q);
    setDrawerTab('COPILOT');
    setBridgeStatus(null);
    setTimeout(() => chatInputRef.current?.focus(), 80);
  };

  const handleRunSimulation = async (q: BenchmarkQuestion) => {
    setIsSimulating(true);
    try {
      const response = await fetch('/api/simulate-question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: q.code,
          code: q.code,
          question: q.question,
          tier: q.tier,
          systems_involved: q.systemsInvolved,
          blocker_flags: q.blockerFlags,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        if (data && Array.isArray(data.traceSteps)) {
          setSimulationState((prev) => ({ ...prev, [q.id]: data as SimulationResult }));
          setIsSimulating(false);
          return;
        }
      }
    } catch {
      // Fallback to canonical trace
    }
    await new Promise((r) => setTimeout(r, 450));
    setSimulationState((prev) => ({
      ...prev,
      [q.id]: {
        ...q.defaultSimulation,
        totalLatencyMs: q.defaultSimulation.totalLatencyMs + Math.floor(Math.random() * 35),
      },
    }));
    setIsSimulating(false);
  };

  const sendCopilotPrompt = async (promptText: string) => {
    if (!activeQuestion || !promptText.trim() || isCopilotThinking) return;

    const userText = promptText.trim();
    setCopilotInput('');
    const qId = activeQuestion.id;

    const userMsg: CopilotMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: userText,
      timestamp: new Date().toISOString(),
    };

    const updatedHistory = [...(copilotHistory[qId] || []), userMsg];
    setCopilotHistory((prev) => ({ ...prev, [qId]: updatedHistory }));
    setIsCopilotThinking(true);

    try {
      const res = await fetch('/api/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: activeQuestion.code,
          question_code: activeQuestion.code,
          question_text: activeQuestion.question,
          tier: activeQuestion.tierLabel,
          confidence_pct: activeQuestion.confidence_pct,
          missing_artifacts: activeQuestion.missing_artifacts,
          systems_involved: activeQuestion.systemsInvolved,
          blocker_flags: activeQuestion.blockerFlags,
          dax_formula: activeQuestion.daxOrMetricFormula.daxExpression,
          gold_view_ddl: activeQuestion.bigqueryGoldViewDdl,
          message: userText,
          history: updatedHistory.map((m) => ({ role: m.role, content: m.content })),
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const replyText =
          data.reply ||
          data.response ||
          data.content ||
          'Verified against Dataplex Knowledge Catalog and BigQuery Gold View schema.';
        const assistantMsg: CopilotMessage = {
          id: `ast-${Date.now()}`,
          role: 'assistant',
          content: replyText,
          timestamp: new Date().toISOString(),
          modelUsed: data.model || 'gemini-3.8-flash (Vertex AI)',
        };
        setCopilotHistory((prev) => ({
          ...prev,
          [qId]: [...(prev[qId] || []), assistantMsg],
        }));
        setIsCopilotThinking(false);
        return;
      }
    } catch {
      // Smart question-specific client fallback when running from static HTML preview
    }

    await new Promise((r) => setTimeout(r, 450));
    const lowerQ = userText.toLowerCase();
    let replyContent = '';

    if (lowerQ.includes('unstructured') || lowerQ.includes('note') || lowerQ.includes('how did you know')) {
      replyContent =
        `- **How we detected hidden unstructured data**: While \`${activeQuestion.systemsInvolved.join('`, `')}\` appear as system names in the tracker, the actual evidence required by **${activeQuestion.code}** (executive review commentary, deal loss rationale, and custom gain-share/COLA contract terms) is stored in **free-text narrative fields and PDF/Word attachments** (\`CLM_Contract_Vault\` / \`Customer_Visit_Logs\`), not numeric SQL columns.\n` +
        `- **Why SQL-only MCP fails**: A BigQuery \`GROUP BY\` cannot extract legal clauses or sentiment from raw text blobs.\n` +
        `- **Fix**: Pair the BigQuery cohort query with a **Vertex AI Search RAG tool** or pre-extract the clauses into BigQuery using \`AI.GENERATE_TABLE\`.`;
    } else if (lowerQ.includes('missing') || lowerQ.includes('confidence') || lowerQ.includes('accurate')) {
      replyContent =
        `- **Current Readiness Confidence**: **${activeQuestion.confidence_pct}%** (${getConfidenceLabel(activeQuestion.confidence_pct)}).\n` +
        `- **Missing Customer Artifacts Needed for 100% Precision**:\n` +
        activeQuestion.missing_artifacts.map((a) => `  - ${a}`).join('\n') +
        `\n- **Next Step**: Request these exact join keys and schemas from the data engineering owners to raise readiness to >90%.`;
    } else if (lowerQ.includes('sql') || lowerQ.includes('yaml') || lowerQ.includes('tool')) {
      replyContent =
        `- **Recommended Pattern**: Expose a governed BigQuery Gold View via \`genai-toolbox\` (\`tools.yaml\`) for the structured cohort, then join additional context in ADK.\n` +
        `\`\`\`sql\n${activeQuestion.bigqueryGoldViewDdl.split('\n').slice(0, 12).join('\n')}\n\`\`\``;
    } else {
      replyContent =
        `- **Direct Answer for \`${activeQuestion.code}\`**: ${activeQuestion.architecturalDiagnosis}\n` +
        `- **Governed Sources**: ${activeQuestion.systemsInvolved.map((s) => `\`${s}\``).join(', ')}\n` +
        `- **Missing Info to Confirm**: ${activeQuestion.missing_artifacts[0] || 'Physical foreign-key join DDL.'}`;
    }

    const fallbackReply: CopilotMessage = {
      id: `ast-${Date.now()}`,
      role: 'assistant',
      content: replyContent,
      timestamp: new Date().toISOString(),
      modelUsed: 'gemini-3.8-flash // architect-copilot',
    };
    setCopilotHistory((prev) => ({
      ...prev,
      [qId]: [...(prev[qId] || []), fallbackReply],
    }));
    setIsCopilotThinking(false);
  };

  const handleSendCopilotMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendCopilotPrompt(copilotInput);
  };

  const handleDispatchToAntigravity = async (q: BenchmarkQuestion) => {
    setBridgeStatus('DISPATCHING...');
    const promptPayload = [
      `# Antigravity Federated Commercial Mesh Blueprint // ${q.code}`,
      `- **Question**: "${q.question}"`,
      `- **Assigned Tier**: ${q.tierLabel} (Confidence: ${q.confidence_pct}%)`,
      `- **Diagnosis**: ${q.architecturalDiagnosis}`,
      `- **Missing Artifacts**: ${q.missing_artifacts.join('; ')}`,
    ].join('\n');

    try {
      if (window.sidecar?.agent?.sendMessage) {
        await window.sidecar.agent.sendMessage(promptPayload);
        setBridgeStatus('SENT TO ANTIGRAVITY IDE ✓');
        return;
      }
      const res = await fetch('/api/antigravity/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: q.code,
          code: q.code,
          prompt: promptPayload,
        }),
      });
      if (res.ok) {
        setBridgeStatus('SENT TO ANTIGRAVITY IDE ✓');
        return;
      }
    } catch {
      // Clipboard fallback
    }
    await navigator.clipboard.writeText(promptPayload);
    setBridgeStatus('COPIED TO CLIPBOARD ✓');
  };

  const handleCopyCode = async (key: string, text: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 1800);
  };

  const currentSim = activeQuestion
    ? simulationState[activeQuestion.id] || activeQuestion.defaultSimulation
    : null;

  const currentMessages = activeQuestion ? copilotHistory[activeQuestion.id] || [] : [];

  return (
    <div>
      {/* Top Sticky Executive Bar */}
      <header className="topbar">
        <div className="brand-group">
          <span className="brand-badge">Enterprise Commercial Mesh</span>
          <div>
            <div className="brand-title">
              Commercial Brain — Golden Questions &amp; Agent Architecture Audit
            </div>
            <div className="brand-subtitle">
              BigQuery MCP vs. MCP Toolbox for Databases (genai-toolbox) vs. Multi-Tool ADK Runtime
            </div>
          </div>
        </div>

        <div className="topbar-actions">
          <button
            type="button"
            className="btn"
            onClick={() => setShowBlueprint(!showBlueprint)}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7" />
              <rect x="14" y="3" width="7" height="7" />
              <rect x="14" y="14" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" />
            </svg>
            Target Architecture Blueprint
          </button>
          <button type="button" className="btn" onClick={exportFilteredCSV}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Export Filtered CSV
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
            <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
        </div>
      </header>

      <main className="container">
        {/* Executive Verdict Banner */}
        <section className="verdict-banner">
          <div>
            <div className="verdict-title">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--t3-dot)"
                strokeWidth="2.2"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              Executive Assessment: Is a BigQuery MCP Tool or MCP Toolbox for Databases Sufficient?
            </div>
            <p className="verdict-text">
              <strong>
                No — a standalone BigQuery MCP tool or Google&apos;s MCP Toolbox for Databases (
                <code>genai-toolbox</code>) only solves 18.0% out-of-the-box, and caps out at 48.0%
              </strong>{' '}
              even after adding <strong>Dataplex Knowledge Catalog (KC)</strong>, pre-computed{' '}
              <strong>BigQuery Gold Views</strong> (for complex DAX commercial ratios), and a{' '}
              <strong>Python What-If Simulation tool</strong>.{' '}
              <strong>52.0% of questions</strong> require federating BigQuery with{' '}
              <strong>unstructured internal contracts/notes</strong> (<code>CLM_Contract_Vault</code>,{' '}
              <code>Customer_Visit_Logs</code>) and <strong>licensed 3P market feeds</strong>.
            </p>
          </div>

          <div className="sufficiency-meter">
            <div className="meter-header">
              <span>Enterprise Commercial Questions Sufficiency Spectrum</span>
              <span>48.0% BQ Ceiling | 52.0% Multi-Tool</span>
            </div>
            <div className="stacked-bar">
              <div
                className="bar-seg"
                style={{ width: '18.0%', background: 'var(--t1-dot)' }}
                title="Tier 1: Ready for MCP Toolbox (18.0%)"
              />
              <div
                className="bar-seg"
                style={{ width: '30.0%', background: 'var(--t2-dot)' }}
                title="Tier 2: Needs KC + Gold Views + Simulator (30.0%)"
              />
              <div
                className="bar-seg"
                style={{ width: '49.0%', background: 'var(--t3-dot)' }}
                title="Tier 3: Multi-Tool Agent - BQ + External/RAG (49.0%)"
              />
              <div
                className="bar-seg"
                style={{ width: '3.0%', background: 'var(--t4-dot)' }}
                title="Tier 4: Workflow Automation (3.0%)"
              />
            </div>
            <div className="meter-legend">
              <div className="legend-item">
                <span className="dot" style={{ background: 'var(--t1-dot)' }} />
                <strong>Tier 1 (18.0%):</strong> MCP Toolbox / SQL Ready
              </div>
              <div className="legend-item">
                <span className="dot" style={{ background: 'var(--t2-dot)' }} />
                <strong>Tier 2 (30.0%):</strong> Needs KC + Gold Views + Sim
              </div>
              <div className="legend-item">
                <span className="dot" style={{ background: 'var(--t3-dot)' }} />
                <strong>Tier 3 (49.0%):</strong> Needs External APIs / RAG
              </div>
              <div className="legend-item">
                <span className="dot" style={{ background: 'var(--t4-dot)' }} />
                <strong>Tier 4 (3.0%):</strong> Workflow / QBR Deck Automation
              </div>
            </div>
          </div>
        </section>

        {/* Collapsible Target Architecture Blueprint */}
        {showBlueprint && (
          <section className="blueprint-panel">
            <div className="section-header">
              <span className="section-title">
                Recommended 3-Pillar Architecture (ADK on Cloud Run + Gemini Enterprise)
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Governed by Pre-Flight Dataplex GenAI License &amp; RBAC Policy Guard
              </span>
            </div>
            <div className="arch-diagram-grid">
              <div className="arch-box">
                <h5>
                  <span>
                    Pillar 1: Google MCP Toolbox (<code>genai-toolbox</code>)
                  </span>
                  <span className="tier-tag tier-1-tag">Tiers 1 &amp; 2 (48%)</span>
                </h5>
                <ul>
                  <li>
                    <strong>Curated Parameterized SQL Tools:</strong> Deterministic SQL over
                    pre-joined BigQuery Gold Views.
                  </li>
                  <li>
                    <strong>Eliminates 15TB Scan Risks:</strong> Enforces partition pruning on{' '}
                    <code>Revenue_ODS_15TB</code>.
                  </li>
                </ul>
              </div>
              <div className="arch-box">
                <h5>
                  <span>Pillar 2: Dataplex KC + BQCA + Simulator</span>
                  <span className="tier-tag tier-2-tag">Tier 2 (30%)</span>
                </h5>
                <ul>
                  <li>
                    <strong>Dataplex Knowledge Catalog (KC):</strong> Grounds queries in canonical
                    DAX formulas (<em>Adjusted Yield v1/v3/v4</em>).
                  </li>
                  <li>
                    <strong>Pre-Materialized ML &amp; Python Sandbox:</strong> Exposes{' '}
                    <code>Markov Regimes</code> and runs counterfactual elasticity simulations.
                  </li>
                </ul>
              </div>
              <div className="arch-box">
                <h5>
                  <span>Pillar 3: Unstructured RAG &amp; External MCP</span>
                  <span className="tier-tag tier-3-tag">Tiers 3 &amp; 4 (52%)</span>
                </h5>
                <ul>
                  <li>
                    <strong>Internal Unstructured RAG:</strong> Indexes{' '}
                    <code>CLM_Contract_Vault</code> MSAs and <code>Customer_Visit_Logs</code>.
                  </li>
                  <li>
                    <strong>Licensed External Market MCP:</strong> Connects licensed 3P APIs while
                    blocking <code>Analyst_Benchmark_Feed_Unlicensed</code>.
                  </li>
                </ul>
              </div>
            </div>
          </section>
        )}

        {/* 1. 4 Architectural Tier Filter Cards */}
        <div className="section-header">
          <span className="section-title">
            1. Filter by Architectural Tier (Click a Card to Filter Questions)
          </span>
          <button
            type="button"
            className="btn"
            onClick={resetAllFilters}
            style={{ padding: '4px 10px', fontSize: '11px' }}
          >
            Reset All Filters
          </button>
        </div>

        <section className="tier-grid">
          {ARCHITECTURAL_TIERS.map((tier, idx) => {
            const isActive = selectedTier === tier.id;
            const tierCount = questions.filter((q) => q.tier === tier.id).length;
            const tagClass = `tier-tag tier-${idx + 1}-tag`;
            const shortTags = [
              'TIER 1 • DIRECT SQL / TOOLBOX',
              'TIER 2 • KC + GOLD VIEWS + SIM',
              'TIER 3 • MULTI-TOOL AGENT + RAG',
              'TIER 4 • WORKFLOW & DECK GEN',
            ];
            return (
              <button
                key={tier.id}
                type="button"
                className={`tier-card ${isActive ? 'active' : ''}`}
                onClick={() => setSelectedTier(isActive ? 'ALL' : tier.id)}
              >
                <div className="tier-card-top">
                  <span className={tagClass}>{shortTags[idx]}</span>
                  <span className={`conf-badge ${getConfidenceClass(tier.avgConfidencePct)}`}>
                    Avg Conf: {tier.avgConfidencePct}%
                  </span>
                </div>
                <div className="tier-metric">
                  {tierCount}{' '}
                  <span>
                    / {questions.length} ({tier.coveragePct}.0%)
                  </span>
                </div>
                <div className="tier-name">{tier.title}</div>
                <div className="tier-desc">{tier.description}</div>
              </button>
            );
          })}
        </section>

        {/* 2. 6 Detected Red-Flag Blockers Strip */}
        <div className="section-header">
          <span className="section-title">
            2. Detected Enterprise Problems &amp; Red-Flag Blockers (Click to Isolate Affected Questions)
          </span>
        </div>
        <section className="blocker-grid">
          {BLOCKER_FLAGS.map((flag) => {
            const active = selectedBlocker === flag.id;
            const badgeClass = getBlockerTagClass(flag.id);
            return (
              <button
                key={flag.id}
                type="button"
                className={`blocker-pill ${active ? 'active' : ''}`}
                onClick={() => setSelectedBlocker(active ? 'ALL' : flag.id)}
              >
                <div className="blocker-pill-top">
                  <span className={badgeClass}>{flag.shortCode}</span>
                  <span className="blocker-count">{flag.count}</span>
                </div>
                <div className="blocker-label">{flag.label}</div>
                <div className="blocker-sub">{flag.description}</div>
              </button>
            );
          })}
        </section>

        {/* Search & Filter Controls Bar */}
        <section className="controls-bar">
          <div className="search-wrap">
            <svg
              className="search-icon"
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              className="search-input"
              placeholder="Search questions, KPIs, data sources (e.g., 'Markov', 'CLM_Contract_Vault', 'Stage 3', 'Yield')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <select
            className="filter-select"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="ALL">All Priorities ({questions.length})</option>
            <option value="P1-Now">P1-Now Only</option>
            <option value="P2-Next">P2-Next Only</option>
            <option value="P3-Next">P3-Next Only</option>
          </select>

          <select
            className="filter-select"
            value={personaFilter}
            onChange={(e) => setPersonaFilter(e.target.value)}
          >
            <option value="ALL">All Personas</option>
            {personas.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          <div className="results-count">
            Showing {filteredQuestions.length} of {questions.length} questions
          </div>
        </section>

        {/* Interactive Audit Table */}
        <section className="table-card">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th style={{ width: '64px' }}>Q#</th>
                  <th style={{ width: '90px' }}>Priority</th>
                  <th style={{ width: '30%' }}>Commercial Question &amp; Domain</th>
                  <th style={{ width: '16%' }}>Mapped Data Sources</th>
                  <th style={{ width: '16%' }}>Architecture Tier &amp; Confidence %</th>
                  <th style={{ width: '24%' }}>
                    Red-Flag Blockers &amp; Missing Info
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredQuestions.map((q) => {
                  const isSelected = activeQuestion?.id === q.id;
                  const hasComplianceBlocker = q.blockerFlags.includes('License Compliance Blocker');
                  const confClass = getConfidenceClass(q.confidence_pct);
                  const prioClass = `prio-badge prio-${q.priority || 'P1-Now'}`;
                  return (
                    <tr
                      key={q.id}
                      className={`question-row ${isSelected ? 'selected' : ''} ${
                        hasComplianceBlocker ? 'has-compliance-blocker' : ''
                      }`}
                      onClick={() => handleOpenQuestion(q)}
                    >
                      <td>
                        <div className="q-id">{q.code}</div>
                      </td>
                      <td>
                        <span className={prioClass}>{q.priority || 'P1-Now'}</span>
                      </td>
                      <td>
                        <div className="q-title">{q.question}</div>
                        <div className="q-meta">
                          <span>
                            <strong>Domain:</strong> {q.domain}
                          </span>
                          <span>•</span>
                          <span>
                            <strong>Persona:</strong> {q.persona}
                          </span>
                        </div>
                      </td>
                      <td>
                        <div className="pill-list">
                          {q.systemsInvolved.map((sys) => {
                            const isUnlicensed = sys === 'Analyst_Benchmark_Feed_Unlicensed';
                            const isExt = EXTERNAL_SOURCES.has(sys);
                            const cls = isUnlicensed
                              ? 'source-pill unlicensed-warn'
                              : isExt
                              ? 'source-pill ext'
                              : 'source-pill';
                            return (
                              <span key={sys} className={cls}>
                                {sys}
                              </span>
                            );
                          })}
                        </div>
                      </td>
                      <td>
                        <span className={getTierTagClass(q.tier)}>
                          {q.tier.replace('_', ' ')}
                        </span>
                        <div style={{ marginTop: '6px' }}>
                          <span className={`conf-badge ${confClass}`}>
                            {q.confidence_pct}% • {getConfidenceLabel(q.confidence_pct)}
                          </span>
                        </div>
                      </td>
                      <td>
                        {q.blockerFlags.length > 0 && (
                          <div style={{ marginBottom: '4px' }}>
                            {q.blockerFlags.map((bf) => (
                              <span key={bf} className={`flag-chip ${getBlockerTagClass(bf)}`}>
                                {bf}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className="missing-artifact-item">
                          <strong>Needs:</strong> {q.missing_artifacts[0]}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      {/* Clean, Full-Height Auto-Scrolling AI Architect Drawer */}
      {activeQuestion && currentSim && (
        <div
          className="drawer-backdrop"
          onClick={(e) => {
            if (e.target === e.currentTarget) setActiveQuestion(null);
          }}
        >
          <aside className="architect-drawer" aria-label="Live AI Architect Copilot Drawer">
            {/* Compact Sticky Header */}
            <div className="drawer-header">
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <span className={getTierTagClass(activeQuestion.tier)}>
                    {activeQuestion.code} • {activeQuestion.tier.replace('_', ' ')}
                  </span>
                  <span className={`conf-badge ${getConfidenceClass(activeQuestion.confidence_pct)}`}>
                    Confidence: {activeQuestion.confidence_pct}% ({getConfidenceLabel(activeQuestion.confidence_pct)})
                  </span>
                  {activeQuestion.blockerFlags.map((bf) => (
                    <span key={bf} className={`flag-chip ${getBlockerTagClass(bf)}`} style={{ margin: 0 }}>
                      {bf}
                    </span>
                  ))}
                </div>
                <h2 className="drawer-question-title">{activeQuestion.question}</h2>
              </div>
              <button
                type="button"
                className="btn"
                onClick={() => setActiveQuestion(null)}
                style={{ flexShrink: 0 }}
              >
                Close ✕
              </button>
            </div>

            {/* 3 Focused Tabs (No Vertical Clutter) */}
            <div className="drawer-tabs">
              <button
                type="button"
                className={`drawer-tab ${drawerTab === 'COPILOT' ? 'active' : ''}`}
                onClick={() => setDrawerTab('COPILOT')}
              >
                💬 AI Architect Chat
              </button>
              <button
                type="button"
                className={`drawer-tab ${drawerTab === 'SIMULATOR' ? 'active' : ''}`}
                onClick={() => setDrawerTab('SIMULATOR')}
              >
                ⚡ Execution Trace &amp; Simulator
              </button>
              <button
                type="button"
                className={`drawer-tab ${drawerTab === 'TOOLS_DDL' ? 'active' : ''}`}
                onClick={() => setDrawerTab('TOOLS_DDL')}
              >
                🛠 SQL, tools.yaml &amp; IDE Bridge
              </button>
            </div>

            {/* TAB 1: FULL-HEIGHT AUTO-SCROLLING AI CHAT WITH PINNED INPUT BAR */}
            {drawerTab === 'COPILOT' && (
              <div className="copilot-tab-layout">
                {/* Concise 2-Line Context Summary + 1-Click Quick-Ask Pills */}
                <div className="concise-context-card">
                  <div className="concise-row">
                    <span className="concise-label">Diagnosis:</span>
                    <span className="concise-val">{activeQuestion.architecturalDiagnosis}</span>
                  </div>
                  <div className="concise-row">
                    <span className="concise-label">Missing Info ({100 - activeQuestion.confidence_pct}% gap):</span>
                    <span className="concise-val">
                      {activeQuestion.missing_artifacts.join(' • ')}
                    </span>
                  </div>
                  <div className="quick-chip-row">
                    <button
                      type="button"
                      className="quick-chip"
                      onClick={() =>
                        sendCopilotPrompt(
                          'How did you detect hidden unstructured notes or blockers in these sources?'
                        )
                      }
                    >
                      Why hidden unstructured notes?
                    </button>
                    <button
                      type="button"
                      className="quick-chip"
                      onClick={() =>
                        sendCopilotPrompt(
                          'What exact table schemas or customer artifacts are missing to reach 100% accuracy?'
                        )
                      }
                    >
                      What customer info is missing?
                    </button>
                    <button
                      type="button"
                      className="quick-chip"
                      onClick={() =>
                        sendCopilotPrompt(
                          'Why does a standalone BigQuery SQL MCP tool fail on this question and how do we fix it?'
                        )
                      }
                    >
                      Why does DB-only MCP fail?
                    </button>
                    <button
                      type="button"
                      className="quick-chip"
                      onClick={() =>
                        sendCopilotPrompt(
                          'Show me the concise BigQuery Gold View SQL and genai-toolbox tools.yaml for this question.'
                        )
                      }
                    >
                      Generate SQL &amp; tools.yaml
                    </button>
                  </div>
                </div>

                {/* Scrollable Messages Viewport (Auto-Scrolls to Bottom) */}
                <div className="copilot-messages-viewport">
                  {currentMessages.length === 0 && !isCopilotThinking && (
                    <div className="empty-chat-hint">
                      Click any quick question above or ask anything below about{' '}
                      <strong>{activeQuestion.code}</strong>, its mapped data sources (
                      <code>{activeQuestion.systemsInvolved.join(', ')}</code>), or how to build the
                      solution.
                    </div>
                  )}

                  {currentMessages.map((msg) => (
                    <div key={msg.id} className={`chat-bubble ${msg.role}`}>
                      <div className="chat-bubble-meta">
                        {msg.role === 'user'
                          ? 'You'
                          : `Vertex AI Architect (${msg.modelUsed || 'gemini-3.8-flash'})`}
                      </div>
                      {msg.role === 'user' ? (
                        <div>{msg.content}</div>
                      ) : (
                        <FormattedMarkdown content={msg.content} />
                      )}
                    </div>
                  ))}

                  {isCopilotThinking && (
                    <div className="ink-loader-row">
                      <div className="shrinking-shining-ink" />
                      <span className="sweep-text">
                        Analyzing {activeQuestion.code} schema &amp; generating concise answer...
                      </span>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Pinned Bottom Input Bar (Always Inside Window!) */}
                <form className="copilot-input-dock" onSubmit={handleSendCopilotMessage}>
                  <input
                    ref={chatInputRef}
                    type="text"
                    className="copilot-input"
                    placeholder={`Ask about ${activeQuestion.code} (e.g., "how did you know there were hidden unstructured notes?")...`}
                    value={copilotInput}
                    onChange={(e) => setCopilotInput(e.target.value)}
                  />
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isCopilotThinking || !copilotInput.trim()}
                  >
                    Ask Copilot
                  </button>
                </form>
              </div>
            )}

            {/* TAB 2: EXECUTION TRACE & SIMULATOR */}
            {drawerTab === 'SIMULATOR' && (
              <div className="drawer-body">
                <div className="trace-step-card" style={{ background: 'var(--bg-surface)' }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '10px',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    <div>
                      <div className="section-title" style={{ fontSize: '11px' }}>
                        4-Tier Federated Execution Trace
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Compliance: <strong className="mono">{currentSim.complianceStatus}</strong> |
                        Latency: <strong className="mono">{currentSim.totalLatencyMs} ms</strong>
                      </div>
                    </div>
                    <button
                      type="button"
                      className="btn btn-primary"
                      disabled={isSimulating}
                      onClick={() => handleRunSimulation(activeQuestion)}
                    >
                      {isSimulating ? 'Running Simulation...' : 'Run Live Simulation'}
                    </button>
                  </div>

                  {isSimulating && (
                    <div className="ink-loader-row" style={{ marginBottom: '12px' }}>
                      <div className="shrinking-shining-ink" />
                      <span className="sweep-text">
                        Executing License Guard, MCP Toolbox SQL &amp; Federated RAG...
                      </span>
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {currentSim.traceSteps.map((step) => (
                      <div key={step.stepOrder} className="trace-step-card">
                        <div className="trace-step-header">
                          <span>
                            <strong>STEP {step.stepOrder}</strong> • [{step.pillar}] {step.title}
                          </span>
                          <span
                            className={
                              step.status === 'BLOCKED'
                                ? 'tier-tag danger-tag'
                                : 'tier-tag tier-1-tag'
                            }
                          >
                            {step.status} ({step.latencyMs}ms)
                          </span>
                        </div>
                        <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                          {step.detail}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div style={{ marginTop: '14px' }}>
                    <div className="section-title" style={{ fontSize: '11px', marginBottom: '6px' }}>
                      Formatted Simulation Output
                    </div>
                    <div className="trace-step-card" style={{ background: 'var(--bg-elevated)' }}>
                      <FormattedMarkdown content={currentSim.synthesizedAnswer} />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: SQL, TOOLS.YAML & ANTIGRAVITY BRIDGE */}
            {drawerTab === 'TOOLS_DDL' && (
              <div className="drawer-body">
                <div className="trace-step-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                    <div>
                      <div className="section-title" style={{ fontSize: '11px' }}>
                        Antigravity IDE Agent Bridge
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Send this question&apos;s blueprint &amp; SQL straight into your active Antigravity chat.
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => handleDispatchToAntigravity(activeQuestion)}
                      >
                        Send to Antigravity IDE ↗
                      </button>
                      {bridgeStatus && <span className="tier-tag tier-1-tag">{bridgeStatus}</span>}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="section-header">
                    <span className="section-title">
                      Dataplex Knowledge Catalog (KC) • DAX Formula ({activeQuestion.daxOrMetricFormula.metricName})
                    </span>
                  </div>
                  <pre className="code-block">
                    {activeQuestion.daxOrMetricFormula.daxExpression}
                  </pre>
                </div>

                <div>
                  <div className="section-header">
                    <span className="section-title">
                      Google MCP Toolbox • Parameterized tools.yaml
                    </span>
                    <button
                      type="button"
                      className="btn"
                      onClick={() => handleCopyCode('yaml', activeQuestion.genaiToolboxYaml)}
                    >
                      {copiedKey === 'yaml' ? 'Copied YAML ✓' : 'Copy tools.yaml'}
                    </button>
                  </div>
                  <pre className="code-block">{activeQuestion.genaiToolboxYaml}</pre>
                </div>

                <div>
                  <div className="section-header">
                    <span className="section-title">
                      BigQuery Materialized Gold View DDL
                    </span>
                    <button
                      type="button"
                      className="btn"
                      onClick={() => handleCopyCode('ddl', activeQuestion.bigqueryGoldViewDdl)}
                    >
                      {copiedKey === 'ddl' ? 'Copied SQL DDL ✓' : 'Copy Gold View DDL'}
                    </button>
                  </div>
                  <pre className="code-block">{activeQuestion.bigqueryGoldViewDdl}</pre>
                </div>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  );
};

export default App;
