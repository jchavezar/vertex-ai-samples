import { create } from 'zustand';

export interface AgentNode {
  id: string;
  label: string;
  status: 'idle' | 'active' | 'complete' | 'error';
  type: 'orchestrator' | 'audit' | 'tax' | 'compliance';
}

export interface DeploymentStats {
  materiality_reached: number; // 0 to 100
  total_exposure: number;
  anomalies_found: number;
  active_agent: string;
}

interface VerityState {
  agents: AgentNode[];
  stats: DeploymentStats;
  reasoning: string[];
  findings: any[];
  isSignOffVisible: boolean;

  updateAgentStatus: (id: string, status: AgentNode['status']) => void;
  updateStats: (updates: Partial<DeploymentStats>) => void;
  addReasoning: (message: string) => void;
  setFindings: (findings: any[]) => void;
  setSignOffVisible: (visible: boolean) => void;
  reset: () => void;
}

export const useVerityStore = create<VerityState>((set) => ({
  agents: [
    { id: 'orchestrator', label: 'Verity Orchestrator', status: 'idle', type: 'orchestrator' },
    { id: 'audit_agent', label: 'Forensic Audit Agent', status: 'idle', type: 'audit' },
    { id: 'tax_agent', label: 'Tax Compliance Agent', status: 'idle', type: 'tax' },
  ],
  stats: {
    materiality_reached: 0,
    total_exposure: 0,
    anomalies_found: 0,
    active_agent: 'none'
  },
  reasoning: [],
  findings: [],
  isSignOffVisible: false,

  updateAgentStatus: (id, status) => set((state) => ({
    agents: state.agents.map(a => a.id === id ? { ...a, status } : a)
  })),

  updateStats: (updates) => set((state) => ({
    stats: { ...state.stats, ...updates }
  })),

  addReasoning: (message) => set((state) => ({
    reasoning: [message, ...state.reasoning].slice(0, 50)
  })),

  setFindings: (findings) => set({ findings }),

  setSignOffVisible: (visible) => set({ isSignOffVisible: visible }),

  reset: () => set({
    reasoning: [],
    findings: [],
    stats: { materiality_reached: 0, total_exposure: 0, anomalies_found: 0, active_agent: 'none' },
    isSignOffVisible: false,
    agents: [
      { id: 'orchestrator', label: 'Verity Orchestrator', status: 'idle', type: 'orchestrator' },
      { id: 'audit_agent', label: 'Forensic Audit Agent', status: 'idle', type: 'audit' },
      { id: 'tax_agent', label: 'Tax Compliance Agent', status: 'idle', type: 'tax' },
    ]
  })
}));
