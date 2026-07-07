// Maintenance-mode gateway. Streams SSE from the q26-maint-bridge running on
// the dev VM (Claude Agent SDK + repo write access). Restricted to player
// "jesus"; auth-checked by cookie. Bearer token added server-side so the
// bridge URL/token never leave Cloud Run.

import { readAuth } from "@/lib/auth-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BRIDGE_URL = process.env.Q26_MAINT_BRIDGE_URL;
const BRIDGE_TOKEN = process.env.Q26_MAINT_BRIDGE_TOKEN;
const ALLOWED_USER = "jesus";

export async function POST(req: Request) {
  if (!BRIDGE_URL || !BRIDGE_TOKEN) {
    return new Response("maintenance bridge not configured", { status: 503 });
  }
  const session = await readAuth();
  if (!session || session.playerId !== ALLOWED_USER) {
    return new Response("forbidden", { status: 403 });
  }

  let body: { message?: string; bypass?: boolean };
  try {
    body = await req.json();
  } catch {
    return new Response("invalid json", { status: 400 });
  }
  if (!body.message || typeof body.message !== "string") {
    return new Response("message required", { status: 400 });
  }

  const upstream = await fetch(`${BRIDGE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${BRIDGE_TOKEN}`,
    },
    body: JSON.stringify({
      userId: ALLOWED_USER,
      message: body.message,
      bypass: Boolean(body.bypass),
    }),
  });

  if (!upstream.ok || !upstream.body) {
    const txt = await upstream.text().catch(() => "");
    return new Response(`bridge error ${upstream.status}: ${txt.slice(0, 200)}`, { status: 502 });
  }

  // Wrap the upstream body in a fresh stream that emits an immediate flush
  // comment + 2KB padding so Cloudflare's edge proxy doesn't buffer the
  // response before the first SDK event arrives (which can take 3-5s).
  const reader = upstream.body.getReader();
  const stream = new ReadableStream({
    async start(controller) {
      const enc = new TextEncoder();
      controller.enqueue(enc.encode(": " + " ".repeat(2048) + "\n\n"));
      controller.enqueue(enc.encode(": connected\n\n"));
      try {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          if (value) controller.enqueue(value);
        }
      } catch (e) {
        controller.enqueue(enc.encode(`data: ${JSON.stringify({ type: "error", error: (e as Error).message })}\n\n`));
      } finally {
        controller.close();
      }
    },
    cancel() {
      reader.cancel().catch(() => {});
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-store, no-transform, must-revalidate",
      "Content-Encoding": "identity",
      "X-Accel-Buffering": "no",
      Connection: "keep-alive",
    },
  });
}
