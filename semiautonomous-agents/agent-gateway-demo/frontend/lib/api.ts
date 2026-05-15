// SSE consumer + small REST helpers. Cribbed from
// adk-drive-ae/frontend/lib/api.ts:23-73 with the message shape adapted for
// our backend (session_id flow + access_token).

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080";

export type AgentEvent =
  | { type: "event"; author?: string; text?: string; tool_call?: { name: string; args: any }; tool_result?: { name: string; preview: string } }
  | { type: "error"; error: string }
  | { type: "done" };

export async function createSession(accessToken: string, userId = "anon"): Promise<{ session_id: string }> {
  const r = await fetch(`${BACKEND}/api/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_token: accessToken, user_id: userId }),
  });
  if (!r.ok) throw new Error(`createSession ${r.status}: ${await r.text()}`);
  return r.json();
}

export async function* streamChat(opts: {
  message: string;
  sessionId: string;
  userId?: string;
  signal?: AbortSignal;
}): AsyncGenerator<AgentEvent> {
  const r = await fetch(`${BACKEND}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ message: opts.message, session_id: opts.sessionId, user_id: opts.userId || "anon" }),
    signal: opts.signal,
  });
  if (!r.ok || !r.body) throw new Error(`/api/chat ${r.status}: ${await r.text()}`);

  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n\n")) !== -1) {
      const chunk = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      const lines = chunk.split("\n");
      let event = "message";
      let data = "";
      for (const ln of lines) {
        if (ln.startsWith("event:")) event = ln.slice(6).trim();
        else if (ln.startsWith("data:")) data += ln.slice(5).trim();
      }
      if (event === "done") {
        yield { type: "done" };
        return;
      }
      if (data) {
        try { yield JSON.parse(data); } catch { /* skip */ }
      }
    }
  }
}

export async function backendHealth(): Promise<any> {
  const r = await fetch(`${BACKEND}/api/health`);
  return r.json();
}
