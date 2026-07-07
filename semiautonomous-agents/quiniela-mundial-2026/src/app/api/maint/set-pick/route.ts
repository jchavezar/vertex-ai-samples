// Admin one-shot: write/overwrite a group-stage pick for any player. Used
// when a compa's pick silently failed to sync (multi-device overwrite or
// 401-during-write) and we need to repair the Firestore record without
// asking them to refill.
//
// Gated to cookie playerId === "jesus" or x-admin-secret header. BYPASSES
// the fixture lock — admin can repair picks that were made before kickoff
// but didn't make it to Firestore. Don't expose this to non-admin clients.

import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { getPicks, PICKS_COLLECTION } from "@/lib/predictions-server";
import { allGroupFixtures } from "@/data/groups";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function authorize(req: NextRequest): Promise<boolean> {
  const secret = process.env.ADMIN_SECRET;
  if (secret && req.headers.get("x-admin-secret") === secret) return true;
  const auth = await readAuth();
  return auth?.playerId === "jesus";
}

type Pick = "H" | "D" | "A";

export async function POST(req: NextRequest) {
  if (!(await authorize(req))) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  type Body = {
    playerId?: string;
    fixtureId?: string;
    pick?: Pick;
    homeGoals?: number;
    awayGoals?: number;
  };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}

  const playerId = (body.playerId ?? "").trim();
  const fixtureId = (body.fixtureId ?? "").trim();
  if (!playerId || !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  const fixtures = allGroupFixtures();
  if (!fixtureId || !fixtures.some(fx => fx.id === fixtureId)) {
    return Response.json({ ok: false, error: "unknown_fixture" }, { status: 400 });
  }
  const pick = body.pick;
  if (pick !== "H" && pick !== "D" && pick !== "A") {
    return Response.json({ ok: false, error: "pick_must_be_H_D_or_A" }, { status: 400 });
  }
  const hg = typeof body.homeGoals === "number" ? body.homeGoals : undefined;
  const ag = typeof body.awayGoals === "number" ? body.awayGoals : undefined;

  const existing = (await getPicks(playerId)) ?? {};
  const existingGroup = (existing.group ?? {}) as Record<string, unknown>;
  const prior = existingGroup[fixtureId];
  const nextGroup = {
    ...existingGroup,
    [fixtureId]: {
      pick,
      ...(typeof hg === "number" ? { homeGoals: hg } : {}),
      ...(typeof ag === "number" ? { awayGoals: ag } : {}),
      source: "maint",
    },
  };
  // Direct Firestore write — bypasses the kickoff lock in upsertPicks. The
  // admin gate above is the only access control for this path.
  const ref = db.collection(PICKS_COLLECTION).doc(playerId);
  await ref.set({
    ...existing,
    group: nextGroup,
    playerId,
    updatedAt: Date.now(),
  }, { merge: false });

  return Response.json({
    ok: true,
    playerId,
    fixtureId,
    written: { pick, homeGoals: hg, awayGoals: ag },
    prior,
  });
}
