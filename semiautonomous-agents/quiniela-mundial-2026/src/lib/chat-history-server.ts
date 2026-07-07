// Server-side reader for per-player chat history persisted by the ADK agent.
// Reads from `quiniela_charales_chats/{playerId}/events`.
import { db } from "@/lib/firestore-server";

export type ChatMessage = {
  id: string;
  role: "user" | "model" | "assistant" | "system" | "tool" | null;
  text: string | null;
  ts: number; // ADK event timestamp (Unix seconds)
  serverTs: number | null; // Firestore SERVER_TIMESTAMP, ms
  sessionId: string | null;
};

export type ChatHistory = {
  playerId: string;
  messageCount: number;
  lastMessageAt: number | null;
  lastMessage: string | null;
  messages: ChatMessage[];
};

const PARENT = "quiniela_charales_chats";
const EVENTS = "events";

export async function getChatHistory(
  playerId: string,
  opts: { limit?: number } = {}
): Promise<ChatHistory> {
  const parentRef = db.collection(PARENT).doc(playerId);
  const [parentSnap, eventsSnap] = await Promise.all([
    parentRef.get(),
    parentRef
      .collection(EVENTS)
      .orderBy("seq", "asc")
      .limit(opts.limit ?? 500)
      .get(),
  ]);

  const meta = parentSnap.exists ? (parentSnap.data() ?? {}) : {};
  const messages: ChatMessage[] = eventsSnap.docs
    .map(d => {
      const data = d.data() as {
        seq?: number;
        ts?: { toMillis?: () => number } | null;
        role?: string | null;
        text?: string | null;
        sessionId?: string | null;
      };
      return {
        id: d.id,
        role: (data.role ?? null) as ChatMessage["role"],
        text: data.text ?? null,
        ts: typeof data.seq === "number" ? data.seq : 0,
        serverTs: data.ts?.toMillis ? data.ts.toMillis() : null,
        sessionId: data.sessionId ?? null,
      };
    })
    // Display only events with text content (skip tool-call events).
    .filter(m => (m.text ?? "").trim().length > 0);

  return {
    playerId,
    messageCount: typeof meta.messageCount === "number" ? meta.messageCount : messages.length,
    lastMessageAt:
      meta.lastMessageAt && typeof meta.lastMessageAt.toMillis === "function"
        ? meta.lastMessageAt.toMillis()
        : null,
    lastMessage: typeof meta.lastMessage === "string" ? meta.lastMessage : null,
    messages,
  };
}

export async function listPlayerChats(): Promise<
  { playerId: string; messageCount: number; lastMessageAt: number | null; lastMessage: string | null }[]
> {
  const snap = await db.collection(PARENT).get();
  return snap.docs.map(d => {
    const data = d.data() as {
      messageCount?: number;
      lastMessageAt?: { toMillis?: () => number } | null;
      lastMessage?: string | null;
    };
    return {
      playerId: d.id,
      messageCount: typeof data.messageCount === "number" ? data.messageCount : 0,
      lastMessageAt:
        data.lastMessageAt && typeof data.lastMessageAt.toMillis === "function"
          ? data.lastMessageAt.toMillis()
          : null,
      lastMessage: typeof data.lastMessage === "string" ? data.lastMessage : null,
    };
  });
}
