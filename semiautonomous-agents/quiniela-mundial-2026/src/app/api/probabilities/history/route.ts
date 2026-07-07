// GET /api/probabilities/history?fixtureId=A-M1
// GET /api/probabilities/history?teamId=BRA
//
// Returns the time-series of daily snapshots for either:
//   - A specific fixture (H/D/A over time), OR
//   - A specific team (P(champion), P(SF), P(R16) over time).
//
// Driven by the `fixture_probabilities_history` and `bracket_probabilities_history`
// collections written every time we re-blend / re-simulate.

import {
  listFixtureProbsHistory,
  listBracketProbsHistory,
} from "@/lib/probability-snapshots";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const fixtureId = url.searchParams.get("fixtureId");
  const teamId = url.searchParams.get("teamId");
  const limit = Math.max(1, Math.min(180, Number(url.searchParams.get("limit") ?? "60")));

  try {
    if (fixtureId) {
      const docs = await listFixtureProbsHistory(limit);
      const series = docs
        .map(d => ({
          date: d.snapshotDate,
          probs: d.fixtures[fixtureId]?.probs ?? null,
        }))
        .filter(p => p.probs !== null)
        .reverse(); // chronological for charting
      return Response.json({
        ok: true,
        kind: "fixture",
        fixtureId,
        series,
      });
    }
    if (teamId) {
      const docs = await listBracketProbsHistory(limit);
      const series = docs
        .map(d => ({
          date: d.snapshotDate,
          team: d.teams[teamId] ?? null,
        }))
        .filter(p => p.team !== null)
        .reverse();
      return Response.json({
        ok: true,
        kind: "team",
        teamId,
        series,
      });
    }
    return Response.json({ ok: false, error: "must provide fixtureId or teamId" }, { status: 400 });
  } catch (e) {
    console.error("[/api/probabilities/history GET] error", e);
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
