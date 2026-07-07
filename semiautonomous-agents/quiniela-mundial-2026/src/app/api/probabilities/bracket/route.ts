// GET /api/probabilities/bracket
//
// Returns per-team bracket probabilities (P(R32), P(R16), ..., P(champion))
// from a 10k Monte Carlo simulation of the tournament using the latest
// per-fixture probabilities + the real results we've already ingested.
//
// Cached in Firestore as the `current` snapshot. Use ?recompute=1 to force.

import { simulateBracket } from "@/lib/bracket-simulator";
import {
  readBracketProbs,
  writeBracketProbs,
  readFixtureProbs,
  writeFixtureProbs,
  type BracketProbsDoc,
} from "@/lib/probability-snapshots";
import { buildAllFixtureProbs } from "@/lib/probabilities-builder";
import { allGroupFixtures } from "@/data/groups";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const SIM_ITERS = 10_000;

export async function GET(req: Request) {
  const url = new URL(req.url);
  const recompute = url.searchParams.get("recompute") === "1";
  try {
    let doc: BracketProbsDoc | null = null;
    if (!recompute) {
      doc = await readBracketProbs();
    }
    if (!doc) {
      doc = await runAndPersist();
    }
    return Response.json({
      ok: true,
      snapshotDate: doc.snapshotDate,
      updatedAt: doc.updatedAt,
      simulations: doc.simulations,
      teams: doc.teams,
    });
  } catch (e) {
    console.error("[/api/probabilities/bracket GET] error", e);
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}

export async function POST() {
  try {
    const doc = await runAndPersist();
    return Response.json({
      ok: true,
      snapshotDate: doc.snapshotDate,
      updatedAt: doc.updatedAt,
      simulations: doc.simulations,
    });
  } catch (e) {
    console.error("[/api/probabilities/bracket POST] error", e);
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}

async function runAndPersist(): Promise<BracketProbsDoc> {
  let fixtureProbs = await readFixtureProbs();
  if (!fixtureProbs) {
    const built = await buildAllFixtureProbs();
    fixtureProbs = await writeFixtureProbs({
      fixtures: built.byFixture,
      source: "blend-v2",
    });
  }
  const probsMap: Record<string, { H: number; D: number; A: number }> = {};
  for (const fx of allGroupFixtures()) {
    const e = fixtureProbs.fixtures[fx.id];
    if (e) probsMap[fx.id] = e.probs;
  }
  const sim = simulateBracket({
    probs: probsMap,
    iterations: SIM_ITERS,
    seed: Date.now() & 0xffffffff,
  });
  return writeBracketProbs({
    simulations: sim.simulations,
    teams: sim.teams,
  });
}
