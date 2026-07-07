// Atomic single-pick writer. Each UI pick fires here immediately (no debounce).
// POST /api/picks  { fixtureId, pick }  → { ok: true } | { ok: false, error }
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { allGroupFixtures } from "@/data/groups";
import { isFixtureLocked } from "@/lib/fixture-time";
import { appendOrUpdateRecentPick } from "@/lib/activity-feed-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const PICKS_COLLECTION = "quiniela_charales_picks";
const FIXTURES_BY_ID = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
const PLAYERS_BY_ID = new Map(PLAYERS.map(p => [p.id, p]));

function pickLabel(home: string, away: string, pick: string): string {
  if (pick === "H") return `Gana ${home}`;
  if (pick === "A") return `Gana ${away}`;
  return "Empate";
}

export async function POST(req: Request) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });

  let body: { fixtureId?: string; pick?: string };
  try { body = await req.json(); }
  catch { return Response.json({ ok: false, error: "invalid_json" }, { status: 400 }); }

  const { fixtureId, pick } = body ?? {};
  if (!fixtureId || !pick || !["H", "D", "A"].includes(pick)) {
    return Response.json({ ok: false, error: "invalid_params" }, { status: 400 });
  }

  const fx = FIXTURES_BY_ID.get(fixtureId);
  if (!fx) return Response.json({ ok: false, error: "not_found" }, { status: 404 });

  if (isFixtureLocked(fx)) {
    return Response.json({ ok: false, error: "locked" }, { status: 423 });
  }

  const { playerId } = auth;
  try {
    // merge:true so we only touch the one field — no race with the bulk PUT
    await db.collection(PICKS_COLLECTION).doc(playerId).set(
      { playerId, group: { [fixtureId]: { pick, source: "manual", updatedAt: Date.now() } }, updatedAt: Date.now() },
      { merge: true },
    );

    const player = PLAYERS_BY_ID.get(playerId);
    if (player) {
      const text = `${player.name} picó ${fx.home} vs ${fx.away} -> ${pickLabel(fx.home, fx.away, pick)}`;
      appendOrUpdateRecentPick(playerId, fixtureId, text).catch(() => {});
    }

    return Response.json({ ok: true });
  } catch (e) {
    console.error("[/api/picks POST]", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
