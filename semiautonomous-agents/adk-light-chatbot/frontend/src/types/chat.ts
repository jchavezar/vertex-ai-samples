export interface GroundingSource {
  title: string;
  uri: string;
}

export interface GroundingData {
  queries?: string[];
  sources?: GroundingSource[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  grounding?: GroundingData;
  activeTool?: string;
  error?: boolean;
}

export interface ModelInfo {
  id: string;
  name: string;
  badge: string;
  description: string;
}

export interface ChatConfig {
  model: string;
  instruction: string;
  enableSearch: boolean;
}

export type StreamEventType = 'text' | 'tool_call' | 'grounding' | 'done' | 'error';

export interface StreamEvent {
  type: StreamEventType;
  content?: string;
  name?: string;
  args?: Record<string, unknown>;
  queries?: string[];
  sources?: GroundingSource[];
  message?: string;
}
