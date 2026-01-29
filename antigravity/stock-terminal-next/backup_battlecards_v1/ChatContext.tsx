import React, { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';
import { useChat, Message } from 'ai/react';
import { useDashboardStore, WidgetData } from '../store/dashboardStore';
import { ProcessorTopology, NodeMetrics } from '../components/dashboard/types';

interface LogEntry {
  type: 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'error' | 'system' | 'debug' | 'system_status';
  content?: string;
  tool?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  duration?: number | string;
  timestamp: string;
}

interface ChatContextType {
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
  stop: () => void;
  resetChat: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const setActiveWidget = useDashboardStore((s) => s.setActiveWidget);
  const setExecutionPath = useDashboardStore((s) => s.setExecutionPath);
  const executionPath = useDashboardStore((s) => s.executionPath);
  const setNodeDurations = useDashboardStore((s) => s.setNodeDurations);
  const nodeDurations = useDashboardStore((s) => s.nodeDurations);
  const setNodeMetrics = useDashboardStore((s) => s.setNodeMetrics);
  const nodeMetrics = useDashboardStore((s) => s.nodeMetrics);

  const [traceLogs, setTraceLogs] = useState<LogEntry[]>([]);
  const [topology, setTopology] = useState<ProcessorTopology | null>(null);
  const [lastLatency, setLastLatency] = useState<number | null>(null);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>("gemini-2.5-flash-lite");
  const [sessionId] = useState(() => Math.random().toString(36).substring(7)); // Simple unique ID for this tab session
  
  useEffect(() => {
    console.log("[ChatContext] Initialized with Session ID:", sessionId);
  }, [sessionId]);

  // Timer Ref
  const startTimeRef = useRef<number | null>(null);

  const { messages, input, handleInputChange, handleSubmit: originalHandleSubmit, data, isLoading, stop, setMessages } = useChat({
    api: 'http://localhost:8001/chat',
    body: {
       model: selectedModel,
       sessionId: sessionId
    },
    
    onResponse: (resp) => {
       console.log("[ChatContext] Response started:", resp.status, resp.statusText);
    },
    
    // AI SDK Protocol: 'data' contains the accumulated Type 2 events
    onFinish: (message) => {
        console.log("Chat finished:", message);
    }
  });

  // Robust Timer using isLoading state
  // WE ONLY STOP here. We start in handleSubmit to capture the "Enter" key press time.
  // Robust Timer using isLoading state
  // WE ONLY STOP here. We start in handleSubmit to capture the "Enter" key press time.
  useEffect(() => {
    if (!isLoading && startTimeRef.current) {
        // Finished loading
        const duration = (Date.now() - startTimeRef.current) / 1000;
        setLastLatency(Number(duration.toFixed(2)));
        
        // CRITICAL FIX: Do NOT reset startTimeRef here.
        // We keep it so if isLoading flickers (tool calls), we preserve the original start time.
        // It will be overwritten only when handleSubmit is called again for a new query.
        
    } else if (isLoading && !startTimeRef.current) {
        // Fallback: If loading started without handleSubmit (e.g. reload or edge case), set start time
        // This handles cases where handleSubmit didn't fire (rare)
        startTimeRef.current = Date.now();
        setLastLatency(null);
    }
  }, [isLoading]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement> | React.KeyboardEvent) => {
      const now = Date.now();
      startTimeRef.current = now;
      setStartTime(now);
      setLastLatency(null); // Reset on new query
    originalHandleSubmit(e as React.FormEvent<HTMLFormElement>); // useChat's handleSubmit expects FormEvent or SyntheticEvent
  };

  const resetChat = () => {
    stop();
    setMessages([]);
    setTraceLogs([]);
    setTopology(null);
    setLastLatency(null);
    setStartTime(null);
    startTimeRef.current = null;

    // Reset Store states
    setExecutionPath([]);
    setNodeDurations({});
    setNodeMetrics({});
    setActiveWidget(null);
  };

  // Basic Trace Log helper
  const addTraceLog = (type: LogEntry['type'], content: string, tool?: string, args?: Record<string, unknown>, result?: unknown, duration?: number) => {
    setTraceLogs(prev => [...prev, {
      type,
      content,
      tool,
      args,
      result,
      duration,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  // Add user message to trace on submit
  useEffect(() => {
    if (messages.length > 0 && messages[messages.length - 1].role === 'user') {
      addTraceLog('user', messages[messages.length - 1].content);
      setExecutionPath([]); // Reset path on new query
      setNodeDurations({}); // Reset durations on new query
    }
  }, [messages.length, setExecutionPath, setNodeDurations]);


  interface StreamEvent {
    type: 'chart' | 'stats' | 'trace' | 'topology' | 'tool_call' | 'tool_result' | 'error' | 'dashboard_command' | 'latency';
    data?: unknown;
    tool?: string;
    args?: Record<string, unknown>;
    result?: unknown;
    duration?: number;
    message?: string;
    view?: string;
    payload?: unknown;
  }

  interface TraceLogPayload {
    type?: LogEntry['type'];
    content?: string;
    tool?: string;
    args?: Record<string, unknown>;
    result?: unknown;
    duration?: number;
    metrics?: NodeMetrics;
  }

  interface DashboardCommandPayload {
    ticker?: string;
  }

  // Track processed data index to avoid missing events in a batch
  const processedDataLengthRef = useRef(0);

  // Reactive Data Processor
  useEffect(() => {
    if (!data || data.length === 0) {
      processedDataLengthRef.current = 0; // Reset on clear
      return;
    }

    // Process only NEW items
    const startIdx = processedDataLengthRef.current;
    const newItems = data.slice(startIdx) as unknown as StreamEvent[];

    if (newItems.length === 0) return;

    newItems.forEach((payload) => {

      // 1. Widget Detection
      if (payload && typeof payload === 'object') {
        if (payload.type === 'chart' || payload.type === 'stats') {
          setActiveWidget(payload as unknown as WidgetData);
        }
      }

      // 2. Event Parsing for Trace & Graph
      // Trace Event
      if (payload.type === 'trace' && payload.data) {
        const traceData = payload.data as TraceLogPayload;
        addTraceLog(
          traceData.type || 'debug',
          traceData.content || '',
          traceData.tool,
          traceData.args,
          traceData.result,
          traceData.duration
        );

        // Metrics (Protocol 9 Extension for TTLT/TTFT)
        if (traceData.metrics && traceData.tool) {
          const currentMetrics = useDashboardStore.getState().nodeMetrics || {};
          setNodeMetrics({ ...currentMetrics, [traceData.tool]: traceData.metrics });
        }

        // Capture Duration
        if (traceData.tool && traceData.duration !== undefined) {
          const currentDurations = useDashboardStore.getState().nodeDurations;
          setNodeDurations({ ...currentDurations, [traceData.tool]: traceData.duration });
        }

        // Sync Execution Path
        if (traceData.type === 'tool_call' && traceData.tool) {
          const nodeId = traceData.tool;
          const currentPath = useDashboardStore.getState().executionPath;
          if (currentPath[currentPath.length - 1] !== nodeId) {
            setExecutionPath([...currentPath, nodeId]);
          }
        }
      }

      // Topology Event
      if (payload.type === 'topology') {
        setTopology(payload.data as ProcessorTopology);
        useDashboardStore.getState().setTopology(payload.data as ProcessorTopology);
      }

      // Tool Call (Protocol 9 Check)
      if (payload.type === 'tool_call' && payload.tool) {
        addTraceLog('tool_call', '', payload.tool, payload.args);
        const nodeId = payload.tool;
        const currentPath = useDashboardStore.getState().executionPath;
        if (currentPath[currentPath.length - 1] !== nodeId) {
          setExecutionPath([...currentPath, nodeId]);
        }
      }

      // Tool Result (Protocol 9 Check)
      if (payload.type === 'tool_result' && payload.tool) {
        addTraceLog('tool_result', '', payload.tool, undefined, payload.result, payload.duration);
      }

      // Error
      if (payload.type === 'error') {
        addTraceLog('error', payload.message || 'Unknown error');
      }

      // dashboard_command (New from Analyst Copilot)
      if (payload.type === 'dashboard_command') {
        const { view, payload: subPayload } = payload;
        const cmdPayload = subPayload as DashboardCommandPayload;
        const store = useDashboardStore.getState();

        if (view) {
          store.setActiveView(view);
          addTraceLog('system', `AI Command: Switched view to ${view}`);
        }

        if (cmdPayload?.ticker) {
          store.setTicker(cmdPayload.ticker);
          addTraceLog('system', `AI Command: Set ticker to ${cmdPayload.ticker}`);
        }
      }

      // Latency Metric (New Granular Event)
      if (payload.type === 'latency' && payload.tool && payload.duration) {
        const toolName = payload.tool as string;
        const duration = payload.duration as number;

        const currentMetrics = useDashboardStore.getState().nodeMetrics || {};
        const toolMetrics = (currentMetrics[toolName] || {}) as NodeMetrics;
        const currentLatencies = Array.isArray(toolMetrics.latencies) ? toolMetrics.latencies : [];

        // Append new latency
        const newLatencies = [...currentLatencies, duration];

        setNodeMetrics({
          ...currentMetrics,
          [toolName]: {
            ...toolMetrics,
            latencies: newLatencies
          } as NodeMetrics
        });
      }
    });

    // Update ref
    processedDataLengthRef.current = data.length;

  }, [data, setActiveWidget, setExecutionPath, setNodeDurations, setNodeMetrics]);

  const value = {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    traceLogs,
    topology,
    executionPath,
    nodeDurations,
    nodeMetrics,
    lastLatency,
    startTime,
    selectedModel,
    setSelectedModel,
    sessionId,
    stop,
    resetChat
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}

export function useWorkstationChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useWorkstationChat must be used within a ChatProvider');
  }
  return context;
}
