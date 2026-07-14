export interface GcpErrorItem {
  id: string;
  timestamp: string;
  severity: string;
  serviceName: string;
  resourceType: string;
  summary: string;
  fullText: string;
  logPayload: Record<string, any>;
  labels: Record<string, string>;
}

export interface HypothesisItem {
  id: string;
  title: string;
  relevanceScore?: number | null;
  overviewText: string;
  rootCauseText: string;
  remediationCommands: string[];
  recommendationText: string;
  relevantResources: string[];
}

export interface EvidenceItem {
  id: string;
  title: string;
  checkType: string;
  commandExecuted?: string | null;
  text: string;
  normalOperation?: boolean | null;
}

export interface CloudAssistDiagnostic {
  investigationName: string;
  title: string;
  executionState: string;
  recapText: string;
  hypotheses: HypothesisItem[];
  evidence: EvidenceItem[];
  rawObservationsCount: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  sourcesCited?: string[];
}
