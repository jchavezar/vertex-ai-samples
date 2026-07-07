// Presence ping: writes/updates `presence/{playerId}` with last heartbeat and
// (optionally) current path/action. Auth required. Called from
// player-context.tsx every 60s + on visibility change.
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export const PRESENCE_COLLECTION = "presence";

type PingBody = {
  currentPath?: string;
  action?: string;
};

export async function POST(req: Request) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });

  let body: PingBody = {};
  try {
    const json = (await req.json()) as PingBody;
    if (json && typeof json === "object") body = json;
  } catch {
    /* empty body is fine */
  }

  const now = Date.now();
  const doc: Record<string, unknown> = {
    playerId: auth.playerId,
    lastPing: now,
  };
  if (typeof body.currentPath === "string" && body.currentPath.length > 0) {
    doc.currentPath = body.currentPath.slice(0, 200);
  }
  if (typeof body.action === "string" && body.action.length > 0) {
    doc.action = body.action.slice(0, 40);
  }

  try {
    await db.collection(PRESENCE_COLLECTION).doc(auth.playerId).set(doc, { merge: true });
    return Response.json({ ok: true, lastPing: now });
  } catch (e) {
    console.error("[/api/presence/ping] firestore error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
