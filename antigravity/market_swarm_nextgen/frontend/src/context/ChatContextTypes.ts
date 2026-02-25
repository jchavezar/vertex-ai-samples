import { createContext } from 'react';
import { Message } from '@ai-sdk/react';
import { NodeMetrics, ProcessorTopology } from '../components/dashboard/types';

export interface LogEntry {
  timestamp: string;
  type: 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'error' | 'system' | 'debug' | 'system_status';
  content: string;
  tool?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  duration?: number;
}

export interface ChatContextType {
  messages: Message[];
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement> | React.KeyboardEvent) => void;
  isLoading: boolean;
  traceLogs: LogEntry[];
  topology: ProcessorTopology | null;
  executionPath: string[];
  nodeDurations: Record<string, number>;
  nodeMetrics: Record<string, NodeMetrics>;
  lastLatency: number | null;
  startTime: number | null;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  sessionId: string;
  selectedFile: string | null;
  setSelectedFile: (file: string | null) => void;
  selectedVideoUrl: string | null;
  setSelectedVideoUrl: (url: string | null) => void;
  stop: () => void;
  resetChat: () => void;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);
