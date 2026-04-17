import type { Session, WSMessage } from '../types';

const API_KEY = localStorage.getItem('sockagent-api-key') || '';

function headers(): Record<string, string> {
  const h: Record<string, string> = { 'Content-Type': 'application/json' };
  if (API_KEY) h['X-API-Key'] = API_KEY;
  return h;
}

export async function healthCheck(): Promise<Record<string, string>> {
  const res = await fetch('/api/health');
  return res.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch('/api/sessions', { headers: headers() });
  return res.json();
}

export async function deleteSession(id: string): Promise<void> {
  await fetch(`/api/sessions/${id}`, { method: 'DELETE', headers: headers() });
}

export async function sendMessage(
  message: string,
  sessionId?: string,
  model?: string,
): Promise<{ response: string; session_id: string; model: string }> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ message, session_id: sessionId, model }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export function createWebSocket(
  onMessage: (msg: WSMessage) => void,
  onClose?: () => void,
): WebSocket {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${proto}//${location.host}/ws/chat`);

  ws.onmessage = (event) => {
    const data: WSMessage = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onclose = () => onClose?.();

  return ws;
}

export function sendWSMessage(
  ws: WebSocket,
  message: string,
  sessionId?: string,
  model?: string,
): void {
  ws.send(
    JSON.stringify({
      message,
      session_id: sessionId,
      model,
      api_key: API_KEY || undefined,
    }),
  );
}
