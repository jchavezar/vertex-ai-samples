import { ModelInfo, GroundingData, StreamEvent } from '../types/chat';

const API_BASE = '';

export async function fetchModels(): Promise<{ default: string; models: ModelInfo[] }> {
  try {
    const res = await fetch(`${API_BASE}/api/models`);
    if (!res.ok) {
      throw new Error(`Failed to fetch models: ${res.statusText}`);
    }
    return await res.json();
  } catch (error) {
    console.warn('Using fallback models due to error:', error);
    return {
      default: 'gemini-2.5-flash',
      models: [
        {
          id: 'gemini-2.5-flash',
          name: 'Gemini 2.5 Flash',
          badge: 'Recomendado • Ultra Rápido',
          description: 'Modelo insignia optimizado para baja latencia y streaming fluido.'
        },
        {
          id: 'gemini-2.5-pro',
          name: 'Gemini 2.5 Pro',
          badge: 'Razonamiento Complejo',
          description: 'Modelo insignia para problemas matemáticos y análisis profundo.'
        },
        {
          id: 'gemini-3-flash-preview',
          name: 'Gemini 3 Flash Preview',
          badge: 'Preview',
          description: 'Vista previa de la próxima generación Gemini 3.'
        },
        {
          id: 'gemini-3-pro-preview',
          name: 'Gemini 3 Pro Preview',
          badge: 'Preview Avanzado',
          description: 'Vista previa de alta capacidad de razonamiento Gemini 3 Pro.'
        }
      ]
    };
  }
}

export async function resetSession(userId: string, sessionId: string): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/session/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, session_id: sessionId })
    });
  } catch (err) {
    console.error('Failed to reset session:', err);
  }
}

interface StreamChatParams {
  message: string;
  userId: string;
  sessionId: string;
  model: string;
  instruction: string;
  enableSearch: boolean;
  onChunk: (text: string) => void;
  onToolCall: (toolName: string) => void;
  onGrounding: (data: GroundingData) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export async function streamChatMessage({
  message,
  userId,
  sessionId,
  model,
  instruction,
  enableSearch,
  onChunk,
  onToolCall,
  onGrounding,
  onDone,
  onError
}: StreamChatParams): Promise<() => void> {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          message,
          user_id: userId,
          session_id: sessionId,
          model,
          instruction,
          enable_search: enableSearch
        }),
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported on response.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith(':')) continue;

          if (trimmed.startsWith('data:')) {
            const jsonStr = trimmed.substring(5).trim();
            if (!jsonStr) continue;

            try {
              const event: StreamEvent = JSON.parse(jsonStr);

              if (event.type === 'text' && event.content) {
                onChunk(event.content);
              } else if (event.type === 'tool_call' && event.name) {
                onToolCall(event.name);
              } else if (event.type === 'grounding') {
                onGrounding({
                  queries: event.queries || [],
                  sources: event.sources || []
                });
              } else if (event.type === 'done') {
                onDone();
                return;
              } else if (event.type === 'error') {
                onError(event.message || 'Error desconocido del agente.');
                return;
              }
            } catch (err) {
              console.warn('Failed to parse SSE line:', jsonStr, err);
            }
          }
        }
      }

      onDone();
    } catch (err: unknown) {
      if ((err as Error)?.name === 'AbortError') {
        onDone();
      } else {
        onError((err as Error)?.message || 'Error de conexión con el agente.');
      }
    }
  })();

  return () => controller.abort();
}
