export type ToolCategory =
  | 'Search'
  | 'Database Query'
  | 'Code Execution'
  | 'Financial Modeling'
  | 'Dynamic Visualization'
  | 'System Tool';

export interface ToolExecution {
  tool_call_id: string;
  tool_name: string;
  category: ToolCategory;
  icon?: string;
  label?: string;
  arguments: Record<string, any>;
  status: 'running' | 'success' | 'error';
  output?: Record<string, any>;
  startTime: number;
  endTime?: number;
  durationMs?: number;
}

export interface ChartDataset {
  label: string;
  data: number[];
  color?: string;
}

export interface KpiHighlight {
  label: string;
  value: string;
  trend?: string;
}

export interface ArtifactData {
  artifact_id: string;
  artifact_type: 'interactive_chart' | 'executive_summary' | 'code_snippet';
  chart_type?: 'line' | 'bar' | 'area' | 'donut' | 'radar';
  title: string;
  subtitle?: string;
  labels?: string[];
  datasets?: ChartDataset[];
  kpi_highlights?: KpiHighlight[];
  content?: string;
  language?: string;
  created_at: number;
}

export interface TokenUsage {
  prompt_tokens: number;
  candidate_tokens: number;
  thought_tokens: number;
  total_tokens: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thoughts: string[];
  tools: ToolExecution[];
  artifacts: ArtifactData[];
  timestamp: number;
  isStreaming?: boolean;
  elapsedSeconds?: number;
  usage?: TokenUsage;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  model: string;
  runner: string;
  adk_version: string;
  project: string;
  location: string;
  active_sessions_count: number;
  capabilities: string[];
}

export interface ToolDefinition {
  name: string;
  category: ToolCategory;
  badge: string;
  description: string;
  color: string;
}
