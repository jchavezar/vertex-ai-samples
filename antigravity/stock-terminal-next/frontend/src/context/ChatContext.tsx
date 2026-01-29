import { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';
import { useChat } from 'ai/react';
import { useDashboardStore, WidgetData } from '../store/dashboardStore';
import { ProcessorTopology } from '../components/chat/AgentGraph';

interface LogEntry {
  type: 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'error' | 'system' | 'debug' | 'system_status';
  content?: string;
  tool?: string;
  args?: any;
  result?: any;
  duration?: number | string;
  timestamp: string;
}

interface ChatContextType {
  messages: any[];
  input: string;
  handleInputChange: (e: any) => void;
  handleSubmit: (e: any) => void;
  isLoading: boolean;
  traceLogs: LogEntry[];
  topology: ProcessorTopology | null;
  executionPath: string[];
  nodeDurations: Record<string, number>;
  nodeMetrics: Record<string, any>;
  lastLatency: number | null;
  startTime: number | null;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  sessionId: string;
  stop: () => void;
  resetChat: () => void;
  image: string | null;
  mimeType: string | null;
  handleImageSelect: (file: File) => Promise<void>;
  clearImage: () => void;
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
  const [selectedModel, setSelectedModel] = useState<string>("gemini-3-flash-preview");
  const [sessionId] = useState(() => Math.random().toString(36).substring(7)); // Simple unique ID for this tab session
  const [image, setImage] = useState<string | null>(null);
  const [mimeType, setMimeType] = useState<string | null>(null);
  
  useEffect(() => {
    console.log("[ChatContext] Initialized with Session ID:", sessionId);
  }, [sessionId]);

  // Timer Ref
  const startTimeRef = useRef<number | null>(null);

  const { messages, input, handleInputChange, handleSubmit: originalHandleSubmit, data, isLoading, stop, setMessages } = useChat({
    api: 'http://localhost:8001/chat',
    body: {
       model: selectedModel,
      sessionId: sessionId,
      image: image,
      mimeType: mimeType
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

  const handleSubmit = (e: any) => {
      const now = Date.now();
      startTimeRef.current = now;
      setStartTime(now);
      setLastLatency(null); // Reset on new query
      originalHandleSubmit(e);
    // Clear image after submit (short delay to ensure it's picked up?)
    // Actually request is formed immediately.
    setTimeout(() => {
      setImage(null);
      setMimeType(null);
    }, 100);
  };

  const handleImageSelect = async (file: File) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      // result is "data:image/png;base64,....."
      if (result) {
        // Split to get base64
        const parts = result.split(',');
        if (parts.length > 1) {
          const mime = parts[0].match(/:(.*?);/)?.[1] || file.type;
          const b64 = parts[1];
          setMimeType(mime);
          setImage(b64);
        }
      }
    };
    reader.readAsDataURL(file);
  };

  const clearImage = () => {
    setImage(null);
    setMimeType(null);
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
  const addTraceLog = (type: LogEntry['type'], content: string, tool?: string, args?: any, result?: any, duration?: number) => {
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
    const newItems = data.slice(startIdx);

    if (newItems.length === 0) return;

    newItems.forEach(item => {
      const payload = item as any;

      // 1. Widget Detection
      if (payload && typeof payload === 'object') {
        if (payload.type === 'chart' || payload.type === 'stats') {
          setActiveWidget(payload as WidgetData);
        }
      }

      // 2. Event Parsing for Trace & Graph
      // Trace Event
      if (payload.type === 'trace' && payload.data) {
        // - [x] Feature: Analyst Copilot (Macro/Investability) <!-- id: 6 -->
        // - [x] Update Implementation Plan with Creative Enhancements <!-- id: 6.1 -->
        // - [x] Implement `src/analyst_copilot.py` (Strategist Agent) <!-- id: 6.2 -->
        // - [x] Add `update_dashboard_view` tool and UI signaling <!-- id: 6.3 -->
        // - [x] Integrate into `smart_agent.py` as a delegated specialist <!-- id: 6.4 -->
        // - [x] Verify scenario with Browser Subagent <!-- id: 6.5 -->
        // - [x] Provide Testing Script for user <!-- id: 6.6 -->
        // - [/] Feature: Creative Analyst UI (Strategist Mode) <!-- id: 7 -->
        // - [/] Implement `MacroPerspectiveCard` (Glassmorphic Container) <!-- id: 7.1 -->
        // - [ ] Implement `PeerPackGrid` (Interactive Competitor Cards) <!-- id: 7.2 -->
        // - [ ] Update `StreamingMarkdown` with JSON/Tag Detection <!-- id: 7.3 -->
        // - [ ] Add Macro Overlay to Dashboard <!-- id: 7.4 -->
        // - [ ] Update Backend to return structured Peer Pack data <!-- id: 7.5 -->
        // - [ ] Final UI/UX Verification in Browser <!-- id: 7.6 -->
        const traceData = payload.data;
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
          // We use functional update to ensure we don't overwrite if multiple calls happen fast
          // detailed check: useDashboardStore.getState().nodeDurations
          const currentDurations = useDashboardStore.getState().nodeDurations;
          // Avoid unnecessary excessive updates if possible, but safe to set
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
        setTopology(payload.data);
        useDashboardStore.getState().setTopology(payload.data);
      }

      // Tool Call (Protocol 9 Check)
      if (payload.type === 'tool_call') {
        addTraceLog('tool_call', '', payload.tool, payload.args);
        const nodeId = payload.tool;
        const currentPath = useDashboardStore.getState().executionPath;
        if (currentPath[currentPath.length - 1] !== nodeId) {
          setExecutionPath([...currentPath, nodeId]);
        }
      }

      // Tool Result (Protocol 9 Check)
      if (payload.type === 'tool_result') {
        // Note: Protocol 9 usually doesn't have duration. We rely on 'trace' for that.
        // But if it did:
        addTraceLog('tool_result', '', payload.tool, null, payload.result, payload.duration);
      }

      // Error
      if (payload.type === 'error') {
        addTraceLog('error', payload.message);
      }

      // dashboard_command (New from Analyst Copilot)
      if (payload.type === 'dashboard_command') {
        const { view, payload: cmdPayload } = payload;
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
        const toolName = payload.tool;
        const duration = payload.duration;

        const currentMetrics = useDashboardStore.getState().nodeMetrics || {};
        const toolMetrics = currentMetrics[toolName] || {};
        const currentLatencies = toolMetrics.latencies || [];

        // Append new latency
        const newLatencies = [...currentLatencies, duration];

        setNodeMetrics({
          ...currentMetrics,
          [toolName]: {
            ...toolMetrics,
            latencies: newLatencies
          }
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
    resetChat,
    image,
    mimeType,
    handleImageSelect,
    clearImage
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
