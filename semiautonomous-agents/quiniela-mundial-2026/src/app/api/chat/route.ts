// BFF endpoint. Forwards to the ADK agent Cloud Run service with an ID token.
// The agent runs google_search-grounded Gemini 3.1 Flash Lite (Vertex global).
// Requires a valid q26_chat_auth cookie (player + PIN-backed session).

import { GoogleAuth } from "google-auth-library";
import { readAuth } from "@/lib/auth-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const AGENT_URL = process.env.AGENT_URL;

const auth = new GoogleAuth();
let cachedClient: Awaited<ReturnType<GoogleAuth["getIdTokenClient"]>> | null = null;
async function getClient(audience: string) {
  if (!cachedClient) cachedClient = await auth.getIdTokenClient(audience);
  return cachedClient;
}

export async function POST(req: Request) {
  if (!AGENT_URL) {
    return new Response("AGENT_URL not configured", { status: 500 });
  }

  const session = await readAuth();
  if (!session) {
    return new Response("unauthorized", { status: 401 });
  }

  let body: { messages?: { role: "user" | "assistant"; text: string }[]; sessionId?: string; userId?: string; tone?: "picante" | "suave" | "ava" | "agi" };
  try {
    body = await req.json();
  } catch {
    return new Response("invalid json", { status: 400 });
  }

  const messages = (body.messages || []).filter(m => m && typeof m.text === "string" && m.text.trim());
  if (messages.length === 0) return new Response("no messages", { status: 400 });
  const last = messages[messages.length - 1];
  if (last.role !== "user") return new Response("last message must be user", { status: 400 });

  let token: string;
  try {
    const client = await getClient(AGENT_URL);
    const headers = await client.getRequestHeaders(AGENT_URL);
    const authHeader = headers.get("authorization") || headers.get("Authorization");
    if (!authHeader) throw new Error("no auth header");
    token = authHeader.replace(/^Bearer\s+/i, "");
  } catch (e) {
    return new Response(`auth failed: ${(e as Error).message}`, { status: 500 });
  }

  const upstream = await fetch(`${AGENT_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message: last.text,
      sessionId: body.sessionId || session.playerId,
      userId: session.playerId,
      userName: PLAYERS.find(p => p.id === session.playerId)?.name || session.playerId,
      // Normalize tone for the upstream ADK agent. Legacy "agi" key from older
      // clients maps to "ava". Default to suave when omitted/unknown.
      tone: body.tone === "ava" || body.tone === "agi" ? "ava" : body.tone === "picante" ? "picante" : "suave",
    }),
  });

  if (!upstream.ok || !upstream.body) {
    const errText = await upstream.text().catch(() => "");
    return new Response(`agent ${upstream.status}: ${errText}`, { status: 502 });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Accel-Buffering": "no",
    },
  });
}
