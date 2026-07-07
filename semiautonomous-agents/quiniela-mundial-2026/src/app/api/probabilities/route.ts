// GET /api/probabilities
//
// Returns the latest blended per-fixture {H, D, A} probabilities for every
// group-stage match. By default returns the cached `current` snapshot from
// Firestore (fast). Pass ?recompute=1 to force a fresh blend + snapshot
// write (used by the cron and during local development).

import { buildAllFixtureProbs } from "@/lib/probabilities-builder";
import {
  readFixtureProbs,
  writeFixtureProbs,
  type FixtureProbsDoc,
} from "@/lib/probability-snapshots";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const recompute = url.searchParams.get("recompute") === "1";
  try {
    let doc: FixtureProbsDoc | null = null;
    if (!recompute) {
      doc = await readFixtureProbs();
    }
    if (!doc) {
      const built = await buildAllFixtureProbs();
      doc = await writeFixtureProbs({
        fixtures: built.byFixture,
        source: "blend-v2",
      });
    }
    return Response.json({
      ok: true,
      snapshotDate: doc.snapshotDate,
      updatedAt: doc.updatedAt,
      source: doc.source,
      count: Object.keys(doc.fixtures).length,
      fixtures: doc.fixtures,
    });
  } catch (e) {
    console.error("[/api/probabilities GET] error", e);
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}

// POST /api/probabilities — force recompute. Same shape as the recompute=1 GET
// but reachable from internal callers (cron) without query encoding.
export async function POST() {
  try {
    const built = await buildAllFixtureProbs();
    const doc = await writeFixtureProbs({
      fixtures: built.byFixture,
      source: "blend-v2",
    });
    return Response.json({
      ok: true,
      snapshotDate: doc.snapshotDate,
      updatedAt: doc.updatedAt,
      marketUpdates: built.marketUpdates,
      ingestedFinals: built.ingestedFinals,
      count: Object.keys(doc.fixtures).length,
    });
  } catch (e) {
    console.error("[/api/probabilities POST] error", e);
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
