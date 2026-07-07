// POST  body: { playerId, picks, fillOnlyEmpty }
// Merges incoming AI picks into the player's stored picks, tagging each with source:"ai".
// Gated by x-q26-agent-secret.
import { getPicks, upsertPicks } from "@/lib/predictions-server";
import type { GroupPrediction, PlayerPredictions, Pick1X2 } from "@/lib/predictions";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type IncomingPick = {
  fixtureId: string;
  pick: Pick1X2;
  homeGoals?: number;
  awayGoals?: number;
};

type Body = {
  playerId?: string;
  picks?: IncomingPick[];
  fillOnlyEmpty?: boolean;
};

export async function POST(req: Request) {
  const secret = process.env.Q26_AGENT_SECRET;
  if (!secret) return Response.json({ ok: false, error: "server misconfigured" }, { status: 500 });
  if (req.headers.get("x-q26-agent-secret") !== secret) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  let body: Body;
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid json" }, { status: 400 });
  }

  const playerId = body.playerId;
  if (!playerId) return Response.json({ ok: false, error: "playerId required" }, { status: 400 });
  if (!Array.isArray(body.picks)) return Response.json({ ok: false, error: "picks required" }, { status: 400 });

  const fillOnlyEmpty = body.fillOnlyEmpty !== false;
  const aiAt = Date.now();

  try {
    const current = (await getPicks(playerId)) as Partial<PlayerPredictions> | null;
    const merged: Record<string, unknown> = {
      playerId,
      group: { ...(current?.group ?? {}) },
      bracket: current?.bracket ?? {},
      updatedAt: aiAt,
    };
    if (current?.champion !== undefined) merged.champion = current.champion;
    if (current?.runnerUp !== undefined) merged.runnerUp = current.runnerUp;
    if (current?.championLockedAt !== undefined) merged.championLockedAt = current.championLockedAt;
    if (current?.runnerUpLockedAt !== undefined) merged.runnerUpLockedAt = current.runnerUpLockedAt;
    const group = merged.group as Record<string, GroupPrediction>;

    let written = 0;
    let skipped = 0;
    for (const incoming of body.picks) {
      if (!incoming?.fixtureId || !incoming.pick) {
        skipped++;
        continue;
      }
      const existing = group[incoming.fixtureId];
      // Hard rule: ONLY overwrite a slot that was previously an AI pick. Anything
      // manual or untagged (= saved before this feature shipped) is sacred.
      if (existing?.pick && existing.source !== "ai") { skipped++; continue; }
      if (existing?.pick && existing.source === "ai" && fillOnlyEmpty) { skipped++; continue; }
      const next: GroupPrediction = {
        pick: incoming.pick,
        source: "ai",
        aiAt,
      };
      if (Number.isFinite(incoming.homeGoals)) next.homeGoals = incoming.homeGoals;
      if (Number.isFinite(incoming.awayGoals)) next.awayGoals = incoming.awayGoals;
      group[incoming.fixtureId] = next;
      written++;
    }

    await upsertPicks(playerId, merged);
    return Response.json({ ok: true, written, skipped });
  } catch (e) {
    console.error("[/api/ai-predictions/commit] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
