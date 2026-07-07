// GET ?playerId=X  -> public read of any player's Mundial picks
// PUT { payload }   -> auth required, can only write own picks
import { readAuth } from "@/lib/auth-server";
import { getPicks, upsertPicks } from "@/lib/predictions-server";
import { appendOrUpdateRecentPick } from "@/lib/activity-feed-server";
import { allGroupFixtures } from "@/data/groups";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const FIXTURES_BY_ID = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
const PLAYERS_BY_ID = new Map(PLAYERS.map(p => [p.id, p]));

function pickLabel(home: string, away: string, pick: string): string {
  if (pick === "H") return `Gana ${home}`;
  if (pick === "A") return `Gana ${away}`;
  if (pick === "D") return "Empate";
  return pick;
}

type RawGroupPick = { pick?: string };

async function emitPickChanges(
  playerId: string,
  oldPicks: Record<string, unknown> | null | undefined,
  newPicks: Record<string, unknown> | null | undefined,
): Promise<void> {
  const player = PLAYERS_BY_ID.get(playerId);
  if (!player) return;
  const oldGroup = (oldPicks?.group ?? {}) as Record<string, RawGroupPick>;
  const newGroup = (newPicks?.group ?? {}) as Record<string, RawGroupPick>;
  const ids = new Set(Object.keys(newGroup));
  for (const fxId of ids) {
    const np = newGroup[fxId]?.pick;
    const op = oldGroup[fxId]?.pick;
    if (!np || np === op) continue;
    const fx = FIXTURES_BY_ID.get(fxId);
    if (!fx) continue;
    const text = `${player.name} picó ${fx.home} vs ${fx.away} -> ${pickLabel(fx.home, fx.away, np)}`;
    try {
      await appendOrUpdateRecentPick(playerId, fxId, text);
    } catch (e) {
      console.error("[activity] pick emit failed", fxId, e);
    }
  }
  // TODO: leader_change, streak, exact_score — require server-side scoring
  // access (real finals + recomputing the leaderboard). Wire in once scoring
  // moves server-side or we add a /api/cron hook.
}

export async function GET(req: Request) {
  const url = new URL(req.url);
  const playerId = url.searchParams.get("playerId");
  if (!playerId) return Response.json({ ok: false, error: "playerId required" }, { status: 400 });
  try {
    const picks = await getPicks(playerId);
    return Response.json({ ok: true, picks });
  } catch (e) {
    console.error("[/api/predictions GET] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  let body: { payload?: Record<string, unknown> };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid json" }, { status: 400 });
  }
  if (!body.payload || typeof body.payload !== "object") {
    return Response.json({ ok: false, error: "payload required" }, { status: 400 });
  }
  try {
    const before = await getPicks(auth.playerId);
    const saved = await upsertPicks(auth.playerId, body.payload);
    // Fire-and-forget: don't block the response on feed writes.
    void emitPickChanges(auth.playerId, before, body.payload).catch(e =>
      console.error("[/api/predictions PUT] emit failed", e),
    );
    // Return canonical merged picks so the client can ack and update
    // localStorage immediately, eliminating the SSE race where stale data
    // arrives just after a fresh pick and reverts it.
    return Response.json({ ok: true, picks: saved });
  } catch (e) {
    console.error("[/api/predictions PUT] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
