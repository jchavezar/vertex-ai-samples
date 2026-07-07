// Returns the chat history for the authenticated player.
// Used by ChatBot on first open to hydrate across devices.
import { readAuth } from "@/lib/auth-server";
import { getChatHistory } from "@/lib/chat-history-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const session = await readAuth();
  if (!session) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  try {
    const history = await getChatHistory(session.playerId);
    return Response.json({ ok: true, history });
  } catch (e) {
    console.error("[/api/chat/history] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
