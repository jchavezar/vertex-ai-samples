// Vertex Cowork Type Definitions

export interface Model {
  model_id: string;
  provider: "vertex" | "model_garden";
  display_name: string;
  capabilities: string[];
  supports_tools: boolean;
  supports_vision: boolean;
}

export interface MCPServer {
  server_id: string;
  name: string;
  transport: "stdio" | "sse" | "http";
  command?: string;
  url?: string;
  tools: string[];
  resources: string[];
  connected: boolean;
}

export type AgentType =
  | "llm"
  | "sequential"
  | "parallel"
  | "loop"
  | "supervisor";

export type Framework = "adk" | "langgraph";

export interface Agent {
  agent_id: string;
  name: string;
  description: string;
  model_id: string;
  framework: Framework;
  agent_type: AgentType;
  system_prompt?: string;
  tools: string[];
  mcp_servers: string[];
  subagents: string[];
  config?: Record<string, unknown>;
}

export interface AgentCreateRequest {
  agent_id: string;
  name: string;
  description?: string;
  model_id: string;
  framework: Framework;
  agent_type: AgentType;
  system_prompt?: string;
  tools?: string[];
  mcp_servers?: string[];
  subagents?: string[];
  max_iterations?: number;
  temperature?: number;
  config?: Record<string, unknown>;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  tool_calls?: ToolCall[];
  timestamp: Date;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result?: string;
}

export interface ChatResponse {
  content: string;
  tool_calls: ToolCall[];
  agent_id: string;
  success: boolean;
  error?: string;
}

export interface FrameworkInfo {
  type: Framework;
  name: string;
  description: string;
  features: string[];
  best_for: string[];
}

export interface EvaluationCase {
  case_id: string;
  description: string;
  input_message: string;
  expected_tools?: string[];
  expected_tool_order?: "exact" | "in_order" | "any";
  expected_content_contains?: string[];
  expected_content_not_contains?: string[];
}

export interface EvaluationResult {
  case_id: string;
  passed: boolean;
  score: number;
  actual_response: string;
  actual_tools: string[];
  errors: string[];
}

export interface EvaluationReport {
  agent_id: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  overall_score: number;
  results: EvaluationResult[];
}
