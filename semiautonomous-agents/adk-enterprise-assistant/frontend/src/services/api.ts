import type { HealthStatus, ToolDefinition, ArtifactData, TokenUsage } from '../types';

export async function fetchHealth(): Promise<HealthStatus> {
  const resp = await fetch('/api/health');
  if (!resp.ok) {
    throw new Error(`Health check failed: HTTP ${resp.status}`);
  }
  return resp.json();
}

export async function fetchTools(): Promise<ToolDefinition[]> {
  try {
    const resp = await fetch('/api/tools');
    if (!resp.ok) return [];
    const data = await resp.json();
    return data.tools || [];
  } catch {
    return [];
  }
}

export async function initSession(sessionId?: string, userId = 'enterprise_user'): Promise<{ session_id: string; user_id: string }> {
  const resp = await fetch('/api/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, user_id: userId }),
  });
  if (!resp.ok) {
    throw new Error(`Failed to initialize session: HTTP ${resp.status}`);
  }
  return resp.json();
}

export interface StreamChatCallbacks {
  onThinking: (thought: string) => void;
  onToolStart: (tool: {
    tool_call_id: string;
    tool_name: string;
    category: any;
    icon?: string;
    label?: string;
    arguments: Record<string, any>;
  }) => void;
  onToolEnd: (tool: {
    tool_call_id: string;
    tool_name: string;
    category: any;
    status: 'success' | 'error';
    output: Record<string, any>;
  }) => void;
  onContent: (delta: string) => void;
  onArtifact: (artifact: ArtifactData) => void;
  onDone: (data: { elapsed_seconds: number; model: string; usage: TokenUsage }) => void;
  onError: (error: string) => void;
}

export async function streamChat(
  message: string,
  sessionId: string,
  userId: string,
  callbacks: StreamChatCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const resp = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: userId,
    }),
    signal,
  });

  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`Chat API error (HTTP ${resp.status}): ${errText}`);
  }

  if (!resp.body) {
    throw new Error('No response body returned from chat stream.');
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith('data:')) continue;

      const jsonStr = trimmed.substring(5).trim();
      if (!jsonStr) continue;

      try {
        const payload = JSON.parse(jsonStr);

        switch (payload.type) {
          case 'thinking':
            if (payload.thought) callbacks.onThinking(payload.thought);
            break;
          case 'tool_start':
            callbacks.onToolStart(payload);
            break;
          case 'tool_end':
            callbacks.onToolEnd(payload);
            break;
          case 'content':
            if (payload.delta) callbacks.onContent(payload.delta);
            break;
          case 'artifact':
            if (payload.artifact) callbacks.onArtifact(payload.artifact);
            break;
          case 'done':
            callbacks.onDone(payload);
            break;
          case 'error':
            callbacks.onError(payload.error || payload.message || 'Stream processing error');
            break;
        }
      } catch (parseErr) {
        console.warn('Failed to parse SSE line:', line, parseErr);
      }
    }
  }
}
