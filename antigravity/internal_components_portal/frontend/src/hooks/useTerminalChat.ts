import { useChat } from '@ai-sdk/react';
import { useEffect, useState } from 'react';
import { useDashboardStore } from '../store/dashboardStore';
import type { ProjectCardData } from '../store/dashboardStore';

export interface ThoughtStatus {
  message: string;
  icon: string;
  pulse: boolean;
}

export interface TelemetryEvent {
  step: string;
  duration_s: number;
}

export interface TokenUsage {
  prompt: number;
  candidates: number;
  total: number;
}

export interface StreamPayload {
  type?: string;
  data?: unknown;
  pulse?: boolean;
  message?: string;
  icon?: string;
  reasoning?: unknown;
  tokens?: unknown;
  adk_events?: unknown;
  [key: string]: unknown;
}

export function useTerminalChat(token: string | null, model: string = 'gemini-3-flash-preview', routerMode: string = 'all_mcp') {
  const addProjectCard = useDashboardStore((s) => s.addProjectCard);
  const [thoughtStatus, setThoughtStatus] = useState<ThoughtStatus | null>(null);
  const [usedSharePoint, setUsedSharePoint] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<TelemetryEvent[]>([]);
  const [reasoningSteps, setReasoningSteps] = useState<string[]>([]);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage | null>(null);
  const [publicInsight, setPublicInsight] = useState<string>('');
  const [isPublicInsightStreaming, setIsPublicInsightStreaming] = useState<boolean>(false);
  const [adkEvents, setAdkEvents] = useState<Record<string, unknown>[]>([]);

  const apiEndpoint = import.meta.env.VITE_BACKEND_URL || (typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://mcp-sharepoint-server-440133963879.us-central1.run.app/chat'
    : '/chat');

  const { messages, input, setMessages, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: apiEndpoint,
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: { model, routerMode },
  });

  // Listen for Type 2 Data events 
  useEffect(() => {
    if (!data || data.length === 0) return;

    // Vercel AI SDK appends JSON objects sent via AIStreamProtocol.data() to the `data` array.
    // Since Public Agent and SharePoint Agent emit concurrently, we must find the *latest* status
    // and *latest* public_insight by searching backwards, avoiding dropped updates if they clobber
    // each other in the same React render cycle.

    // Wrap in setTimeout to avoid 'Calling setState synchronously within an effect' warning
    setTimeout(() => {
      let foundStatus = false;
      let foundInsight = false;
      let foundTelemetry = false;

      for (let i = data.length - 1; i >= 0; i--) {
        const currentChunk = data[i] as StreamPayload | StreamPayload[];
        const payloads: StreamPayload[] = Array.isArray(currentChunk) ? currentChunk : [currentChunk];
        // Reverse through payloads inside the chunk too
        for (let j = payloads.length - 1; j >= 0; j--) {
          const p = payloads[j];
          if (!p) continue;

          if (p.type === 'public_insight' && !foundInsight) {
            setPublicInsight((p.data as string) || '');
            setIsPublicInsightStreaming(p.pulse === true);
            foundInsight = true;
          } else if (p.type === 'status' && !foundStatus) {
            if (p.icon === 'search' || p.icon === 'database' || p.icon === 'file-search') {
              setUsedSharePoint(true);
            }
            setThoughtStatus({
              message: p.message || '',
              icon: p.icon || 'cpu',
              pulse: p.pulse !== false
            });
            foundStatus = true;
          }

          if (p.type === 'telemetry' && !foundTelemetry) {
            if (p.reasoning) setReasoningSteps(p.reasoning as string[]);
            if (p.tokens) setTokenUsage(p.tokens as TokenUsage);
            if (p.data) setTelemetry(p.data as TelemetryEvent[]);
            if (p.adk_events) setAdkEvents(p.adk_events as Record<string, unknown>[]);
            foundTelemetry = true;
          }
        }
      }

      const lastChunk = data[data.length - 1] as StreamPayload | StreamPayload[];
      const lastPayloads: StreamPayload[] = Array.isArray(lastChunk) ? lastChunk : [lastChunk];
      for (const p of lastPayloads) {
        if (!p) continue;
        if (p.type === 'project_card' && p.data) {
          addProjectCard(p.data as ProjectCardData);
        }
      }
    }, 0);
  }, [data, addProjectCard]);

  useEffect(() => {
    if (!isLoading) {
      setTimeout(() => setThoughtStatus(null), 1500);
    }
  }, [isLoading]);

  const customHandleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // We don't clear projectCards here to avoid a blank screen "flash"
    // Instead, we mark the current state as "stale" or simply wait for the first data chunk.
    setUsedSharePoint(false);
    setTelemetry([]);
    setReasoningSteps([]);
    setTokenUsage(null);
    setPublicInsight('');
    setAdkEvents([]);
    setMessages([]); // This clears the chat list, which is expected for a new query
    setThoughtStatus({ message: 'Initializing Zero-Leak Security Proxy...', icon: 'shield-alert', pulse: true });

    // We'll clear the cards just before submitting, but we'll improve this with a "clearing" event if needed
    // clearCards(); 

    handleSubmit(e);
  };

  return { messages, input, handleInputChange, handleSubmit: customHandleSubmit, isLoading, hasData: !!data && data.length > 0, thoughtStatus, usedSharePoint, telemetry, reasoningSteps, tokenUsage, publicInsight, isPublicInsightStreaming, adkEvents };
}
