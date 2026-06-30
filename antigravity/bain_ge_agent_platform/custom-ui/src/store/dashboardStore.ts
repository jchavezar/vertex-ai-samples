import { create } from 'zustand';

export interface CompanyMetrics {
  name: string;
  ticker: string;
  sector: string;
  cfo: string;
  revenue: string;
  yoyGrowth: string;
  cashPosition: string;
  sources: { title: string; url: string }[];
  summary: string;
}

interface DashboardState {
  companies: CompanyMetrics[];
  activeCompany: CompanyMetrics | null;
  setActiveCompany: (company: CompanyMetrics | null) => void;
  chatOpen: boolean;
  setChatOpen: (open: boolean) => void;
  quickMode: boolean;
  setQuickMode: (quick: boolean) => void;
  
  // Bain & Company // Gemini Enterprise Agent Platform State
  activeView: 'main' | 'chart' | 'topology';
  setActiveView: (view: 'main' | 'chart' | 'topology') => void;
  isNeuralLink: boolean;
  setIsNeuralLink: (isNeural: boolean) => void;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  activeSignalTab: 'global' | 'social' | 'semiai';
  setActiveSignalTab: (tab: 'global' | 'social' | 'semiai') => void;

  // Dynamic Resizable Panels State
  sidebarWidth: number;
  setSidebarWidth: (width: number) => void;
  chatWidth: number;
  setChatWidth: (width: number) => void;

  // Shared Enterprise Authentication State (Header & Chat Overlay)
  entraToken: string;
  setEntraToken: (token: string) => void;
  accountName: string | null;
  setAccountName: (name: string | null) => void;
  reasoningEngineId: string;
  setReasoningEngineId: (id: string) => void;
  showAuthDrawer: boolean;
  setShowAuthDrawer: (show: boolean) => void;
  msalLog: string | null;
  setMsalLog: (log: string | null) => void;

  // Multiple Specialized Agents State
  selectedAgentId: string;
  setSelectedAgentId: (id: string) => void;

  // Dynamic Canvas Elements (Charts, Tables) Stream State
  canvasElements: Array<{
    id: string;
    type: 'chart' | 'table';
    title: string;
    data: any;
    timestamp: string;
  }>;
  addCanvasElement: (el: { type: 'chart' | 'table'; title: string; data: any }) => void;
  clearCanvasElements: () => void;

  // Agent Gateway Logging & Telemetry Traces
  //
  // Entries are now sourced from REAL Cloud Logging by polling
  // /api/gateway-logs (proxied to bain-ge-gateway-logs-svc), which queries
  // structured entries written by bain-ge-policy-svc on Cloud Run. The
  // previous hardcoded simulator strings have been removed.
  gatewayLogs: Array<{
    id: string;
    timestamp: string;
    type: string;
    text: string;
    decision?: 'ALLOW' | 'DENY';
    rule?: string;
    reason?: string;
    tool?: string;
    user?: string;
    sourceAgent?: string;
    targetService?: string;
    correlationId?: string;
    latencyMs?: number;
    logUrl?: string;
  }>;
  addGatewayLog: (log: { type: string; text: string }) => void;
  mergeGatewayLogs: (
    entries: Array<{
      correlationId: string;
      ts?: string;
      decision?: 'ALLOW' | 'DENY';
      rule?: string;
      reason?: string;
      tool?: string;
      user?: string;
      sourceAgent?: string;
      targetService?: string;
      latencyMs?: number;
      logUrl?: string;
      text?: string;
    }>
  ) => void;
  clearGatewayLogs: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  companies: [
    {
      name: "Meridian Technologies Corporation",
      ticker: "MRDN",
      sector: "Financial Technology & Enterprise Services",
      cfo: "Jennifer Walsh",
      revenue: "$182.4M (FY2025)",
      yoyGrowth: "+24.5%",
      cashPosition: "$42.8M",
      sources: [
        { title: "Governance_Risk_Advisory_Report_FY2024.docx", url: "https://sockcop.sharepoint.com/sites/FinancialDocument/_layouts/15/Doc.aspx?sourcedoc=%7B4C4E1D5D-A770-4C74-9FB1-A454C4036713%7D&file=Governance_Risk_Advisory_Report_FY2024.docx" },
        { title: "03_Client_Contract_Apex_Financial.pdf", url: "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/03_Client_Contract_Apex_Financial.pdf" },
        { title: "05_MA_Due_Diligence_Project_Starlight.pdf", url: "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/05_MA_Due_Diligence_Project_Starlight.pdf" }
      ],
      summary: "Meridian Technologies maintains an exceptionally robust cash position and accelerating SaaS recurring revenues. Diligence confirmed CFO Jennifer Walsh has effectively locked in long-term enterprise contract commitments with Apex Financial through FY2028."
    },
    {
      name: "Starlight European Banking HoldCo",
      ticker: "STRB",
      sector: "M&A Strategic Expansion Target",
      cfo: "Marcus Vance",
      revenue: "$45.0M (Projected ARR)",
      yoyGrowth: "+32.0%",
      cashPosition: "$12.4M",
      sources: [
        { title: "05_MA_Due_Diligence_Project_Starlight.pdf", url: "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/05_MA_Due_Diligence_Project_Starlight.pdf" }
      ],
      summary: "Project Starlight outlines Meridian Technologies' strategic expansion into European enterprise banking sectors. Diligence indicates significant market demand for secure, AI-powered corporate governance tools, projecting an additional $45.0M in ARR by FY2027."
    },
    {
      name: "Apex Financial Services Group",
      ticker: "APEX",
      sector: "Institutional Prime Infrastructure",
      cfo: "Elena Rostova",
      revenue: "$120.0M (Contract Value)",
      yoyGrowth: "Stable (SLA)",
      cashPosition: "$18.5M",
      sources: [
        { title: "03_Client_Contract_Apex_Financial.pdf", url: "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/03_Client_Contract_Apex_Financial.pdf" }
      ],
      summary: "Master Services Agreement establishing a binding, long-term enterprise commitment extending through December 31, 2028. Structured and executed by CFO Jennifer Walsh to establish recurring pricing models and institutional SLA guarantees."
    }
  ],
  activeCompany: null,
  setActiveCompany: (company) => set({ activeCompany: company }),
  chatOpen: true,
  setChatOpen: (open) => set({ chatOpen: open }),
  quickMode: false,
  setQuickMode: (quick) => set({ quickMode: quick }),

  // Bain & Company // Gemini Enterprise Agent Platform State
  activeView: 'main',
  setActiveView: (view) => set({ activeView: view }),
  isNeuralLink: true,
  setIsNeuralLink: (isNeural) => set({ isNeuralLink: isNeural }),
  selectedModel: 'Gemini 3.0 Flash (Global)',
  setSelectedModel: (model) => set({ selectedModel: model }),
  activeSignalTab: 'global',
  setActiveSignalTab: (tab) => set({ activeSignalTab: tab }),

  // Dynamic Resizable Panels State
  sidebarWidth: 288, // Default 288px (w-72)
  setSidebarWidth: (width) => set({ sidebarWidth: width }),
  chatWidth: 480,    // Default 480px (w-[480px])
  setChatWidth: (width) => set({ chatWidth: width }),
  
  entraToken: import.meta.env.VITE_ENTRA_ID_TOKEN || '',
  setEntraToken: (token) => set({ entraToken: token }),
  accountName: null,
  setAccountName: (name) => set({ accountName: name }),
  // Default Reasoning Engine ID — bain-financial-secure-agent with real
  // Agent Gateway policy guard wired through bain-ge-policy-svc.
  // Deployed 2026-06-30. Override via the Settings drawer if needed.
  reasoningEngineId: '5849699277663633408',
  setReasoningEngineId: (id) => set({ reasoningEngineId: id }),
  showAuthDrawer: false,
  setShowAuthDrawer: (show) => set({ showAuthDrawer: show }),
  msalLog: null,
  setMsalLog: (log) => set({ msalLog: log }),

  // Multiple Specialized Agents Implementation
  selectedAgentId: 'ma-analyst',
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),

  // Dynamic Canvas Elements (Charts, Tables) Stream Implementation
  canvasElements: [],
  addCanvasElement: (el) => set((state) => ({
    canvasElements: [
      ...state.canvasElements,
      {
        id: Math.random().toString(),
        type: el.type,
        title: el.title,
        data: el.data,
        timestamp: new Date().toLocaleTimeString()
      }
    ]
  })),
  clearCanvasElements: () => set({ canvasElements: [] }),

  // Agent Gateway Logging & Telemetry Traces — real entries from Cloud Logging
  gatewayLogs: [],
  addGatewayLog: (log) => set((state) => ({
    gatewayLogs: [
      ...state.gatewayLogs,
      {
        id: Math.random().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: log.type,
        text: log.text
      }
    ]
  })),
  mergeGatewayLogs: (entries) => set((state) => {
    const seen = new Set(state.gatewayLogs.map((l) => l.correlationId).filter(Boolean));
    const fresh = entries.filter((e) => e.correlationId && !seen.has(e.correlationId));
    if (fresh.length === 0) return {} as any;
    const mapped = fresh.map((e) => {
      const decision = e.decision;
      const type = decision === 'DENY' ? 'policy' : decision === 'ALLOW' ? 'auth' : 'engine';
      const ts = e.ts ? new Date(e.ts).toLocaleTimeString() : new Date().toLocaleTimeString();
      const text =
        e.text ||
        `[GATEWAY-${decision || 'EVENT'}] ${e.tool ?? '?'} → ${(e.targetService || '').split(':').pop()} ` +
        `[${e.rule || '?'}] ${e.reason || ''}`;
      return {
        id: e.correlationId!,
        timestamp: ts,
        type,
        text,
        decision: decision as 'ALLOW' | 'DENY' | undefined,
        rule: e.rule,
        reason: e.reason,
        tool: e.tool,
        user: e.user || undefined,
        sourceAgent: e.sourceAgent,
        targetService: e.targetService,
        correlationId: e.correlationId,
        latencyMs: e.latencyMs,
        logUrl: e.logUrl,
      };
    });
    return { gatewayLogs: [...state.gatewayLogs, ...mapped] };
  }),
  clearGatewayLogs: () => set({ gatewayLogs: [] }),
}));
