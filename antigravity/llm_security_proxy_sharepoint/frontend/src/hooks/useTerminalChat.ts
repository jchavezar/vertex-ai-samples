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

export function useTerminalChat(token: string | null, model: string = 'gemini-3-pro-preview') {
  const addProjectCard = useDashboardStore((s) => s.addProjectCard);
  const clearCards = useDashboardStore((s) => s.clearCards);
  const [thoughtStatus, setThoughtStatus] = useState<ThoughtStatus | null>(null);
  const [usedSharePoint, setUsedSharePoint] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<TelemetryEvent[]>([]);
  const [reasoningSteps, setReasoningSteps] = useState<string[]>([]);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage | null>(null);
  const [publicInsight, setPublicInsight] = useState<string>('');

  const { messages, input, setMessages, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: '/chat',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: { model },
  });

  // Listen for Type 2 Data events 
  useEffect(() => {
    if (!data || data.length === 0) return;

    // Vercel AI SDK appends JSON objects sent via AIStreamProtocol.data() to the `data` array.
    // Since Public Agent and SharePoint Agent emit concurrently, we must find the *latest* status
    // and *latest* public_insight by searching backwards, avoiding dropped updates if they clobber
    // each other in the same React render cycle.

    let foundStatus = false;
    let foundInsight = false;

    for (let i = data.length - 1; i >= 0; i--) {
      const currentChunk = data[i] as any;
      const payloads: any[] = Array.isArray(currentChunk) ? currentChunk : [currentChunk];
      // Reverse through payloads inside the chunk too
      for (let j = payloads.length - 1; j >= 0; j--) {
        const p = payloads[j] as any;
        if (!p) continue;

        if (p.type === 'public_insight' && !foundInsight) {
          setPublicInsight(p.data || '');
          foundInsight = true;
        } else if (p.type === 'status' && !foundStatus) {
          if (p.icon === 'search' || p.icon === 'database' || p.icon === 'file-search') {
            setUsedSharePoint(true);
          }
          setThoughtStatus({
            message: p.message,
            icon: p.icon || 'cpu',
            pulse: p.pulse !== false
          });
          foundStatus = true;
        }

        if (p.type === 'telemetry') {
          if (p.reasoning) setReasoningSteps(p.reasoning as string[]);
          if (p.tokens) setTokenUsage(p.tokens as TokenUsage);
          if (p.data) setTelemetry(p.data as TelemetryEvent[]);
          break; // Avoid overwriting with older telemetry from same chunk
        }
      }
    }

    const lastChunk = data[data.length - 1] as any;
    const payloads: any[] = Array.isArray(lastChunk) ? lastChunk : [lastChunk];
    for (const p of payloads) {
      if (!p) continue;
      if (p.type === 'project_card' && p.data) {
        addProjectCard(p.data as ProjectCardData);
      } else if (p.type === 'telemetry') {
        if (p.reasoning) setReasoningSteps(p.reasoning as string[]);
        if (p.tokens) setTokenUsage(p.tokens as TokenUsage);
        if (p.data) setTelemetry(p.data as TelemetryEvent[]);
      }
    }
  }, [data, addProjectCard]);

  useEffect(() => {
    if (!isLoading) {
      setTimeout(() => setThoughtStatus(null), 1500);
    }
  }, [isLoading]);

  const customHandleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearCards();
    setUsedSharePoint(false);
    setTelemetry([]);
    setReasoningSteps([]);
    setTokenUsage(null);
    setPublicInsight('');
    setMessages([]);
    setThoughtStatus({ message: 'Requesting proxy access...', icon: 'shield-alert', pulse: true });
    handleSubmit(e);
  };

  return { messages, input, handleInputChange, handleSubmit: customHandleSubmit, isLoading, hasData: !!data && data.length > 0, thoughtStatus, usedSharePoint, telemetry, reasoningSteps, tokenUsage, publicInsight };
}
