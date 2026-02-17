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

  const { messages, input, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: '/chat',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: { model },
  });

  // Listen for Type 2 Data events 
  useEffect(() => {
    if (!data || data.length === 0) return;
    const latestList = data[data.length - 1];

    // Handle Vercel AI SDK array parsing combinations
    const payloads = Array.isArray(latestList) ? latestList : [latestList];

    for (const rawP of payloads) {
      if (!rawP) continue;
      const p = rawP as any;
      if (p.type === 'project_card' && p.data) {
        addProjectCard(p.data as ProjectCardData);
      } else if (p.type === 'status') {
        if (p.icon === 'search' || p.icon === 'database' || p.icon === 'file-search') {
          setUsedSharePoint(true);
        }
        setThoughtStatus({
          message: p.message,
          icon: p.icon || 'cpu',
          pulse: p.pulse !== false
        });
      } else if (p.type === 'telemetry') {
        if (p.data) setTelemetry(p.data as TelemetryEvent[]);
        if (p.reasoning) setReasoningSteps(p.reasoning as string[]);
        if (p.tokens) setTokenUsage(p.tokens as TokenUsage);
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
    setThoughtStatus({ message: 'Requesting proxy access...', icon: 'shield-alert', pulse: true });
    handleSubmit(e);
  };

  return { messages, input, handleInputChange, handleSubmit: customHandleSubmit, isLoading, hasData: !!data && data.length > 0, thoughtStatus, usedSharePoint, telemetry, reasoningSteps, tokenUsage };
}
