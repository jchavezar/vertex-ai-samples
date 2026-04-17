export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  model?: string;
}

export interface Session {
  id: string;
  title: string;
  created_at: number;
  updated_at: number;
  message_count: number;
  model: string;
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result?: string;
}

export type ModelKey = '2.5-flash' | '2.5-pro';

export interface WSMessage {
  type: 'chunk' | 'done' | 'error' | 'session';
  content?: string;
  session_id?: string;
}
