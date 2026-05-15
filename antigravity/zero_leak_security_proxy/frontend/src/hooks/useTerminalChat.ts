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

export function useTerminalChat(token: string | null, model: string = 'gemini-3-flash-preview', mode: 'chat' | 'deep' = 'chat') {
  const addProjectCard = useDashboardStore((s) => s.addProjectCard);
  const [thoughtStatus, setThoughtStatus] = useState<ThoughtStatus | null>(null);
  const [usedSharePoint, setUsedSharePoint] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<TelemetryEvent[]>([]);
  const [reasoningSteps, setReasoningSteps] = useState<string[]>([]);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage | null>(null);
  const [publicInsight, setPublicInsight] = useState<string>('');
  const [isPublicInsightStreaming, setIsPublicInsightStreaming] = useState<boolean>(false);

  const apiEndpoint = import.meta.env.VITE_BACKEND_URL || (typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://mcp-sharepoint-server-REDACTED_PROJECT_NUMBER.us-central1.run.app/chat'
    : '/chat');

  // @ai-sdk/react v1 captures the `headers` option once at hook init and
  // ignores `fetch`. We install a one-time global fetch wrapper, scoped to the
  // backend chat URL, that pulls the MSAL access token straight from MSAL's
  // sessionStorage cache at request time — bypassing React state entirely so
  // there's no race with async token acquisition.
  void token;
  useEffect(() => {
    const w = window as unknown as { __zlspOriginalFetch?: typeof fetch };
    if (w.__zlspOriginalFetch) return;
    w.__zlspOriginalFetch = window.fetch.bind(window);
    const readMsalAccessToken = (): string | null => {
      try {
        for (let i = 0; i < sessionStorage.length; i++) {
          const k = sessionStorage.key(i);
          if (!k || !k.includes('accesstoken') || k.includes('refresh')) continue;
          const raw = sessionStorage.getItem(k);
          if (!raw) continue;
          const v = JSON.parse(raw);
          if (v && typeof v.secret === 'string') return v.secret;
        }
      } catch (_) { /* ignore */ }
      return null;
    };
    window.fetch = ((input: RequestInfo | URL, init: RequestInit = {}) => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : (input as Request).url;
      if (url && url.startsWith(apiEndpoint)) {
        const t = readMsalAccessToken();
        if (t) {
          const headers = new Headers(init.headers);
          if (!headers.has('Authorization')) headers.set('Authorization', `Bearer ${t}`);
          return w.__zlspOriginalFetch!(input, { ...init, headers });
        }
      }
      return w.__zlspOriginalFetch!(input, init);
    }) as typeof fetch;
  }, [apiEndpoint]);

  // We pass model/mode per-submit (see customHandleSubmit) instead of via the
  // hook init body, because @ai-sdk/react v1 captures `body` once at mount and
  // would freeze the user's first toggle state forever.
  const { messages, input, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: apiEndpoint,
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
    let foundTelemetry = false;

    for (let i = data.length - 1; i >= 0; i--) {
      const currentChunk = data[i] as any;
      const payloads: any[] = Array.isArray(currentChunk) ? currentChunk : [currentChunk];
      // Reverse through payloads inside the chunk too
      for (let j = payloads.length - 1; j >= 0; j--) {
        const p = payloads[j] as any;
        if (!p) continue;

        if (p.type === 'public_insight' && !foundInsight) {
          setPublicInsight(p.data || '');
          setIsPublicInsightStreaming(p.pulse === true);
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

        if (p.type === 'telemetry' && !foundTelemetry) {
          if (p.reasoning) setReasoningSteps(p.reasoning as string[]);
          if (p.tokens) setTokenUsage(p.tokens as TokenUsage);
          if (p.data) setTelemetry(p.data as TelemetryEvent[]);
          foundTelemetry = true;
        }
      }
    }

    const lastChunk = data[data.length - 1] as any;
    const payloads: any[] = Array.isArray(lastChunk) ? lastChunk : [lastChunk];
    for (const p of payloads) {
      if (!p) continue;
      if (p.type === 'project_card' && p.data) {
        addProjectCard(p.data as ProjectCardData);
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
    // Reset transient per-query state but KEEP the chat history so users can
    // see the running thread. Vercel useChat will append the new user/assistant
    // turns to the existing messages array.
    setUsedSharePoint(false);
    setTelemetry([]);
    setReasoningSteps([]);
    setTokenUsage(null);
    setPublicInsight('');
    setThoughtStatus({ message: 'Initializing Zero-Leak Security Proxy...', icon: 'shield-alert', pulse: true });
    handleSubmit(e, { body: { model, mode } });
  };

  return { messages, input, handleInputChange, handleSubmit: customHandleSubmit, isLoading, hasData: !!data && data.length > 0, thoughtStatus, usedSharePoint, telemetry, reasoningSteps, tokenUsage, publicInsight, isPublicInsightStreaming };
}
