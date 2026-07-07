// HTTP surface for the workshop's keeper store. The actual GCS plumbing lives
// in src/lib/cromo-keepers.ts so both the compare page AND the live album
// pipeline read/write the same bucket without import cycles.

import { NextRequest } from "next/server";
import { PLAYERS } from "@/data/players";
import { PORTRAIT_STYLES, styleForDay } from "@/app/api/cromos/portrait/route";
import { isAdminRequest } from "@/lib/admin-gate";
import { saveKeeper, deleteKeeper, readKeeper } from "@/lib/cromo-keepers";
import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function gate(req: NextRequest): Promise<string | Response> {
  if (!(await isAdminRequest(req))) {
    return new Response("forbidden", { status: 403 });
  }
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  if (!playerId) return new Response("playerId required", { status: 400 });
  if (!PLAYERS.some(p => p.id === playerId)) return new Response("unknown player", { status: 400 });
  const styleStr = searchParams.get("style");
  const idx = styleStr === null ? NaN : parseInt(styleStr, 10);
  if (!Number.isFinite(idx) || idx < 0 || idx >= PORTRAIT_STYLES.length) {
    return new Response("invalid style", { status: 400 });
  }
  return `${playerId}::${PORTRAIT_STYLES[idx].name}`;
}

function todayKeyET(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}

export async function POST(req: NextRequest) {
  const g = await gate(req);
  if (typeof g !== "string") return g;
  const [playerId, styleName] = g.split("::");
  const buf = Buffer.from(await req.arrayBuffer());
  if (buf.length === 0) return new Response("empty body", { status: 400 });
  if (buf.length > 5 * 1024 * 1024) return new Response("too large", { status: 413 });
  await saveKeeper(playerId, styleName, buf);

  // Auto-apply: if the keeper's style matches the cromo for TODAY, drop today's
  // cached doc so the next GET regenerates from the freshly-saved keeper (1s,
  // no model call). Admin never has to ask "apply this to my album now".
  let appliedToToday = false;
  try {
    const today = todayKeyET();
    const todayStyle = styleForDay(today, undefined, false);
    if (todayStyle.name === styleName) {
      await db.collection("cromo_portraits").doc(`${playerId}_${today}`).delete();
      appliedToToday = true;
    }
  } catch (e) {
    console.warn("[keeper POST] today-doc cleanup failed (non-fatal)", e instanceof Error ? e.message : e);
  }

  return Response.json({ ok: true, bytes: buf.length, style: styleName, appliedToToday });
}

export async function DELETE(req: NextRequest) {
  const g = await gate(req);
  if (typeof g !== "string") return g;
  const [playerId, styleName] = g.split("::");
  try {
    await deleteKeeper(playerId, styleName);
    return Response.json({ ok: true, removed: true });
  } catch {
    return Response.json({ ok: true, removed: false });
  }
}

export async function GET(req: NextRequest) {
  const g = await gate(req);
  if (typeof g !== "string") return g;
  const [playerId, styleName] = g.split("::");
  const buf = await readKeeper(playerId, styleName);
  if (!buf) return new Response("not found", { status: 404 });
  return new Response(new Uint8Array(buf), {
    status: 200,
    headers: { "content-type": "image/png", "cache-control": "no-store" },
  });
}

// Re-export for callers (variant route) that historically imported from here.
export { readKeeper, listKeepers } from "@/lib/cromo-keepers";
