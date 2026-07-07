// SSE endpoint: pushes Firestore pick changes to the client in real time.
// Each authenticated user gets their own stream. Firestore onSnapshot fires
// immediately with current state, then again on every server-side write.
//
// Cloud Run default timeout is 300s. We self-close at 240s and rely on
// EventSource's native auto-reconnect so clients never stall.
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const SELF_CLOSE_MS = 240_000; // 4 min — under Cloud Run 300s default
const HEARTBEAT_MS  = 25_000;  // keep connection alive

export async function GET(req: Request) {
  const auth = await readAuth();
  if (!auth) return new Response("Unauthorized", { status: 401 });

  const { playerId } = auth;
  const enc = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      let closed = false;

      const enqueue = (chunk: string) => {
        if (closed) return;
        try { controller.enqueue(enc.encode(chunk)); } catch { closed = true; }
      };

      const close = () => {
        if (closed) return;
        closed = true;
        clearInterval(heartbeat);
        clearTimeout(selfClose);
        unsub();
        try { controller.close(); } catch {}
      };

      // Firestore real-time listener — fires immediately with current doc,
      // then on every write from any device/tab.
      const unsub = db
        .collection("quiniela_charales_picks")
        .doc(playerId)
        .onSnapshot(
          (snap) => {
            if (!snap.exists) return;
            enqueue(`data: ${JSON.stringify({ type: "picks", picks: snap.data() })}\n\n`);
          },
          () => close(),
        );

      const heartbeat = setInterval(() => enqueue(": heartbeat\n\n"), HEARTBEAT_MS);
      const selfClose = setTimeout(close, SELF_CLOSE_MS);

      req.signal.addEventListener("abort", close);
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type":  "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      "Connection":    "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
