const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8080";

export async function createSession(accessToken: string, userId: string): Promise<string> {
  const r = await fetch(`${BACKEND}/api/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_token: accessToken, user_id: userId, message: "" }),
  });
  if (!r.ok) throw new Error(`createSession failed: ${r.status} ${await r.text()}`);
  const data = await r.json();
  return data.session_id as string;
}

export type StreamChunk = {
  type?: string;
  text?: string;
  thought?: string;
  tool_call?: { name?: string; args?: unknown };
  tool_result?: { name?: string; preview?: string; response?: any };
  usage_metadata?: {
    prompt_token_count?: number;
    candidates_token_count?: number;
    total_token_count?: number;
    thoughts_token_count?: number;
  };
  error?: string;
  raw?: unknown;
};

export async function streamChat(
  accessToken: string,
  userId: string,
  sessionId: string,
  message: string,
  thinkingLevel: string | undefined,
  selectedModel: string | undefined,
  onChunk: (c: StreamChunk) => void,
): Promise<void> {
  const resp = await fetch(`${BACKEND}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      access_token: accessToken,
      user_id: userId,
      session_id: sessionId,
      message,
      thinking_level: thinkingLevel,
      model: selectedModel,
    }),
  });
  if (!resp.ok || !resp.body) throw new Error(`chat failed: ${resp.status} ${await resp.text()}`);

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // Split into SSE events on blank lines
    let idx;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const rawEvent = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const lines = rawEvent.split("\n");
      let dataPayload = "";
      let eventName = "message";
      for (const line of lines) {
        if (line.startsWith("data:")) dataPayload += line.slice(5).trim();
        else if (line.startsWith("event:")) eventName = line.slice(6).trim();
      }
      if (eventName === "done") return;
      if (!dataPayload) continue;
      try {
        const parsed = JSON.parse(dataPayload);
        onChunk(parsed);
      } catch {
        // ignore unparseable chunks
      }
    }
  }
}
